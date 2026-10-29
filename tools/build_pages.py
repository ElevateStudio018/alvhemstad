#!/usr/bin/env python3
"""Bygger tjänstesidorna och den gemensamma menyn/sidfoten.

Kör från projektroten:  python3 tools/build_pages.py

- Skriver en HTML-sida per tjänst i SERVICES (t.ex. hemstadning.html).
- Byter ut menyn och sidfoten i index.html mellan markörerna
  <!-- HEADER:START --> / <!-- HEADER:END --> och <!-- FOOTER:START --> / <!-- FOOTER:END -->,
  så att alla sidor alltid har samma meny.
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

# Elevate Studio's credit under every footer: the mark and the name, the whole of it one link to elevatestudio.nu.
ELEVATE_CREDIT = '''<!-- elevate-credit -->
<style>.elevate-credit{max-width:1240px;margin:24px auto 0;padding:20px 16px 0;border-top:1px solid rgba(128,128,128,.25);display:flex;justify-content:center;box-sizing:border-box}.elevate-credit a{display:inline-flex;align-items:center;gap:10px;padding:8px 0;font:inherit;font-size:15px;line-height:1;color:inherit;opacity:.55;text-decoration:none;transition:opacity .2s}.elevate-credit a:hover,.elevate-credit a:focus-visible{opacity:1}.elevate-credit svg{width:20px;height:20px;flex:none;display:block}@media(min-width:1024px){.elevate-credit a{font-size:16px}}</style>
<div class="elevate-credit"><a href="https://elevatestudio.nu" target="_blank" rel="noopener"><svg viewBox="0 0 1884.3 1353.9" aria-hidden="true"><path d="M0.0 1353.9 L1218.7 0.0 L1218.7 329.1 L479.7 1136.4 L786.7 1132.4 L1215.5 687.4 L1884.3 1349.9 L1590.1 1349.9 L1218.6 994.7 L865.4 1349.9Z" fill="currentColor"/></svg>Byggd av Elevate Studio</a></div>
'''


ROOT = Path(__file__).resolve().parent.parent
PHONE = "076 022 39 90"
PHONE_HREF = "tel:+46760223990"
EMAIL = "info@alvhemstad.se"
# Webbplatsens riktiga adress. Används för canonical, sitemap och strukturerad data.
SITE_URL = "https://www.alvhemstad.se/"
BUSINESS_ID = SITE_URL + "#foretag"

# Bredder som tools/optimize_images.py skapar för varje bild (assets/img/<namn>-<bredd>.webp)
IMAGE_WIDTHS = {
    "hem": [480, 800, 1200, 1400],
    "stor": [480, 800, 1200, 1400],
    "flytt": [480, 800, 1200, 1400],
    "kontor": [480, 800, 1200, 1400],
    "hero-fonster-poster": [480, 800, 1280],
}

# Vanliga frågor på startsidan (visas på sidan och som FAQPage-data för Google och AI-sök)
HOME_FAQ = [
    ("Vad kostar hemstädning hos Alvhem Städ?", "Hemstädning kostar 249 kr per timme inklusive moms efter RUT-avdrag. Vi har fasta priser, så du vet alltid vad du betalar."),
    ("Hur fungerar RUT-avdraget?", "Du får 50 % RUT-avdrag direkt på fakturan för hemstädning, storstädning och flyttstädning. Alla priser för privatpersoner anges inklusive moms och efter RUT-avdrag."),
    ("Vilka tjänster erbjuder ni?", "Hemstädning, storstädning, flyttstädning och kontorsstädning. Vi erbjuder nu även fönsterputsning och trädgårdsarbete."),
    ("Vad kostar fönsterputs och trädgårdsarbete?", "Fönsterputsning och trädgårdsarbete kostar 299 kr per timme inklusive moms efter RUT-avdrag."),
    ("Var finns Alvhem Städ?", "Vi finns på Näckens väg 23 i Älvängen i Ale kommun. Kontakta oss så berättar vi om vi kan hjälpa dig där du bor."),
    ("Hur kommer jag igång?", "Vi börjar alltid med ett kostnadsfritt uppstartsmöte där vi anpassar städningen efter dina behov. Ring 076 022 39 90 eller mejla info@alvhemstad.se."),
    ("Får jag samma städare varje gång?", "Ja. Du får samma städare vid alla städtillfällen."),
    ("Finns det bindningstid?", "Hemstädning på abonnemang har en månads bindningstid. Du kan avboka ett städtillfälle kostnadsfritt senast 2 arbetsdagar i förväg."),
    ("Ingår rengöringsmedel?", "Vid hemstädning står vi för rengöringsmedel om du vill. Då debiteras 60 kr inklusive moms per städtillfälle."),
]

SERVICES = [
    {
        "slug": "hemstadning",
        "name": "Hemstädning",
        "form_value": "Hemstädning",
        "image": "assets/img/hem.jpg",
        "image_alt": "Välstädat vardagsrum i dagsljus",
        "title": "Hemstädning i Ale – fast pris och samma städare varje gång",
        "description": "Regelbunden hemstädning på abonnemang i Ale. 249 kr/h inkl. moms efter RUT, samma städare vid alla tillfällen och nöjd kund-garanti.",
        "headline": "Hemstädning",
        "lead": "Kom hem till ett rent och fräscht hem – varje vecka, varannan vecka eller var fjärde vecka. Vi sköter städningen så att du får mer tid till det som betyder något.",
        "price": "249 kr",
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
        "title": "Storstädning i Ale – grundlig städning från 275 kr/h",
        "description": "Storstädning i Ale som får bostaden att kännas som ny. Från 275 kr/h inkl. moms efter RUT, med kvalitetsgaranti.",
        "headline": "Storstädning",
        "lead": "Ett riktigt grundligt städtillfälle som får bostaden att kännas som ny – inför långhelger, gäster, högtider eller bara när det är dags.",
        "price": "275 kr",
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
            ("Vad kostar en storstädning?", "Från 275 kr per timme inklusive moms efter RUT-avdrag. Abonnemangskunder betalar sitt vanliga pris."),
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
            ("Ingår fönsterputsning?", "Fönsterputsning kan läggas till för 299 kr per timme inklusive moms efter RUT-avdrag. Berätta när du bokar."),
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
        "description": "Fönsterputsning och trädgårdsarbete i Ale för 299 kr/h inkl. moms efter RUT-avdrag. Nu även hos Alvhem Städ – samma städare och nöjd kund-garanti.",
        "headline": "Fönsterputs & trädgård",
        "lead": "Nyhet hos Alvhem Städ: vi hjälper dig nu även med fönsterputsning och trädgårdsarbete. Hör av dig så berättar vi mer.",
        "price": "299 kr",
        "price_unit": "/timme",
        "price_from": False,
        "price_note": "Gäller både fönsterputs och trädgårdsarbete. Inkl. moms, efter 50 % RUT-avdrag.",
        "intro": [
            "Skinande rena fönster gör stor skillnad för hur ett hem känns – mer ljus och en klarare utsikt. Vi putsar fönster i bostäder och lokaler.",
            "Vi hjälper även till med trädgårdsarbete, så att du kan njuta av trädgården i stället för att arbeta i den. Berätta vad du behöver hjälp med så tar vi fram ett förslag.",
        ],
        "facts": [
            ("Fönsterputs", "Bostäder och lokaler"),
            ("Trädgård", "Efter dina behov"),
            ("Pris", "299 kr/h efter RUT"),
            ("Garanti", "Nöjd kund-garanti"),
        ],
        "includes": [
            ("Fönsterputsning", ["Fönster in- och utvändigt", "Mellan glasen på kopplade fönster", "Avtorkning av karmar och fönsterbänkar", "Glaspartier och altandörrar"]),
            ("Trädgårdsarbete", ["Gräsklippning", "Rensning av rabatter och gångar", "Häckklippning", "Lövkrattning och bortforsling efter överenskommelse"]),
        ],
        "faq": [
            ("Vad kostar det?", "Fönsterputsning och trädgårdsarbete kostar 299 kr per timme inklusive moms efter RUT-avdrag."),
            ("Får jag RUT-avdrag?", "Ja, du får 50 % RUT-avdrag direkt på fakturan. Priset 299 kr/h är efter avdraget."),
            ("Kan jag kombinera med hemstädning?", "Ja, hör av dig så tar vi fram ett upplägg som passar dig."),
        ],
    },
]

def srcset(stem):
    return ", ".join(f"assets/img/{stem}-{w}.webp {w}w" for w in IMAGE_WIDTHS[stem])


def img_src(stem, max_w=1200):
    fitting = [w for w in IMAGE_WIDTHS[stem] if w <= max_w]
    return f"assets/img/{stem}-{(fitting or IMAGE_WIDTHS[stem])[-1]}.webp"


def stem_of(service):
    return Path(service["image"]).stem


def business_jsonld():
    return {
        "@context": "https://schema.org",
        "@type": "HouseCleaningService",
        "@id": BUSINESS_ID,
        "name": "Alvhem Städ AB",
        "alternateName": "Alvhem Städ",
        "description": "Städfirma i Älvängen, Ale kommun. Hemstädning, storstädning, flyttstädning, kontorsstädning, fönsterputsning och trädgårdsarbete med fasta priser och 50 % RUT-avdrag direkt på fakturan.",
        "url": SITE_URL,
        "logo": SITE_URL + "assets/img/logo.png",
        "image": SITE_URL + "assets/img/hero-fonster-poster.jpg",
        "telephone": "+46760223990",
        "email": EMAIL,
        "priceRange": "249–350 kr/h",
        "currenciesAccepted": "SEK",
        "address": {"@type": "PostalAddress", "streetAddress": "Näckens väg 23", "postalCode": "446 34", "addressLocality": "Älvängen", "addressRegion": "Västra Götalands län", "addressCountry": "SE"},
        "areaServed": [{"@type": "City", "name": "Älvängen"}, {"@type": "AdministrativeArea", "name": "Ale kommun"}],
        "hasMap": "https://www.google.com/maps/dir//N%C3%A4ckens+v%C3%A4g+23,+44634+%C3%84lv%C3%A4ngen",
        "award": "Certifierad kvalitetspartner 2024",
        "knowsLanguage": "sv",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Städtjänster",
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": SITE_URL + s["slug"] + ".html"}} for s in SERVICES],
        },
    }


def faq_jsonld(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items],
    }


def price_number(s):
    return "".join(ch for ch in s["price"] if ch.isdigit())


def service_jsonld(s):
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": s["name"],
        "serviceType": s["name"],
        "description": s["description"],
        "url": SITE_URL + s["slug"] + ".html",
        "image": SITE_URL + img_src(stem_of(s)),
        "provider": {"@id": BUSINESS_ID},
        "areaServed": [{"@type": "City", "name": "Älvängen"}, {"@type": "AdministrativeArea", "name": "Ale kommun"}],
    }
    if price_number(s):
        unit = {"/timme": "HUR", "/kvm": "MTK"}.get(s["price_unit"], "")
        spec = {"@type": "UnitPriceSpecification", "price": price_number(s), "priceCurrency": "SEK", "description": s["price_note"]}
        if unit:
            spec["unitCode"] = unit
        if s["price_from"]:
            spec["minPrice"] = price_number(s)
        data["offers"] = {"@type": "Offer", "priceCurrency": "SEK", "price": price_number(s), "priceSpecification": spec}
    return data


def breadcrumb_jsonld(s):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Hem", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Tjänster", "item": SITE_URL + "#tjanster"},
            {"@type": "ListItem", "position": 3, "name": s["name"], "item": SITE_URL + s["slug"] + ".html"},
        ],
    }


def website_jsonld():
    return {"@context": "https://schema.org", "@type": "WebSite", "name": "Alvhem Städ", "url": SITE_URL, "inLanguage": "sv-SE", "publisher": {"@id": BUSINESS_ID}}


def inline_css():
    """styles.css minifierad och inbäddad i sidan, så att ingen CSS-fil blockerar första visningen."""
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    # url() i CSS:en är relativa till styles.css i roten, vilket är samma som sidorna
    return css.strip()


def head_tags(title, description, path, og_image, jsonld, preloads=""):
    url = SITE_URL + path
    scripts = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>' for d in jsonld
    )
    return f"""  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#8a4c7d">
  <meta name="geo.region" content="SE-O">
  <meta name="geo.placename" content="Älvängen">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="sv_SE">
  <meta property="og:site_name" content="Alvhem Städ">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE_URL + og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/img/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="preload" href="assets/fonts/fraunces-var-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{preloads}  <style>{inline_css()}</style>
{scripts}"""


def page_head(*args, **kwargs):
    return f"""<!doctype html>
<html lang="sv">
<head>
{head_tags(*args, **kwargs)}
</head>"""


def header(active=""):
    service_links = "\n".join(
        f'          <a href="{s["slug"]}.html"{" aria-current=\"page\"" if s["slug"] == active else ""}>{escape(s["name"])}</a>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(f'    <a href="{s["slug"]}.html" class="sub">{escape(s["name"])}</a>' for s in SERVICES)
    home_active = ' class="is-active" aria-current="page"' if active == "index" else ""
    services_active = " is-active" if active and active != "index" else ""
    return f"""<header class="header" id="header">
  <div class="header__inner">
    <a href="index.html" class="header__logo" aria-label="Alvhem Städ – till startsidan">
      <img src="assets/img/logo-300.webp" alt="Alvhem Städ" class="logo-dark" width="300" height="182">
      <img src="assets/img/logo-light-300.webp" alt="" class="logo-light" width="300" height="182">
    </a>
    <nav class="header__nav" aria-label="Huvudmeny">
      <a href="index.html"{home_active}>Hem</a>
      <a href="index.html#kontakt">Boka nu</a>
      <div class="dropdown">
        <a href="index.html#tjanster" class="dropdown__toggle{services_active}">Våra tjänster</a>
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
    <img src="assets/img/logo-300.webp" alt="Alvhem Städ" class="footer__logo" width="300" height="182" loading="lazy">
    <nav class="footer__links" aria-label="Tjänster">
{links}
    </nav>
    <address>Alvhem Städ AB<br>Näckens väg 23, 446 34 Älvängen<br>Telefon: <a href="{PHONE_HREF}">{PHONE}</a><br>Mail: <a href="mailto:{EMAIL}">{EMAIL}</a></address>
  </div>
  <p class="footer__copy">© <span id="year">2026</span> Alvhem Städ AB · Priser för privatpersoner inkl. moms och efter RUT-avdrag</p>
{ELEVATE_CREDIT}</footer>"""


CHECK = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def faq_html(items, open_first=True):
    return "\n".join(
        f"""        <details class="faq__item"{" open" if open_first and n == 0 else ""}>
          <summary>{escape(q)}</summary>
          <p>{escape(a)}</p>
        </details>"""
        for n, (q, a) in enumerate(items)
    )


def service_page(s):
    contact_href = f'index.html?tjanst={s["form_value"]}#kontakt'
    price_from = '<span class="price-from">från</span> ' if s["price_from"] else ""
    stem = stem_of(s)
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
    others = "\n".join(
        f"""        <a class="other" href="{o["slug"]}.html">
          <img src="{img_src(stem_of(o), 480)}" srcset="{srcset(stem_of(o))}" sizes="(max-width: 560px) 100vw, (max-width: 860px) 50vw, 300px" alt="" width="480" height="360" loading="lazy" decoding="async">
          <span>{escape(o["name"])}</span>
        </a>"""
        for o in SERVICES if o["slug"] != s["slug"]
    )
    preload = f'  <link rel="preload" as="image" imagesrcset="{srcset(stem)}" imagesizes="100vw" fetchpriority="high">\n'
    head = page_head(
        s["title"], s["description"], f'{s["slug"]}.html', s["image"],
        [business_jsonld(), service_jsonld(s), breadcrumb_jsonld(s), faq_jsonld(s["faq"])],
        preloads=preload,
    )
    return f"""{head}
<body>

<a class="skip" href="#main">Hoppa till innehållet</a>

{header(active=s["slug"])}

<main id="main">

  <section class="page-hero">
    <img class="page-hero__bg" src="{img_src(stem)}" srcset="{srcset(stem)}" sizes="100vw" alt="{escape(s["image_alt"])}" width="1200" height="900" fetchpriority="high" decoding="async">
    <div class="container page-hero__content">
      <nav class="crumbs" aria-label="Brödsmulor"><a href="index.html">Hem</a><span aria-hidden="true">/</span><a href="index.html#tjanster">Tjänster</a><span aria-hidden="true">/</span><span aria-current="page">{escape(s["name"])}</span></nav>
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
        <p class="kicker">{escape(s["name"])} i Ale</p>
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
        <li><span class="steps__num" aria-hidden="true">01</span><h3>Kontakta oss</h3><p>Ring, mejla eller fyll i formuläret så hör vi av oss.</p></li>
        <li><span class="steps__num" aria-hidden="true">02</span><h3>Uppstartsmöte</h3><p>Vi går igenom dina behov – helt kostnadsfritt.</p></li>
        <li><span class="steps__num" aria-hidden="true">03</span><h3>Vi städar</h3><p>Samma städare, fast pris och RUT direkt på fakturan.</p></li>
      </ol>
    </div>
  </section>

  <section class="svc-faq">
    <div class="container svc-faq__grid">
      <h2 class="h2">Vanliga frågor om {escape(s["name"].lower())}</h2>
      <div class="faq">
{faq_html(s["faq"])}
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
        <a href="{PHONE_HREF}" class="btn btn--outline">Ring {PHONE}</a>
      </div>
    </div>
  </section>

</main>

{footer()}

<script src="main.js" defer></script>
</body>
</html>
"""


INDEX_TITLE = "Städfirma i Älvängen & Ale – Hemstädning från 249 kr/h | Alvhem Städ"
INDEX_DESCRIPTION = "Alvhem Städ i Älvängen, Ale: hemstädning 249 kr/h efter RUT, storstädning, flyttstädning och kontorsstädning. Fasta priser, samma städare och nöjd kund-garanti."


def index_head():
    preloads = (
        '  <link rel="preload" as="image" href="assets/img/hero-fonster-poster-mobil.webp" media="(max-width: 860px)" fetchpriority="high">\n'
        '  <link rel="preload" as="image" href="assets/img/hero-fonster-poster-1280.webp" media="(min-width: 861px)" fetchpriority="high">\n'
    )
    return head_tags(INDEX_TITLE, INDEX_DESCRIPTION, "", "assets/img/hero-fonster-poster.jpg",
                     [business_jsonld(), website_jsonld(), faq_jsonld(HOME_FAQ)], preloads=preloads)


def sitemap():
    today = date.today().isoformat()
    urls = [("", "1.0")] + [(s["slug"] + ".html", "0.8") for s in SERVICES]
    rows = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>" for u, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'


def robots():
    return f"""User-agent: *
Allow: /

# AI-sökmotorer och assistenter är välkomna
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /

Sitemap: {SITE_URL}sitemap.xml
"""


def llms_txt():
    lines = [
        "# Alvhem Städ AB",
        "",
        "> Städfirma i Älvängen, Ale kommun. Hemstädning, storstädning, flyttstädning, kontorsstädning, fönsterputsning och trädgårdsarbete. Fasta priser, samma städare vid varje tillfälle, nöjd kund-garanti och 50 % RUT-avdrag direkt på fakturan.",
        "",
        "## Kontakt",
        f"- Telefon: {PHONE}",
        f"- E-post: {EMAIL}",
        "- Adress: Näckens väg 23, 446 34 Älvängen",
        "- Första steget: kostnadsfritt uppstartsmöte",
        "",
        "## Tjänster och priser (privatpersoner, inkl. moms efter RUT)",
    ]
    for s in SERVICES:
        price = ("från " if s["price_from"] else "") + s["price"] + s["price_unit"]
        lines.append(f'- [{s["name"]}]({SITE_URL}{s["slug"]}.html): {price}. {s["price_note"]}')
    lines += ["", "## Vanliga frågor"]
    lines += [f"- {q} {a}" for q, a in HOME_FAQ]
    lines += ["", "## Villkor",
              "- Hemstädning på abonnemang: en månads bindningstid.",
              "- Rengöringsmedel vid hemstädning: 60 kr inkl. moms per tillfälle (valfritt).",
              "- Avbokning: kostnadsfritt senast 2 arbetsdagar i förväg.",
              "- Certifierad kvalitetspartner 2024.", ""]
    return "\n".join(lines)


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
    text = replace_between(text, "<!-- HEAD:START -->", "<!-- HEAD:END -->", index_head())
    text = replace_between(text, "<!-- HEADER:START -->", "<!-- HEADER:END -->", header(active="index"))
    text = replace_between(text, "<!-- FAQ:START -->", "<!-- FAQ:END -->", faq_html(HOME_FAQ))
    text = replace_between(text, "<!-- FOOTER:START -->", "<!-- FOOTER:END -->", footer())
    index.write_text(text, encoding="utf-8")
    print("uppdaterade index.html")

    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots(), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms_txt(), encoding="utf-8")
    print("skrev sitemap.xml, robots.txt, llms.txt")


if __name__ == "__main__":
    main()
