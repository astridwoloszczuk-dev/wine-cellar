<template>
  <div class="wine-list-page">
    <header class="list-header">
      <div class="header-top">
        <span class="logo">🍷</span>
        <h1>Home Cellar</h1>
        <button class="btn-signout" @click="$emit('sign-out')" title="Sign out">↩</button>
      </div>
      <div class="search-wrap">
        <input
          v-model="search"
          type="search"
          placeholder="Search wine, region…"
          class="search-input"
          autocomplete="off"
          autocorrect="off"
          spellcheck="false"
        />
      </div>
    </header>

    <div class="list-body">
      <div v-if="loading" class="state-msg">Loading wines…</div>
      <div v-else-if="!filteredWines.length" class="state-msg">No wines found</div>

      <div v-else class="cards">
        <button
          v-for="wine in filteredWines"
          :key="wine.id"
          class="wine-card"
          @click="selectedWine = wine"
        >
          <div class="card-main">
            <div class="card-title">
              <span class="card-name">{{ wine.name }}</span>
              <span class="card-vintage">{{ wine.vintage || 'NV' }}</span>
            </div>
            <span class="card-category">{{ wine.category }}</span>
          </div>
          <div class="card-meta">
            <span class="card-bottles">{{ wine.bottle_count ?? 0 }} {{ wine.bottle_count === 1 ? 'bottle' : 'bottles' }}</span>
            <span class="card-score" v-if="avgScore(wine.id) !== null">
              {{ avgScore(wine.id) }} ★
            </span>
            <span class="card-score no-score" v-else>no tastings yet</span>
          </div>
        </button>
      </div>
    </div>

    <div class="list-footer">
      {{ filteredWines.length }} wine{{ filteredWines.length !== 1 ? 's' : '' }}
      · {{ totalBottles }} bottle{{ totalBottles !== 1 ? 's' : '' }}
    </div>

    <WineDetail
      v-if="selectedWine"
      :wine="selectedWine"
      :tastings="tastings"
      @close="selectedWine = null"
      @updated="onWineUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supabase } from '../supabase'
import WineDetail from './WineDetail.vue'

defineEmits(['sign-out'])

const wines        = ref([])
const tastings     = ref([])
const loading      = ref(true)
const search       = ref('')
const selectedWine = ref(null)

const filteredWines = computed(() => {
  if (!search.value.trim()) return wines.value
  const q = search.value.toLowerCase()
  return wines.value.filter(w =>
    (w.name             || '').toLowerCase().includes(q) ||
    (w.sub_region       || '').toLowerCase().includes(q) ||
    (w.category         || '').toLowerCase().includes(q) ||
    (w.merchant         || '').toLowerCase().includes(q) ||
    (w.storage_location || '').toLowerCase().includes(q) ||
    (w.notes            || '').toLowerCase().includes(q) ||
    (w.grape_variety    || '').toLowerCase().includes(q) ||
    (w.super_region     || '').toLowerCase().includes(q) ||
    String(w.vintage    || '').includes(q)
  )
})

const totalBottles = computed(() =>
  filteredWines.value.reduce((s, w) => s + (w.bottle_count ?? 0), 0)
)

function avgScore(wineId) {
  const scores = tastings.value
    .filter(t => t.wine_id === wineId && t.score != null)
    .map(t => Number(t.score))
  if (!scores.length) return null
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length
  return avg % 1 === 0 ? avg.toFixed(0) : avg.toFixed(1)
}

async function loadData() {
  loading.value = true
  try {
    const [winesRes, tastingsRes] = await Promise.all([
      supabase
        .from('wines')
        .select('*')
        .eq('storage_location', 'Wien')
        .in('status', ['in_storage'])
        .order('name'),
      supabase
        .from('tastings')
        .select('*')
        .order('drunk_at', { ascending: false }),
    ])

    if (winesRes.error) throw winesRes.error
    if (tastingsRes.error) throw tastingsRes.error

    wines.value    = winesRes.data    || []
    tastings.value = tastingsRes.data || []
  } catch (err) {
    console.error('Failed to load data:', err)
  } finally {
    loading.value = false
  }
}

function onWineUpdated(updatedWine) {
  const idx = wines.value.findIndex(w => w.id === updatedWine.id)
  if (idx !== -1) {
    if (updatedWine.status === 'consumed') {
      wines.value.splice(idx, 1)
      selectedWine.value = null
    } else {
      wines.value[idx] = updatedWine
      if (selectedWine.value?.id === updatedWine.id) {
        selectedWine.value = updatedWine
      }
    }
  }
}

onMounted(loadData)
</script>

<style scoped>
.wine-list-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f6fa;
  overflow: hidden;
}

.list-header {
  background: #8B1A1A;
  color: white;
  flex-shrink: 0;
  padding-bottom: 12px;
  padding-top: env(safe-area-inset-top, 0);
}
.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px 8px;
}
.logo { font-size: 1.4rem; }
h1 {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.btn-signout {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.9rem;
  cursor: pointer;
  min-height: 44px;
  min-width: 44px;
}
.btn-signout:active { background: rgba(255,255,255,0.25); }

.search-wrap { padding: 0 12px; }
.search-input {
  width: 100%;
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  background: rgba(255,255,255,0.18);
  color: white;
  outline: none;
  -webkit-appearance: none;
}
.search-input::placeholder { color: rgba(255,255,255,0.6); }
.search-input:focus { background: rgba(255,255,255,0.25); }

.list-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.state-msg {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 1rem;
  padding: 48px 0;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.wine-card {
  background: white;
  border-radius: 12px;
  padding: 14px 16px;
  border: none;
  cursor: pointer;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 72px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  width: 100%;
  -webkit-tap-highlight-color: transparent;
}
.wine-card:active { background: #fdf5f5; }

.card-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.card-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.card-name {
  font-size: 1rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.3;
  flex: 1;
}
.card-vintage {
  font-size: 0.875rem;
  color: #888;
  font-weight: 500;
  flex-shrink: 0;
}
.card-category {
  font-size: 0.8rem;
  color: #999;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-bottles {
  font-size: 0.85rem;
  color: #666;
}
.card-score {
  font-size: 0.9rem;
  font-weight: 700;
  color: #8B1A1A;
}
.card-score.no-score {
  font-size: 0.78rem;
  font-weight: 400;
  color: #bbb;
}

.list-footer {
  text-align: center;
  padding: 8px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  font-size: 0.8rem;
  color: #aaa;
  background: white;
  border-top: 1px solid #e8e8e8;
  flex-shrink: 0;
}
</style>
