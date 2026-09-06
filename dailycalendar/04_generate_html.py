#!/usr/bin/env python3
"""
04_generate_html.py
-------------------
Generates a print-ready HTML daily calendar for 2027.
Page size: 127 mm × 102 mm (landscape-ish).

Each physical day = 2 HTML pages in the output:
  Front – header (Ayah/Hadith | Date | Event) + 28-city prayer times table
  Back  – Islamic reminder (Topic + Text + Dua)

Page order in HTML: front₁, back₁, front₂, back₂ … (duplex-friendly)

Reads:
  dailycalendar/data/prayer_times_2027.json
  dailycalendar/data/reminders_no.json

Output:
  dailycalendar/output/kalender-2027-daglig.html
"""

import base64
import json
import re
import sys
from datetime import date as _date
from html import escape as esc
from pathlib import Path

HERE     = Path(__file__).resolve().parent
LOGO     = HERE.parent / "logo.png"
COVER_IMG = HERE.parent / "cover.png"
PRAYER   = HERE / "data" / "prayer_times_2027.json"
REM_NO   = HERE / "data" / "reminders_no.json"
QUOTES   = HERE / "data" / "quotes.json"
OUTPUT   = HERE / "output" / "kalender-2027-daglig.html"

# Cities in Norwegian alphabetical order (Æ, Ø, Å come after Z)
CITY_LEFT = [
    "Bastøy", "Bergen", "Bjørgvin", "Bodø", "Eidsberg",
    "Froland", "Halden", "Hamar", "Hustad", "Ila", "Kongsvinger",
    "Kroksrud", "Mandal", "Ringerike",
]
CITY_RIGHT = [
    "Sandeid", "Sarpsborg", "Sem", "Skien", "Stavanger",
    "Tromsø", "Trondheim", "Trøgstad", "Tønsberg", "Ullersmo", "Vadsø", "Vik",
    "Ålesund", "Åna",
]

PRAYER_KEYS  = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
PRAYER_HEADS = ["Fajr", "Sol↑", "Zuhr", "Asr", "Maghr", "Isha"]

# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
@page { size: 127mm 102mm; margin: 1.5mm; }
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 6pt; color: #111; }

/* ── shared page shell ── */
.page {
  width: 124mm;
  height: 99mm;
  overflow: hidden;
  page-break-after: always;
  position: relative;
}
.page:last-child { page-break-after: auto; }

/* ────────────────────────── FRONT PAGE ───────────────────────────────── */

/* Make the front page a flex column so prayer area fills all leftover height */
.front {
  display: flex;
  flex-direction: column;
  padding: 1mm 1.5mm 0.5mm;
}

.front .header {
  display: flex;
  flex-shrink: 0;
  border-bottom: 0.35mm solid #1a3a5c;
  padding-bottom: 0.8mm;
  margin-bottom: 0.8mm;
  gap: 1mm;
}

/* Left column – Ayah / Hadith */
.col-ayah {
  width: 36mm;
  padding: 0.5mm 1mm 0.5mm 0;
  border-right: 0.2mm solid #c0cfe0;
  overflow: hidden;
}
.col-ayah h4 {
  font-size: 4.5pt;
  font-weight: bold;
  color: #1a3a5c;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: 0.5mm;
}
.col-ayah p {
  font-size: 5pt;
  font-style: italic;
  color: #333;
  line-height: 1.35;
}

/* Centre column – Date block */
.col-date {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.1mm;
}
.date-num {
  font-size: 26pt;
  font-weight: 900;
  color: #1a3a5c;
  line-height: 1;
}
.date-wd {
  font-size: 7pt;
  font-weight: bold;
  color: #222;
  letter-spacing: 0.03em;
}
.date-mth {
  font-size: 6.5pt;
  color: #333;
}
.date-hijri {
  font-size: 5pt;
  color: #555;
}
.date-doy {
  font-size: 4.5pt;
  color: #888;
  margin-top: 0.3mm;
}

/* Right column – Event (historical events) */
.col-event {
  width: 36mm;
  padding: 0.5mm 0 0.5mm 1mm;
  border-left: 0.2mm solid #c0cfe0;
  overflow: hidden;
}
.col-event h4 {
  font-size: 4.5pt;
  font-weight: bold;
  color: #1a3a5c;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: 0.5mm;
}
.col-event p {
  font-size: 5pt;
  color: #333;
  line-height: 1.35;
}
.col-event p.qt { font-style: italic; }
.col-event p.qa {
  font-size: 4.5pt;
  color: #666;
  text-align: right;
  margin-top: 0.6mm;
  font-style: normal;
}

/* ── Prayer-times section ── */
.prayer-area {
  flex: 1;                  /* grow to fill remaining page height */
  display: flex;
  gap: 0;
  position: relative;
}
/* Logo watermark centred behind both tables */
.prayer-watermark {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 72mm; height: 72mm;
  margin: auto;
  background: url("__LOGO_URI__") no-repeat center center;
  background-size: contain;
  opacity: 0.06;
  pointer-events: none;
  z-index: 2;
}
.prayer-wrap {
  flex: 1;
  overflow: hidden;
  position: relative;
  z-index: 1;
}
.prayer-wrap:first-child { border-right: 0.3mm solid #c0cfe0; padding-right: 0.3mm; }
.pt {
  border-collapse: collapse;
  width: 100%;
  height: 100%;             /* stretch rows to fill the prayer-wrap */
  font-size: 6pt;
}
.pt thead tr th {
  background: #1a3a5c;
  color: #fff;
  padding: 0.8mm 0.3mm;
  text-align: center;
  font-size: 5.5pt;
  font-weight: bold;
  white-space: nowrap;
}
.pt thead tr th.ch {
  text-align: left;
  padding-left: 0.8mm;
}
.pt tbody tr td {
  padding: 0.5mm 0.3mm;
  text-align: center;
  border-bottom: 0.15mm solid #d8e8f4;
  color: #1a4060;
  font-size: 6pt;
}
.pt tbody tr td.city {
  text-align: left;
  font-weight: 600;
  color: #1a3a5c;
  padding-left: 0.8mm;
  white-space: nowrap;
  overflow: hidden;
  max-width: 16mm;
}
.pt tbody tr:nth-child(even) td { background: #e6f0f9; }
.pt tbody tr:nth-child(odd)  td { background: #f4f9fd; }

/* ────────────────────────── BACK PAGE ────────────────────────────────── */

.back {
  padding: 2mm 2.5mm 1.5mm;
  height: 99mm;
  display: flex;
  flex-direction: column;
  background: #fafcff;
}
.back-topic {
  font-size: 7.5pt;
  font-weight: bold;
  color: #1a3a5c;
  text-align: center;
  border-bottom: 0.5mm solid #1a3a5c;
  padding-bottom: 1mm;
  margin-bottom: 1.5mm;
  line-height: 1.25;
}
.back-text {
  font-size: 5.5pt;
  line-height: 1.4;
  text-align: justify;
  color: #1a1a1a;
  flex: 1;
  overflow: hidden;
  hyphens: auto;
}
.back-dua {
  margin-top: 1.5mm;
  padding: 1mm 1.5mm;
  background: #e8f0fb;
  border: 0.3mm solid #2c5f8a;
  border-radius: 0.8mm;
  flex-shrink: 0;
}
.dua-label {
  font-size: 4.5pt;
  font-weight: bold;
  color: #1a3a5c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.dua-text {
  font-size: 5pt;
  font-style: italic;
  color: #1a3a5c;
  line-height: 1.35;
  margin-top: 0.3mm;
}
.dua-translit {
  font-size: 4.8pt;
  color: #2c5f8a;
  font-style: italic;
  line-height: 1.4;
  margin-top: 0.5mm;
  border-top: 0.15mm solid #b0c8e8;
  padding-top: 0.4mm;
}
.dua-source {
  font-size: 4.2pt;
  color: #7a8fa6;
  font-style: normal;
  margin-top: 0.5mm;
  line-height: 1.3;
}
.translit-badge {
  display: inline-block;
  background: #1a3a5c;
  color: #fff;
  font-weight: 700;
  font-size: 5pt;
  padding: 0.3mm 1mm;
  border-radius: 0.6mm;
  letter-spacing: 0.02em;
  margin: 0.5mm 0;
}
/* ── Page number (bottom-right corner) ── */
.page-num {
  position: absolute;
  bottom: 0.8mm;
  right: 1.5mm;
  font-size: 4pt;
  color: #7a8fa6;
}
.page.back .page-num {
  font-size: 5.5pt;
  color: #2c5f8a;
}

/* ──────────────────────── DUA TABLE OF CONTENTS ──────────────────────── */
.toc-page {
  padding: 2mm 2mm 1mm;
  background: #fafcff;
}
.toc-title {
  font-size: 8pt;
  font-weight: 900;
  color: #1a3a5c;
  text-align: center;
  border-bottom: 0.5mm solid #1a3a5c;
  padding-bottom: 0.8mm;
  margin-bottom: 1.5mm;
  letter-spacing: 0.02em;
}
.toc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0 2mm;
  font-size: 4.5pt;
  line-height: 1.55;
}
.toc-entry {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.toc-pg {
  color: #2c5f8a;
  font-weight: 600;
}

/* ────────────────────────── COVER PAGE ───────────────────────────────── */
.cover {
  background: #fff;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
  position: relative;
}
.cover-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
}

/* ────────────────────────── EMPTY PAGE ───────────────────────────────── */
.empty {
  background: #fafcff;
}

/* ────────────────────────── INFO PAGE ────────────────────────────────── */
.info-page {
  padding: 3mm 3.5mm 2mm;
  background: #fafcff;
  display: flex;
  flex-direction: column;
}
.info-page h2 {
  font-size: 8.5pt;
  font-weight: 900;
  color: #1a3a5c;
  border-bottom: 0.5mm solid #1a3a5c;
  padding-bottom: 1mm;
  margin-bottom: 2mm;
  text-align: center;
  letter-spacing: 0.02em;
}
.info-page h3 {
  font-size: 6pt;
  font-weight: bold;
  color: #1a3a5c;
  margin-top: 1.5mm;
  margin-bottom: 0.5mm;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.info-page p {
  font-size: 5.4pt;
  line-height: 1.45;
  color: #1a1a1a;
  text-align: justify;
  hyphens: auto;
  margin-bottom: 1mm;
}
.info-page ul {
  font-size: 5.4pt;
  line-height: 1.5;
  color: #1a1a1a;
  padding-left: 3.5mm;
  margin-bottom: 1mm;
}
.info-page ul li {
  margin-bottom: 0.3mm;
}
.info-page .highlight-box {
  background: #e8f0fb;
  border-left: 0.8mm solid #1a3a5c;
  padding: 1mm 1.5mm;
  margin: 1.5mm 0;
  font-size: 5.4pt;
  color: #1a1a1a;
  line-height: 1.45;
}
.info-page .web-link {
  font-size: 5pt;
  color: #2c5f8a;
  text-align: center;
  margin-top: auto;
  padding-top: 1.5mm;
  border-top: 0.2mm solid #c0cfe0;
}

/* ── Screen preview ── */
@media screen {
  body { background: #3a3a3a; padding: 10px; }
  .page {
    background: #fff;
    margin: 6px auto;
    box-shadow: 0 2px 10px rgba(0,0,0,.45);
  }
}
"""

# ── helpers ──────────────────────────────────────────────────────────────────

def _p(text: str, cls: str = "") -> str:
    """Wrap escaped text in <p>."""
    cls_attr = f' class="{cls}"' if cls else ""
    return f"<p{cls_attr}>{esc(text)}</p>"


def prayer_table(cities: list[str], city_data: dict) -> str:
    """Build one half-page prayer-time <table>."""
    heads = "".join(
        f'<th class="ch">Sted</th>' +
        "".join(f"<th>{h}</th>" for h in PRAYER_HEADS)
    )
    rows = []
    for city in cities:
        times = city_data.get(city, {})
        cells = "".join(
            f"<td>{esc(times.get(k, '—'))}</td>" for k in PRAYER_KEYS
        )
        rows.append(
            f'<tr><td class="city">{esc(city)}</td>{cells}</tr>'
        )
    return (
        '<table class="pt">'
        f"<thead><tr>{heads}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def front_page(date_str: str, meta: dict, rem: dict, quote_entry: dict = None, page_num: int = 0) -> str:
    if quote_entry is None:
        quote_entry = {}
    hijri    = meta.get("hijri", {})
    ayah     = rem.get("ayah_hadith", "")
    q_title  = quote_entry.get("title", "Vise ord")
    q_text   = quote_entry.get("quote", rem.get("event", ""))
    q_author = quote_entry.get("author", "")
    cities_data = meta.get("cities", {})

    hijri_str = (
        f"{hijri.get('day', '')} {hijri.get('month', '')} {hijri.get('year', '')} H"
    )
    doy       = meta.get("day_of_year", "")
    days_left = meta.get("days_left", "")
    week_num  = _date.fromisoformat(date_str).isocalendar()[1]

    header = f"""
<div class="header">
  <div class="col-ayah">
    <h4>Ayah / Hadith</h4>
    <p>{esc(ayah)}</p>
  </div>
  <div class="col-date">
    <div class="date-num">{meta.get('day', ''):02d}</div>
    <div class="date-wd">{esc(meta.get('weekday', ''))}</div>
    <div class="date-mth">{esc(meta.get('month', ''))} {meta.get('year', '')}</div>
    <div class="date-hijri">{esc(hijri_str)}</div>
    <div class="date-doy">Uke {week_num} &nbsp;·&nbsp; Dag {doy} &nbsp;·&nbsp; {days_left} igjen</div>
  </div>
  <div class="col-event">
    <h4>{esc(q_title)}</h4>
    <p class="qt">{esc(q_text)}</p>
    {f'<p class="qa">— {esc(q_author)}</p>' if q_author else ''}
  </div>
</div>"""

    prayers = f"""
<div class="prayer-area">
  <div class="prayer-watermark"></div>
  <div class="prayer-wrap">{prayer_table(CITY_LEFT,  cities_data)}</div>
  <div class="prayer-wrap">{prayer_table(CITY_RIGHT, cities_data)}</div>
</div>"""

    pn_tag = f'<div class="page-num">{page_num}</div>' if page_num else ""

    return (
        f'<div class="page front" data-date="{date_str}">'
        f"{header}{prayers}"
        f"{pn_tag}"
        f"</div>"
    )


def back_page(date_str: str, rem: dict, page_num: int = 0) -> str:
    topic        = rem.get("topic", "")
    text         = rem.get("text",  "")
    dua          = rem.get("dua",   "")
    dua_translit = rem.get("dua_translit", "")

    def render_line(line: str) -> str:
        """Escape HTML then convert **bold**, _italic_, and [translit] markers."""
        s = esc(line)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'_(.+?)_', r'<em>\1</em>', s)
        s = re.sub(
            r'\[translit\](.+?)\[/translit\]',
            r'<span class="translit-badge">\1</span>',
            s,
        )
        return s

    # Convert newlines in text to <br> tags, applying inline formatting
    text_html = "<br>".join(render_line(line) for line in text.splitlines()) if text else ""

    dua_source = rem.get("dua_source", "")
    dua_grade  = rem.get("dua_grade",  "")

    dua_block = ""
    if dua:
        translit_html = (
            f'<div class="dua-translit">{esc(dua_translit)}</div>'
            if dua_translit else ""
        )
        source_parts = [p for p in [dua_source, dua_grade] if p]
        source_html = (
            f'<div class="dua-source">{esc(" · ".join(source_parts))}</div>'
            if source_parts else ""
        )
        dua_block = (
            '<div class="back-dua">'
            '<div class="dua-label">Dua</div>'
            f'<div class="dua-text">{esc(dua)}</div>'
            f'{translit_html}'
            f'{source_html}'
            "</div>"
        )

    pn_tag = f'<div class="page-num">{page_num}</div>' if page_num else ""

    return (
        f'<div class="page back" data-date="{date_str}">'
        f'<div class="back">'
        f'<div class="back-topic">{esc(topic)}</div>'
        f'<div class="back-text">{text_html}</div>'
        f"{dua_block}"
        f"</div>"
        f"{pn_tag}"
        f"</div>"
    )


def cover_page(logo_uri: str, cover_uri: str = "") -> str:
    """Hard cover page: background image only."""
    cover_bg = f'<div class="cover-bg" style="background-image:url({cover_uri})"></div>' if cover_uri else ""
    return (
        '<div class="page cover">'
        f"{cover_bg}"
        "</div>"
    )


def empty_page() -> str:
    """A completely blank page (back of cover, back of info pages)."""
    return '<div class="page empty"></div>'


def org_info_page() -> str:
    """Page about the Fengselsimamene organisation."""
    return (
        '<div class="page info-page">'
        "<h2>Om Fengselsimamene</h2>"

        "<p>Fengselsimamene er en frivillig norsk organisasjon som arbeider for å "
        "gi deg som er innsatt muligheten til åndelig veiledning, bønn og refleksjon. "
        "Vi er her for deg – ikke som dommere, men som brødre i tro og som støttespillere "
        "på din vei.</p>"

        "<h3>Hva gjør vi?</h3>"
        "<ul>"
        "<li>Jobber for at du skal ha lik tilgang på religiøs veiledning</li>"
        "<li>Formidler islamsk litteratur og materiell til innsatte</li>"
        "<li>Tilbyr personlige samtaler og sjelesorg i fortrolighet</li>"
        "<li>Holder fredagsbønn og eid-bønn i norske fengsler</li>"
        "</ul>"

        '<div class="highlight-box">'
        "En stor andel innsatte rundt omkring i Norge har muslimsk bakgrunn – likevel "
        "har disse ikke tilgang til islamsk veiledning og materiell. Dette vil vi gjøre noe med!"
        "</div>"

        "<h3>Vår visjon</h3>"
        "<p>Vi tror at tro, håp og fellesskap er blant de sterkeste kreftene for forandring. "
        "Mange av oss som jobber i Fengselsimamene har sett med egne øyne hvordan troen "
        "kan gi et menneske ny retning og ny styrke. Det er den forandringen vi ønsker "
        "å være en del av – for deg.</p>"

        "<h3>Hvordan kan du kontakte oss?</h3>"
        "<p>Vår hovedkanal for kommunikasjon er gjennom fengslelsadministrasjonene, som kan formidle beskjeder og materiell mellom deg og oss. "
        "Du kan også skrive til oss på følgende adresse:</p>"
        '<div class="highlight-box">'
        "<p> Hjemmeside: www.fengselsimamene.no</p>"
        "<p> Epost: <a href='mailto:fengselsimamene@gmail.com'>fengselsimamene@gmail.com</a></p>"
        "</div>"

        '<div class="web-link">fengselsimamene.no</div>'
        "</div>"
    )


def calendar_info_page() -> str:
    """Page explaining how to use the prayer calendar."""
    return (
        '<div class="page info-page">'
        "<h2>Om denne kalenderen</h2>"

        "<p>Denne bønnetidskalenderen er laget spesielt for deg som er innsatt i et norsk "
        "fengsel. For hvert eneste av årets 365 dager finner du to sider: én med bønnetider "
        "og én med en islamsk refleksjon. Alle sidene er nummerert, og kalenderen åpner med "
        "en innholdsfortegnelse over alle duaene.</p>"

        "<h3>Forsiden – bønnetider</h3>"
        "<ul>"
        "<li><b>28 norske fengsler og byer</b> – Fajr, Soloppgang, Zuhr, Asr, Maghrib og Isha</li>"
        "<li>Gregoriansk dato, ukedag og <b>hijri-dato</b> (islamsk kalender)</li>"
        "<li>Et vers fra Koranen eller et hadith øverst på siden</li>"
        "<li><b>Vise ord</b> fra inspirerende personligheter gjennom historien – et nytt sitat hver dag</li>"
        "</ul>"

        "<h3>Baksiden – daglig refleksjon</h3>"
        "<ul>"
        "<li>Et islamsk tema med tekst på norsk</li>"
        "<li>Annenhver dag: en <b>dua</b> (bønn) i <b>latinsk translitterasjon</b> – "
        "slik at du kan lese og uttale bønnen, uansett språkbakgrunn</li>"
        "</ul>"

        '<div class="highlight-box">'
        "Bønnetidene er beregnet etter Den islamske verdensliguens metode (MWL), "
        "tilpasset norske breddegrader med midnatt-metoden for høye breddegrader "
        "(nord for 48°N)."
        "</div>"

        "<p>Måtte denne kalenderen være et daglig ankerpunkt for deg – en påminnelse "
        "om at Allah er nær, uansett hvor du er.</p>"
        "</div>"
    )


def build_html(pages_html: list[str], logo_uri: str = "") -> str:
    body = "\n".join(pages_html)
    css  = CSS.replace("__LOGO_URI__", logo_uri)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="no">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        "<title>Bønnetidskalender 2027 – Daglig</title>\n"
        f"<style>{css}</style>\n"
        "</head>\n"
        f"<body>\n{body}\n</body>\n"
        "</html>\n"
    )


def dua_toc_page(entries: list[tuple[int, str]], label: str) -> str:
    """Render one Dua TOC page with entries as (page_num, title)."""
    rows = "".join(
        (
            f'<div class="toc-entry">'
            f'<span class="toc-pg">{n:03d}</span>&ensp;{esc(t)}</div>'
        )
        for n, t in entries
    )
    return (
        f'<div class="page toc-page">'
        f'<div class="toc-title">{esc(label)}</div>'
        f'<div class="toc-grid">{rows}</div>'
        f"</div>"
    )


def main():
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    OUTPUT.parent.mkdir(exist_ok=True)

    # Embed logo as inline base64 so the watermark works when printing / offline
    logo_uri = ""
    if LOGO.exists():
        logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
        logo_uri = f"data:image/png;base64,{logo_b64}"
        print(f"Logo: {LOGO.name} ({len(logo_b64)//1024} KB base64)")
    else:
        print(f"Warning: logo not found at {LOGO}")

    # Embed cover image as inline base64 for the hard cover page
    cover_uri = ""
    if COVER_IMG.exists():
        ext = COVER_IMG.suffix.lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg", ".jfif") else "image/png"
        cover_b64 = base64.b64encode(COVER_IMG.read_bytes()).decode()
        cover_uri = f"data:{mime};base64,{cover_b64}"
        print(f"Cover: {COVER_IMG.name} ({len(cover_b64)//1024} KB base64)")
    else:
        print(f"Warning: cover image not found at {COVER_IMG}")

    if not PRAYER.exists():
        print(f"ERROR: {PRAYER} not found.\nRun 02_prayer_times.py first.")
        raise SystemExit(1)

    prayer_data: dict = json.loads(PRAYER.read_text(encoding="utf-8"))
    print(f"Prayer data: {len(prayer_data)} days")

    # Load motivational quotes (from 06_fetch_quotes.py)
    quotes_data: dict = {}
    if QUOTES.exists():
        quotes_data = json.loads(QUOTES.read_text(encoding="utf-8"))
        print(f"Quotes: {len(quotes_data)} entries")
    else:
        print("Note: quotes.json not found – run 06_fetch_quotes.py")

    rem_no: dict = {}
    if REM_NO.exists():
        rem_no = json.loads(REM_NO.read_text(encoding="utf-8"))
        print(f"Reminders: {len(rem_no)} entries")
    else:
        print(f"ERROR: No reminder data found.\nRun 08_fetch_hadith_reminders.py first.")
        raise SystemExit(1)

    def get_reminder(date_str: str) -> dict:
        return rem_no.get(date_str, {})

    pages: list[str] = []

    # ── Front matter ──
    pages.append(cover_page(logo_uri, cover_uri))       # p1: hard cover
    pages.append(org_info_page())            # unnumbered
    pages.append(empty_page())               # unnumbered (back of org)
    pages.append(calendar_info_page())       # unnumbered
    pages.append(empty_page())               # unnumbered (back of info)

    sorted_dates = sorted(prayer_data.keys())

    # ── Dua TOC (table of contents) ──
    # Compute every dua-day entry: (page_num, dua_title) — 182 entries total.
    # Page numbering: calendar day i (0-based) → front=2*i+1, back=2*i+2.
    toc_entries: list[tuple[int, str]] = []
    for i, date_str in enumerate(sorted_dates):
        rem = get_reminder(date_str)
        if i % 2 == 1:  # dua day
            toc_entries.append((2 * i + 2, rem.get("topic", "")))

    # Split into two TOC pages (one sheet, front+back)
    mid = (len(toc_entries) + 1) // 2
    pages.append(dua_toc_page(toc_entries[:mid], "Duas in this Calendar"))
    pages.append(dua_toc_page(toc_entries[mid:], "Duas in this Calendar (cont.)" if len(toc_entries) > mid else ""))

    for i, date_str in enumerate(sorted_dates):
        meta       = prayer_data[date_str]
        rem        = get_reminder(date_str)
        quote_entry = quotes_data.get(date_str, {})
        pages.append(front_page(date_str, meta, rem, quote_entry, page_num=2*i+1))
        pages.append(back_page(date_str, rem, page_num=2*i+2))

    html = build_html(pages, logo_uri=logo_uri)
    OUTPUT.write_text(html, encoding="utf-8")

    size_kb = OUTPUT.stat().st_size // 1024
    print(f"Generated {len(sorted_dates)} days ({len(pages)} pages) → {OUTPUT}  [{size_kb} KB]")


if __name__ == "__main__":
    main()
