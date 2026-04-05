"""
Fix all Hijri dates, spesiell fields, and rearrange themed content
to align with correct 2027 Hijri calendar.

Key corrections (2027, not 2026):
  Sha'ban 1448  starts  9 jan  (was 30 jan)
  Ramadan 1448  starts  8 feb  (was 28 feb)
  Eid al-Fitr           9 mar  (was 30 mar)
  Eid al-Adha          16 mai  (was  6 jun)
  1 Muharram 1449       6 jun  (was 26 jun)
  Ashura (10 Muh.)     15 jun  (was  5 jul)
  Mawlid (12 R.Aw.)   14 aug  (was 13 sep)
  1 Rajab 1449         29 nov  (was 20 des)
"""

import json, copy

# ── Load data ──────────────────────────────────────────────────────
with open("bonnetider/2027-bonnetider.json", "r", encoding="utf-8") as f:
    prayer = json.load(f)

content = []
for fname in ["uker-1-13.json", "uker-14-26.json",
              "uker-27-39.json", "uker-40-52.json"]:
    with open(f"innhold/{fname}", "r", encoding="utf-8") as f:
        content.extend(json.load(f))

by_week = {item["uke"]: item for item in content}

# ── Month name normalisation (API → content convention) ───────────
MONTH_MAP = {
    "Dhul Qi'dah":       "Dhul Qa'da",
    "Dhul Hijjah":       "Dhul Hijja",
    "Jumada al-Ula":     "Jumada al-Awwal",
    "Jumada al-Akhirah": "Jumada al-Thani",
}

def norm_month(m):
    return MONTH_MAP.get(m, m)

def parse_label(label):
    """'26.Rajab' → (26, 'Rajab')"""
    day_s, month = label.split(".", 1)
    return int(day_s), norm_month(month)

def hijri_range(week_num):
    """Build hijri range string from prayer-time data."""
    k = f"uke_{week_num:02d}"
    dager = prayer[k]["dager"]
    keys = sorted(dager.keys())
    first, last = dager[keys[0]], dager[keys[-1]]

    fd, fm = parse_label(first["hijriLabel"])
    ld, lm = parse_label(last["hijriLabel"])
    fy = int(first.get("hijriAar", "1448"))
    ly = int(last.get("hijriAar", str(fy)))

    if fm == lm and fy == ly:
        return f"{fd}–{ld} {fm} {fy}"
    elif fy == ly:
        return f"{fd} {fm} – {ld} {lm} {fy}"
    else:
        return f"{fd} {fm} {fy} – {ld} {lm} {ly}"

# ── Content-reordering map ────────────────────────────────────────
# target_week → (source_week, spesiell_text | None)
# None ⇒ spesiell becomes null
MAP = {
    # Weeks 1-4: keep general intro themes
    1:  (1,  "Sha'ban begynner 9. jan."),
    2:  (2,  None),
    3:  (3,  None),
    4:  (4,  None),
    # Week 5: Sha'ban prep (was week 8)
    5:  (8,  "Siste Sha'ban-uke. Ramadan begynner 8. feb (mandag)."),
    # Weeks 6-9: Ramadan (was 9-12)
    6:  (9,  "Ramadan uke 1. Suhur/Iftar-tider aktivert i bønnetabellen."),
    7:  (10, "Ramadan uke 2."),
    8:  (11, "Ramadan uke 3."),
    9:  (12, "Ramadan uke 4. Laylat al-Qadr ca. 6. mars (natt til lørdag, 27. Ramadan)."),
    # Week 10: Eid al-Fitr (was 13)
    10: (13, "EID AL-FITR 9. mars 2027. Ramadan avsluttes. Tema: Ny begynnelse."),
    # Weeks 11-13: displaced general content (was 5-7)
    11: (5,  None),
    12: (6,  None),
    13: (7,  None),
    # Weeks 14-18: keep
    14: (14, None),
    15: (15, None),
    16: (16, None),
    17: (17, None),
    18: (18, None),
    # Weeks 19-20: Eid al-Adha block (was 22-23)
    19: (22, "EID AL-ADHA 16. mai 2027 (10. Dhul Hijja). Arafat-dagen 15. mai."),
    20: (23, None),
    # Weeks 21-22: Year-end / new Hijri year (was 25-26)
    21: (25, None),
    22: (26, "Islamsk nyttår 1449 AH. 1. Muharram ≈ 6. juni 2027. "
             "Muharram er en av de fire hellige månedene."),
    # Displaced general + Ashura
    23: (19, None),
    24: (27, "Ashura – 10. Muharram 1449, ca. 15. juni 2027 (tirsdag)."),
    25: (20, None),
    26: (21, None),
    27: (24, None),
    # Weeks 28-31: keep
    28: (28, None),
    29: (29, None),
    30: (30, None),   # was "Safar begynner 26. jul" – wrong, removed
    31: (31, None),
    # Weeks 32-34: Mawlid block (was 35-37)
    32: (35, "Mawlid al-Nabi 12. Rabi al-Awwal ≈ 14. august 2027 (lørdag)."),
    33: (36, None),
    34: (37, None),
    # Weeks 35-37: displaced general (was 32-34)
    35: (32, None),
    36: (33, None),
    37: (34, None),
    # Weeks 38-47: keep
    38: (38, None),
    39: (39, "Avslutning av tema 3. Muhasabah-uke."),
    40: (40, None),
    41: (41, None),
    42: (42, None),
    43: (43, "Klokken stilles tilbake til normaltid (CET) søndag 31. oktober."),
    44: (44, None),
    45: (45, None),
    46: (46, None),
    47: (47, None),
    # Weeks 48-51: Rajab rearrangement (51→48, 48-50→49-51)
    48: (51, "1. Rajab 1449 AH starter 29. november 2027. "
             "Rajab er en av de fire hellige månedene."),
    49: (48, None),
    50: (49, None),
    51: (50, None),
    52: (52, "Kalenderåret 2027 avsluttes. Det siste oppslaget i kalenderen."),
}

# ── Build corrected 52-week content ───────────────────────────────
new_content = []
for target in range(1, 53):
    source_week, spesiell = MAP[target]
    src = by_week[source_week]

    item = {
        "uke":        target,
        "gregOrisk":  by_week[target]["gregOrisk"],   # stays with calendar position
        "hijri":      hijri_range(target),
        "tema":       src["tema"],
        "spesiell":   spesiell,
        "quran":      copy.deepcopy(src["quran"]),
        "hadith":     copy.deepcopy(src["hadith"]),
        "visdom":     src["visdom"],
        "visdomKilde": src["visdomKilde"],
    }
    new_content.append(item)

# ── Write 4 output files ─────────────────────────────────────────
ranges = [(1, 13), (14, 26), (27, 39), (40, 52)]
for start, end in ranges:
    fname = f"uker-{start}-{end}.json"
    chunk = [i for i in new_content if start <= i["uke"] <= end]
    with open(f"innhold/{fname}", "w", encoding="utf-8") as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {fname}  (uke {start}–{end})")

# ── Summary ──────────────────────────────────────────────────────
print("\nKey corrections applied:")
print("  Ramadan:       uke 6–9  (was 9–12)")
print("  Eid al-Fitr:   uke 10   (was 13,  9. mars)")
print("  Eid al-Adha:   uke 19   (was 22, 16. mai)")
print("  Hijri nyttår:  uke 22   (was 25–26,  6. juni)")
print("  Ashura:        uke 24   (was 27, 15. juni)")
print("  Mawlid:        uke 32   (was 35–37, 14. august)")
print("  Rajab 1449:    uke 48   (was 51, 29. november)")
print("\nDone! Run  python scripts\\bygg_kalender.py  to rebuild HTML.")
