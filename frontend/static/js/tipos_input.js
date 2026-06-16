// Input de tipo de evaluación: nombre editable inline + alta, sin recargar.
// Reusa el ABM de tipos por fetch (las rutas responden 204 a las llamadas AJAX).
// Se carga como módulo: el scope ya es local, sin IIFE.
import { post } from "./api.js";

const root = document.querySelector("[data-tipo-input]");

if (root) {
  const lista = root.querySelector("[data-tipo-list]");

  const marcarGuardado = (row) => {
    const s = row.querySelector("[data-saved]");
    if (!s) return;
    s.classList.add("is-on");
    setTimeout(() => s.classList.remove("is-on"), 1200);
  };

  const guardarFila = (row) => {
    if (!row) return;
    const nombre = row.querySelector("[data-nombre]").value.trim();
    if (!nombre) return;
    const grupal = row.querySelector("[data-grupal]").checked;
    post(row.dataset.updateUrl, { nombre, es_grupal: grupal ? "on" : null }).then((r) => {
      if (r.ok) marcarGuardado(row);
    });
  };

  const refrescarFilas = () => {
    const sel = lista.querySelector('input[name="tipo_evaluacion_id"]:checked');
    const qs = sel ? "?seleccion=" + encodeURIComponent(sel.value) : "";
    return fetch(root.dataset.rowsUrl + qs, { credentials: "same-origin" })
      .then((r) => r.text())
      .then((html) => {
        lista.innerHTML = html;
      });
  };

  // Renombrar al salir del campo; Enter = confirmar (blur).
  lista.addEventListener("focusout", (e) => {
    const inp = e.target.closest("[data-nombre]");
    if (inp) guardarFila(inp.closest("[data-tipo-row]"));
  });
  lista.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.target.matches("[data-nombre]")) {
      e.preventDefault();
      e.target.blur();
    }
  });
  // Toggle grupal.
  lista.addEventListener("change", (e) => {
    if (e.target.matches("[data-grupal]")) guardarFila(e.target.closest("[data-tipo-row]"));
  });

  // Agregar nuevo tipo.
  root.querySelector("[data-add]").addEventListener("click", () => {
    const nombreEl = root.querySelector("[data-new-nombre]");
    const nombre = nombreEl.value.trim();
    if (!nombre) {
      nombreEl.focus();
      return;
    }
    const grupalEl = root.querySelector("[data-new-grupal]");
    post(root.dataset.createUrl, { nombre, es_grupal: grupalEl.checked ? "on" : null })
      .then((r) => (r.ok ? refrescarFilas() : null))
      .then(() => {
        nombreEl.value = "";
        grupalEl.checked = false;
      });
  });
}
