// Grilla de carga masiva de notas (evaluación individual).
// Habilita el input de nota de una fila cuando se le elige una entrega, y lo
// deshabilita/limpia si se vuelve a "sin entrega". Se carga como módulo: scope
// local, sin IIFE.

const notaDeFila = (alumnoId) =>
  document.querySelector(`.eval-masiva__nota[data-alumno="${alumnoId}"]`);

for (const select of document.querySelectorAll(".eval-masiva__entrega")) {
  select.addEventListener("change", () => {
    const nota = notaDeFila(select.dataset.alumno);
    if (!nota) return;

    if (select.value) {
      nota.disabled = false;
      nota.focus();
    } else {
      nota.disabled = true;
      nota.value = "";
    }
  });
}
