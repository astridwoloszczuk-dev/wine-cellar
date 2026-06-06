"""
One-time script to populate grape_variety for all wines using Claude Haiku.
Run once: python enrich_grapes.py
Skips wines that already have grape_variety set.
"""

import os, json, time
from supabase import create_client
import anthropic
from dotenv import load_dotenv

load_dotenv()

supa = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
ai   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_grape(wines_batch):
    """Ask Claude Haiku for primary grape variety for a batch of wines."""
    lines = []
    for i, w in enumerate(wines_batch):
        lines.append(
            f"{i+1}. Name: {w.get('name','')} | Vintage: {w.get('vintage','')} "
            f"| Category: {w.get('category','')} | Region: {w.get('sub_region','')} "
            f"| Notes: {w.get('notes','')}"
        )

    prompt = f"""For each wine below, state the primary grape variety (or blend, e.g. "Cabernet Sauvignon" or "Cabernet Sauvignon / Merlot").
Be concise — grape name(s) only, no explanation.
If genuinely unknown, write "Unknown".

{chr(10).join(lines)}

Reply with a JSON array of strings, one per wine, in the same order:
["Grape 1", "Grape 2", ...]"""

    response = ai.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def main():
    # Fetch wines missing grape_variety
    res = supa.from_("wines").select("id,name,vintage,category,sub_region,notes") \
        .is_("grape_variety", "null").execute()
    wines = res.data
    if not wines:
        print("All wines already have grape_variety set.")
        return

    print(f"{len(wines)} wines to enrich...")

    BATCH = 20
    updated = 0
    errors  = 0

    for i in range(0, len(wines), BATCH):
        batch = wines[i:i+BATCH]
        try:
            grapes = get_grape(batch)
            for wine, grape in zip(batch, grapes):
                supa.from_("wines").update({"grape_variety": grape}).eq("id", wine["id"]).execute()
                print(f"  ✓ {wine['name']} {wine.get('vintage','')} → {grape}")
                updated += 1
            time.sleep(0.5)  # gentle rate limiting
        except Exception as e:
            print(f"  ✗ Batch {i//BATCH + 1} failed: {e}")
            errors += 1

    print(f"\nDone. {updated} updated, {errors} batch errors.")


if __name__ == "__main__":
    main()
