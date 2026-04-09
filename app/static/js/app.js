"use strict";

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert.alert-success, .alert.alert-info").forEach((el) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });

  // Confirm dangerous actions
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // Highlight active nav link more precisely
  const path = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach((link) => {
    if (link.getAttribute("href") && path.startsWith(link.getAttribute("href")) && link.getAttribute("href") !== "/") {
      link.classList.add("active");
    }
  });
});
