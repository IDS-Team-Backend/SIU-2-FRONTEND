

(function () {
  "use strict";

  /** Posiciona el menú fixed debajo del botón summary. */
  function posicionarMenu(details) {
    var btn  = details.querySelector("summary");
    var menu = details.querySelector(".row-actions__menu");
    if (!btn || !menu) return;

    var rect = btn.getBoundingClientRect();

    // Alinear lado derecho del menú con lado derecho del botón
    var left = rect.right - menu.offsetWidth;

    // Si se saldría por la izquierda, pegarlo al margen
    if (left < 8) left = 8;

    menu.style.top  = (rect.bottom + 4) + "px";
    menu.style.left = left + "px";
  }

  /** Cierra todos los dropdowns abiertos. */
  function cerrarTodos() {
    document.querySelectorAll("details.row-actions[open]").forEach(function (d) {
      d.removeAttribute("open");
    });
  }

  /** Inicializa los listeners de cada dropdown en la página. */
  function init() {
    document.querySelectorAll("details.row-actions").forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (d.open) {
          // Cerrar los demás antes de posicionar el nuevo
          document.querySelectorAll("details.row-actions[open]").forEach(function (other) {
            if (other !== d) other.removeAttribute("open");
          });
          posicionarMenu(d);
        }
      });
    });

    // Cerrar al hacer click fuera de cualquier dropdown
    document.addEventListener("click", function (e) {
      document.querySelectorAll("details.row-actions[open]").forEach(function (d) {
        if (!d.contains(e.target)) d.removeAttribute("open");
      });
    });

    // Cerrar al scrollear (el menú fixed quedaría desalineado)
    window.addEventListener("scroll", cerrarTodos, { passive: true });
    document.querySelector(".main")?.addEventListener("scroll", cerrarTodos, { passive: true });
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
