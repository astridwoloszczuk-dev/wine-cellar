# Wine Cellar App — Handover Notes

## What's been built

A full wine cellar management system for Astrid and her husband Niko.
Note: **James** = the Mac Mini home server. **Niko** = the husband.

### Architecture
- **Supabase** (family-apps project, ref: `mezayharkjyvnnhvdlww`) — single source of truth
- **Vue 3 + AG Grid PWA** (`app/`) — desktop browser interface
- **Power Query** (`supabase_power_query.m`) — live Excel connection for James's modelling
- **Python scripts** — one-time import and window data population

### What's in Supabase
- **1,450 lots** across BBR Bond, Justerini Bond, IG Bond, Fine & Rare, Hatton Edwards, Lay Wheeler, Vinotheque (Vienna), Wien (home)
- **9,707 bottles** total
- Drinking windows populated for 1,071 lots from the Claude plans file
- 379 lots still missing window data (add manually via PWA or run fresh Claude analysis)

### Tables
- `wines` — master inventory (one row = one physical case barcode)
- `sell_listings` — listing history with prices
- `delivery_plan` — year-by-year drinking plan 2027–2041 (schema ready, not yet populated)

### Key schema decisions
- `cost_per_bottle` not `cost_total` (Astrid's correct instinct)
- `merchant` = who bought from (immutable), `storage_location` = where it is now (mutable)
- UK in-bond wines can be sold; Vinotheque/Wien wines cannot (duties make it uneconomical)
- Sold wines: soft delete only — keep record with `sold_at`, `sold_price_per_bottle`, `sold_via`
- Urgency auto-calculated from `window_end` vs today in the PWA — never manually set

### Status values
`in_storage` → `pending_listing` → `listed` → `sold`
`in_storage` → storage_location change (when delivered to Vinotheque/Wien)

---

## The PWA app (`app/`)

### To run locally (dev)
```bash
cd app
npm install
npm run dev
# → http://localhost:5173
```

### To deploy on James (TODO)
```bash
cd app
npm install
npm run build
# dist/ folder contains the static site — serve with nginx or `npx serve dist`
```

The app needs a `.env` file in `app/` with:
```
VITE_SUPABASE_URL=https://mezayharkjyvnnhvdlww.supabase.co
VITE_SUPABASE_KEY=<anon key>
```
The `.env` is already populated on Astrid's machine.

### Features working
- Full AG Grid table with sorting, filtering, column resize
- Filter bar: search, status, location, urgency
- Click row → edit side panel (status, location, asking price, sold price, drinking window, value, notes)
- Add new wine modal
- Urgency colour-coding (red/orange/yellow/green) auto-calculated from window dates
- P&L display in edit panel
- Footer stats: lots, bottles, estimated value

---

## What's next

### Priority 1 — Deploy on James
Ask the James migration Claude window how to serve a static site from a `dist/` folder. Simplest options:
- `npx serve dist` (zero config)
- nginx static site config pointing at the `dist/` folder

### Priority 2 — Drinking windows for remaining 379 lots
Run a Claude analysis script to look up windows for unmatched wines, or add manually via the PWA.

### Priority 3 — Automation
- Sell urgency alerts → integrate into morning briefing (`morning-briefing/briefing.py`)
- Price checker via Wine-Searcher for wines listed/pending listing
- Listing status checker against merchant portals

### Priority 4 — Mobile Vienna app (separate project)
A simple mobile PWA for the Wien/Vinotheque wines only:
- What's here tonight?
- Open a bottle → mark as consumed
- Rate it (simple 1-5 or notes)
- Wine diary / history

---

## Files
```
wine-cellar/
├── HANDOVER.md                          ← this file
├── schema.sql                           ← Supabase schema (already run)
├── import.py                            ← one-time Excel → Supabase import (done)
├── update_windows.py                    ← populated drinking windows (done)
├── supabase_power_query.m               ← paste into Excel Power Query Advanced Editor
├── requirements.txt                     ← Python deps
├── .env                                 ← Supabase credentials (Python scripts)
└── app/                                 ← Vue PWA
    ├── .env                             ← Supabase credentials (Vite/browser)
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── supabase.js
        ├── utils/urgency.js
        └── components/
            ├── WineTable.vue
            ├── WinePanel.vue
            └── AddWineModal.vue
```

---

## Source data files (do not delete)
- `IG BBR FR Wine Personal Post Handover NEW 2026 05 17.xlsx` — real source of truth (husband's cellar tracker)
- `Wine_furture_plans_-_Claude (7).xlsx` — Claude's planning output (used for window data, not authoritative)
