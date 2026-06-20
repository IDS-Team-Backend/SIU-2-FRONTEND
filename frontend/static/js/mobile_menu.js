const toggle    = document.getElementById("sidebar-toggle");
const sidebar   = document.querySelector(".sidebar");
const overlay   = document.getElementById("sidebar-overlay");

function abrirSidebar() {
sidebar.classList.add("is-open");
overlay.classList.add("is-open");
document.body.style.overflow = "hidden";
}

function cerrarSidebar() {
sidebar.classList.remove("is-open");
overlay.classList.remove("is-open");
document.body.style.overflow = "";
}

toggle?.addEventListener("click", abrirSidebar);
overlay?.addEventListener("click", cerrarSidebar);

// Cerrar al navegar (links del sidebar)
sidebar?.querySelectorAll("a").forEach(link => {
link.addEventListener("click", cerrarSidebar);
});