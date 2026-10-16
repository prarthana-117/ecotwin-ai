const canvas = document.getElementById("campus3d");

if (canvas) {
  const ctx = canvas.getContext("2d");
  canvas.width = 800;
  canvas.height = 450;

  ctx.fillStyle = "#0b1711";
  ctx.fillRect(0, 0, 800, 450);

  function building(x, y, w, h, color, name) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = "#e8f1eb";
    ctx.font = "14px Arial";
    ctx.fillText(name, x, y - 8);
  }

  building(80, 100, 140, 100, "#327d55", "LIBRARY");
  building(300, 70, 160, 130, "#326b8a", "SCIENCE");
  building(550, 110, 150, 90, "#79613a", "HOSTEL");
  building(120, 270, 130, 80, "#70518a", "CAFETERIA");
  building(350, 270, 150, 80, "#476b91", "AUDITORIUM");

  const colors = ["#46d39a", "#ffad60", "#46d39a", "#ffad60"];

  colors.forEach((color, i) => {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(100 + i * 190, 220, 10, 0, Math.PI * 2);
    ctx.fill();
  });
}