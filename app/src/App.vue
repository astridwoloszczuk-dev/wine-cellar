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
      <input v-model="filters.search" placeholder="Search wine, region…" class="filter-search" />
      <select v-model="filters.status" class="filter-select">
        <option value="">All statuses</option>
        <option value="in_storage">In storage</option>
        <option value="pending_listing">Pending listing</option>
        <option value="listed">Listed</option>
        <option value="sold">Sold</option>
        <option value="consumed">Consumed</option>
      </select>
      <select v-model="filters.location" class="filter-select">
        <option value="">All locations</option>
        <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
      </select>
      <select v-model="filters.urgency" class="filter-select">
        <option value="">All urgency</option>
        <option value="past_window">Past window</option>
        <option value="closing_soon">Closing soon</option>
        <option value="near_midpoint">Near midpoint</option>
        <option value="approaching_midpoint">Approaching mid</option>
        <option value="hold">Hold</option>
      </select>
      <button v-if="anyFilter" class="btn-clear" @click="clearFilters">Clear</button>
    </div>

    <div class="content" :class="{ 'panel-open': selectedWine }">
      <WineTable
        :wines="filteredWines"
        :loading="loading"
        :selectedId="selectedWine?.id"
        @select="onSelect"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supabase } from './supabase'
import { calcUrgency } from './utils/urgency'
import WineTable from './components/WineTable.vue'
import WinePanel from './components/WinePanel.vue'
import AddWineModal from './components/AddWineModal.vue'
import LoginScreen from './components/LoginScreen.vue'

const session = ref(null)

const wines        = ref([])
const loading      = ref(true)
const selectedWine = ref(null)
const showAddModal = ref(false)
const filters      = ref({ search: '', status: '', location: '', urgency: '' })

const locations = computed(() => {
  const s = new Set(wines.value.map(w => w.storage_location).filter(Boolean))
  return [...s].sort()
})

const anyFilter = computed(() =>
  Object.values(filters.value).some(v => v !== '')
)

function clearFilters() {
  filters.value = { search: '', status: '', location: '', urgency: '' }
}

const filteredWines = computed(() => {
  let r = wines.value
  const { search, status, location, urgency } = filters.value
  if (search) {
    const q = search.toLowerCase()
    r = r.filter(w =>
      (w.name       || '').toLowerCase().includes(q) ||
      (w.sub_region || '').toLowerCase().includes(q) ||
      (w.category   || '').toLowerCase().includes(q) ||
      String(w.vintage || '').includes(q)
    )
  }
  if (status)   r = r.filter(w => w.status           === status)
  if (location) r = r.filter(w => w.storage_location === location)
  if (urgency)  r = r.filter(w => w.urgency          === urgency)
  return r
})

const stats = computed(() => ({
  lots:    filteredWines.value.length,
  bottles: filteredWines.value.reduce((s, w) => s + (w.bottle_count || 0), 0),
  value:   filteredWines.value.reduce((s, w) => s + (w.value_per_bottle || 0) * (w.bottle_count || 0), 0)
}))

function withUrgency(w) {
  return { ...w, urgency: w.window_end ? calcUrgency(w.window_end, w.window_mid) : (w.urgency || null) }
}

async function loadWines() {
  loading.value = true
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
  wines.value = all.map(withUrgency)
  loading.value = false
}

function onSelect(wine) {
  selectedWine.value = wine
}

function onSaved(updated) {
  const u = withUrgency(updated)
  const idx = wines.value.findIndex(w => w.id === u.id)
  if (idx !== -1) wines.value[idx] = u
  selectedWine.value = u
}

function onAdded(newWine) {
  wines.value.unshift(withUrgency(newWine))
  showAddModal.value = false
}

async function signOut() {
  await supabase.auth.signOut()
  session.value = null
}

onMounted(async () => {
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
</style>
