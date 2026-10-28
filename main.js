(() => {
  const header = document.getElementById("header");
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("mobileMenu");

  // Header shadow once scrolled
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 10);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Mobile menu
  const setMenu = (open) => {
    header.classList.toggle("is-open", open);
    menu.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Stäng meny" : "Öppna meny");
  };
  toggle.addEventListener("click", () => setMenu(menu.hidden));
  menu.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  // Contact form — opens the visitor's mail client with a prefilled message
  const form = document.getElementById("contactForm");
  const status = document.getElementById("formStatus");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    let ok = true;
    ["f-name", "f-email"].forEach((id) => {
      const el = document.getElementById(id);
      const valid = el.checkValidity() && el.value.trim() !== "";
      el.closest(".field").classList.toggle("is-invalid", !valid);
      if (!valid) ok = false;
    });
    if (!ok) {
      status.textContent = "Fyll i namn och en giltig e-postadress.";
      return;
    }
    const d = new FormData(form);
    const subject = "Förfrågan: " + d.get("typ") + " – " + d.get("namn");
    const body = [
      "Namn: " + d.get("namn"),
      "E-post: " + d.get("epost"),
      "Telefon: " + (d.get("telefon") || "-"),
      "Typ av städning: " + d.get("typ"),
      "",
      d.get("meddelande") || "",
    ].join("\n");
    window.location.href = "mailto:info@alvhemstad.se?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    status.textContent = "Ditt e-postprogram öppnas med förfrågan ifylld. Tack!";
  });

  document.getElementById("year").textContent = new Date().getFullYear();
})();

// Hero videos: crossfade between the clips, mobile gets smaller files
(() => {
  const videos = [...document.querySelectorAll(".hero__bg")];
  if (!videos.length) return;
  const mobile = window.matchMedia("(max-width: 860px)").matches;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const load = (v) => { if (!v.src) { v.src = mobile ? v.dataset.srcMobile : v.dataset.src; v.load(); } };
  load(videos[0]);
  if (reduced) return; // first clip's poster stays as a still image

  // Fetch the following clips only once the first one is playing, so they don't compete for bandwidth
  videos[0].addEventListener("playing", () => {
    setTimeout(() => videos.slice(1).forEach((v) => { v.preload = "auto"; load(v); }), 1500);
  }, { once: true });

  let i = 0;
  const play = (v) => { load(v); v.currentTime = 0; const p = v.play(); if (p) p.catch(() => {}); };
  const next = () => {
    const cur = videos[i];
    i = (i + 1) % videos.length;
    const nxt = videos[i];
    play(nxt);
    nxt.classList.add("is-active");
    cur.classList.remove("is-active");
  };
  videos.forEach((v) => v.addEventListener("ended", () => { if (v === videos[i]) next(); }));
  // Start the next clip slightly before the current ends so the fade overlaps
  videos.forEach((v) => v.addEventListener("timeupdate", () => {
    if (v === videos[i] && v.duration && v.duration - v.currentTime < 1.2 && !v.dataset.fading) {
      v.dataset.fading = "1";
      next();
      setTimeout(() => { delete v.dataset.fading; }, 2000);
    }
  }));
  play(videos[0]);
})();
