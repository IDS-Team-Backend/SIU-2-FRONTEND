document.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".sidebar-user-wrapper");
  if (!wrapper) return;

  const button = wrapper.querySelector(".sidebar-user");
  if (!button) return;

  const close = () => {
    if (!wrapper.classList.contains("is-open")) return;
    wrapper.classList.remove("is-open");
    button.setAttribute("aria-expanded", "false");
  };

  const open = () => {
    wrapper.classList.add("is-open");
    button.setAttribute("aria-expanded", "true");
  };

  button.addEventListener("click", (event) => {
    event.stopPropagation();
    if (wrapper.classList.contains("is-open")) {
      close();
    } else {
      open();
    }
  });

  document.addEventListener("click", (event) => {
    if (!wrapper.contains(event.target)) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && wrapper.classList.contains("is-open")) {
      close();
      button.focus();
    }
  });
});
