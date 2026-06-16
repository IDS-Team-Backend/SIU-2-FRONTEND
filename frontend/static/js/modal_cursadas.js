// Modal "Cursadas de un profesor" (módulo ES, sin IIFE).
//
// Abre un modal con la tabla de cursadas en que participa un profesor. Los datos
// llegan por data-attributes en los botones .btn-cursadas-prof (data-nombre y
// data-cursadas con JSON) y se renderizan con createElement/textContent para
// evitar inyección de HTML (no se usa innerHTML por concatenación).

const ROL_LABELS = { titular: "Titular", jefe_tp: "Jefe TP", ayudante: "Ayudante", colaborador: "Colaborador" };

const overlay = document.getElementById("modal-cursadas-prof");
const titulo = document.getElementById("modal-cursadas-prof-titulo");
const body = document.getElementById("modal-cursadas-prof-body");
const btnCerrar = document.getElementById("btn-cerrar-modal-cursadas-prof");

function celda(texto, clase) {
  const td = document.createElement("td");
  if (clase) td.className = clase;
  td.textContent = texto;
  return td;
}

function celdaCursada(nombre, activa) {
  const td = document.createElement("td");
  td.textContent = nombre;
  if (activa) {
    const badge = document.createElement("span");
    badge.className = "badge badge--success badge--pill";
    badge.textContent = "Activa";
    td.appendChild(badge);
  }
  return td;
}

function fila(c) {
  const periodo = (c.anio || "") + " · " + (c.cuatrimestre || "") + "°C";
  const rolLabel = c.rol ? (ROL_LABELS[c.rol] || c.rol) : "";
  const tr = document.createElement("tr");
  tr.appendChild(celda(periodo, "text-bold"));
  tr.appendChild(celdaCursada(c.curso_nombre || "", c.activa));
  tr.appendChild(celda(rolLabel));
  return tr;
}

function tabla(cursadas) {
  const table = document.createElement("table");
  table.className = "table";

  const thead = document.createElement("thead");
  const trHead = document.createElement("tr");
  ["Período", "Cursada", "Rol"].forEach(function (texto) {
    const th = document.createElement("th");
    th.textContent = texto;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  cursadas.forEach(function (c) {
    tbody.appendChild(fila(c));
  });
  table.appendChild(tbody);

  return table;
}

function abrir(nombre, cursadas) {
  titulo.textContent = nombre;
  body.replaceChildren(tabla(cursadas));
  overlay.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function cerrar() {
  overlay.style.display = "none";
  document.body.style.overflow = "";
}

document.querySelectorAll(".btn-cursadas-prof").forEach(function (btn) {
  btn.addEventListener("click", function () {
    abrir(btn.dataset.nombre, JSON.parse(btn.dataset.cursadas));
  });
});

if (btnCerrar) btnCerrar.addEventListener("click", cerrar);
if (overlay) {
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) cerrar();
  });
}
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape" && overlay && overlay.style.display !== "none") cerrar();
});
