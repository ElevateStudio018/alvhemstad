(() => {
  const nav = document.getElementById("nav");
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("mobileMenu");

  // Header: transparent over hero, solid once scrolled
  const onScroll = () => nav.classList.toggle("is-solid", window.scrollY > 40);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Mobile menu
  const setMenu = (open) => {
    nav.classList.toggle("is-open", open);
    menu.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Stäng meny" : "Öppna meny");
  };
  toggle.addEventListener("click", () => setMenu(menu.hidden));
  menu.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  // Reveal on scroll
  const items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add("is-in"));
  }

  // Price calculator — prices from the price list (incl. VAT, after 50 % RUT)
  const SERVICES = {
    hem:    { unit: "h",   label: "Antal timmar per tillfälle", min: 1,  max: 10,  step: 1,  value: 3,  price: 230, rut: true,  from: false },
    stor:   { unit: "h",   label: "Antal timmar",               min: 2,  max: 16,  step: 1,  value: 6,  price: 250, rut: true,  from: true },
    flytt:  { unit: "kvm", label: "Bostadens yta",              min: 20, max: 250, step: 5,  value: 75, price: 40,  rut: true,  from: true },
    kontor: { unit: "h",   label: "Antal timmar per tillfälle", min: 1,  max: 12,  step: 1,  value: 3,  price: 350, rut: false, from: true },
  };
  const fmt = (n) => Math.round(n).toLocaleString("sv-SE") + " kr";

  const calc = document.getElementById("calc");
  const qty = document.getElementById("qty");
  const qtyOut = document.getElementById("qtyOut");
  const qtyLabel = document.getElementById("qtyLabel");
  const resLabel = document.getElementById("resLabel");
  const resTotal = document.getElementById("resTotal");
  const resMeta = document.getElementById("resMeta");
  const resFine = document.getElementById("resFine");
  let current = "hem";

  const render = () => {
    const s = SERVICES[current];
    const n = Number(qty.value);
    const total = n * s.price;
    qty.style.setProperty("--p", ((n - s.min) / (s.max - s.min)) * 100 + "%");
    qtyOut.textContent = n + " " + s.unit;
    resTotal.textContent = (s.from ? "fr. " : "") + fmt(total);

    if (current === "kontor") {
      resLabel.textContent = "Uppskattat pris per tillfälle";
      resMeta.textContent = s.price + " kr/h exkl. moms första månaden";
      resFine.textContent = "Därefter fast pris per städtillfälle enligt överenskommelse.";
    } else {
      resLabel.textContent = current === "hem" ? "Du betalar per tillfälle" : "Du betalar";
      resMeta.textContent = "Ordinarie pris " + fmt(total * 2) + " · RUT-avdrag −" + fmt(total);
      resFine.textContent = current === "hem"
        ? "Inkl. moms och efter 50 % RUT-avdrag. Rengöringsmedel kan ingå för 60 kr/tillfälle."
        : "Inkl. moms och efter 50 % RUT-avdrag. Slutpris bekräftas på uppstartsmötet.";
    }
  };

  const setService = (key) => {
    current = key;
    const s = SERVICES[key];
    qty.min = s.min; qty.max = s.max; qty.step = s.step; qty.value = s.value;
    qtyLabel.textContent = s.label;
    render();
  };

  calc.addEventListener("change", (e) => { if (e.target.name === "svc") setService(e.target.value); });
  qty.addEventListener("input", render);
  setService("hem");

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
      "Adress: " + (d.get("adress") || "-"),
      "Typ av städning: " + d.get("typ"),
      "Yta (m²): " + (d.get("yta") || "-"),
      "",
      d.get("meddelande") || "",
    ].join("\n");
    window.location.href = "mailto:info@alvhemstad.se?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    status.textContent = "Ditt e-postprogram öppnas med förfrågan ifylld. Tack!";
  });

  document.getElementById("year").textContent = new Date().getFullYear();
})();
