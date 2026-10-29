# Alvhem Städ – ny webbplats

Statisk, modern webbplats för Alvhem Städ AB baserad på innehållet från alvhemstad.se.

- `index.html` – all sidinnehåll (hero, tjänster, priskalkyl, process, villkor, kontakt)
- `styles.css` – design (rundade kanter, fullskärmshero, ljust/mörkt)
- `main.js` – meny, scroll-animationer, RUT-priskalkyl och kontaktformulär (öppnar e-post till info@alvhemstad.se)
- `assets/img/` – logotyp, Guldsigill och foton (Unsplash, fri licens)

Öppna `index.html` direkt i webbläsaren eller publicera mappen på valfri statisk hosting (Netlify, Vercel, GitHub Pages).

## Tjänstesidor

Tjänstesidorna (`hemstadning.html`, `storstadning.html`, `flyttstadning.html`, `kontorsstadning.html`, `fonsterputsning-tradgard.html`) genereras från `tools/build_pages.py`, som också uppdaterar menyn och sidfoten i `index.html`. Ändra texter och priser i skriptet och kör:

    python3 tools/build_pages.py

## Bygga och optimera

    python3 tools/optimize_images.py   # skapar WebP-bilder i flera storlekar
    python3 tools/build_pages.py       # bygger tjänstesidor, SEO-taggar, sitemap.xml, robots.txt, llms.txt

`styles.css` är källan för all CSS. Bygget minifierar den och lägger in den direkt i varje sida, så kör `build_pages.py` efter varje CSS-ändring.
`SITE_URL` i `tools/build_pages.py` styr canonical-länkar, sitemap och strukturerad data (nu https://www.alvhemstad.se/).
