"""
One-time script to populate grape_variety and super_region for all wines using Claude Haiku.
Run once: python enrich_wines.py
Skips wines that already have both fields set.
"""

import os, json, time
from supabase import create_client
import anthropic
from dotenv import load_dotenv

load_dotenv()

supa = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
ai   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def enrich_batch(wines_batch):
    """Ask Claude Haiku for grape variety + super_region for a batch of wines."""
    lines = []
    for i, w in enumerate(wines_batch):
        lines.append(
            f"{i+1}. Name: {w.get('name','')} | Vintage: {w.get('vintage','')} "
            f"| Category: {w.get('category','')} | Region: {w.get('sub_region','')} "
            f"| Notes: {w.get('notes','')}"
        )

    prompt = f"""For each wine below, provide:
1. grape: primary grape variety or blend (e.g. "Cabernet Sauvignon" or "Cabernet Sauvignon / Merlot"). If unknown: "Unknown".
2. super_region: producing country or broad origin (e.g. "France", "Italy", "Australia", "USA", "Spain", "Germany", "New Zealand", "South Africa", "Argentina", "Portugal"). If unknown: "Unknown".

Be concise — no explanation.

{chr(10).join(lines)}

Reply with a JSON array, one object per wine, in the same order:
[{{"grape": "...", "super_region": "..."}}, ...]"""

    response = ai.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def needs_enrichment(w):
    return not w.get("grape_variety") or not w.get("super_region")


def main():
    res = supa.from_("wines").select("id,name,vintage,category,sub_region,notes,grape_variety,super_region").execute()
    wines = [w for w in res.data if needs_enrichment(w)]

    if not wines:
        print("All wines already enriched.")
        return

    print(f"{len(wines)} wines to enrich...")

    BATCH = 20
    updated = 0
    errors  = 0

    for i in range(0, len(wines), BATCH):
        batch = wines[i:i+BATCH]
        try:
            results = enrich_batch(batch)
            for wine, r in zip(batch, results):
                updates = {}
                if not wine.get("grape_variety"):
                    updates["grape_variety"] = r.get("grape", "Unknown")
                if not wine.get("super_region"):
                    updates["super_region"] = r.get("super_region", "Unknown")
                if updates:
                    supa.from_("wines").update(updates).eq("id", wine["id"]).execute()
                    print(f"  ✓ {wine['name']} {wine.get('vintage','')} → {updates}")
                    updated += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Batch {i//BATCH + 1} failed: {e}")
            errors += 1

    print(f"\nDone. {updated} updated, {errors} batch errors.")


if __name__ == "__main__":
    main()
