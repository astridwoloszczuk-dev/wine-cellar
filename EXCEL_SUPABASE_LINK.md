# Excel ↔ Supabase Connection

## Concept

Supabase is the single source of truth. Excel is a read-only modelling and analysis tool that pulls live data from Supabase via Power Query. No data is ever edited in Excel — all edits go through the PWA.

```
Supabase (live database)
    ↓  Power Query refresh
Excel (pivot tables, analysis, modelling)
```

---

## How the connection works

The connection uses Supabase's **REST API** — the same API the PWA uses. Power Query calls two paginated HTTP endpoints and combines the results into a single Excel table.

**Endpoint:**
```
GET https://mezayharkjyvnnhvdlww.supabase.co/rest/v1/wines?select=*&order=id&limit=1000&offset=0
GET https://mezayharkjyvnnhvdlww.supabase.co/rest/v1/wines?select=*&order=id&limit=1000&offset=1000
```

**Authentication:** The anon API key is passed as a request header (`apikey` and `Authorization: Bearer`). This is embedded directly in the M code — Excel does not store credentials separately. Authentication type in Excel is set to **Anonymous**.

**Pagination:** Supabase returns a maximum of 1,000 rows per request. With ~1,450 lots, two pages are needed. If the cellar ever exceeds 2,000 lots, add a `Page3` call.

---

## Setup instructions (for a new machine)

1. Open Excel
2. **Data → Get Data → From Other Sources → Blank Query**
3. In the Query Editor, click **Advanced Editor**
4. Press **Ctrl+A** to select all existing text
5. Paste the contents of `supabase_power_query.m` (copy from this folder)
6. Replace `PASTE_YOUR_KEY_HERE` with the Supabase anon key (keep the quotes and trailing comma)
7. Click **Done**
8. When prompted for authentication, choose **Anonymous (Anonym)**
9. Click **Close & Load** — data lands on a new sheet as `tbl_Cellar`

---

## Columns returned

| Column | Type | Notes |
|---|---|---|
| id | text | UUID, primary key |
| name | text | Wine name |
| category | text | e.g. "Bordeaux Red", "Burgundy - White" |
| sub_region | text | e.g. "Pauillac", "Meursault" |
| super_region | text | Country/broad region e.g. "France" |
| grape_variety | text | e.g. "Cabernet Sauvignon", "Chardonnay" |
| vintage | integer | Year, null = NV |
| merchant | text | Who it was bought from |
| storage_location | text | Where it is now |
| bottle_count | integer | Number of bottles in this lot |
| bottle_format | text | "75cl", "150cl", "300cl" |
| cost_per_bottle | decimal | What was paid per bottle £ |
| value_per_bottle | decimal | Current market estimate per bottle £ |
| window_start | text | "NOW" or year |
| window_mid | text | "NOW" or year |
| window_end | text | Year |
| urgency | text | Auto-calculated: past_window / closing_soon / near_midpoint / approaching_midpoint / hold |
| status | text | in_storage / pending_listing / listed / sold / consumed |
| invoice_no | text | |
| paid | boolean | |
| notes | text | |
| sold_at | date | |
| sold_price_per_bottle | decimal | |
| sold_via | text | |
| created_at | datetime | |
| updated_at | datetime | |

---

## Refreshing

- **Manual:** Right-click the table → Refresh, or Data → Refresh All
- **Automatic:** Data → Queries & Connections → right-click the query → Properties → set refresh interval

The table is named `tbl_Cellar` and can be used as the source for any pivot table or XLOOKUP.

---

## Adding new columns to Supabase

If a new column is added to the `wines` table in Supabase:

1. Open the M code in Power Query Advanced Editor
2. Add the new column name to the list inside `Table.ExpandRecordColumn`
3. The `select=*` in the URL already fetches all columns — no URL change needed
4. Refresh

The current M code is in `supabase_power_query.m` in this folder.

---

## Key rule

**Never type data directly into `tbl_Cellar`.** It is overwritten on every refresh. All edits go through the PWA. Excel is read-only by convention.
