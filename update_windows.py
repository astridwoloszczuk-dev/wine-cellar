"""
Populate drinking windows and value_per_bottle from the Claude plans file.
Matches on (wine name, vintage) — updates all matching lots in Supabase.

Run:
    python update_windows.py
"""

import openpyxl
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

PLANS_FILE = "Wine_furture_plans_-_Claude (7).xlsx"


def safe_window(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def build_window_lookup():
    """
    Read plans file, return dict keyed by (name_lower, vintage) →
    {window_start, window_mid, window_end, value_now, amount}
    For duplicates, keep entry with highest value_now (most up-to-date estimate).
    """
    wb = openpyxl.load_workbook(PLANS_FILE, read_only=True, data_only=True)
    ws = wb["Wine Cellar"]
    rows = list(ws.iter_rows(values_only=True))
    header_idx = next(i for i, r in enumerate(rows) if r[4] == "Vintage")

    lookup = {}
    for row in rows[header_idx + 1:]:
        name    = row[3]
        vintage = row[4]
        amount  = row[5]
        value   = row[8]
        w_start = safe_window(row[9])
        w_mid   = safe_window(row[10])
        w_end   = safe_window(row[11])

        if not name or not vintage:
            continue
        try:
            vintage = int(vintage)
        except Exception:
            continue

        key = (str(name).strip().lower(), vintage)
        value_num = float(value) if value else None
        amount_num = int(float(str(amount))) if amount else None

        # Keep entry with highest value estimate; skip if no window at all
        if not any([w_start, w_mid, w_end]):
            continue

        existing = lookup.get(key)
        if existing is None or (value_num or 0) > (existing.get("value_now") or 0):
            lookup[key] = {
                "window_start": w_start,
                "window_mid":   w_mid,
                "window_end":   w_end,
                "value_now":    value_num,
                "amount":       amount_num,
            }

    wb.close()
    return lookup


def load_all_wines():
    all_wines = []
    offset = 0
    while True:
        result = supabase.from_("wines").select("id,name,vintage,bottle_count").range(offset, offset + 999).execute()
        all_wines.extend(result.data)
        if len(result.data) < 1000:
            break
        offset += 1000
    return all_wines


def main():
    print("Reading plans file …")
    lookup = build_window_lookup()
    print(f"  {len(lookup)} unique wine+vintage windows found")

    print("Loading wines from Supabase …")
    wines = load_all_wines()
    print(f"  {len(wines)} lots loaded")

    matched, unmatched = [], []

    for wine in wines:
        key = (str(wine["name"]).strip().lower(), wine["vintage"])
        plan = lookup.get(key)
        if plan:
            matched.append((wine, plan))
        else:
            unmatched.append(wine)

    print(f"\nMatched:   {len(matched)} lots")
    print(f"Unmatched: {len(unmatched)} lots")

    if unmatched:
        print("\nSample unmatched (first 10):")
        for w in unmatched[:10]:
            print(f"  {w['name']} {w['vintage']}")

    answer = input(f"\nUpdate {len(matched)} matched lots in Supabase? (yes/no): ").strip().lower()
    if answer != "yes":
        print("Aborted.")
        return

    updated = 0
    errors  = 0
    for wine, plan in matched:
        bottle_count = wine.get("bottle_count") or plan.get("amount") or 1
        value_ppb = round(plan["value_now"] / bottle_count, 2) if plan["value_now"] else None

        def to_window_str(v):
            if not v or v == "NOW":
                return v
            try:
                return str(int(float(str(v))))
            except (ValueError, TypeError):
                return None  # "Keeps" and other non-numeric values → null

        w_start = to_window_str(plan["window_start"])
        w_mid   = to_window_str(plan["window_mid"])
        w_end   = to_window_str(plan["window_end"])

        payload = {
            "window_start":    w_start,
            "window_mid":      w_mid,
            "window_end":      w_end,
            "value_per_bottle": value_ppb,
        }

        result = supabase.from_("wines").update(payload).eq("id", wine["id"]).execute()
        if hasattr(result, "error") and result.error:
            errors += 1
        else:
            updated += 1

        if updated % 100 == 0:
            print(f"  {updated}/{len(matched)} updated …", end="\r")

    print(f"\nDone. {updated} updated, {errors} errors.")
    if unmatched:
        print(f"\n{len(unmatched)} lots have no window data — add manually via the PWA or ask Claude to analyse them.")


if __name__ == "__main__":
    main()
