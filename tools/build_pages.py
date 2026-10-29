#!/usr/bin/env python3
"""Bygger tjänstesidorna och den gemensamma menyn/sidfoten.

Kör från projektroten:  python3 tools/build_pages.py

- Skriver en HTML-sida per tjänst i SERVICES (t.ex. hemstadning.html).
- Byter ut menyn och sidfoten i index.html mellan markörerna
  <!-- HEADER:START --> / <!-- HEADER:END --> och <!-- FOOTER:START --> / <!-- FOOTER:END -->,
  så att alla sidor alltid har samma meny.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHONE = "076 022 39 90"
PHONE_HREF = "tel:+46760223990"
EMAIL = "info@alvhemstad.se"

SERVICES = [
    {
        "slug": "hemstadning",
        "name": "Hemstädning",
        "form_value": "Hemstädning",
        "image": "assets/img/hem.jpg",
        "image_alt": "Välstädat vardagsrum i dagsljus",
        "title": "Hemstädning i Ale – fast pris och samma städare varje gång",
        "description": "Regelbunden hemstädning på abonnemang i Ale. 230 kr/h inkl. moms efter RUT, samma städare vid alla tillfällen och nöjd kund-garanti.",
        "headline": "Hemstädning",
        "lead": "Kom hem till ett rent och fräscht hem – varje vecka, varannan vecka eller var fjärde vecka. Vi sköter städningen så att du får mer tid till det som betyder något.",
        "price": "230 kr",
        "price_unit": "/timme",
        "price_from": False,
        "price_note": "Fast pris inkl. moms, efter 50 % RUT-avdrag.",
        "intro": [
            "Med hemstädning på abonnemang får du ett hem som alltid känns välskött. Du väljer hur ofta vi kommer, och du får samma städare vid varje tillfälle – någon som lär känna ditt hem och hur du vill ha det.",
            "Vi börjar alltid med ett kostnadsfritt uppstartsmöte där vi går igenom ditt hem, dina önskemål och vad som är viktigast för dig. Därefter vet du exakt vad som ingår och vad det kostar.",
        ],
        "facts": [
            ("Frekvens", "Varje, varannan eller var fjärde vecka"),
            ("Bindningstid", "En månad"),
            ("Rengöringsmedel", "Kan ingå för 60 kr/tillfälle"),
            ("Avbokning", "Kostnadsfritt 2 arbetsdagar innan"),
        ],
        "includes": [
            ("Alla rum", ["Dammsugning och våttorkning av golv", "Damning av fria ytor, fönsterbänkar och lister", "Avtorkning av handtag och strömbrytare", "Tömning av papperskorgar"]),
            ("Kök", ["Avtorkning av bänkar och kakel ovanför bänk", "Spis och mikrovågsugn utvändigt", "Diskho och blandare", "Avtorkning av skåpluckor vid behov"]),
            ("Badrum", ["Toalett, handfat och blandare", "Dusch, badkar och kakel i duschzon", "Speglar och glasytor", "Golv och golvbrunn"]),
        ],
        "faq": [
            ("Hur ofta kan ni komma?", "Du väljer själv: varje vecka, varannan vecka eller var fjärde vecka. Frekvensen kan justeras efter dina behov."),
            ("Får jag samma städare varje gång?", "Ja. Du får samma städare vid alla städtillfällen."),
            ("Finns det bindningstid?", "Hemstädning på abonnemang har en månads bindningstid."),
            ("Tar ni med rengöringsmedel?", "Ja, om du vill. Då debiteras 60 kr inklusive moms per städtillfälle."),
            ("Hur avbokar jag?", "Du kan avboka ett städtillfälle kostnadsfritt senast 2 arbetsdagar i förväg."),
        ],
    },
    {
        "slug": "storstadning",
        "name": "Storstädning",
        "form_value": "Storstädning",
        "image": "assets/img/stor.jpg",
        "image_alt": "Dammsugning av matta",
        "title": "Storstädning i Ale – grundlig städning från 250 kr/h",
        "description": "Storstädning i Ale som får bostaden att kännas som ny. Från 250 kr/h inkl. moms efter RUT, med kvalitetsgaranti.",
        "headline": "Storstädning",
        "lead": "Ett riktigt grundligt städtillfälle som får bostaden att kännas som ny – inför långhelger, gäster, högtider eller bara när det är dags.",
        "price": "250 kr",
        "price_unit": "/timme",
        "price_from": True,
        "price_note": "Inkl. moms, efter 50 % RUT-avdrag. Abonnemangskunder betalar sitt vanliga timpris.",
        "intro": [
            "En storstädning går på djupet. Utöver det som ingår i en vanlig hemstädning tar vi hand om ytor och utrymmen som sällan hinns med i vardagen.",
            "Är du redan abonnemangskund hos oss gäller ditt vanliga pris även för storstädning.",
        ],
        "facts": [
            ("Passar inför", "Högtider, gäster och säsongsskiften"),
            ("Abonnemangskund", "Ditt vanliga timpris gäller"),
            ("Garanti", "Nöjd kund-garanti"),
            ("Avbokning", "Kostnadsfritt 2 arbetsdagar innan"),
        ],
        "includes": [
            ("Utöver hemstädning", ["Dörrar, dörrkarmar och socklar", "Element och ventiler", "Lampor och armaturer som går att nå", "Fönsterbänkar och lister i hela bostaden"]),
            ("Kök", ["Ugn och plåtar invändigt", "Spisfläkt och filter", "Kyl och frys invändigt", "Skåp och lådor, in- och utvändigt"]),
            ("Badrum", ["Avkalkning av kakel och glasytor", "Rengöring av golvbrunn", "Badkarsfront och bakom toalett", "Skåp och hyllor"]),
        ],
        "faq": [
            ("Vad kostar en storstädning?", "Från 250 kr per timme inklusive moms efter RUT-avdrag. Abonnemangskunder betalar sitt vanliga pris."),
            ("Hur lång tid tar det?", "Det beror på bostadens storlek och skick. På uppstartsmötet går vi igenom vad som ska göras och ger dig en tydlig uppskattning."),
            ("Måste jag vara hemma?", "Nej, det bestämmer du. Vi kommer överens om nycklar och tillträde innan."),
            ("Hur avbokar jag?", "Du kan avboka kostnadsfritt senast 2 arbetsdagar i förväg."),
        ],
    },
    {
        "slug": "flyttstadning",
        "name": "Flyttstädning",
        "form_value": "Flyttstädning",
        "image": "assets/img/flytt.jpg",
        "image_alt": "Ljust och tomt rum redo för inflyttning",
        "title": "Flyttstädning i Ale – från 40 kr/kvm med kvalitetsgaranti",
        "description": "Flyttstädning i Ale från 40 kr/kvm inkl. moms efter RUT. Snabbt, professionellt och med kvalitetsgaranti.",
        "headline": "Flyttstädning",
        "lead": "Vi tar hand om ditt tidigare boende snabbt, professionellt och till ett riktigt bra pris – så att du kan fokusera på flytten.",
        "price": "40 kr",
        "price_unit": "/kvm",
        "price_from": True,
        "price_note": "Inkl. moms, efter 50 % RUT-avdrag.",
        "intro": [
            "En flyttstädning ställer särskilda krav. Vi ser till att de uppfylls, så att bostaden lämnas över i det skick som förväntas av nästa ägare eller hyresvärd.",
            "Alla flyttstädningar utförs med kvalitetsgaranti. Skulle något ha missats kommer vi tillbaka och åtgärdar det.",
        ],
        "facts": [
            ("Pris", "Från 40 kr/kvm efter RUT"),
            ("Garanti", "Kvalitetsgaranti"),
            ("Passar för", "Lägenhet, radhus och villa"),
            ("Bokning", "Boka i god tid före tillträdet"),
        ],
        "includes": [
            ("Alla rum", ["Golv, socklar och lister", "Dörrar, karmar och handtag", "Element, ventiler och eluttag", "Garderober och skåp in- och utvändigt"]),
            ("Kök", ["Ugn, plåtar och galler", "Spisfläkt och filter", "Kyl och frys invändigt", "Diskmaskin, diskho och kakel"]),
            ("Badrum", ["Avkalkning av kakel, golv och glas", "Golvbrunn och vattenlås", "Toalett inklusive bakom och under", "Badrumsskåp och ventiler"]),
        ],
        "faq": [
            ("Vad kostar flyttstädning?", "Från 40 kr per kvadratmeter inklusive moms efter RUT-avdrag. Exakt pris beror på bostadens storlek och skick."),
            ("Ingår fönsterputsning?", "Fönsterputsning kan läggas till. Berätta när du bokar så tar vi med det i offerten."),
            ("Vad händer om något missats?", "Alla flyttstädningar har kvalitetsgaranti. Hör av dig så åtgärdar vi det."),
            ("Kan jag få RUT-avdrag?", "Ja, du får 50 % RUT-avdrag direkt på fakturan."),
        ],
    },
    {
        "slug": "kontorsstadning",
        "name": "Kontorsstädning",
        "form_value": "Kontorsstädning",
        "image": "assets/img/kontor.jpg",
        "image_alt": "Ljust och rent kontor med stora fönster",
        "title": "Kontorsstädning i Ale – ren och trivsam arbetsmiljö",
        "description": "Kontorsstädning i Ale anpassad efter era behov. Från 350 kr/h exkl. moms första månaden, därefter fast pris per tillfälle.",
        "headline": "Kontorsstädning",
        "lead": "En ren och trivsam arbetsmiljö för dig och dina medarbetare. Vi anpassar frekvens och omfattning efter era önskemål.",
        "price": "350 kr",
        "price_unit": "/timme",
        "price_from": True,
        "price_note": "Exkl. moms första månaden, därefter fast pris per städtillfälle enligt överenskommelse.",
        "intro": [
            "Ett rent kontor ger ett bättre första intryck och en skönare vardag för alla som arbetar där. Vi kommer överens om ett upplägg som passar er verksamhet – oavsett om ni behöver städning varje dag eller en gång i veckan.",
            "Första månaden debiterar vi per timme. Därefter går vi över till ett fast pris per städtillfälle, så att ni alltid vet vad städningen kostar.",
        ],
        "facts": [
            ("Frekvens", "Efter era önskemål"),
            ("Första månaden", "Från 350 kr/h exkl. moms"),
            ("Därefter", "Fast pris per tillfälle"),
            ("Garanti", "Nöjd kund-garanti"),
        ],
        "includes": [
            ("Arbetsplatser", ["Dammsugning och våttorkning av golv", "Avtorkning av skrivbord och fria ytor", "Tömning av papperskorgar och återvinning", "Mötesrum och gemensamma ytor"]),
            ("Pentry", ["Bänkar, diskho och blandare", "Mikrovågsugn och kaffemaskin utvändigt", "Bord och stolar", "Påfyllning av förbrukningsmaterial vid behov"]),
            ("Toaletter och entré", ["Toaletter, handfat och speglar", "Golv och golvbrunn", "Entré och trappor", "Glaspartier och dörrar"]),
        ],
        "faq": [
            ("Hur ofta kan ni städa?", "Så ofta ni behöver – vi anpassar frekvens och omfattning efter era önskemål."),
            ("Vad kostar kontorsstädning?", "Första månaden från 350 kr per timme exklusive moms. Därefter tillämpar vi ett fast pris per städtillfälle enligt överenskommelse."),
            ("Kan ni städa utanför kontorstid?", "Berätta vilka tider som passar er så hittar vi ett upplägg som fungerar."),
        ],
    },
    {
        "slug": "fonsterputsning-tradgard",
        "name": "Fönsterputs & trädgård",
        "form_value": "Fönsterputsning",
        "image": "assets/img/hero-fonster-poster.jpg",
        "image_alt": "Fönsterputsning med gul trasa",
        "title": "Fönsterputsning och trädgårdsarbete i Ale",
        "description": "Nu erbjuder Alvhem Städ även fönsterputsning och trädgårdsarbete i Ale. Kontakta oss för ett upplägg som passar dig.",
        "headline": "Fönsterputs & trädgård",
        "lead": "Nyhet hos Alvhem Städ: vi hjälper dig nu även med fönsterputsning och trädgårdsarbete. Hör av dig så berättar vi mer.",
        "price": "Offert",
        "price_unit": "",
        "price_from": False,
        "price_note": "Kontakta oss så tar vi fram ett pris som passar ditt hem och din trädgård.",
        "intro": [
            "Skinande rena fönster gör stor skillnad för hur ett hem känns – mer ljus och en klarare utsikt. Vi putsar fönster i bostäder och lokaler.",
            "Vi hjälper även till med trädgårdsarbete, så att du kan njuta av trädgården i stället för att arbeta i den. Berätta vad du behöver hjälp med så tar vi fram ett förslag.",
        ],
        "facts": [
            ("Fönsterputs", "Bostäder och lokaler"),
            ("Trädgård", "Efter dina behov"),
            ("Pris", "Enligt offert"),
            ("Garanti", "Nöjd kund-garanti"),
        ],
        "includes": [
            ("Fönsterputsning", ["Fönster in- och utvändigt", "Mellan glasen på kopplade fönster", "Avtorkning av karmar och fönsterbänkar", "Glaspartier och altandörrar"]),
            ("Trädgårdsarbete", ["Gräsklippning", "Rensning av rabatter och gångar", "Häckklippning", "Lövkrattning och bortforsling efter överenskommelse"]),
        ],
        "faq": [
            ("Vad kostar det?", "Priset beror på antal fönster eller vilka trädgårdssysslor det gäller. Kontakta oss så får du en offert."),
            ("Kan jag kombinera med hemstädning?", "Ja, hör av dig så tar vi fram ett upplägg som passar dig."),
        ],
    },
]

NAV = [("Hem", "index.html"), ("Boka nu", "index.html#kontakt"), ("Kontakta oss", "index.html#kontakt")]


def header(active=""):
    service_links = "\n".join(
        f'          <a href="{s["slug"]}.html"{" aria-current=\"page\"" if s["slug"] == active else ""}>{escape(s["name"])}</a>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(f'    <a href="{s["slug"]}.html" class="sub">{escape(s["name"])}</a>' for s in SERVICES)
    home_active = ' class="is-active"' if active == "index" else ""
    services_active = " is-active" if active and active != "index" else ""
    return f"""<header class="header" id="header">
  <div class="header__inner">
    <a href="index.html" class="header__logo" aria-label="Alvhem Städ – till startsidan">
      <img src="assets/img/logo.png" alt="Alvhem Städ" class="logo-dark" width="640" height="388">
      <img src="assets/img/logo-light.png" alt="" class="logo-light" width="640" height="388" aria-hidden="true">
    </a>
    <nav class="header__nav" aria-label="Huvudmeny">
      <a href="index.html"{home_active}>Hem</a>
      <a href="index.html#kontakt">Boka nu</a>
      <div class="dropdown">
        <a href="index.html#tjanster" class="dropdown__toggle{services_active}" aria-haspopup="true">Våra tjänster</a>
        <div class="dropdown__menu">
{service_links}
        </div>
      </div>
      <a href="index.html#kontakt">Kontakta oss</a>
    </nav>
    <button class="header__toggle" id="navToggle" aria-label="Öppna meny" aria-expanded="false" aria-controls="mobileMenu">
      <span></span><span></span><span></span>
    </button>
  </div>
  <nav class="header__mobile" id="mobileMenu" aria-label="Mobilmeny" hidden>
    <a href="index.html">Hem</a>
    <a href="index.html#kontakt">Boka nu</a>
    <a href="index.html#tjanster">Våra tjänster</a>
{mobile_service_links}
    <a href="index.html#kontakt">Kontakta oss</a>
  </nav>
</header>"""


def footer():
    links = "\n".join(f'      <a href="{s["slug"]}.html">{escape(s["name"])}</a>' for s in SERVICES)
    return f"""<footer class="footer">
  <div class="container footer__grid">
    <img src="assets/img/logo.png" alt="Alvhem Städ" class="footer__logo" width="640" height="388" loading="lazy">
    <div class="footer__links">
{links}
    </div>
    <p>Alvhem Städ AB<br>Näckens väg 23, 446 34 Älvängen<br>Telefon: <a href="{PHONE_HREF}">{PHONE}</a><br>Mail: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>
  <p class="footer__copy">© <span id="year">2026</span> Alvhem Städ AB · Priser för privatpersoner inkl. moms och efter RUT-avdrag</p>
</footer>"""


def head(title, description):
    return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="theme-color" content="#ffffff">
  <link rel="icon" href="assets/img/logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400&family=Jost:wght@400;500;600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>"""


CHECK = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def service_page(s):
    contact_href = f'index.html?tjanst={s["form_value"]}#kontakt'
    price_from = '<span class="price-from">från</span> ' if s["price_from"] else ""
    intro = "\n".join(f"          <p>{escape(p)}</p>" for p in s["intro"])
    facts = "\n".join(f"            <div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>" for k, v in s["facts"])
    groups = "\n".join(
        f"""          <div class="includes__group">
            <h3>{escape(title)}</h3>
            <ul>
{chr(10).join(f'              <li>{CHECK}<span>{escape(item)}</span></li>' for item in items)}
            </ul>
          </div>"""
        for title, items in s["includes"]
    )
    faq = "\n".join(
        f"""        <details class="faq__item"{" open" if n == 0 else ""}>
          <summary>{escape(q)}</summary>
          <p>{escape(a)}</p>
        </details>"""
        for n, (q, a) in enumerate(s["faq"])
    )
    others = "\n".join(
        f"""        <a class="other" href="{o["slug"]}.html">
          <img src="{o["image"]}" alt="" loading="lazy">
          <span>{escape(o["name"])}</span>
        </a>"""
        for o in SERVICES if o["slug"] != s["slug"]
    )
    return f"""{head(s["title"], s["description"])}
<body>

{header(active=s["slug"])}

<main>

  <section class="page-hero">
    <img class="page-hero__bg" src="{s["image"]}" alt="">
    <div class="container page-hero__content">
      <nav class="crumbs" aria-label="Brödsmulor"><a href="index.html">Hem</a><span>/</span><a href="index.html#tjanster">Tjänster</a><span>/</span><span aria-current="page">{escape(s["name"])}</span></nav>
      <h1 class="display">{escape(s["headline"])}</h1>
      <p class="page-hero__lead">{escape(s["lead"])}</p>
      <div class="page-hero__actions">
        <a href="{contact_href}" class="btn btn--white">Boka kostnadsfritt uppstartsmöte</a>
        <a href="{PHONE_HREF}" class="btn btn--outline">Ring {PHONE}</a>
      </div>
    </div>
  </section>

  <section class="svc-intro">
    <div class="container svc-intro__grid">
      <div class="svc-intro__text">
        <p class="kicker">{escape(s["name"])}</p>
        <h2 class="h2">Så funkar det</h2>
{intro}
        <dl class="facts">
{facts}
        </dl>
      </div>
      <aside class="price-card" aria-label="Pris">
        <p class="price-card__label">Pris</p>
        <p class="price-card__price">{price_from}{escape(s["price"])}<small>{escape(s["price_unit"])}</small></p>
        <p class="price-card__note">{escape(s["price_note"])}</p>
        <a href="{contact_href}" class="btn btn--brand btn--block">Boka uppstartsmöte</a>
        <ul class="price-card__list">
          <li>{CHECK}<span>Kostnadsfritt uppstartsmöte</span></li>
          <li>{CHECK}<span>Nöjd kund-garanti</span></li>
          <li>{CHECK}<span>Samma städare varje gång</span></li>
        </ul>
      </aside>
    </div>
  </section>

  <section class="includes">
    <div class="container">
      <h2 class="h2">Det här ingår</h2>
      <p class="includes__lead">Exempel på vad som ingår. Det exakta upplägget anpassar vi efter dina önskemål på uppstartsmötet.</p>
      <div class="includes__grid">
{groups}
      </div>
    </div>
  </section>

  <section class="steps">
    <div class="container">
      <h2 class="h2">Tre steg till ett rent hem</h2>
      <ol class="steps__list">
        <li><span class="steps__num">01</span><h3>Kontakta oss</h3><p>Ring, mejla eller fyll i formuläret så hör vi av oss.</p></li>
        <li><span class="steps__num">02</span><h3>Uppstartsmöte</h3><p>Vi går igenom dina behov – helt kostnadsfritt.</p></li>
        <li><span class="steps__num">03</span><h3>Vi städar</h3><p>Samma städare, fast pris och RUT direkt på fakturan.</p></li>
      </ol>
    </div>
  </section>

  <section class="svc-faq">
    <div class="container svc-faq__grid">
      <h2 class="h2">Vanliga frågor</h2>
      <div class="faq">
{faq}
      </div>
    </div>
  </section>

  <section class="others">
    <div class="container">
      <h2 class="h2">Fler tjänster</h2>
      <div class="others__grid">
{others}
      </div>
    </div>
  </section>

  <section class="cta-band">
    <div class="container cta-band__inner">
      <h2 class="display display--sm">Redo för ett skinande rent hem?</h2>
      <div class="cta-band__actions">
        <a href="{contact_href}" class="btn btn--white">Boka uppstartsmöte</a>
        <a href="{PHONE_HREF}" class="btn btn--outline">{PHONE}</a>
      </div>
    </div>
  </section>

</main>

{footer()}

<script src="main.js" defer></script>
</body>
</html>
"""


def replace_between(text, start, end, new):
    a = text.index(start) + len(start)
    b = text.index(end)
    return text[:a] + "\n" + new + "\n" + text[b:]


def main():
    for s in SERVICES:
        (ROOT / f'{s["slug"]}.html').write_text(service_page(s), encoding="utf-8")
        print("skrev", f'{s["slug"]}.html')

    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    text = replace_between(text, "<!-- HEADER:START -->", "<!-- HEADER:END -->", header(active="index"))
    text = replace_between(text, "<!-- FOOTER:START -->", "<!-- FOOTER:END -->", footer())
    index.write_text(text, encoding="utf-8")
    print("uppdaterade index.html (meny och sidfot)")


if __name__ == "__main__":
    main()
