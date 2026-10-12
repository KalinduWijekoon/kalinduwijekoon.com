const menuButton = document.querySelector(".nav-toggle");
const navigation = document.querySelector("#nav-links");

if (menuButton && navigation) {
  const setOpen = (open) => {
    navigation.classList.toggle("is-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
  };

  menuButton.addEventListener("click", () => {
    setOpen(!navigation.classList.contains("is-open"));
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && navigation.classList.contains("is-open")) {
      setOpen(false);
      menuButton.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (
      navigation.classList.contains("is-open") &&
      !navigation.contains(event.target) &&
      !menuButton.contains(event.target)
    ) {
      setOpen(false);
    }
  });
}

const year = document.querySelector("#year");
if (year) year.textContent = String(new Date().getFullYear());

const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
const arts = document.querySelectorAll(".art");

// SMIL (packets, ripple, shield pulse, policy-tree requests) ignores CSS media
// queries, so handle it here. Every SVG in an illustration is controlled, since
// the hero's animated parts live in separate depth layers.
const svgsOf = (art) =>
  Array.from(art.querySelectorAll("svg")).filter((svg) => svg.pauseAnimations);
const syncSmil = () => {
  arts.forEach((art) => {
    svgsOf(art).forEach((svg) => {
      if (motionQuery.matches) {
        // a calm still: one packet mid-stream, nothing pulsing
        svg.setCurrentTime(3.5);
        svg.pauseAnimations();
      } else if (!art.classList.contains("is-paused")) {
        svg.unpauseAnimations();
      }
    });
  });
};
syncSmil();
motionQuery.addEventListener("change", syncSmil);

if ("IntersectionObserver" in window) {
  // Illustrations pause when scrolled out of view, to save battery.
  const pauseObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const art = entry.target;
        const off = !entry.isIntersecting;
        art.classList.toggle("is-paused", off);
        if (!motionQuery.matches) {
          svgsOf(art).forEach((svg) => {
            if (off) svg.pauseAnimations();
            else svg.unpauseAnimations();
          });
        }
      });
    },
    { rootMargin: "80px" },
  );
  arts.forEach((art) => pauseObserver.observe(art));

  if (!motionQuery.matches) {
    // Entrances: rows rise in a short stagger.
    const rise = document.querySelectorAll(".lane, .row, .principle");
    const riseObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            riseObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );
    rise.forEach((el, i) => {
      el.classList.add("reveal");
      el.style.transitionDelay = `${(i % 3) * 70}ms`;
      // the stagger must not lag hover transitions afterwards
      el.addEventListener(
        "transitionend",
        () => {
          el.style.transitionDelay = "";
        },
        { once: true },
      );
      riseObserver.observe(el);
    });
  }
}

// Gentle parallax: the hero world (and each sky cloud, in its own way)
// leans toward the pointer. The variables live on the hero so every layer
// inside it can read them.
const hero = document.querySelector(".hero");
if (hero && window.matchMedia("(pointer: fine)").matches) {
  let frame = 0;
  hero.addEventListener("pointermove", (event) => {
    if (motionQuery.matches || frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      const rect = hero.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
      const y = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
      hero.style.setProperty("--px", x.toFixed(3));
      hero.style.setProperty("--py", y.toFixed(3));
    });
  });
  hero.addEventListener("pointerleave", () => {
    hero.style.setProperty("--px", "0");
    hero.style.setProperty("--py", "0");
  });
}

// Keep the hero world inside the hero at any window size. The CSS --k values
// are the largest the scene should get; this scales it down when the hero is
// shorter or narrower than the layout it was composed for (1440 x 900), and
// keeps the dome and the cloud row clear of the headline and summary.
const world = document.querySelector(".world");
if (hero && world && "ResizeObserver" in window) {
  const narrowQuery = window.matchMedia("(max-width: 50rem)");
  const copyParts = hero.querySelectorAll(
    ".hero-copy h1, .hero-summary, .hero-actions",
  );
  const fitWorld = () => {
    world.style.removeProperty("--k");
    world.style.removeProperty("--ox");
    const base =
      parseFloat(getComputedStyle(world).getPropertyValue("--k")) || 1;
    const box = hero.getBoundingClientRect();
    if (narrowQuery.matches) {
      const k = Math.min(base, box.width / 860);
      world.style.setProperty("--k", Math.max(0.35, k).toFixed(3));
      return;
    }
    // where the text actually ends
    let copyRight = 0;
    copyParts.forEach((el) => {
      copyRight = Math.max(copyRight, el.getBoundingClientRect().right);
    });
    copyRight -= box.left;
    // shrink to fit the hero, and to leave room beside the text. The cloud
    // row spreads about 420px either side of the centre at full size.
    const clearOfText = (box.width * 0.68 - copyRight + 40) / 420;
    const fitsBeside = (box.width - 24 - copyRight) / 840;
    const k = Math.max(
      0.45,
      Math.min(
        base,
        box.height / 832,
        box.width / 1016,
        fitsBeside,
        Math.max(0.6, clearOfText),
      ),
    );
    // then centre the scene (68% by default) so the cloud row starts after
    // the text, without running off the right edge
    const half = 420 * k;
    let ox = Math.max(box.width * 0.68, copyRight + 16 + half);
    ox = Math.min(ox, box.width - 8 - half);
    world.style.setProperty("--k", k.toFixed(3));
    world.style.setProperty("--ox", `${ox.toFixed(0)}px`);
  };
  new ResizeObserver(fitWorld).observe(hero);
  fitWorld();
}
