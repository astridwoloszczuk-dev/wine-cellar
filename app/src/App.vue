<template>
  <LoginScreen v-if="!session" @signed-in="session = $event" />
  <div v-else class="app">
    <header class="header">
      <div class="header-left">
        <span class="logo">🍷</span>
        <h1>Wine Cellar</h1>
      </div>
      <div class="header-right">
        <button class="btn-primary" @click="showAddModal = true">+ Add Wine</button>
        <button class="btn-signout" @click="signOut" title="Sign out">↩</button>
      </div>
    </header>

    <div class="filter-bar">
      <input v-model="filters.search" placeholder="Search wine, region, grape…" class="filter-search" />
      <button class="btn-filters" :class="{ active: activeFilterCount > 0 }" @click="showFilters = !showFilters">
        Filters{{ activeFilterCount > 0 ? ` (${activeFilterCount})` : '' }} {{ showFilters ? '▲' : '▼' }}
      </button>
      <button v-if="anyFilter" class="btn-clear" @click="clearFilters">Clear all</button>
    </div>

    <div v-if="showFilters" class="filter-panel">
      <div class="filter-grid">
        <div class="filter-item">
          <label>Wine name</label>
          <input v-model="filters.name" placeholder="contains…" class="fi-text" />
        </div>
        <div class="filter-item">
          <label>Vintage</label>
          <div class="fi-range">
            <select v-model="filters.vintage.op" class="fi-op">
              <option value="">—</option>
              <option value="eq">=</option>
              <option value="lt">before</option>
              <option value="gt">after</option>
              <option value="between">between</option>
            </select>
            <input v-if="filters.vintage.op" v-model.number="filters.vintage.val1" type="number" placeholder="year" class="fi-num" />
            <input v-if="filters.vintage.op === 'between'" v-model.number="filters.vintage.val2" type="number" placeholder="year" class="fi-num" />
          </div>
        </div>
        <div class="filter-item">
          <label>Category</label>
          <MultiSelect placeholder="Any" :options="categoryOptions" v-model="filters.category" />
        </div>
        <div class="filter-item">
          <label>Sub-region</label>
          <MultiSelect placeholder="Any" :options="subRegionOptions" v-model="filters.sub_region" />
        </div>
        <div class="filter-item">
          <label>Country</label>
          <MultiSelect placeholder="Any" :options="countryOptions" v-model="filters.country" />
        </div>
        <div class="filter-item">
          <label>Grape</label>
          <input v-model="filters.grape" placeholder="contains…" class="fi-text" />
        </div>
        <div class="filter-item">
          <label>Merchant</label>
          <MultiSelect placeholder="Any" :options="merchantOptions" v-model="filters.merchant" />
        </div>
        <div class="filter-item">
          <label>Location</label>
          <MultiSelect placeholder="Any" :options="locationOptions" v-model="filters.location" />
        </div>
        <div class="filter-item">
          <label>Bottles</label>
          <div class="fi-range">
            <select v-model="filters.bottles.op" class="fi-op">
              <option value="">—</option>
              <option value="lt">&lt;</option>
              <option value="gt">&gt;</option>
              <option value="between">between</option>
            </select>
            <input v-if="filters.bottles.op" v-model.number="filters.bottles.val1" type="number" class="fi-num" />
            <input v-if="filters.bottles.op === 'between'" v-model.number="filters.bottles.val2" type="number" class="fi-num" />
          </div>
        </div>
        <div class="filter-item">
          <label>Cost/btl (£)</label>
          <div class="fi-range">
            <select v-model="filters.cost.op" class="fi-op">
              <option value="">—</option>
              <option value="lt">&lt;</option>
              <option value="gt">&gt;</option>
              <option value="between">between</option>
            </select>
            <input v-if="filters.cost.op" v-model.number="filters.cost.val1" type="number" class="fi-num" />
            <input v-if="filters.cost.op === 'between'" v-model.number="filters.cost.val2" type="number" class="fi-num" />
          </div>
        </div>
        <div class="filter-item">
          <label>Window Start</label>
          <MultiSelect placeholder="Any year" :options="windowStartOptions" v-model="filters.window_start" />
        </div>
        <div class="filter-item">
          <label>Window End</label>
          <MultiSelect placeholder="Any year" :options="windowEndOptions" v-model="filters.window_end" />
        </div>
        <div class="filter-item">
          <label>Urgency</label>
          <MultiSelect placeholder="Any" :options="urgencyOptions" v-model="filters.urgency" />
        </div>
        <div class="filter-item">
          <label>Status</label>
          <MultiSelect placeholder="Any" :options="STATUSES" v-model="filters.status" />
        </div>
        <div class="filter-item">
          <label>Working notes</label>
          <input v-model="filters.working_notes" placeholder="contains…" class="fi-text" />
        </div>
      </div>
    </div>

    <div class="summary-panel">
      <button class="summary-toggle" @click="showSummary = !showSummary">
        {{ showSummary ? '▲' : '▼' }} Summary
      </button>
      <template v-if="showSummary">
        <span class="sum-stat"><strong>{{ stats.lots.toLocaleString() }}</strong> lots</span>
        <span class="sum-sep">·</span>
        <span class="sum-stat"><strong>{{ stats.bottles.toLocaleString() }}</strong> bottles</span>
        <span v-if="stats.value" class="sum-sep">·</span>
        <span v-if="stats.value" class="sum-stat">Value <strong>£{{ Math.round(stats.value).toLocaleString() }}</strong></span>
        <span v-if="anyFilter" class="sum-sep">·</span>
        <span v-for="(count, urg) in urgencyBreakdown" :key="urg" class="sum-urgency" :class="urg">
          {{ URGENCY_LABEL[urg] }}: <strong>{{ count }}</strong>
        </span>
      </template>
    </div>

    <div v-if="selectedWines.length" class="bulk-bar">
      <span class="bulk-info">{{ selectedWines.length }} wine{{ selectedWines.length !== 1 ? 's' : '' }} selected — {{ selectedBottles }} bottle{{ selectedBottles !== 1 ? 's' : '' }}</span>
      <template v-if="bulkNoteMode">
        <input v-model="bulkNoteText" class="bulk-note-input" placeholder="e.g. possible sale…" @keyup.enter="applyBulkNote" @keyup.esc="bulkNoteMode = false" autofocus />
        <button class="btn-bulk-action" @click="applyBulkNote" :disabled="bulkSaving">Apply</button>
        <button class="btn-bulk-clear" @click="bulkNoteMode = false">✕</button>
      </template>
      <template v-else>
        <button class="btn-bulk-action" @click="requestDelivery">📦 Request delivery</button>
        <button class="btn-bulk-action btn-sale" @click="markForSale" :disabled="bulkSaving">🏷 Mark for sale</button>
        <button class="btn-bulk-action btn-note" @click="bulkNoteMode = true; bulkNoteText = ''">📝 Set note</button>
        <button class="btn-bulk-clear" @click="clearSelection">✕ Clear</button>
      </template>
    </div>

    <div class="content" :class="{ 'panel-open': selectedWine }">
      <WineTable
        ref="wineTableRef"
        :wines="filteredWines"
        :loading="loading"
        :selectedId="selectedWine?.id"
        @select="onSelect"
        @selection-changed="onSelectionChanged"
      />
      <WinePanel
        v-if="selectedWine"
        :wine="selectedWine"
        @close="selectedWine = null"
        @saved="onSaved"
      />
    </div>

    <footer class="footer">
      <span><strong>{{ stats.lots.toLocaleString() }}</strong> lots</span>
      <span class="sep">•</span>
      <span><strong>{{ stats.bottles.toLocaleString() }}</strong> bottles</span>
      <span v-if="stats.value" class="sep">•</span>
      <span v-if="stats.value">Est. value <strong>£{{ Math.round(stats.value).toLocaleString() }}</strong></span>
      <span v-if="anyFilter" class="filter-note"> — {{ filteredWines.length }} shown</span>
    </footer>

    <AddWineModal
      v-if="showAddModal"
      @close="showAddModal = false"
      @saved="onAdded"
    />

    <div v-if="deliveryModal" class="overlay" @click.self="deliveryModal = null">
      <div class="delivery-modal">
        <div class="dm-header">
          <h2>Delivery requests</h2>
          <button @click="deliveryModal = null">✕</button>
        </div>
        <div class="dm-body">
          <div v-for="e in deliveryModal.emails" :key="e.merchant" class="dm-email">
            <div class="dm-merchant">
              {{ e.merchant }} — {{ e.wines.length }} lot{{ e.wines.length !== 1 ? 's' : '' }}
              <span v-if="e.email" class="dm-email-addr">{{ e.email }}</span>
            </div>
            <textarea class="dm-text" :value="e.body" rows="14" readonly />
            <button class="btn-copy" @click="navigator.clipboard.writeText(e.body)">Copy to clipboard</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { supabase } from './supabase'
import { calcUrgency, STATUSES, STORAGE_LOCATIONS, URGENCY_LABEL } from './utils/urgency'
import WineTable from './components/WineTable.vue'
import WinePanel from './components/WinePanel.vue'
import AddWineModal from './components/AddWineModal.vue'
import LoginScreen from './components/LoginScreen.vue'
import MultiSelect from './components/MultiSelect.vue'

const session = ref(null)

const wines        = ref([])
const allTastings  = ref([])
const loading      = ref(true)
const selectedWine = ref(null)
const showAddModal = ref(false)
const showFilters  = ref(false)
const filters      = ref(emptyFilters())
const selectedWines = ref([])
const wineTableRef  = ref(null)
const showSummary   = ref(true)
const deliveryModal = ref(null)
const bulkSaving    = ref(false)
const bulkNoteMode  = ref(false)
const bulkNoteText  = ref('')
const cellarConfig  = ref(null)

function emptyFilters() {
  return {
    search: '',
    name: '',
    vintage: { op: '', val1: null, val2: null },
    category: [],
    sub_region: [],
    country: [],
    grape: '',
    merchant: [],
    location: [],
    bottles: { op: '', val1: null, val2: null },
    cost: { op: '', val1: null, val2: null },
    window_start: [],
    window_end: [],
    urgency: [],
    status: [],
    working_notes: '',
  }
}

async function loadConfig() {
  try {
    const { data } = await supabase.from('settings').select('value').eq('key', 'cellar_config').single()
    if (data) cellarConfig.value = data.value
  } catch { /* config missing, use defaults */ }
}

const BLANK = '__blank__'

function makeOptions(vals, withBlank = false) {
  const filled = [...new Set(vals.filter(v => v != null && v !== ''))].sort().map(v => ({ value: v, label: String(v) }))
  const hasBlank = vals.some(v => v == null || v === '')
  if (withBlank && hasBlank) filled.push({ value: BLANK, label: '(blank)' })
  return filled
}

const categoryOptions    = computed(() => makeOptions(wines.value.map(w => w.category), true))
const subRegionOptions   = computed(() => makeOptions(wines.value.map(w => w.sub_region), true))
const countryOptions     = computed(() => makeOptions(wines.value.map(w => w.super_region), true))
const merchantOptions    = computed(() => makeOptions(wines.value.map(w => w.merchant), true))
const locationOptions    = computed(() => makeOptions(wines.value.map(w => w.storage_location), true))
const windowStartOptions = computed(() => makeOptions(wines.value.map(w => w.window_start), true))
const windowMidOptions   = computed(() => makeOptions(wines.value.map(w => w.window_mid), true))
const windowEndOptions   = computed(() => makeOptions(wines.value.map(w => w.window_end), true))

const urgencyOptions = [
  { value: 'past_window',          label: 'Past window' },
  { value: 'closing_soon',         label: 'Closing soon' },
  { value: 'near_midpoint',        label: 'Near midpoint' },
  { value: 'approaching_midpoint', label: 'Approaching mid' },
  { value: 'hold',                 label: 'Hold' },
  { value: BLANK,                  label: '(blank)' },
]

function matchesMulti(value, selected) {
  if (selected.includes(BLANK)) {
    if (value == null || value === '') return true
    return selected.some(s => s !== BLANK && s === value)
  }
  return selected.includes(value)
}

function matchesRange(value, { op, val1, val2 }) {
  if (!op || val1 == null) return true
  const v = Number(value)
  if (op === 'eq')      return v === val1
  if (op === 'lt')      return v < val1
  if (op === 'gt')      return v > val1
  if (op === 'between') return val2 != null ? v >= val1 && v <= val2 : v >= val1
  return true
}

const activeFilterCount = computed(() => {
  const f = filters.value
  return [
    f.name, f.vintage.op, f.grape, f.bottles.op, f.cost.op, f.working_notes,
    ...f.category, ...f.sub_region, ...f.country, ...f.merchant,
    ...f.location, ...f.window_start, ...f.window_end,
    ...f.urgency, ...f.status,
  ].filter(Boolean).length
})

const anyFilter = computed(() => filters.value.search !== '' || activeFilterCount.value > 0)

function clearFilters() {
  filters.value = emptyFilters()
}

const filteredWines = computed(() => {
  let r = wines.value
  const f = filters.value

  if (f.search) {
    const q = f.search.toLowerCase()
    r = r.filter(w =>
      (w.name          || '').toLowerCase().includes(q) ||
      (w.sub_region    || '').toLowerCase().includes(q) ||
      (w.category      || '').toLowerCase().includes(q) ||
      (w.grape_variety || '').toLowerCase().includes(q) ||
      (w.super_region  || '').toLowerCase().includes(q) ||
      String(w.vintage || '').includes(q)
    )
  }
  if (f.name)               r = r.filter(w => (w.name || '').toLowerCase().includes(f.name.toLowerCase()))
  if (f.vintage.op)         r = r.filter(w => matchesRange(w.vintage, f.vintage))
  if (f.category.length)    r = r.filter(w => matchesMulti(w.category, f.category))
  if (f.sub_region.length)  r = r.filter(w => matchesMulti(w.sub_region, f.sub_region))
  if (f.country.length)     r = r.filter(w => matchesMulti(w.super_region, f.country))
  if (f.grape)              r = r.filter(w => (w.grape_variety || '').toLowerCase().includes(f.grape.toLowerCase()))
  if (f.merchant.length)    r = r.filter(w => matchesMulti(w.merchant, f.merchant))
  if (f.location.length)    r = r.filter(w => matchesMulti(w.storage_location, f.location))
  if (f.bottles.op)         r = r.filter(w => matchesRange(w.bottle_count, f.bottles))
  if (f.cost.op)            r = r.filter(w => matchesRange(w.cost_per_bottle, f.cost))
  if (f.window_start.length)  r = r.filter(w => matchesMulti(w.window_start, f.window_start))
  if (f.window_end.length)    r = r.filter(w => matchesMulti(w.window_end, f.window_end))
  if (f.urgency.length)       r = r.filter(w => matchesMulti(w.urgency, f.urgency))
  if (f.status.length)        r = r.filter(w => matchesMulti(w.status, f.status))
  if (f.working_notes)        r = r.filter(w => (w.working_notes || '').toLowerCase().includes(f.working_notes.toLowerCase()))
  return r
})

const stats = computed(() => ({
  lots:    filteredWines.value.length,
  bottles: filteredWines.value.reduce((s, w) => s + (w.bottle_count || 0), 0),
  value:   filteredWines.value.reduce((s, w) => s + (w.value_per_bottle || 0) * (w.bottle_count || 0), 0)
}))

const selectedBottles = computed(() => selectedWines.value.reduce((s, w) => s + (w.bottle_count || 0), 0))

const urgencyBreakdown = computed(() => {
  const counts = {}
  for (const w of filteredWines.value) {
    if (w.urgency) counts[w.urgency] = (counts[w.urgency] || 0) + 1
  }
  return counts
})

function withUrgency(w) {
  return { ...w, urgency: w.window_end ? calcUrgency(w.window_end, w.window_mid) : (w.urgency || null) }
}

function buildTastingSummary(wineId, tastings) {
  const scores = tastings
    .filter(t => t.wine_id === wineId && t.score != null)
    .map(t => Number(t.score))
  if (!scores.length) return null
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length
  return {
    avg:   avg % 1 === 0 ? avg.toFixed(0) : avg.toFixed(1),
    count: scores.length,
  }
}

async function loadWines() {
  loading.value = true

  const [winesPages, tastingsRes] = await Promise.all([
    (async () => {
      const all = []
      let offset = 0
      while (true) {
        const { data, error } = await supabase
          .from('wines')
          .select('*')
          .order('name')
          .range(offset, offset + 999)
        if (error) { console.error(error); break }
        all.push(...data)
        if (data.length < 1000) break
        offset += 1000
      }
      return all
    })(),
    supabase.from('tastings').select('*'),
  ])

  allTastings.value = tastingsRes.data || []
  wines.value = winesPages.map(w => ({
    ...withUrgency(w),
    tasting_summary: buildTastingSummary(w.id, allTastings.value),
  }))
  loading.value = false
}

function onSelect(wine) {
  selectedWine.value = wine
}

function onSelectionChanged(rows) { selectedWines.value = rows }

function clearSelection() {
  wineTableRef.value?.clearSelection()
  selectedWines.value = []
}

async function requestDelivery() {
  const cfg = cellarConfig.value || {}
  const ownerName = cfg.owner?.name || '[Your name]'
  const address   = (cfg.delivery_address || ['[Your Vienna delivery address]']).join('\n')

  const byMerchant = {}
  for (const w of selectedWines.value) {
    const m = w.merchant || 'Unknown merchant'
    if (!byMerchant[m]) byMerchant[m] = []
    byMerchant[m].push(w)
  }

  const emails = Object.entries(byMerchant).map(([merchant, mWines]) => {
    const contact = cfg.merchants?.find(m => m.name === merchant)
    const greeting = contact?.contact_name ? `Dear ${contact.contact_name},` : `Dear ${merchant} team,`
    const email     = contact?.email || ''
    const lines     = mWines.map(w => `  - ${w.name} ${w.vintage || 'NV'} — ${w.bottle_count} × ${w.bottle_format || '75cl'}`).join('\n')
    const totalBottles = mWines.reduce((s, w) => s + (w.bottle_count || 0), 0)
    const body = `${greeting}\n\nPlease arrange release from bond and delivery to our Vienna address for the following wines:\n\n${lines}\n\nTotal: ${mWines.length} lot${mWines.length !== 1 ? 's' : ''}, ${totalBottles} bottle${totalBottles !== 1 ? 's' : ''}.\n\nPlease ship to:\n${address}\n\nThank you for your assistance.\n\nKind regards,\n${ownerName}`
    return { merchant, wines: mWines, email, body }
  })

  const ids = selectedWines.value.map(w => w.id)
  await supabase.from('wines').update({ storage_location: 'In transit' }).in('id', ids)
  for (const id of ids) {
    const idx = wines.value.findIndex(w => w.id === id)
    if (idx !== -1) wines.value[idx] = { ...wines.value[idx], storage_location: 'In transit' }
  }

  deliveryModal.value = { emails }
  clearSelection()
}

async function applyBulkNote() {
  if (!selectedWines.value.length) return
  bulkSaving.value = true
  const ids = selectedWines.value.map(w => w.id)
  const { error } = await supabase.from('wines').update({ working_notes: bulkNoteText.value || null }).in('id', ids)
  if (!error) {
    for (const id of ids) {
      const idx = wines.value.findIndex(w => w.id === id)
      if (idx !== -1) wines.value[idx] = { ...wines.value[idx], working_notes: bulkNoteText.value || null }
    }
    bulkNoteMode.value = false
    clearSelection()
  }
  bulkSaving.value = false
}

async function markForSale() {
  if (!selectedWines.value.length) return
  bulkSaving.value = true
  const ids = selectedWines.value.map(w => w.id)
  const { error } = await supabase.from('wines').update({ status: 'pending_listing', urgency: null }).in('id', ids)
  if (!error) {
    for (const id of ids) {
      const idx = wines.value.findIndex(w => w.id === id)
      if (idx !== -1) wines.value[idx] = { ...wines.value[idx], status: 'pending_listing' }
    }
    clearSelection()
  }
  bulkSaving.value = false
}

function onSaved(updated) {
  const u = {
    ...withUrgency(updated),
    tasting_summary: buildTastingSummary(updated.id, allTastings.value),
  }
  const idx = wines.value.findIndex(w => w.id === u.id)
  if (idx !== -1) wines.value[idx] = u
  selectedWine.value = u
}

function onAdded(newWine) {
  wines.value.unshift({
    ...withUrgency(newWine),
    tasting_summary: null,
  })
  showAddModal.value = false
}

watch(session, (s) => { if (s) loadWines() })

async function signOut() {
  await supabase.auth.signOut()
  session.value = null
}

onMounted(async () => {
  loadConfig()
  const { data } = await supabase.auth.getSession()
  session.value = data.session
  supabase.auth.onAuthStateChange((_event, s) => { session.value = s })
  if (session.value) loadWines()
})
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f6fa;
  color: #2c3e50;
}

#app { height: 100vh; }

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 52px;
  background: #2c3e50;
  color: white;
  flex-shrink: 0;
}
.header-left  { display: flex; align-items: center; gap: 10px; }
.header-right { display: flex; align-items: center; gap: 8px; }

.btn-signout {
  padding: 6px 10px;
  background: transparent;
  color: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-signout:hover { color: white; border-color: rgba(255,255,255,0.6); }
.logo { font-size: 1.4rem; }
.header h1 { font-size: 1.15rem; font-weight: 600; letter-spacing: 0.02em; }

/* ── Filter bar ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}
.filter-search {
  flex: 1;
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
}
.btn-filters {
  padding: 5px 12px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  color: #555;
  white-space: nowrap;
}
.btn-filters:hover { background: #f5f5f5; }
.btn-filters.active { border-color: #8B1A1A; color: #8B1A1A; font-weight: 600; }

.btn-clear {
  padding: 5px 10px;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  color: #666;
}
.btn-clear:hover { background: #f5f5f5; }

/* ── Filter panel ── */
.filter-panel {
  background: #fafafa;
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 16px;
  flex-shrink: 0;
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px 16px;
}
.filter-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.filter-item label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.fi-text {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.82rem;
}
.fi-range {
  display: flex;
  gap: 4px;
  align-items: center;
}
.fi-op {
  padding: 4px 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.82rem;
  background: white;
  flex-shrink: 0;
}
.fi-num {
  width: 72px;
  padding: 4px 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.82rem;
}

/* ── Summary panel ── */
.summary-panel {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 16px;
  background: #f9f9f9;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.8rem;
  color: #555;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.summary-toggle {
  background: none; border: none; cursor: pointer;
  font-size: 0.75rem; color: #888; padding: 0;
}
.sum-sep { color: #ccc; }
.sum-urgency { padding: 1px 6px; border-radius: 10px; font-size: 0.75rem; }
.sum-urgency.past_window { background: #ffcccc; color: #b71c1c; }
.sum-urgency.closing_soon { background: #ffe0b2; color: #e65100; }
.sum-urgency.near_midpoint { background: #fff9c4; color: #827717; }
.sum-urgency.approaching_midpoint { background: #f9fbe7; color: #558b2f; }
.sum-urgency.hold { background: #f0f0f0; color: #555; }

/* ── Bulk bar ── */
.bulk-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: #2c3e50;
  color: white;
  flex-shrink: 0;
}
.bulk-info { flex: 1; font-size: 0.85rem; }
.btn-bulk-action {
  padding: 5px 12px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}
.btn-bulk-action:hover:not(:disabled) { background: #a02020; }
.btn-bulk-action:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-bulk-action.btn-sale { background: #1a5c8b; }
.btn-bulk-action.btn-sale:hover:not(:disabled) { background: #206ea8; }
.btn-bulk-clear {
  padding: 5px 10px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 4px;
  color: rgba(255,255,255,0.8);
  font-size: 0.8rem;
  cursor: pointer;
}
.btn-bulk-action.btn-note { background: #4a6741; }
.btn-bulk-action.btn-note:hover { background: #5a7a50; }
.bulk-note-input {
  padding: 4px 8px;
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 4px;
  font-size: 0.82rem;
  background: rgba(255,255,255,0.15);
  color: white;
  width: 220px;
}
.bulk-note-input::placeholder { color: rgba(255,255,255,0.5); }

/* ── Content ── */
.content {
  display: flex;
  flex: 1;
  min-height: 0;
}
.content.panel-open .table-wrap { flex: 3; }

/* ── Footer ── */
.footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
  font-size: 0.8rem;
  color: #555;
  flex-shrink: 0;
}
.sep { color: #ccc; }
.filter-note { color: #888; }

/* ── Buttons ── */
.btn-primary {
  padding: 6px 14px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary:hover { background: #a02020; }

/* ── Delivery modal ── */
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.delivery-modal {
  background: white;
  border-radius: 8px;
  width: 680px;
  max-width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.dm-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px; border-bottom: 1px solid #e0e0e0;
}
.dm-header h2 { font-size: 1rem; font-weight: 600; }
.dm-header button { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #888; }
.dm-body { overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 20px; }
.dm-email { display: flex; flex-direction: column; gap: 8px; }
.dm-merchant { font-weight: 600; font-size: 0.9rem; color: #2c3e50; display: flex; align-items: center; gap: 12px; }
.dm-email-addr { font-weight: 400; font-size: 0.8rem; color: #888; }
.dm-text {
  width: 100%; font-family: inherit; font-size: 0.82rem;
  border: 1px solid #ddd; border-radius: 4px; padding: 10px;
  background: #fafafa; resize: vertical; color: #333;
}
.btn-copy {
  align-self: flex-start; padding: 5px 12px;
  background: #f0f0f0; border: 1px solid #ccc;
  border-radius: 4px; font-size: 0.8rem; cursor: pointer;
}
.btn-copy:hover { background: #e5e5e5; }
</style>
