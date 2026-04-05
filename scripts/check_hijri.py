import json

with open("bonnetider/2027-bonnetider.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for w in range(1, 53):
    k = f"uke_{w:02d}"
    dager = data[k]["dager"]
    keys = sorted(dager.keys())
    first = dager[keys[0]]
    last = dager[keys[-1]]
    hijri_year = first.get("hijriAar", "?")
    print(f"Uke {w:2d}: {keys[0]} ({first['hijriLabel']}) – {keys[-1]} ({last['hijriLabel']})  [{hijri_year}]")
