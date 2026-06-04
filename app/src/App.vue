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
      <MultiSelect
        placeholder="Status"
        :options="STATUSES"
        v-model="filters.status"
      />
      <MultiSelect
        placeholder="Location"
        :options="locationOptions"
        v-model="filters.location"
      />
      <MultiSelect
        placeholder="Urgency"
        :options="urgencyOptions"
        v-model="filters.urgency"
      />
      <button v-if="anyFilter" class="btn-clear" @click="clearFilters">Clear all</button>
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
      <button class="btn-bulk-action" @click="requestDelivery">📦 Request delivery</button>
      <button class="btn-bulk-action btn-sale" @click="markForSale" :disabled="bulkSaving">🏷 Mark for sale</button>
      <button class="btn-bulk-clear" @click="clearSelection">✕ Clear</button>
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
const filters      = ref({ search: '', status: [], location: [], urgency: [] })
const selectedWines = ref([])
const wineTableRef  = ref(null)
const showSummary   = ref(true)
const deliveryModal = ref(null)
const bulkSaving    = ref(false)
const cellarConfig  = ref(null)

async function loadConfig() {
  try {
    const { data } = await supabase.from('settings').select('value').eq('key', 'cellar_config').single()
    if (data) cellarConfig.value = data.value
  } catch { /* config missing, use defaults */ }
}

const locationOptions = computed(() => {
  const s = new Set(wines.value.map(w => w.storage_location).filter(Boolean))
  return [...s].sort().map(l => ({ value: l, label: l }))
})

const urgencyOptions = [
  { value: 'past_window',          label: 'Past window' },
  { value: 'closing_soon',         label: 'Closing soon' },
  { value: 'near_midpoint',        label: 'Near midpoint' },
  { value: 'approaching_midpoint', label: 'Approaching mid' },
  { value: 'hold',                 label: 'Hold' },
]

const anyFilter = computed(() =>
  filters.value.search !== '' ||
  filters.value.status.length > 0 ||
  filters.value.location.length > 0 ||
  filters.value.urgency.length > 0
)

function clearFilters() {
  filters.value = { search: '', status: [], location: [], urgency: [] }
}

const filteredWines = computed(() => {
  let r = wines.value
  const { search, status, location, urgency } = filters.value
  if (search) {
    const q = search.toLowerCase()
    r = r.filter(w =>
      (w.name         || '').toLowerCase().includes(q) ||
      (w.sub_region   || '').toLowerCase().includes(q) ||
      (w.category     || '').toLowerCase().includes(q) ||
      (w.grape_variety|| '').toLowerCase().includes(q) ||
      (w.super_region || '').toLowerCase().includes(q) ||
      String(w.vintage || '').includes(q)
    )
  }
  if (status.length)   r = r.filter(w => status.includes(w.status))
  if (location.length) r = r.filter(w => location.includes(w.storage_location))
  if (urgency.length)  r = r.filter(w => urgency.includes(w.urgency))
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

  // Update storage_location to In transit for all selected wines
  const ids = selectedWines.value.map(w => w.id)
  await supabase.from('wines').update({ storage_location: 'In transit' }).in('id', ids)
  for (const id of ids) {
    const idx = wines.value.findIndex(w => w.id === id)
    if (idx !== -1) wines.value[idx] = { ...wines.value[idx], storage_location: 'In transit' }
  }

  deliveryModal.value = { emails }
  clearSelection()
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
  max-width: 280px;
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
}
.filter-select {
  padding: 5px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
  background: white;
}

.content {
  display: flex;
  flex: 1;
  min-height: 0;
}
.content.panel-open .table-wrap { flex: 3; }

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
.sum-stat { }
.sum-urgency { padding: 1px 6px; border-radius: 10px; font-size: 0.75rem; }
.sum-urgency.past_window { background: #ffcccc; color: #b71c1c; }
.sum-urgency.closing_soon { background: #ffe0b2; color: #e65100; }
.sum-urgency.near_midpoint { background: #fff9c4; color: #827717; }
.sum-urgency.approaching_midpoint { background: #f9fbe7; color: #558b2f; }
.sum-urgency.hold { background: #f0f0f0; color: #555; }

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
