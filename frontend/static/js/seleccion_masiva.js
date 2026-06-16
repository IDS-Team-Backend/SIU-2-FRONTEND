// Selección múltiple de alumnos en la tabla (módulo ES, sin IIFE):
//   - "seleccionar todos" tilda/destilda todas las filas
//   - muestra la barra de acción masiva cuando hay al menos un tilde
//   - actualiza el contador de seleccionados
//
// Los checkboxes usan el atributo form="form-masivo" (HTML5) para asociarse al
// form de desvinculación masiva sin anidar forms.

function init() {
  const checkTodos = document.getElementById("check-todos");
  const barra = document.getElementById("barra-masiva");
  const contador = document.getElementById("contador-seleccion");

  if (!barra || !contador) return; // la página no tiene tabla de selección

  const filas = () => Array.from(document.querySelectorAll(".check-fila"));

  function actualizar() {
    const todas = filas();
    const tildados = todas.filter((c) => c.checked).length;

    contador.textContent = tildados + (tildados === 1 ? " seleccionado" : " seleccionados");
    barra.style.display = tildados > 0 ? "flex" : "none";

    if (checkTodos) {
      checkTodos.checked = tildados > 0 && tildados === todas.length;
      checkTodos.indeterminate = tildados > 0 && tildados < todas.length;
    }
  }

  if (checkTodos) {
    checkTodos.addEventListener("change", () => {
      filas().forEach((c) => { c.checked = checkTodos.checked; });
      actualizar();
    });
  }

  filas().forEach((c) => c.addEventListener("change", actualizar));

  actualizar();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
