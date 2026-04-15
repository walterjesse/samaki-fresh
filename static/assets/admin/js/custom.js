document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("shopzatao-admin");

  const brandText = document.querySelector(".brand-text");
  if (brandText) {
    brandText.textContent = "ShopZatao";
  }

  const header = document.querySelector(".main-header.navbar");
  if (header) {
    header.classList.add("shadow-sm");
  }

  document.querySelectorAll(".nav-sidebar .nav-link").forEach((link) => {
    link.addEventListener("mouseenter", () => {
      link.style.transform = "translateX(2px)";
    });

    link.addEventListener("mouseleave", () => {
      link.style.transform = "translateX(0)";
    });
  });
});