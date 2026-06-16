// Utilidades de menús desplegables (módulo ES, sin IIFE).
// Unifica la lógica que antes estaba duplicada en toggle_dropdown.js
// (dropdown genérico por clases) y row_actions.js (menú ⋮ por fila con <details>).

// ── Dropdown genérico por clases ────────────────────────────────────────────
// Un menú abierto a la vez por tipo; cierra al click afuera o con Escape, y
// mantiene aria-expanded del botón disparador.
export function setupDropdown(config) {
  const rootSel = config.root;
  const toggleSel = config.toggle;
  const contentSel = config.content || rootSel;
  const openClass = config.openClass || "open";
  const refocus = config.refocus || false;

  function cerrar(root) {
    if (!root.classList.contains(openClass)) return;
    root.classList.remove(openClass);
    const toggle = root.querySelector(toggleSel);
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }

  function cerrarTodos(excepto) {
    document.querySelectorAll(rootSel + "." + openClass).forEach((root) => {
      if (root !== excepto) cerrar(root);
    });
  }

  document.addEventListener("click", (e) => {
    const toggle = e.target.closest(toggleSel);
    const root = toggle && toggle.closest(rootSel);

    if (root) {
      e.preventDefault();
      const estabaAbierto = root.classList.contains(openClass);
      cerrarTodos(root);
      if (estabaAbierto) {
        cerrar(root);
      } else {
        root.classList.add(openClass);
        toggle.setAttribute("aria-expanded", "true");
      }
      return;
    }

    // Click fuera del contenido abierto: cerrar todo.
    if (!e.target.closest(contentSel)) cerrarTodos(null);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const abierto = document.querySelector(rootSel + "." + openClass);
    if (!abierto) return;
    cerrarTodos(null);
    if (refocus) {
      const toggle = abierto.querySelector(toggleSel);
      if (toggle) toggle.focus();
    }
  });
}

// ── Menú de acciones (⋮) por fila con <details class="row-actions"> ──────────
// El menú se posiciona fixed debajo del botón summary.
function posicionarMenu(details) {
  const btn = details.querySelector("summary");
  const menu = details.querySelector(".row-actions__menu");
  if (!btn || !menu) return;

  const rect = btn.getBoundingClientRect();
  let left = rect.right - menu.offsetWidth; // alinear lado derecho con el botón
  if (left < 8) left = 8; // no salirse por la izquierda

  menu.style.top = rect.bottom + 4 + "px";
  menu.style.left = left + "px";
}

function cerrarRowActions() {
  document.querySelectorAll("details.row-actions[open]").forEach((d) => {
    d.removeAttribute("open");
  });
}

export function setupRowActions() {
  document.querySelectorAll("details.row-actions").forEach((d) => {
    d.addEventListener("toggle", () => {
      if (!d.open) return;
      // Cerrar los demás antes de posicionar el nuevo.
      document.querySelectorAll("details.row-actions[open]").forEach((other) => {
        if (other !== d) other.removeAttribute("open");
      });
      posicionarMenu(d);
    });
  });

  // Cerrar al hacer click fuera de cualquier dropdown.
  document.addEventListener("click", (e) => {
    document.querySelectorAll("details.row-actions[open]").forEach((d) => {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });

  // Cerrar al scrollear (el menú fixed quedaría desalineado).
  window.addEventListener("scroll", cerrarRowActions, { passive: true });
  document.querySelector(".main")?.addEventListener("scroll", cerrarRowActions, { passive: true });
}
