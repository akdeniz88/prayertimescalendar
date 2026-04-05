import json

for fname in ["uker-1-13.json", "uker-14-26.json", "uker-27-39.json", "uker-40-52.json"]:
    with open(f"innhold/{fname}", "r", encoding="utf-8") as f:
        data = json.load(f)
    for w in data:
        uke = w["uke"]
        hijri = w["hijri"]
        tema = w["tema"][:55]
        sp = w.get("spesiell") or ""
        print(f"Uke {uke:2d}: {hijri:45s} {tema}")
        if sp:
            print(f"         spesiell: {sp}")
