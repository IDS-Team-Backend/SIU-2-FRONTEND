/**
 * seleccion_masiva.js
 * Maneja la selección múltiple de alumnos en la tabla:
 *   - "seleccionar todos" tilda/destilda todas las filas
 *   - muestra la barra de acción masiva cuando hay al menos un tilde
 *   - actualiza el contador de seleccionados
 *
 * Los checkboxes usan el atributo form="form-masivo" (HTML5) para asociarse
 * al form de vinculación masiva sin necesidad de anidar forms.
 */
(function () {
  "use strict";

  function init() {
    var checkTodos = document.getElementById("check-todos");
    var barra      = document.getElementById("barra-masiva");
    var contador   = document.getElementById("contador-seleccion");

    if (!barra || !contador) return;  // la página no tiene tabla de selección

    function filas() {
      return Array.prototype.slice.call(document.querySelectorAll(".check-fila"));
    }

    function actualizar() {
      var todas    = filas();
      var tildados = todas.filter(function (c) { return c.checked; }).length;

      contador.textContent = tildados + (tildados === 1 ? " seleccionado" : " seleccionados");
      barra.style.display = tildados > 0 ? "flex" : "none";

      if (checkTodos) {
        checkTodos.checked = tildados > 0 && tildados === todas.length;
        checkTodos.indeterminate = tildados > 0 && tildados < todas.length;
      }
    }

    if (checkTodos) {
      checkTodos.addEventListener("change", function () {
        filas().forEach(function (c) { c.checked = checkTodos.checked; });
        actualizar();
      });
    }

    filas().forEach(function (c) {
      c.addEventListener("change", actualizar);
    });

    actualizar();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
