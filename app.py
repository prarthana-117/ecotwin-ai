from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# ---------------- DEMO DATA ----------------

buildings = [
    {"id": "library", "name": "Library", "water": 6200,
     "energy": 175, "health": 94, "status": "Normal"},
    {"id": "science", "name": "Science Block", "water": 12800,
     "energy": 310, "health": 61, "status": "Critical"},
    {"id": "hostel", "name": "Hostel", "water": 15400,
     "energy": 290, "health": 78, "status": "Attention"},
    {"id": "cafeteria", "name": "Cafeteria", "water": 9800,
     "energy": 245, "health": 72, "status": "Attention"}
]

alerts = [
    {"id": 1, "title": "High Water Flow Detected",
     "building": "Science Block", "severity": "Critical",
     "category": "Water",
     "description": "Unusual water flow during non-peak hours.",
     "status": "open"},
    {"id": 2, "title": "High Energy Consumption",
     "building": "Cafeteria", "severity": "Medium",
     "category": "Energy",
     "description": "Energy usage is above the demo baseline.",
     "status": "open"},
    {"id": 3, "title": "Waste Bin Nearly Full",
     "building": "Hostel", "severity": "Medium",
     "category": "Waste",
     "description": "Waste bin is estimated to be nearly full.",
     "status": "open"}
]

reuse_items = [
    {"id": 1, "item": "Study desks", "department": "Admin Block",
     "quantity": 12, "condition": "Good"},
    {"id": 2, "item": "Lab stools", "department": "Science Block",
     "quantity": 20, "condition": "Usable"},
    {"id": 3, "item": "Reference books", "department": "Library",
     "quantity": 45, "condition": "Good"},
    {"id": 4, "item": "Desktop monitors", "department": "IT Lab",
     "quantity": 6, "condition": "Needs testing"}
]

actions = []
claimed_items = set()
next_alert_id = 4

# ---------------- WEBSITE ----------------

PAGE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EcoTwin AI - Smart Campus</title>

<style>
*{box-sizing:border-box}
body{margin:0;background:#07131e;color:#e8f3f6;
font:14px Arial,sans-serif}
button,input,select,textarea{font:inherit}
button{cursor:pointer}
.layout{display:flex;min-height:100vh}
.sidebar{width:220px;background:#06101a;padding:18px;
flex-shrink:0;border-right:1px solid #254252}
.sidebar h2{color:#40e28b}
.sidebar button{display:block;width:100%;text-align:left;
padding:12px;margin:4px 0;border:0;border-radius:7px;
background:transparent;color:#d7e9ef}
.sidebar button:hover,.sidebar button.active{
background:#124333}
main{flex:1;min-width:0;padding:22px}
header{display:flex;justify-content:space-between;
align-items:center;flex-wrap:wrap;gap:10px}
h1{font-size:26px}
h2{font-size:18px}
p{color:#a8c2cc;line-height:1.6}
.page{display:none}
.page.active{display:block}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
gap:12px;margin:20px 0}
.metric,.panel{background:#0c2433;border:1px solid #254252;
border-radius:10px;padding:16px;margin-bottom:14px}
.metric strong{display:block;color:#40e28b;font-size:23px;
margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
gap:12px}
button.primary{background:#40e28b;color:#052218;border:0;
padding:10px 14px;border-radius:7px;font-weight:bold}
button.secondary{background:#153443;color:#dff8fa;
border:1px solid #315767;padding:8px;border-radius:7px}
label{display:block;margin:14px 0;color:#c5d8df}
input,select,textarea{display:block;width:100%;margin-top:6px;
padding:10px;border:1px solid #315160;border-radius:6px;
background:#071722;color:white}
textarea{min-height:65px}
.card{padding:12px;background:#102c3b;border-radius:8px;
margin:8px 0;border:1px solid #284958}
.badge{display:inline-block;padding:5px 8px;border-radius:5px;
background:#45371b;color:#ffd166;font-size:11px}
.Critical{background:#4b1d29;color:#ff8994}
.Normal{background:#124333;color:#72f0ae}
.Attention{background:#45371b;color:#ffd166}
#campus3d{height:460px;border:1px solid #315160;
border-radius:10px;overflow:hidden;background:#071722}
#campus3d canvas{width:100%;height:100%;display:block}
.info{padding:14px;background:#071b27;border-radius:8px}
.result{color:#40e28b;font-weight:bold;margin:12px 0}
.notice{padding:12px;background:#103a30;border-radius:8px;
margin:10px 0}
footer{text-align:center;color:#7997a5;padding:20px}
@media(max-width:850px){
.layout{display:block}.sidebar{width:100%}
.sidebar button{display:inline-block;width:auto}
.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
.grid{grid-template-columns:1fr}
}
</style>
</head>

<body>
<div class="layout">
<aside class="sidebar">
<h2>🌱 EcoTwin AI</h2>
<p>Predict · Act · Prove</p>
<button class="active" data-page="dashboard">▦ Dashboard</button>
<button data-page="digital">🏢 3D Digital Twin</button>
<button data-page="alerts">⚠ Priority Alerts</button>
<button data-page="planner">✧ Mission Planner</button>
<button data-page="simulator">▥ Resource Simulator</button>
<button data-page="hostel">⌂ HostelFlow</button>
<button data-page="solar">☀ SolarTwin</button>
<button data-page="reuse">♻ ReUse University</button>
<button data-page="report">▤ Sustainability Report</button>
</aside>

<main>
<header>
<div>
<small>CAMPUS SUSTAINABILITY PLATFORM</small>
<h1 id="title">Command Center</h1>
</div>
<span>● SIMULATED DATA</span>
</header>

<div id="message"></div>

<section id="page-dashboard" class="page active">
<div class="metrics">
<div class="metric">💧 Water Usage<strong>48,250 L</strong>
<small>Litres per day</small></div>
<div class="metric">⚡ Energy<strong>1,280 kWh</strong>
<small>Per day</small></div>
<div class="metric">🚨 Active Issues<strong id="issueCount">3</strong>
<small>Open alerts</small></div>
<div class="metric">🌱 Campus Health<strong>82/100</strong>
<small>Simulated score</small></div>
</div>
<div class="grid">
<div class="panel">
<h2>Campus Buildings</h2>
<div id="buildingList"></div>
<button class="primary" onclick="go('digital')">Open 3D Twin</button>
</div>
<div class="panel">
<h2>Priority Alerts</h2>
<div id="dashboardAlerts"></div>
<button class="secondary" onclick="go('alerts')">View all alerts</button>
</div>
</div>
<div class="panel">
<h2>How EcoTwin AI works</h2>
<div class="grid">
<div><b>01 · Predict</b><p>Identify unusual resource consumption.</p></div>
<div><b>02 · Act</b><p>Recommend actions and reuse resources.</p></div>
<div><b>03 · Prove</b><p>Track actions and estimate savings.</p></div>
</div>
</div>
</section>

<section id="page-digital" class="page">
<div class="panel">
<h2>Interactive 3D Campus Digital Twin</h2>
<p>Drag to rotate. Scroll to zoom. Click a building to inspect it.</p>
<div class="grid">
<div id="campus3d"></div>
<div class="info">
<h2 id="selectedName">Science Block</h2>
<p id="selectedStatus">Critical · Simulated building profile</p>
<p>Water use: <b id="selectedWater">12,800 L/day</b></p>
<p>Energy: <b id="selectedEnergy">310 kWh/day</b></p>
<p>Health: <b id="selectedHealth">61/100</b></p>
<button class="primary" onclick="resetCamera()">Reset camera</button>
</div>
</div>
<p>🟢 Normal &nbsp; 🟡 Attention &nbsp; 🔴 Critical</p>
<div id="twinCards" class="grid"></div>
<p>All readings and building geometry are simulated.</p>
</div>
</section>

<section id="page-alerts" class="page">
<div class="panel">
<h2>Priority Alerts</h2>
<button class="primary" onclick="document.getElementById('alertForm').hidden=
!document.getElementById('alertForm').hidden">+ Add alert</button>
<form id="alertForm" hidden>
<label>Title<input name="title" required></label>
<label>Building<input name="building" required></label>
<label>Severity<select name="severity">
<option>Critical</option><option>Medium</option><option>Low</option>
</select></label>
<label>Category<select name="category">
<option>Water</option><option>Energy</option><option>Waste</option>
</select></label>
<label>Description<textarea name="description" required></textarea></label>
<button class="primary">Save alert</button>
</form>
<div id="alertList"></div>
</div>
</section>

<section id="page-planner" class="page">
<div class="panel">
<h2>Mission Planner</h2>
<p>Generate recommended actions for a campus issue.</p>
<label>Category<select id="planCategory">
<option>Water</option><option>Energy</option><option>Waste</option>
</select></label>
<label>Building<input id="planBuilding" value="Science Block"></label>
<button class="primary" onclick="makePlan()">Generate action plan</button>
<div id="planOutput"></div>
</div>
</section>

<section id="page-simulator" class="page">
<div class="panel">
<h2>What If? Resource Simulator</h2>
<label>Resource<select id="resource" onchange="simulate()">
<option>Energy</option><option>Water</option>
</select></label>
<label>Reduction target: <span id="reductionLabel">20</span>%
<input id="reduction" type="range" min="0" max="50" value="20"
oninput="simulate()"></label>
<div class="result" id="simulationResult"></div>
<p>These are illustrative estimates, not measured savings.</p>
</div>
</section>

<section id="page-hostel" class="page">
<div class="panel">
<h2>HostelFlow</h2>
<p>Manage shared laundry facilities and water schedules.</p>
<div id="machines"></div>
<form id="bookingForm">
<label>Machine<select id="machine">
<option>Laundry Machine A</option>
<option>Laundry Machine B</option>
<option>Laundry Machine C</option>
</select></label>
<label>Preferred time<select id="slot">
<option>07:00–08:00</option><option>08:00–09:00</option>
<option>18:00–19:00</option><option>19:00–20:00</option>
</select></label>
<button class="primary">Request slot</button>
</form>
<h2>Water-use schedule</h2>
<p>06:00–08:00: Hostel floors 1–3</p>
<p>18:00–20:00: Hostel floors 4–6</p>
</div>
</section>

<section id="page-solar" class="page">
<div class="panel">
<h2>SolarTwin</h2>
<p>Estimate solar power generation for campus rooftops.</p>
<label>Number of panels<input id="panels" type="number" value="100"></label>
<label>Panel capacity (kW)<input id="panelKw" type="number"
value="0.45" step="0.05"></label>
<label>Peak sun hours per day<input id="sunHours" type="number"
value="4.5" step="0.5"></label>
<label>System losses (%)<input id="loss" type="number" value="20"></label>
<button class="primary" onclick="solarCalc()">Calculate output</button>
<div id="solarResult" class="result"></div>
</div>
</section>

<section id="page-reuse" class="page">
<div class="panel">
<h2>ReUse University</h2>
<p>Find available furniture, books and equipment.</p>
<div id="reuseList" class="grid"></div>
<form id="reuseForm">
<label>Item<select id="reuseItem"></select></label>
<label>Claiming department<input id="claimDepartment" required
placeholder="Computer Science"></label>
<button class="primary">Request item</button>
</form>
</div>
</section>

<section id="page-report" class="page">
<div class="panel">
<h2>Sustainability Report</h2>
<button class="primary" onclick="loadReport()">Refresh report</button>
<div id="reportResult"></div>
<p>All figures are simulated prototype data.</p>
</div>
</section>

<footer>EcoTwin AI · Campus Sustainability Hackathon Prototype</footer>
</main>
</div>

<script>
const $ = id => document.getElementById(id);

const titles = {
dashboard:"Command Center", digital:"Campus Digital Twin",
alerts:"Priority Alerts", planner:"Mission Planner",
simulator:"What If? Simulator", hostel:"HostelFlow",
solar:"SolarTwin", reuse:"ReUse University",
report:"Sustainability Report"
};

function go(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  $("page-" + page).classList.add("active");
  document.querySelectorAll("[data-page]").forEach(b =>
    b.classList.toggle("active", b.dataset.page === page));
  $("title").textContent = titles[page];

  if (page === "digital") init3D();
  if (page === "report") loadReport();
}

document.querySelectorAll("[data-page]").forEach(b =>
  b.addEventListener("click", () => go(b.dataset.page)));

function showMessage(text) {
  $("message").innerHTML = '<div class="notice">' + text + '</div>';
  setTimeout(() => $("message").innerHTML = "", 3000);
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  })[c]);
}

// ---------------- BUILDING DASHBOARD ----------------

function renderBuildings() {
  $("buildingList").innerHTML = buildings.map(b =>
    `<div class="card">
      <b>${escapeHTML(b.name)}</b>
      <span class="badge ${b.status}">${b.status}</span>
      <p>Water: ${b.water.toLocaleString()} L/day</p>
      <p>Energy: ${b.energy} kWh/day</p>
      <p>Health: ${b.health}/100</p>
    </div>`
  ).join("");

  $("twinCards").innerHTML = $("buildingList").innerHTML;
}

// ---------------- ALERTS ----------------

function renderAlerts() {
  const open = alerts.filter(a => a.status === "open");
  $("issueCount").textContent = open.length;

  function html(a, compact = false) {
    return `<div class="card">
      <b>${escapeHTML(a.title)}</b>
      <p>${escapeHTML(a.description)}</p>
      <span class="badge ${a.severity}">${a.severity}</span>
      <p>${escapeHTML(a.building)} · ${escapeHTML(a.category)}</p>
      ${compact ? "" :
        `<button class="secondary" onclick="planAlert(${a.id})">Plan action</button>
         <button class="secondary" onclick="resolveAlert(${a.id})">Resolve</button>`}
    </div>`;
  }

  $("alertList").innerHTML = open.length
    ? open.map(a => html(a)).join("")
    : "<p>No open alerts.</p>";

  $("dashboardAlerts").innerHTML = open.slice(0, 3).map(a => html(a, true)).join("");
}

$("alertForm").addEventListener("submit", e => {
  e.preventDefault();
  const f = new FormData(e.target);
  alerts.unshift({
    id: Math.max(0, ...alerts.map(a => a.id)) + 1,
    title: f.get("title"),
    building: f.get("building"),
    severity: f.get("severity"),
    category: f.get("category"),
    description: f.get("description"),
    status: "open"
  });
  e.target.reset();
  e.target.hidden = true;
  renderAlerts();
  showMessage("Alert created.");
});

function resolveAlert(id) {
  const a = alerts.find(a => a.id === id);
  if (a) a.status = "resolved";
  renderAlerts();
  loadReport();
  showMessage("Alert resolved.");
}

function planAlert(id) {
  const a = alerts.find(a => a.id === id);
  $("planCategory").value = a.category;
  $("planBuilding").value = a.building;
  go("planner");
  makePlan();
}

// ---------------- MISSION PLANNER ----------------

function makePlan() {
  const category = $("planCategory").value;
  const building = $("planBuilding").value;

  const plans = {
    Water: [
      "Inspect pipes, valves and washroom fixtures.",
      "Compare meter readings after 15 minutes.",
      "Record a follow-up reading after repairs."
    ],
    Energy: [
      "Inspect lighting and idle equipment.",
      "Review operating schedules.",
      "Compare readings with the baseline."
    ],
    Waste: [
      "Arrange waste collection.",
      "Check nearby bins for overflow.",
      "Record bin levels after collection."
    ]
  };

  $("planOutput").innerHTML =
    `<h3>Recommended plan for ${escapeHTML(building)}</h3>
     <ol>${plans[category].map(x => `<li>${x}</li>`).join("")}</ol>`;
}

// ---------------- RESOURCE SIMULATOR ----------------

function simulate() {
  const reduction = Number($("reduction").value);
  const resource = $("resource").value;
  const baseline = resource === "Water" ? 48250 : 1280;
  const unit = resource === "Water" ? "L/day" : "kWh/day";
  const saved = baseline * reduction / 100;

  $("reductionLabel").textContent = reduction;
  $("simulationResult").innerHTML =
    `Baseline: ${baseline.toLocaleString()} ${unit}<br>
     Projected savings: ${saved.toLocaleString()} ${unit}<br>
     Projected usage: ${(baseline-saved).toLocaleString()} ${unit}`;
}

// ---------------- HOSTELFLOW ----------------

function renderHostel() {
  const machines = [
    ["Laundry Machine A", "Available", "Available now"],
    ["Laundry Machine B", "In Use", "Estimated free in 18 minutes"],
    ["Laundry Machine C", "Maintenance", "Needs inspection"]
  ];

  $("machines").innerHTML = machines.map(m =>
    `<div class="card"><b>${m[0]}</b><p>${m[1]} · ${m[2]}</p></div>`
  ).join("");
}

$("bookingForm").addEventListener("submit", e => {
  e.preventDefault();
  actions.push({
    type: "hostel booking",
    machine: $("machine").value,
    slot: $("slot").value,
    time: new Date().toISOString()
  });
  showMessage("Laundry slot request recorded.");
});

// ---------------- SOLARTWIN ----------------

function solarCalc() {
  const panels = Math.max(0, Number($("panels").value));
  const capacity = Math.max(0, Number($("panelKw").value));
  const sun = Math.max(0, Number($("sunHours").value));
  const loss = Math.min(100, Math.max(0, Number($("loss").value)));

  const peak = panels * capacity;
  const daily = peak * sun * (1 - loss / 100);

  $("solarResult").innerHTML =
    `Peak capacity: ${peak.toFixed(2)} kW<br>
     Daily generation: ${daily.toFixed(2)} kWh<br>
     Monthly generation: ${(daily * 30).toFixed(2)} kWh`;
}

// ---------------- REUSE UNIVERSITY ----------------

function renderReuse() {
  $("reuseList").innerHTML = reuseItems.map(x =>
    `<div class="card">
      <b>${escapeHTML(x.item)}</b>
      <p>Department: ${escapeHTML(x.department)}</p>
      <p>Quantity: ${x.quantity}</p>
      <p>Condition: ${escapeHTML(x.condition)}</p>
      <p>${claimedItems.has(x.id) ? "Requested" : "Available"}</p>
      <button class="secondary" onclick="selectReuse(${x.id})">Request item</button>
    </div>`
  ).join("");

  $("reuseItem").innerHTML = reuseItems.map(x =>
    `<option value="${x.id}">${escapeHTML(x.item)} (${x.quantity})</option>`
  ).join("");
}

function selectReuse(id) {
  $("reuseItem").value = id;
  $("claimDepartment").focus();
}

$("reuseForm").addEventListener("submit", e => {
  e.preventDefault();
  const id = Number($("reuseItem").value);
  const item = reuseItems.find(x => x.id === id);

  if (item) {
    claimedItems.add(id);
    actions.push({
      type: "reuse claim",
      item: item.item,
      department: $("claimDepartment").value,
      time: new Date().toISOString()
    });
    renderReuse();
    loadReport();
    showMessage("Reuse request recorded.");
  }
  e.target.reset();
});

// ---------------- SUSTAINABILITY REPORT ----------------

function loadReport() {
  const total = alerts.length;
  const open = alerts.filter(a => a.status === "open").length;
  const resolved = total - open;

  $("reportResult").innerHTML =
    `<div class="card">Total alerts: ${total}</div>
     <div class="card">Open alerts: ${open}</div>
     <div class="card">Resolved alerts: ${resolved}</div>
     <div class="card">Recorded actions: ${actions.length}</div>
     <div class="card">Data mode: SIMULATED</div>
     <div class="card">Generated: ${new Date().toLocaleString()}</div>`;
}

// ---------------- INTERACTIVE 3D CAMPUS ----------------
// Three.js is loaded from a CDN. Internet is required.

let scene, camera, renderer, controls, raycaster, mouse;
let buildingMeshes = [];
let initialPosition;

function init3D() {
  if (renderer) {
    resize3D();
    return;
  }

  if (!window.THREE) {
    $("campus3d").innerHTML =
      "<p>3D library is loading. Check your internet connection.</p>";
    return;
  }

  const T = window.THREE;
  const mount = $("campus3d");

  scene = new T.Scene();
  scene.background = new T.Color("#071722");
  scene.fog = new T.Fog("#071722", 35, 90);

  camera = new T.PerspectiveCamera(45, 1, 0.1, 150);
  initialPosition = new T.Vector3(18, 17, 23);
  camera.position.copy(initialPosition);

  renderer = new T.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.outputColorSpace = T.SRGBColorSpace;
  mount.innerHTML = "";
  mount.appendChild(renderer.domElement);

  // OrbitControls are included in the non-module Three.js bundle.
  controls = new T.OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1, 0);
  controls.enableDamping = true;
  controls.minDistance = 7;
  controls.maxDistance = 45;
  controls.maxPolarAngle = Math.PI / 2.05;

  scene.add(new T.HemisphereLight(0xd5f4ff, 0x193526, 2));

  const light = new T.DirectionalLight(0xffffff, 3);
  light.position.set(10, 22, 12);
  light.castShadow = true;
  scene.add(light);

  // Campus ground
  const ground = new T.Mesh(
    new T.PlaneGeometry(45, 38),
    new T.MeshStandardMaterial({ color: "#173b35" })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.1;
  ground.receiveShadow = true;
  scene.add(ground);

  // Roads
  function box(w, h, d, x, y, z, color) {
    const mesh = new T.Mesh(
      new T.BoxGeometry(w, h, d),
      new T.MeshStandardMaterial({ color, roughness: 0.8 })
    );
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
    return mesh;
  }

  box(2, 0.04, 34, 0, -0.05, 0, "#526b63");
  box(42, 0.04, 1.5, 0, -0.04, 0, "#526b63");
  box(1, 0.04, 27, -7, -0.02, 0, "#89948a");
  box(1, 0.04, 27, 7, -0.02, 0, "#89948a");

  // Trees
  for (const [x, z] of [
    [-16,-10],[-14,1],[-15,10],[-10,14],
    [14,-11],[16,-3],[14,9],[10,14],[-2,-14],[3,14]
  ]) {
    const trunk = new T.Mesh(
      new T.CylinderGeometry(0.12, 0.17, 0.8, 8),
      new T.MeshStandardMaterial({ color: "#735039" })
    );
    trunk.position.set(x, 0.3, z);
    scene.add(trunk);

    const crown = new T.Mesh(
      new T.IcosahedronGeometry(0.7, 1),
      new T.MeshStandardMaterial({ color: "#277b50" })
    );
    crown.position.set(x, 1.1, z);
    scene.add(crown);
  }

  // Buildings: height and color represent status.
  const positions = {
    library:   { x:-10, z:-6, w:5.5, d:4.5, h:3.2 },
    science:   { x:1, z:-7, w:6.2, d:5, h:5 },
    hostel:    { x:10, z:4, w:5.3, d:5, h:5.7 },
    cafeteria: { x:-7, z:6, w:5.5, d:4.2, h:2.8 }
  };

  const statusColors = {
    Normal: "#40e28b",
    Attention: "#ffbf47",
    Critical: "#ff6573"
  };

  buildingMeshes = [];

  buildings.forEach(b => {
    const p = positions[b.id];
    const color = statusColors[b.status];
    const group = new T.Group();
    group.position.set(p.x, 0, p.z);
    scene.add(group);

    const material = new T.MeshStandardMaterial({
      color: color,
      roughness: 0.65,
      emissive: color,
      emissiveIntensity: 0.08
    });

    const body = new T.Mesh(
      new T.BoxGeometry(p.w, p.h, p.d), material
    );
    body.position.y = p.h / 2;
    body.castShadow = true;
    body.userData.buildingId = b.id;
    group.add(body);

    const roof = new T.Mesh(
      new T.BoxGeometry(p.w + 0.2, 0.18, p.d + 0.2),
      new T.MeshStandardMaterial({ color: "#a9c5c8" })
    );
    roof.position.y = p.h + 0.08;
    group.add(roof);

    // Windows
    const rows = Math.max(1, Math.round(p.h / 1.4));
    const cols = Math.max(2, Math.floor(p.w / 1.2));

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const win = new T.Mesh(
          new T.BoxGeometry(0.42, 0.42, 0.06),
          new T.MeshStandardMaterial({
            color: "#bcecff",
            emissive: "#4b9eb8",
            emissiveIntensity: 0.3
          })
        );

        win.position.set(
          -p.w / 2 + 0.65 + c * ((p.w - 1.1) / Math.max(1, cols - 1)),
          0.7 + r * (p.h - 0.8) / rows,
          p.d / 2 + 0.04
        );
        group.add(win);
      }
    }

    // Ground ring
    const ring = new T.Mesh(
      new T.RingGeometry(0.85, 1.02, 48),
      new T.MeshBasicMaterial({
        color, side: T.DoubleSide, transparent: true, opacity: 0.9
      })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.02;
    group.add(ring);

    // Building name label
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#071722";
    ctx.fillRect(0, 0, 512, 128);
    ctx.strokeStyle = color;
    ctx.lineWidth = 6;
    ctx.strokeRect(4, 4, 504, 120);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 34px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(b.name, 256, 64);

    const texture = new T.CanvasTexture(canvas);
    const label = new T.Sprite(
      new T.SpriteMaterial({ map: texture, depthTest: false })
    );
    label.scale.set(4.4, 1.1, 1);
    label.position.set(0, p.h + 1.4, 0);
    group.add(label);

    buildingMeshes.push(body);
  });

  // Decorative campus pond
  const pond = new T.Mesh(
    new T.CircleGeometry(2.1, 40),
    new T.MeshStandardMaterial({ color: "#198eaa", roughness: 0.2 })
  );
  pond.rotation.x = -Math.PI / 2;
  pond.position.set(2, 0.01, 7);
  scene.add(pond);

  raycaster = new T.Raycaster();
  mouse = new T.Vector2();

  renderer.domElement.addEventListener("pointerdown", event => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(buildingMeshes);

    if (hits.length) {
      const id = hits[0].object.userData.buildingId;
      selectBuilding(id);
    }
  });

  window.addEventListener("resize", resize3D);
  resize3D();
  animate3D();
  selectBuilding("science");
}

function selectBuilding(id) {
  const b = buildings.find(x => x.id === id);
  if (!b) return;

  $("selectedName").textContent = b.name;
  $("selectedStatus").textContent = b.status + " · Simulated profile";
  $("selectedWater").textContent = b.water.toLocaleString() + " L/day";
  $("selectedEnergy").textContent = b.energy + " kWh/day";
  $("selectedHealth").textContent = b.health + "/100";

  buildingMeshes.forEach(mesh => {
    const selected = mesh.userData.buildingId === id;
    mesh.material.emissiveIntensity = selected ? 0.3 : 0.08;
    mesh.scale.setScalar(selected ? 1.035 : 1);
  });
}

function resize3D() {
  if (!renderer || !$("campus3d")) return;
  const w = Math.max(1, $("campus3d").clientWidth);
  const h = Math.max(1, $("campus3d").clientHeight);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}

function animate3D() {
  if (!renderer) return;
  requestAnimationFrame(animate3D);
  controls.update();
  renderer.render(scene, camera);
}

function resetCamera() {
  if (!camera) return;
  camera.position.copy(initialPosition);
  controls.target.set(0, 1, 0);
  controls.update();
}

// Load the classic Three.js bundle and OrbitControls.
function loadThreeJS() {
  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js";

  script.onload = () => {
    const orbit = document.createElement("script");
    orbit.src = "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js";
    orbit.onload = () => {
      if ($("page-digital").classList.contains("active")) init3D();
    };
    orbit.onerror = () => {
      $("campus3d").innerHTML =
        "<p>Could not load OrbitControls. Check your internet connection.</p>";
    };
    document.head.appendChild(orbit);
  };

  script.onerror = () => {
    $("campus3d").innerHTML =
      "<p>Could not load Three.js. Check your internet connection.</p>";
  };

  document.head.appendChild(script);
}

// ---------------- INITIALIZE ----------------

const buildings = window.buildings = [
  {id:"library", name:"Library", water:6200, energy:175,
   health:94, status:"Normal"},
  {id:"science", name:"Science Block", water:12800, energy:310,
   health:61, status:"Critical"},
  {id:"hostel", name:"Hostel", water:15400, energy:290,
   health:78, status:"Attention"},
  {id:"cafeteria", name:"Cafeteria", water:9800, energy:245,
   health:72, status:"Attention"}
];

const reuseItems = [
  {id:1,item:"Study desks",department:"Admin Block",
   quantity:12,condition:"Good"},
  {id:2,item:"Lab stools",department:"Science Block",
   quantity:20,condition:"Usable"},
  {id:3,item:"Reference books",department:"Library",
   quantity:45,condition:"Good"},
  {id:4,item:"Desktop monitors",department:"IT Lab",
   quantity:6,condition:"Needs testing"}
];

renderBuildings();
renderAlerts();
renderHostel();
renderReuse();
simulate();
loadReport();
loadThreeJS();
</script>
</body>
</html>
"""

# ---------------- FLASK ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "EcoTwin AI"})


@app.route("/api/buildings")
def get_buildings():
    return jsonify(buildings)


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify(alerts)


@app.route("/api/alerts", methods=["POST"])
def create_alert():
    global next_alert_id
    data = request.get_json(silent=True) or {}

    required = ("title", "building", "severity", "category", "description")
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "Please complete every field."}), 400

    item = {k: str(data[k]).strip() for k in required}
    item.update({"id": next_alert_id, "status": "open"})
    next_alert_id += 1
    alerts.insert(0, item)
    return jsonify(item), 201


@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def resolve_alert(alert_id):
    for item in alerts:
        if item["id"] == alert_id:
            item["status"] = "resolved"
            return jsonify({"success": True})
    return jsonify({"error": "Alert not found."}), 404


@app.route("/api/recommendations", methods=["POST"])
def recommendations():
    data = request.get_json(silent=True) or {}
    category = data.get("category", "Water")
    building = data.get("building", "Science Block")

    plans = {
        "Water": [
            "Inspect pipes, valves and washroom fixtures.",
            "Compare meter readings after 15 minutes.",
            "Record a follow-up reading after repairs."
        ],
        "Energy": [
            "Inspect lighting and idle equipment.",
            "Review operating schedules.",
            "Compare readings with the baseline."
        ],
        "Waste": [
            "Arrange waste collection.",
            "Check nearby bins for overflow.",
            "Record bin levels after collection."
        ]
    }

    return jsonify({
        "title": f"Recommended plan for {building}",
        "summary": f"Investigate the {category.lower()} issue.",
        "actions": plans.get(category, plans["Water"]),
        "source": "Rule-based demo recommendations"
    })


@app.route("/api/scenarios", methods=["POST"])
def scenarios():
    data = request.get_json(silent=True) or {}
    resource = data.get("resource", "Energy")

    try:
        reduction = max(0, min(50, float(data.get("reduction", 20))))
    except (TypeError, ValueError):
        return jsonify({"error": "Reduction must be numeric."}), 400

    baseline, unit = (
        (48250, "L/day") if resource == "Water"
        else (1280, "kWh/day")
    )

    saved = baseline * reduction / 100
    return jsonify({
        "baseline": baseline,
        "unit": unit,
        "saved": round(saved, 1),
        "projected": round(baseline - saved, 1),
        "reduction": reduction
    })


@app.route("/api/hostel", methods=["GET"])
def hostel():
    return jsonify({
        "machines": [
            {"name": "Laundry Machine A", "status": "Available"},
            {"name": "Laundry Machine B", "status": "In Use"},
            {"name": "Laundry Machine C", "status": "Maintenance"}
        ],
        "water_schedule": [
            {"time": "06:00–08:00", "area": "Hostel floors 1–3"},
            {"time": "18:00–20:00", "area": "Hostel floors 4–6"}
        ]
    })


@app.route("/api/hostel/booking", methods=["POST"])
def hostel_booking():
    data = request.get_json(silent=True) or {}
    machine = str(data.get("machine", "")).strip()
    slot = str(data.get("slot", "")).strip()

    if not machine or not slot:
        return jsonify({"error": "Choose a machine and slot."}), 400

    entry = {
        "type": "hostel booking",
        "machine": machine,
        "slot": slot,
        "created_at": datetime.now().isoformat(timespec="minutes")
    }
    actions.append(entry)
    return jsonify({"success": True, "booking": entry}), 201


@app.route("/api/solar", methods=["POST"])
def solar():
    data = request.get_json(silent=True) or {}

    try:
        panels = max(0, min(100000, int(data.get("panels", 100))))
        panel_kw = max(0, min(2, float(data.get("panel_kw", 0.45))))
        sun_hours = max(0, min(12, float(data.get("sun_hours", 4.5))))
        loss = max(0, min(80, float(data.get("loss", 20))))
    except (TypeError, ValueError):
        return jsonify({"error": "Solar inputs must be numeric."}), 400

    peak = panels * panel_kw
    daily = peak * sun_hours * (1 - loss / 100)

    return jsonify({
        "panels": panels,
        "peak_kw": round(peak, 2),
        "daily_kwh": round(daily, 2),
        "monthly_kwh": round(daily * 30, 2)
    })


@app.route("/api/reuse", methods=["GET"])
def get_reuse():
    return jsonify([
        dict(item, status="Requested" if item["id"] in claimed_items
             else "Available")
        for item in reuse_items
    ])


@app.route("/api/reuse/claim", methods=["POST"])
def reuse_claim():
    data = request.get_json(silent=True) or {}
    item = str(data.get("item", "")).strip()
    department = str(data.get("department", "")).strip()

    if not item or not department:
        return jsonify({"error": "Enter an item and department."}), 400

    actions.append({
        "type": "reuse claim",
        "item": item,
        "department": department,
        "created_at": datetime.now().isoformat(timespec="minutes")
    })

    match = next((x for x in reuse_items if x["item"] == item), None)
    if match:
        claimed_items.add(match["id"])

    return jsonify({
        "success": True,
        "message": f"Claim request recorded for {item} by {department}."
    }), 201


@app.route("/api/report", methods=["GET"])
def report():
    return jsonify({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_alerts": len(alerts),
        "open_alerts": sum(a["status"] == "open" for a in alerts),
        "resolved_alerts": sum(a["status"] == "resolved" for a in alerts),
        "recorded_actions": len(actions),
        "data_mode": "SIMULATED"
    })


if __name__ == "__main__":
    print("EcoTwin AI running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)