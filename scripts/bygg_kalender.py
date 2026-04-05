#!/usr/bin/env python3
"""
bygg_kalender.py  (v4 — HTML A4 liggende, 2 uker per ark, 13 byer)
--------------------------------------------------------------------
Genererer to A4-sider per ark (26 ark = 52 sider):
  Side 1 (bønnetider): 13 byer × 6 bønner × 14 dager (2 uker side om side)
  Side 2 (innhold):    2 uker med Koranvers, Hadith, Visdomsord + bonus

Output:
  uker/uke-01-02.html … uker/uke-51-52.html
  kalender-2027.html   (alle 52 sider samlet)
"""

import json
import glob
import base64
from pathlib import Path
from html import escape as esc

BASE         = Path(__file__).resolve().parent.parent
INNHOLD_GLOB = str(BASE / "innhold" / "uker-*.json")
BONNETIDER   = BASE / "bonnetider" / "2027-bonnetider.json"
UKER_MAPPE   = BASE / "uker"
MASTER       = BASE / "kalender-2027.html"

BYER      = ["Oslo", "Hønefoss", "Drammen", "Fredrikstad", "Hamar", "Skien",
             "Kristiansand", "Stavanger", "Bergen", "Trondheim", "Ålesund", "Bodø", "Tromsø"]
BYER_KORT = ["Oslo", "Hønefoss", "Drammen", "F.stad", "Hamar", "Skien",
             "K.sand", "Stavanger", "Bergen", "Trondh.", "Ålesund", "Bodø", "Tromsø"]
PKEYS  = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
PNAMES = ["Fajr", "Sol.↑", "Dhuhr", "Asr", "Maghr.", "Isha"]
PCLS   = ["fajr", "solopp",  "dhuhr", "asr", "maghrib", "isha"]

# Logo (legg logo.png i prosjektmappen — bygges inn som base64)
_logo_path = BASE / "logo.png"
LOGO_B64 = base64.b64encode(_logo_path.read_bytes()).decode() if _logo_path.exists() else ""

# ---------------------------------------------------------------------------
# CSS  (note: all {} are literal CSS braces — delivered via concatenation,
#       NOT via str.format(), so no escaping needed)
# ---------------------------------------------------------------------------
CSS = """
@page { size: A4 landscape; margin: 4mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #fff; }

.pg {
  page-break-after: always;
  width: 289mm;
  min-height: 200mm;
  position: relative;
  overflow: hidden;
  padding: 2mm;
}
.pg:last-child { page-break-after: auto; }

@media screen {
  body { background: #555; padding: 10px; }
  .pg { background: #fff; margin: 8px auto; box-shadow: 0 3px 14px rgba(0,0,0,.4); }
}

/* ================================================================
   BØNNETIDER-SIDE (front)
   ================================================================ */
.b { font-family: Arial, Helvetica, sans-serif; }

.b-top {
  display: flex; align-items: center;
  margin-bottom: 1mm;
}
.b-logo {
  height: 8mm; width: auto; margin-left: auto; flex-shrink: 0;
}
.b-uke {
  font-size: 11pt; font-weight: 900; color: #1a1a2e;
  background: #f7e636; padding: .2mm 2mm; margin-right: 2mm;
  letter-spacing: .4pt; white-space: nowrap;
}
.b-h {
  font-size: 7.5pt; font-weight: bold;
  color: #1a1a2e; letter-spacing: .2pt;
}
.b-s {
  font-size: 5pt; color: #888;
}

table.bt {
  width: 100%; border-collapse: collapse; table-layout: fixed;
  position: relative; z-index: 1;
}
.bt-wrap {
  position: relative;
}
.bt-wm {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 75%;
  opacity: .045;
  pointer-events: none;
  z-index: 2;
}
table.bt thead th {
  background: #1a1a2e; color: #fff;
  font-size: 8.5pt; font-weight: bold;
  text-align: center; padding: .8mm .5mm;
  border: .3pt solid #111;
  overflow: hidden;
}
table.bt thead th.lc { background: #2d3561; width: 7mm; }
table.bt thead th.lp { background: #2d3561; width: 9mm; }
table.bt thead th.dh { vertical-align: bottom; padding-bottom: .8mm; }
table.bt thead th.ws { background: #0d1333; width: 1.5mm; padding: 0; border-left: .8pt solid #f7e636; border-right: .8pt solid #f7e636; }
table.bt thead th.wl {
  background: #2d3561; font-size: 8pt; font-weight: 900;
  letter-spacing: .3pt; color: #f7e636; padding: .5mm;
}

.dhn { font-size: 7pt; font-weight: 900; display: block; }
.dhg { font-size: 5.5pt; display: block; opacity: .85; }
.dhh { font-size: 4.5pt; display: block; opacity: .65; }

td.by {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  text-align: center;
  vertical-align: middle;
  background: #edf0fc;
  border: .3pt solid #b4bde0;
  width: 7mm;
  padding: .3mm;
  font-size: 6pt;
  font-weight: bold;
  color: #1a1a2e;
}

td.bn {
  font-size: 6pt; font-weight: bold;
  padding: .3mm .5mm;
  border: .2pt solid #e0e0e0;
  width: 9mm; white-space: nowrap;
  line-height: 1.15;
}
.fajr    { color: #7B3000; }
.solopp  { color: #1B5E20; }
.dhuhr   { color: #0D47A1; }
.asr     { color: #BF360C; }
.maghrib { color: #283593; }
.isha    { color: #1a1a2e; }

td.t {
  font-size: 6.5pt; text-align: center;
  padding: .3mm .2mm;
  border: .2pt solid #e8e8e8;
  line-height: 1.15;
}
td.wsep { background: #f0f0f0; width: 1.5mm; border-left: .8pt solid #f7e636; border-right: .8pt solid #f7e636; }
tr.de td.t, tr.de td.bn { background: #f4f6fe; }
tr.ds td { border-top: .5pt solid #7a8fc0 !important; }

.b-f {
  font-size: 4.5pt; color: #bbb; text-align: center; margin-top: 1mm;
}

/* ================================================================
   INNHOLD-SIDE (back — two-column layout for 2 weeks)
   ================================================================ */
.inn {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 8.5pt; line-height: 1.45; color: #111;
}
.inn-top {
  display: flex; align-items: center;
  margin-bottom: 2mm;
}
.inn-top .b-uke { font-size: 10pt; }
.inn-cols {
  display: flex; gap: 4mm;
}
.inn-col {
  flex: 1; min-width: 0;
}
.inn-col + .inn-col {
  border-left: .4pt solid #e0d8c8; padding-left: 4mm;
}
.in-wh {
  font-family: Arial, sans-serif;
  font-size: 8pt; font-weight: 900; color: #1a1a2e;
  background: #f7f0d8; padding: .5mm 1.5mm; margin-bottom: 1.5mm;
  display: inline-block;
}
.in-hj {
  font-family: Arial, sans-serif; font-size: 6pt;
  color: #888; margin-bottom: 2mm;
}
.in-t {
  font-size: 8pt; font-weight: bold; color: #7B3000;
  font-style: italic; margin-bottom: 2.5mm;
  border-bottom: .3pt solid #e8c8a0; padding-bottom: 1mm;
}
.spes {
  background: #fff8e1; border: .5pt solid #f0c000;
  padding: 1mm 1.5mm; font-size: 6.5pt; color: #5c4000;
  margin-bottom: 2mm; font-family: Arial, sans-serif;
}
.s { margin-bottom: 2.5mm; }
.si {
  font-family: Arial, sans-serif;
  font-size: 5pt; font-weight: bold; text-transform: uppercase;
  letter-spacing: 1pt; color: #aaa;
  border-bottom: .3pt solid #eee;
  padding-bottom: .3mm; margin-bottom: 1mm;
}
.vt  { font-style: italic; color: #1a1a2e; font-size: 8pt; }
.rf  { font-size: 6pt; color: #666; margin-top: .4mm; }
.hdt { font-size: 8pt; color: #222; }
.kd  { font-size: 6pt; color: #888; margin-top: .3mm; }
.vis {
  font-style: italic; color: #3d2b1f; font-size: 8pt;
  border-left: 1.2pt solid #7B3000; padding-left: 2mm;
}
.vk  {
  font-size: 6pt; color: #aaa; margin-top: .3mm;
  padding-left: 2.5mm; font-family: Arial, sans-serif;
}
.in-f {
  position: absolute; bottom: 2mm; right: 2mm;
  font-size: 5pt; color: #ddd;
  font-family: Arial, sans-serif;
}
"""

HTML_HEAD = (
    '<!DOCTYPE html>\n<html lang="no">\n<head>\n'
    '<meta charset="UTF-8">\n<title>'
)
HTML_MID1 = '</title>\n<style>\n'
HTML_MID2 = '\n</style>\n</head>\n<body>\n'
HTML_TAIL = '\n</body>\n</html>\n'


def html_page(tittel: str, sider: str) -> str:
    return HTML_HEAD + tittel + HTML_MID1 + CSS + HTML_MID2 + sider + HTML_TAIL


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def last_innhold() -> list:
    alle = []
    for f in sorted(glob.glob(INNHOLD_GLOB)):
        with open(f, encoding="utf-8") as fh:
            alle.extend(json.load(fh))
    return sorted(alle, key=lambda u: u["uke"])


def last_bonne() -> dict:
    if BONNETIDER.exists():
        with open(BONNETIDER, encoding="utf-8") as fh:
            return json.load(fh)
    print(f"ADVARSEL: {BONNETIDER} ikke funnet – tomme tabeller brukes.")
    return {}


# ---------------------------------------------------------------------------
# Side-bygger: Bønnetider (2 uker = 14 dager side om side)
# ---------------------------------------------------------------------------

def _get_sorted_days(bonne: dict, uke_nr: int) -> list:
    uk = f"uke_{uke_nr:02d}"
    dag_data = bonne.get(uk, {}).get("dager", {})
    return sorted(dag_data.items(), key=lambda x: x[1]["offset"])


def build_bonnetider(uke_a: dict, uke_b: dict, bonne: dict) -> str:
    nr_a = uke_a["uke"]
    nr_b = uke_b["uke"]
    days_a = _get_sorted_days(bonne, nr_a)
    days_b = _get_sorted_days(bonne, nr_b)

    # ---- Header row: city | prayer | 7 days week A | sep | 7 days week B ----
    def day_ths(days):
        h = ""
        for _, dag in days:
            dn = esc(dag.get("dagNavn", "")[:3])
            gl = esc(dag.get("gregLabel", ""))
            hl = esc(dag.get("hijriLabel", ""))
            h += (f'<th class="dh">'
                  f'<span class="dhn">{dn}</span>'
                  f'<span class="dhg">{gl}</span>'
                  f'<span class="dhh">{hl}</span></th>')
        return h

    thead = (
        f'<thead><tr>'
        f'<th class="lc"></th><th class="lp"></th>'
        f'<th class="wl" colspan="7">Uke {nr_a:02d}</th>'
        f'<th class="ws"></th>'
        f'<th class="wl" colspan="7">Uke {nr_b:02d}</th>'
        f'</tr><tr>'
        f'<th class="lc"></th><th class="lp"></th>'
        f'{day_ths(days_a)}'
        f'<th class="ws"></th>'
        f'{day_ths(days_b)}'
        f'</tr></thead>'
    )

    # ---- Body rows: city × prayer ----
    rows = []
    even = False
    for by_navn, by_kort in zip(BYER, BYER_KORT):
        row_cls = "de" if even else "do"
        even = not even

        for i, (pk, pn, pc) in enumerate(zip(PKEYS, PNAMES, PCLS)):
            city_cell = ""
            if i == 0:
                city_cell = f'<td class="by" rowspan="6">{esc(by_kort)}</td>'

            tds_a = "".join(
                f'<td class="t">{esc(dag.get("byer", {}).get(by_navn, {}).get(pk, "\u2014"))}</td>'
                for _, dag in days_a
            )
            tds_b = "".join(
                f'<td class="t">{esc(dag.get("byer", {}).get(by_navn, {}).get(pk, "\u2014"))}</td>'
                for _, dag in days_b
            )
            border_cls = " ds" if i == 0 else ""
            rows.append(
                f'<tr class="{row_cls}{border_cls}">'
                f'{city_cell}'
                f'<td class="bn {pc}">{pn}</td>'
                f'{tds_a}'
                f'<td class="wsep"></td>'
                f'{tds_b}'
                f'</tr>'
            )

    rows_html = "\n".join(rows)
    gregor = f'{esc(uke_a["gregOrisk"])}  /  {esc(uke_b["gregOrisk"])}'
    hijri  = f'{esc(uke_a["hijri"])}  /  {esc(uke_b["hijri"])}'
    logo_html = (f'<img class="b-logo" src="data:image/png;base64,{LOGO_B64}" alt="Fengselsimamene">'
                 if LOGO_B64 else '')

    wm_html = (f'<img class="bt-wm" src="data:image/png;base64,{LOGO_B64}" alt="">'
                if LOGO_B64 else '')

    return (
        f'<div class="pg b">'
        f'<div class="b-top">'
        f'<div class="b-uke">Uke {nr_a:02d}\u2013{nr_b:02d}</div>'
        f'<div><div class="b-h">{gregor}</div>'
        f'<div class="b-s">{hijri}</div></div>'
        f'{logo_html}'
        f'</div>'
        f'<div class="bt-wrap">'
        f'{wm_html}'
        f'<table class="bt">'
        f'{thead}'
        f'<tbody>{rows_html}</tbody>'
        f'</table>'
        f'</div>'
        f'<div class="b-f">Bønnetidskalender 2027 &nbsp;&middot;&nbsp; '
        f'For muslimske innsatte i norske fengsler &nbsp;&middot;&nbsp; '
        f'www.fengselsimamene.no</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Side-bygger: Åndelig innhold (2 uker i to kolonner)
# ---------------------------------------------------------------------------

def _build_one_col(uke: dict) -> str:
    """En kolonne med åndelig innhold for én uke."""
    nr     = uke["uke"]
    gregor = esc(uke["gregOrisk"])
    hijri  = esc(uke["hijri"])
    tema   = esc(uke["tema"])
    qt     = esc(uke["quran"]["tekst"])
    qr     = esc(uke["quran"]["referanse"])
    ht     = esc(uke["hadith"]["tekst"])
    hk     = esc(uke["hadith"]["kilde"])
    vt     = esc(uke["visdom"])
    vk     = esc(uke.get("visdomKilde", ""))
    sp     = uke.get("spesiell", "")

    sp_html = (
        f'<div class="spes">&#128197; {esc(sp)}</div>' if sp else ""
    )

    return (
        f'<div class="inn-col">'
        f'<div class="in-wh">Uke {nr:02d} &mdash; {gregor}</div>'
        f'<div class="in-hj">{hijri} H</div>'
        f'<div class="in-t">{tema}</div>'
        f'{sp_html}'
        f'<div class="s">'
        f'<div class="si">Koranen</div>'
        f'<div class="vt">&laquo;{qt}&raquo;</div>'
        f'<div class="rf">&mdash; <em>{qr}</em></div>'
        f'</div>'
        f'<div class="s">'
        f'<div class="si">Hadith</div>'
        f'<div class="hdt">&laquo;{ht}&raquo;</div>'
        f'<div class="kd">&mdash; {hk}</div>'
        f'</div>'
        f'<div class="s">'
        f'<div class="si">Visdomsord</div>'
        f'<div class="vis">&laquo;{vt}&raquo;</div>'
        f'<div class="vk">&mdash; {vk}</div>'
        f'</div>'
        f'</div>'
    )


def build_innhold(uke_a: dict, uke_b: dict) -> str:
    nr_a = uke_a["uke"]
    nr_b = uke_b["uke"]
    logo_html = (f'<img class="b-logo" src="data:image/png;base64,{LOGO_B64}" alt="Fengselsimamene">'
                 if LOGO_B64 else '')

    return (
        f'<div class="pg inn">'
        f'<div class="inn-top">'
        f'<div class="b-uke">Uke {nr_a:02d}\u2013{nr_b:02d}</div>'
        f'<div><div class="b-h" style="font-family:Georgia,serif;">'
        f'Islamske p\u00e5minnelser</div></div>'
        f'{logo_html}'
        f'</div>'
        f'<div class="inn-cols">'
        f'{_build_one_col(uke_a)}'
        f'{_build_one_col(uke_b)}'
        f'</div>'
        f'<div class="in-f">&#9790; Uke {nr_a:02d}\u2013{nr_b:02d}/52 &nbsp; 2027</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Hoved-rutine
# ---------------------------------------------------------------------------

def main():
    print("Laster innhold...")
    innhold = last_innhold()
    print(f"  {len(innhold)} uker.")

    print("Laster bønnetider...")
    bonne = last_bonne()
    print(f"  {'OK — alle 7 dager per uke' if bonne else 'Mangler — tomme tabeller'}.")

    UKER_MAPPE.mkdir(exist_ok=True)

    alle_sider = []
    ark = 0

    print("\nGenererer HTML-filer (2 uker per ark)...")
    for i in range(0, len(innhold), 2):
        uke_a = innhold[i]
        uke_b = innhold[i + 1] if i + 1 < len(innhold) else uke_a
        nr_a = uke_a["uke"]
        nr_b = uke_b["uke"]

        b_side = build_bonnetider(uke_a, uke_b, bonne)
        i_side = build_innhold(uke_a, uke_b)
        sider  = b_side + "\n" + i_side

        html = html_page(f"Uke {nr_a:02d}–{nr_b:02d} – Bønnetidskalender 2027", sider)
        fil  = UKER_MAPPE / f"uke-{nr_a:02d}-{nr_b:02d}.html"
        with open(fil, "w", encoding="utf-8") as f:
            f.write(html)

        alle_sider.append(sider)
        ark += 1
        print(f"  uke-{nr_a:02d}-{nr_b:02d}.html ✓")

    print("\nSkriver kalender-2027.html...")
    master = html_page(
        "Bønnetidskalender 2027 – Muslimske innsatte i norske fengsler",
        "\n".join(alle_sider),
    )
    with open(MASTER, "w", encoding="utf-8") as f:
        f.write(master)

    total_sider = ark * 2
    print(f"\n{'='*60}")
    print(f"Ferdig!  {ark} ark × 2 sider = {total_sider} sider")
    print(f"  ({len(innhold)} uker, 2 per ark)")
    print(f"  Ukefiler:   {UKER_MAPPE}")
    print(f"  Master HTML: {MASTER}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
