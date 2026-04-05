#!/usr/bin/env python3
"""
generer_bonnetider.py  (v3 — 13 byer, alle norske fengsler med >30 innsatte)
------------------------------------------------------------------------------
Henter bønnetider for alle 7 dager i alle 52 ISO-uker i 2027.
Bruker AlAdhan månedlig kalender-API: 13 byer × 13 måneder = 169 kall.

Byer: Oslo, Hønefoss, Drammen, Fredrikstad, Hamar, Skien,
      Kristiansand, Stavanger, Bergen, Trondheim, Ålesund, Bodø, Tromsø
Metode: MWL (3) + MidNight høybreddegrad-regel

Output: bonnetider/2027-bonnetider.json
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path("bonnetider/2027-bonnetider.json")

BYER = [
    {"navn": "Oslo",          "lat": 59.9139, "lng": 10.7522},  # Oslo fengsel, Ila
    {"navn": "Hønefoss",      "lat": 60.1674, "lng": 10.2539},  # Ringerike fengsel
    {"navn": "Drammen",       "lat": 59.7440, "lng": 10.2045},  # Drammen fengsel
    {"navn": "Fredrikstad",   "lat": 59.2181, "lng": 10.9298},  # Østfold fengsel
    {"navn": "Hamar",         "lat": 60.7945, "lng": 11.0679},  # Hamar fengsel
    {"navn": "Skien",         "lat": 59.2093, "lng":  9.6097},  # Skien fengsel
    {"navn": "Kristiansand",  "lat": 58.1467, "lng":  7.9956},  # Kristiansand fengsel
    {"navn": "Stavanger",     "lat": 58.9700, "lng":  5.7331},  # Stavanger fengsel
    {"navn": "Bergen",        "lat": 60.3913, "lng":  5.3221},  # Bergen fengsel
    {"navn": "Trondheim",     "lat": 63.4305, "lng": 10.3951},  # Trondheim fengsel
    {"navn": "Ålesund",       "lat": 62.4723, "lng":  6.1549},  # Ålesund fengsel
    {"navn": "Bodø",          "lat": 67.2803, "lng": 14.4050},  # Bodø fengsel
    {"navn": "Tromsø",        "lat": 69.6489, "lng": 18.9551},  # Tromsø fengsel
]

METHOD   = 3            # Muslim World League
HIGH_LAT = "MidNight"
TIMEZONE = "Europe/Oslo"

UKE1_MAN = date(2027, 1, 4)   # Mandag i ISO-uke 1

DAGER = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

MND_NO = {
    "January": "jan", "February": "feb", "March": "mar", "April": "apr",
    "May": "mai",     "June": "jun",     "July": "jul",  "August": "aug",
    "September": "sep", "October": "okt", "November": "nov", "December": "des",
}

HIJRI_MND = {
    "Muharram": "Muharram",    "Safar": "Safar",
    "Rabi al-awwal": "Rabi al-Awwal",    "Rabi al-thani": "Rabi al-Thani",
    "Jumada al-ula": "Jumada al-Ula",    "Jumada al-akhirah": "Jumada al-Akhirah",
    "Rajab": "Rajab",             "Shaban": "Sha'ban",
    "Ramadan": "Ramadan",            "Shawwal": "Shawwal",
    "Dhu al-Qidah": "Dhul Qi'dah",   "Dhu al-Hijjah": "Dhul Hijjah",
    # AlAdhan returns transliterated forms with diacritical marks:
    "Ramaḍān":      "Ramadan",
    "Sha\u02BFbān":      "Sha'ban",
    "Sha'bān":      "Sha'ban",
    "Shawwāl":      "Shawwal",
    "Muḥarram":     "Muharram",
    "Ṣafar":        "Safar",
    "Rabīʿ al-awwal":  "Rabi al-Awwal",
    "Rabīʿ al-thānī":  "Rabi al-Thani",
    "Jumādá al-ūlá":   "Jumada al-Ula",
    "Jumādá al-ākhirah": "Jumada al-Akhirah",
    "Rajab":        "Rajab",
    "Dhū al-Qaʿdah":  "Dhul Qi'dah",
    "Dhū al-Ḥijjah":  "Dhul Hijjah",
}


def lookup_hijri_mnd(api_name: str) -> str:
    """Slår opp hijri måned med fallback til normalisert ASCII-sammenligning."""
    if api_name in HIJRI_MND:
        return HIJRI_MND[api_name]
    # Normalize: strip diacritics roughly by checking lowercase ASCII start
    lower = api_name.lower()
    for key, val in HIJRI_MND.items():
        if key.lower()[:4] == lower[:4]:
            return val
    return api_name[:6]  # last-resort truncation


def hent_maaned(by: dict, aar: int, mnd: int) -> list:
    p = {
        "latitude":         by["lat"],
        "longitude":        by["lng"],
        "method":           METHOD,
        "highLatitudeRule": HIGH_LAT,
        "timezonestring":   TIMEZONE,
    }
    url = f"https://api.aladhan.com/v1/calendar/{aar}/{mnd}?{urllib.parse.urlencode(p)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
            if payload.get("code") == 200:
                return payload["data"]
    except Exception as exc:
        print(f" FEIL: {exc}")
    return []


def rens(t: str) -> str:
    """Fjerner tidssone-suffiks som '(CET)' fra API-svaret."""
    return t.split()[0] if t else "—"


def main():
    # Bygg dato → uke-mapping for alle 364 dager i de 52 ukene
    dato_uke:  dict[date, int]  = {}
    dato_info: dict[date, dict] = {}
    for u in range(1, 53):
        man = UKE1_MAN + timedelta(weeks=u - 1)
        for i in range(7):
            d = man + timedelta(days=i)
            dato_uke[d]  = u
            dato_info[d] = {"dagNavn": DAGER[i], "offset": i}

    # Initialiser output-struktur
    data: dict = {f"uke_{u:02d}": {"uke": u, "dager": {}} for u in range(1, 53)}

    # 2027 jan–des + 2028 jan (for uke 52 som slutter 2. jan 2028)
    maneder = [(2027, m) for m in range(1, 13)] + [(2028, 1)]

    for by in BYER:
        print(f"\n{by['navn']}:")
        for aar, mnd in maneder:
            print(f"  {aar}-{mnd:02d} ...", end=" ", flush=True)
            dager_api = hent_maaned(by, aar, mnd)
            if not dager_api:
                print("FEIL")
                time.sleep(2)
                continue

            n = 0
            for d_api in dager_api:
                g = d_api["date"]["gregorian"]
                h = d_api["date"]["hijri"]

                # AlAdhan returnerer "DD-MM-YYYY"
                dd, mm, yy = g["date"].split("-")
                dato = date(int(yy), int(mm), int(dd))

                if dato not in dato_uke:
                    continue  # Utenfor kalenderens 52 uker

                u    = dato_uke[dato]
                info = dato_info[dato]
                uk   = f"uke_{u:02d}"
                iso  = dato.isoformat()

                # Lag daglabel første gang (felles for alle byer)
                if iso not in data[uk]["dager"]:
                    g_lbl = f"{dato.day}.{MND_NO.get(g['month']['en'], '?')}"
                    h_mnd = lookup_hijri_mnd(h["month"]["en"])
                    h_lbl = f"{int(h['day'])}.{h_mnd}"
                    data[uk]["dager"][iso] = {
                        "dagNavn":    info["dagNavn"],
                        "offset":     info["offset"],
                        "gregLabel":  g_lbl,
                        "hijriLabel": h_lbl,
                        "hijriAar":   h["year"],
                        "byer":       {},
                    }

                t = d_api["timings"]
                data[uk]["dager"][iso]["byer"][by["navn"]] = {
                    k: rens(t.get(k, "—"))
                    for k in ("Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha")
                }
                n += 1

            print(f"OK ({n})")
            time.sleep(0.6)

    # Sorter dager per uke etter ukedag-offset
    for uk_data in data.values():
        uk_data["dager"] = dict(
            sorted(uk_data["dager"].items(), key=lambda x: x[1]["offset"])
        )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nFerdig! Lagret til: {OUTPUT}")


if __name__ == "__main__":
    main()
