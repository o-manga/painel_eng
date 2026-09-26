"use strict";
const toggle = document.querySelector(".menu-toggle");
const sidebar = document.querySelector(".sidebar");
toggle?.addEventListener("click", () => {
  const expanded = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", String(expanded));
  sidebar.classList.toggle("is-open", expanded);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    sidebar.classList.remove("is-open");
    toggle?.setAttribute("aria-expanded", "false");
  }
});
