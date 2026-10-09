const menuButton = document.querySelector(".nav-toggle");
const navigation = document.querySelector("#nav-links");

if (menuButton && navigation) {
  menuButton.addEventListener("click", () => {
    const isOpen = navigation.classList.toggle("is-open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navigation.classList.remove("is-open");
      menuButton.setAttribute("aria-expanded", "false");
    });
  });
}

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());

const hero = document.querySelector(".hero");
const bannerParallax = document.querySelector(".banner-parallax");
const reduceMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

if (hero && bannerParallax && !reduceMotion) {
  const maxOffset = 34;

  const handleMove = (event) => {
    const rect = hero.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const relativeX = (event.clientX - centerX) / (rect.width / 2);
    const relativeY = (event.clientY - centerY) / (rect.height / 2);
    const clampedX = Math.max(-1, Math.min(1, relativeX));
    const clampedY = Math.max(-1, Math.min(1, relativeY));
    const offsetX = -clampedX * maxOffset;
    const offsetY = -clampedY * maxOffset;
    bannerParallax.style.transform = `translate(${offsetX.toFixed(1)}px, ${offsetY.toFixed(1)}px)`;
  };

  const reset = () => {
    bannerParallax.style.transform = "translate(0px, 0px)";
  };

  hero.addEventListener("mousemove", handleMove);
  hero.addEventListener("mouseleave", reset);
}
