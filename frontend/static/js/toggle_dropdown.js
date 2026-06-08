// Util genérico de dropdowns (menús desplegables).
// Un menú abierto a la vez por tipo; cierra al click afuera o con Escape,
// y mantiene el atributo aria-expanded del botón disparador.
function setupDropdown(config) {
  var rootSel = config.root;
  var toggleSel = config.toggle;
  var contentSel = config.content || rootSel;
  var openClass = config.openClass || "open";
  var refocus = config.refocus || false;

  function cerrar(root) {
    if (!root.classList.contains(openClass)) return;
    root.classList.remove(openClass);
    var toggle = root.querySelector(toggleSel);
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }

  function cerrarTodos(excepto) {
    document
      .querySelectorAll(rootSel + "." + openClass)
      .forEach(function (root) {
        if (root !== excepto) cerrar(root);
      });
  }

  document.addEventListener("click", function (e) {
    var toggle = e.target.closest(toggleSel);
    var root = toggle && toggle.closest(rootSel);

    if (root) {
      e.preventDefault();
      var estabaAbierto = root.classList.contains(openClass);
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
    if (!e.target.closest(contentSel)) {
      cerrarTodos(null);
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var abierto = document.querySelector(rootSel + "." + openClass);
    if (!abierto) return;
    cerrarTodos(null);
    if (refocus) {
      var toggle = abierto.querySelector(toggleSel);
      if (toggle) toggle.focus();
    }
  });
}

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
