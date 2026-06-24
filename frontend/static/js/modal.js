// Modal client-side reutilizable (módulo ES, sin IIFE).
// Para modales que se abren/cierran en el cliente (sin recargar): maneja el
// foco del overlay, cierre con Escape, click en el fondo y lock del scroll.
//
// Markup esperado:
//   <button data-modal-open="miModal">Abrir</button>
//   <div class="modal-overlay" id="miModal" hidden>
//     <div class="modal">... <button data-modal-close>×</button> ...</div>
//   </div>
//
// Reemplaza los onclick="...style.display=flex/none" inline repartidos por los
// templates (material, profesores, etc.).

function abrir(overlay) {
  overlay.hidden = false;
  overlay.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function cerrar(overlay) {
  overlay.hidden = true;
  overlay.style.display = "none";
  document.body.style.overflow = "";
}

function cerrarTodos() {
  document.querySelectorAll(".modal-overlay:not([hidden])").forEach(cerrar);
}

// Abrir: cualquier elemento con data-modal-open="<id del overlay>".
document.addEventListener("click", (e) => {
  const opener = e.target.closest("[data-modal-open]");
  if (opener) {
    const overlay = document.getElementById(opener.dataset.modalOpen);
    if (overlay) {
      e.preventDefault();
      abrir(overlay);
    }
    return;
  }

  // Cerrar: botón con data-modal-close, o click en el fondo del overlay.
  if (e.target.closest("[data-modal-close]")) {
    const overlay = e.target.closest(".modal-overlay");
    if (overlay) cerrar(overlay);
    return;
  }
  if (e.target.classList.contains("modal-overlay")) cerrar(e.target);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") cerrarTodos();
});
