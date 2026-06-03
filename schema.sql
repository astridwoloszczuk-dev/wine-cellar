-- Wine Cellar Schema
-- Each row in `wines` = one physical lot (one case barcode in the warehouse)
-- Run this in the Supabase SQL editor for your project

create extension if not exists "uuid-ossp";

-- ============================================================
-- WINES — master inventory
-- ============================================================
create table wines (
  id uuid primary key default uuid_generate_v4(),

  -- Identity
  name            text not null,
  category        text,          -- "Bordeaux Red", "Burgundy - White", "Sangiovese", etc.
  sub_region      text,          -- "Pauillac", "Meursault", "SuperTuscan", etc.
  vintage         integer,

  -- Provenance & location
  merchant        text,          -- "BBR", "Justerini", "IG", "Hatton Edwards", "Fine and Rare"
  storage_location text,         -- "BBR Bond", "Justerini Bond", "IG Bond", "Vinotheque", "Wien", etc.

  -- Lot details (immutable after purchase)
  bottle_count    integer,       -- number of bottles in this lot
  bottle_format   text default '75cl',  -- "75cl", "150cl" (magnum), "300cl" (double magnum)
  cost_per_bottle numeric(10,2), -- what you paid per bottle £ — never changes

  -- Current valuation (updated periodically)
  value_per_bottle numeric(10,2),

  -- Drinking window
  window_start    text,          -- "NOW" or year e.g. "2029"
  window_mid      text,
  window_end      text,

  -- Status & urgency
  urgency         text,          -- "past_window" | "closing_soon" | "near_midpoint" | "approaching_midpoint" | "hold"
  status          text default 'in_storage', -- "in_storage" | "listed" | "sold" | "consumed"

  -- Admin
  invoice_no      text,
  paid            boolean default true,
  notes           text,

  -- Sale record (populated when status → "sold")
  sold_at         date,
  sold_price_per_bottle numeric(10,2),
  sold_via        text,          -- "BBR", "Justerini", "private", etc.

  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- Auto-update updated_at on any change
create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger wines_updated_at
  before update on wines
  for each row execute function update_updated_at();


-- ============================================================
-- SELL LISTINGS — one row per listing event
-- Keeps full history: listed → sold/withdrawn
-- ============================================================
create table sell_listings (
  id uuid primary key default uuid_generate_v4(),
  wine_id         uuid references wines(id) on delete cascade,
  merchant        text,          -- where listed: "BBR", "Justerini", "Wine-Searcher", etc.
  bottles_listed  integer,
  listed_at       date,
  list_price_per_bottle numeric(10,2),
  status          text default 'active',  -- "active" | "sold" | "withdrawn"
  sold_at         date,
  sold_price_per_bottle numeric(10,2),
  notes           text,
  created_at      timestamptz default now()
);


-- ============================================================
-- DELIVERY PLAN — year-by-year drinking schedule 2027–2041
-- ============================================================
create table delivery_plan (
  id uuid primary key default uuid_generate_v4(),
  planned_year    integer not null,  -- 2027 … 2041
  wine_id         uuid references wines(id) on delete set null,
  wine_name       text,              -- denormalized — for entries not yet purchased
  bottles_planned integer,
  cost_per_bottle numeric(10,2),
  window_start    text,
  window_mid      text,
  window_end      text,
  source          text default 'Cellar',  -- "Cellar" | "Buy"
  is_alternative  boolean default false,  -- true = the alternative row below the primary pick
  notes           text,
  created_at      timestamptz default now()
);


-- ============================================================
-- VIEWS — useful pre-built queries
-- ============================================================

-- Portfolio summary by storage location
create view v_cellar_summary as
select
  storage_location,
  count(*)                              as lots,
  sum(bottle_count)                     as bottles,
  round(sum(cost_per_bottle * bottle_count)::numeric, 2)   as total_cost_gbp,
  round(sum(value_per_bottle * bottle_count)::numeric, 2)  as total_value_gbp
from wines
where status in ('in_storage', 'listed')
group by storage_location
order by total_value_gbp desc nulls last;


-- Wines to act on now (past window or closing soon, UK in-bond only)
create view v_sell_now as
select
  id, name, vintage, category, sub_region,
  merchant, storage_location,
  bottle_count, bottle_format,
  cost_per_bottle,
  value_per_bottle,
  round((value_per_bottle * bottle_count)::numeric, 2)                         as total_value_gbp,
  round(((value_per_bottle - cost_per_bottle) * bottle_count)::numeric, 2)     as estimated_profit_gbp,
  window_end,
  urgency,
  status
from wines
where urgency in ('past_window', 'closing_soon')
  and status = 'in_storage'
  and storage_location not in ('Vinotheque', 'Wien')
order by
  case urgency
    when 'past_window'   then 1
    when 'closing_soon'  then 2
    else 3
  end,
  window_end;


-- P&L on sold wines
create view v_pnl as
select
  name, vintage, merchant,
  bottle_count,
  cost_per_bottle,
  sold_price_per_bottle,
  round(((sold_price_per_bottle - cost_per_bottle) * bottle_count)::numeric, 2) as profit_gbp,
  round(((sold_price_per_bottle - cost_per_bottle) / cost_per_bottle * 100)::numeric, 1) as return_pct,
  sold_at,
  sold_via
from wines
where status = 'sold'
  and sold_price_per_bottle is not null
order by sold_at desc;
