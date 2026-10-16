from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="EcoTwin AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bins = [
    {"id": 1, "name": "Library", "zone": "Academic", "category": "Paper", "fill": 42},
    {"id": 2, "name": "Science Block", "zone": "Academic", "category": "Plastic", "fill": 68},
    {"id": 3, "name": "Cafeteria", "zone": "Food", "category": "Organic", "fill": 91},
    {"id": 4, "name": "Hostel A", "zone": "Residential", "category": "Mixed", "fill": 73},
    {"id": 5, "name": "Hostel B", "zone": "Residential", "category": "Plastic", "fill": 35},
    {"id": 6, "name": "Sports Ground", "zone": "Recreation", "category": "Mixed", "fill": 56},
    {"id": 7, "name": "Auditorium", "zone": "Academic", "category": "Paper", "fill": 82},
    {"id": 8, "name": "Garden", "zone": "Food", "category": "Organic", "fill": 27},
]

inventory = {
    "plastic": 42,
    "paper": 28,
    "organic": 67,
    "glass": 20,
    "metal": 15,
}

total_waste = 128.0
recycled_waste = 76.0
deposit_count = 0

DISPOSAL = {
    "plastic": {
        "bin": "Blue recycling bin",
        "instruction": "Empty and rinse containers before recycling."
    },
    "paper": {
        "bin": "Paper recycling bin",
        "instruction": "Keep paper clean and dry."
    },
    "organic": {
        "bin": "Green compost bin",
        "instruction": "Separate food scraps from packaging."
    },
    "glass": {
        "bin": "Glass recycling bin",
        "instruction": "Handle glass carefully and use the designated bin."
    },
    "metal": {
        "bin": "Metal recycling bin",
        "instruction": "Empty cans before placing them in recycling."
    },
}


class DepositRequest(BaseModel):
    category: str
    weight_kg: float = 1.0


class ScenarioRequest(BaseModel):
    segregation_improvement: int = 20
    collection_frequency: int = 2


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/app.js")
def frontend_js():
    return FileResponse(BASE_DIR / "app.js", media_type="text/javascript")


@app.get("/styles.css")
def frontend_css():
    return FileResponse(BASE_DIR / "styles.css", media_type="text/css")


@app.get("/api/dashboard")
def dashboard():
    return {
        "total_waste_kg": round(total_waste, 1),
        "recycled_kg": round(recycled_waste, 1),
        "recycling_rate": round(recycled_waste / total_waste * 100, 1),
        "deposits": deposit_count,
        "active_bins": len(bins),
        "priority_bins": sum(item["fill"] >= 80 for item in bins),
        "inventory": inventory,
    }


@app.get("/api/bins")
def get_bins():
    return {"bins": bins}


@app.post("/api/detect")
async def detect(image: UploadFile = File(...)):
    filename = image.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPG, JPEG, PNG or WEBP image."
        )

    content = await image.read()

    if not content:
        raise HTTPException(status_code=400, detail="The image is empty.")

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image limit is 10 MB.")

    # DEMO ONLY: classification is based on the filename,
    # not on the actual image pixels.
    name = filename.lower()

    keywords = {
        "paper": ["paper", "cardboard", "newspaper", "book"],
        "organic": ["food", "banana", "apple", "organic", "peel"],
        "glass": ["glass"],
        "metal": ["metal", "can", "tin"],
        "plastic": ["plastic", "wrapper", "bottle", "cup"],
    }

    category = "plastic"

    for candidate, words in keywords.items():
        if any(word in name for word in words):
            category = candidate
            break

    return {
        "category": category,
        "bin": DISPOSAL[category]["bin"],
        "instruction": DISPOSAL[category]["instruction"],
        "notice": "Demo result based on the filename, not visual AI."
    }


@app.post("/api/deposit")
def deposit(data: DepositRequest):
    global total_waste, recycled_waste, deposit_count

    category = data.category.lower()

    if category not in DISPOSAL:
        raise HTTPException(status_code=400, detail="Unknown category.")

    if not 0.1 <= data.weight_kg <= 100:
        raise HTTPException(
            status_code=400,
            detail="Weight must be between 0.1 and 100 kg."
        )

    deposit_count += 1
    total_waste += data.weight_kg

    if category != "organic":
        recycled_waste += data.weight_kg

    inventory[category] += 1

    target = min(bins, key=lambda item: item["fill"])
    target["fill"] = min(100, target["fill"] + 3)

    return {
        "message": "Demo deposit confirmed.",
        "dashboard": dashboard()
    }


@app.get("/api/insights")
def insights():
    results = []

    for item in bins:
        if item["fill"] >= 80:
            results.append({
                "priority": "High",
                "title": "Collect " + item["name"],
                "message": (
                    f"The simulated bin is {item['fill']}% full. "
                    "Prioritize collection."
                )
            })

    results.extend([
        {
            "priority": "Medium",
            "title": "Improve waste segregation",
            "message": "Use clear labels and separate recyclable materials."
        },
        {
            "priority": "Medium",
            "title": "Review collection schedules",
            "message": "Compare simulated bin levels before changing schedules."
        }
    ])

    return {"insights": results}


@app.post("/api/simulate")
def simulate():
    ordered = sorted(
        bins,
        key=lambda item: item["fill"],
        reverse=True
    )

    return {
        "route": [
            {
                "step": index + 1,
                "location": item["name"],
                "fill": item["fill"],
                "action": "Collect now" if item["fill"] >= 80 else "Monitor"
            }
            for index, item in enumerate(ordered)
        ],
        "notice": "Simulated priority order, not GPS route optimization."
    }


@app.post("/api/what-if")
def what_if(data: ScenarioRequest):
    improvement = max(0, min(100, data.segregation_improvement))
    frequency = max(1, min(7, data.collection_frequency))

    current = recycled_waste / total_waste * 100
    projected = min(
        100,
        current + improvement * 0.35 + (frequency - 1) * 1.5
    )

    return {
        "current_recycling_rate": round(current, 1),
        "projected_recycling_rate": round(projected, 1),
        "improvement_points": round(projected - current, 1),
        "notice": "Illustrative formula, not a validated forecast."
    }