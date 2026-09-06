#!/usr/bin/env python3
"""
08_fetch_hadith_reminders.py
-----------------------------
Fills all 365 back-page texts with authentic hadiths and duas from
https://ummahapi.com — plain English as provided by the API (no AI).

Each calendar day alternates:
  even day → one hadith  (Nawawi's 40 → 40 Hadith Qudsi → Nawawi's 40 → …)
  odd day  → one dua    (categories cycling distress → forgiveness →
                          knowledge → parents → guidance → gratitude →
                          protection → dhikr → distress → …)

Hadith sources:
  https://ummahapi.com/api/hadith/nawawi
  https://ummahapi.com/api/hadith/qudsi
  (extracted keys: collection_name, english; hadithnumber appended in italics)

Dua sources:
  https://ummahapi.com/api/duas/category/{category}
  (extracted keys: title, translation, transliteration, source)

Output per date:
  event       – preserved from reminders_no.json
  ayah_hadith – preserved from reminders_no.json
  topic       – collection_name (hadith) or title (dua)
  text        – english + italic hadith number, or translation +
                transliteration + italic source
  dua*        – cleared (the alternating content replaces the old Dua block)

Reads:
  data/reminders_no.json        (event + ayah_hadith)
  data/prayer_times_2027.json   (date list)
Writes:
  data/hadith_pool.json         (resume-safe cache of fetched data)
  data/reminders_hadith.json    (resume-safe output)

After this script completes:
  copy data\\reminders_hadith.json data\\reminders_no.json
  python 04_generate_html.py
"""

import json
import sys
import time
from pathlib import Path

import requests
import urllib3

# ummahapi.com currently serves an expired TLS certificate, so verification
# must be disabled for the fetch to succeed.
urllib3.disable_warnings()

# Ensure unicode output doesn't crash on Windows' default console encoding.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent

# ── API config ─────────────────────────────────────────────────────────────────
API_KEY = "umh_4420725154a1c04b7a957d4ab19e27301b18c0af"
BASE    = "https://ummahapi.com/api"

HADITH_COLLECTIONS = ["nawawi", "qudsi"]
DUA_CATEGORIES = [
    "distress", "forgiveness", "knowledge", "parents",
    "guidance", "gratitude", "protection", "dhikr",
]

# ── File paths ────────────────────────────────────────────────────────────────
POOL_FILE = HERE / "data" / "hadith_pool.json"
OUT_FILE  = HERE / "data" / "reminders_hadith.json"
REM_ORIG  = HERE / "data" / "reminders_no.json"
PRAYER_F  = HERE / "data" / "prayer_times_2027.json"


# ── Fetch helpers ─────────────────────────────────────────────────────────────

def fetch_json(url: str) -> dict:
    """GET → parsed JSON. Retries 3×; SSL verification disabled for ummahapi."""
    for attempt in range(3):
        try:
            resp = requests.get(url, verify=False, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                raise RuntimeError(f"GET failed after 3 attempts: {url[:80]} — {e}") from e


def fetch_hadiths() -> dict[str, list[dict]]:
    """Return {collection: [hadith, …]} for every collection."""
    out: dict[str, list[dict]] = {}
    for coll in HADITH_COLLECTIONS:
        data = fetch_json(f"{BASE}/hadith/{coll}?apikey={API_KEY}")
        items = data.get("data", {}).get("hadiths", [])
        out[coll] = [
            {
                "collection_name": (h.get("collection_name") or "").strip(),
                "english":         (h.get("english") or "").strip(),
                "hadithnumber":    h.get("hadithnumber"),
            }
            for h in items
            if (h.get("english") or "").strip()
        ]
        print(f"  Hadith '{coll}': {len(out[coll])} items")
        time.sleep(0.25)
    return out


def fetch_duas() -> dict[str, list[dict]]:
    """Return {category: [dua, …]} for every category."""
    out: dict[str, list[dict]] = {}
    for cat in DUA_CATEGORIES:
        data = fetch_json(f"{BASE}/duas/category/{cat}?apikey={API_KEY}")
        items = data.get("data", {}).get("duas", [])
        out[cat] = [
            {
                "title":           (d.get("title") or "").strip(),
                "translation":     (d.get("translation") or "").strip(),
                "transliteration": (d.get("transliteration") or "").strip(),
                "source":          (d.get("source") or "").strip(),
            }
            for d in items
            if (d.get("title") or "").strip()
        ]
        print(f"  Dua '{cat}': {len(out[cat])} items")
        time.sleep(0.25)
    return out


def build_pool() -> dict:
    """Load a valid cached pool, otherwise fetch and cache it."""
    if POOL_FILE.exists():
        try:
            pool = json.loads(POOL_FILE.read_text(encoding="utf-8"))
            if isinstance(pool, dict) and "hadiths" in pool and "duas" in pool:
                print(f"  Loaded cached pool: "
                      f"{len(pool['hadiths'])} hadith collections, "
                      f"{len(pool['duas'])} dua categories")
                return pool
            print("  Cached pool is outdated — refetching.")
        except (json.JSONDecodeError, OSError):
            print("  Cached pool unreadable — refetching.")

    print("Fetching hadiths + duas from ummahapi.com …")
    pool = {"hadiths": fetch_hadiths(), "duas": fetch_duas()}
    POOL_FILE.write_text(
        json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved pool → {POOL_FILE.name}")
    return pool


# ── Build entries ─────────────────────────────────────────────────────────────

def build_entry(pool: dict, index: int, orig: dict) -> dict:
    """Build one date's entry. `index` is 0-based across sorted dates."""
    base = {
        "event":        orig.get("event", ""),
        "ayah_hadith":  orig.get("ayah_hadith", ""),
        "dua":          "",
        "dua_translit": "",
        "dua_source":   "",
        "dua_grade":    "",
    }

    slot = index // 2

    if index % 2 == 0:
        # ── Hadith day ──
        coll_idx = slot % len(HADITH_COLLECTIONS)
        coll     = HADITH_COLLECTIONS[coll_idx]
        hadiths  = pool["hadiths"][coll]
        h        = hadiths[(slot // len(HADITH_COLLECTIONS)) % len(hadiths)]
        base["topic"] = h["collection_name"]
        base["text"]  = f"{h['english']}\n\n_Hadith nr. {h['hadithnumber']}_"
    else:
        # ── Dua day ──
        cat_idx = slot % len(DUA_CATEGORIES)
        cat     = DUA_CATEGORIES[cat_idx]
        duas    = pool["duas"][cat]
        d       = duas[(slot // len(DUA_CATEGORIES)) % len(duas)]
        base["topic"] = d["title"]
        parts = [d["translation"]]
        if d["transliteration"]:
            parts.append(f"[translit]{d['transliteration']}[/translit]")
        if d["source"]:
            parts.append(f"_{d['source']}_")
        base["text"] = "\n\n".join(parts)

    return base


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    dates     = sorted(json.loads(PRAYER_F.read_text(encoding="utf-8")).keys())
    orig_rems = json.loads(REM_ORIG.read_text(encoding="utf-8")) if REM_ORIG.exists() else {}

    pool = build_pool()

    empty_hadith = [c for c in HADITH_COLLECTIONS if not pool["hadiths"].get(c)]
    empty_dua    = [c for c in DUA_CATEGORIES     if not pool["duas"].get(c)]
    if empty_hadith or empty_dua:
        raise SystemExit(
            f"❌ Pool incomplete (empty hadith: {empty_hadith}, empty dua: {empty_dua}). "
            f"Delete {POOL_FILE.name} and re-run."
        )

    # ── Resume ──
    out_data: dict = {}
    if OUT_FILE.exists():
        out_data = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        already  = sum(1 for v in out_data.values() if v.get("text", "").strip())
        print(f"Resuming — {already} already done.\n")

    total   = len(dates)
    done    = 0
    skipped = 0

    for i, date_str in enumerate(dates):
        if date_str in out_data and out_data[date_str].get("text", "").strip():
            skipped += 1
            continue

        orig = orig_rems.get(date_str, {})
        out_data[date_str] = build_entry(pool, i, orig)
        print(f"[{i+1:3d}/{total}] {date_str}  {out_data[date_str]['topic'][:55]}")

        OUT_FILE.write_text(
            json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        done += 1

    print(f"\n✓ Done.  {done} new,  {skipped} skipped,  {total} total.")
    print(f"  Output → {OUT_FILE}\n")
    print("Neste steg:")
    print(f"  copy \"{OUT_FILE}\" \"{REM_ORIG}\"")
    print(f"  python \"{HERE / '04_generate_html.py'}\"")


if __name__ == "__main__":
    main()
