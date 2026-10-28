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
