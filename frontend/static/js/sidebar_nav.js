// Grupos colapsables del sidebar admin.
// Persiste el estado abierto/cerrado de cada grupo en localStorage (la app
// recarga la página entera en cada navegación). Al cargar restaura ese estado,
// pero fuerza abierto el grupo que contiene el item activo para nunca ocultar
// la página actual.
var STORAGE_PREFIX = "sidebar.group.";

function claveGrupo(group) {
  return STORAGE_PREFIX + (group.dataset.group || "");
}

function aplicarEstado(group, colapsado) {
  group.classList.toggle("is-collapsed", colapsado);
  var toggle = group.querySelector(".nav-group__toggle");
  if (toggle) toggle.setAttribute("aria-expanded", colapsado ? "false" : "true");
}

function leerGuardado(group) {
  try {
    return localStorage.getItem(claveGrupo(group));
  } catch (e) {
    return null;
  }
}

function guardar(group, colapsado) {
  try {
    localStorage.setItem(claveGrupo(group), colapsado ? "collapsed" : "open");
  } catch (e) {
    /* localStorage no disponible: el toggle igual funciona en la sesión */
  }
}

function init() {
  var grupos = document.querySelectorAll(".sidebar .nav-group");
  grupos.forEach(function (group) {
    var tieneActivo = !!group.querySelector("a.active");
    // El grupo con el item activo siempre arranca abierto.
    var colapsado = tieneActivo ? false : leerGuardado(group) === "collapsed";
    aplicarEstado(group, colapsado);

    var toggle = group.querySelector(".nav-group__toggle");
    if (!toggle) return;
    toggle.addEventListener("click", function () {
      var ahoraColapsado = !group.classList.contains("is-collapsed");
      aplicarEstado(group, ahoraColapsado);
      guardar(group, ahoraColapsado);
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
