// Menú de acciones (⋮) por fila. Ahora es un módulo ES (sin IIFE) que usa el
// util compartido en dropdown.js.
import { setupRowActions } from "./dropdown.js";

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setupRowActions);
} else {
  setupRowActions();
}
