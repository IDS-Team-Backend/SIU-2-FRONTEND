// Configura los dropdowns concretos de la app usando el util compartido.
import { setupDropdown } from "./dropdown.js";

// Menú de acciones (⋮) por fila (tabla de equipos en evaluación detalle).
setupDropdown({
  root: ".row-menu",
  toggle: ".row-menu__toggle",
  content: ".row-menu__list",
  openClass: "open",
});

// Dropdown de usuario en el sidebar.
setupDropdown({
  root: ".sidebar-user-wrapper",
  toggle: ".sidebar-user",
  openClass: "is-open",
  refocus: true,
});
