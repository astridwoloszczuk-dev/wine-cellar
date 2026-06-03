<template>
  <div class="detail-overlay">
    <div class="detail-header">
      <button class="btn-back" @click="$emit('close')">
        <span class="back-arrow">←</span> Back
      </button>
    </div>

    <div class="detail-body">
      <div class="wine-heading">
        <h1 class="wine-name">{{ wine.name }}</h1>
        <span class="wine-vintage">{{ wine.vintage || 'NV' }}</span>
      </div>

      <div class="info-grid">
        <div class="info-item" v-if="wine.category">
          <span class="info-label">Category</span>
          <span class="info-value">{{ wine.category }}</span>
        </div>
        <div class="info-item" v-if="wine.sub_region">
          <span class="info-label">Region</span>
          <span class="info-value">{{ wine.sub_region }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Bottles</span>
          <span class="info-value">{{ wine.bottle_count ?? 0 }}</span>
        </div>
        <div class="info-item" v-if="wine.window_start || wine.window_end">
          <span class="info-label">Drinking window</span>
          <span class="info-value">
            {{ wine.window_start || '?' }}–{{ wine.window_end || '?' }}
          </span>
        </div>
      </div>

      <section class="tastings-section">
        <h2 class="section-title">Tastings</h2>

        <div v-if="wineTastings.length" class="tastings-aggregate">
          <span class="aggregate-formula">{{ aggregateFormula }}</span>
          <span class="aggregate-avg">= {{ avgScore }}</span>
        </div>

        <div v-if="wineTastings.length" class="tastings-list">
          <div
            v-for="t in wineTastings"
            :key="t.id"
            class="tasting-card"
          >
            <div class="tasting-header">
              <span class="tasting-date">{{ formatDate(t.drunk_at) }}</span>
              <span class="tasting-score">{{ t.score != null ? t.score + ' / 10' : '—' }}</span>
            </div>
            <p v-if="t.notes" class="tasting-notes">{{ t.notes }}</p>
            <div v-if="t.fault" class="tasting-fault">
              🚫 Fault<span v-if="t.fault_note">: {{ t.fault_note }}</span>
            </div>
          </div>
        </div>

        <p v-else class="no-tastings">No tastings recorded yet</p>
      </section>
    </div>

    <div class="detail-footer">
      <button
        class="btn-drink"
        @click="showDrinkModal = true"
        :disabled="(wine.bottle_count ?? 0) === 0"
      >
        🍷 Drink a bottle
      </button>
    </div>

    <DrinkModal
      v-if="showDrinkModal"
      :wine="currentWine"
      @close="showDrinkModal = false"
      @logged="onLogged"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DrinkModal from './DrinkModal.vue'

const props = defineProps({
  wine:     { type: Object, required: true },
  tastings: { type: Array,  default: () => [] },
})
const emit = defineEmits(['close', 'updated'])

const showDrinkModal = ref(false)
const currentWine    = ref({ ...props.wine })

watch(() => props.wine, w => { currentWine.value = { ...w } })

const wineTastings = computed(() =>
  props.tastings
    .filter(t => t.wine_id === props.wine.id)
    .slice()
    .sort((a, b) => (b.drunk_at || '').localeCompare(a.drunk_at || ''))
)

const scores = computed(() => wineTastings.value.map(t => t.score).filter(s => s != null))

const aggregateFormula = computed(() => {
  if (!scores.value.length) return ''
  return scores.value.join('+') + '/' + scores.value.length
})

const avgScore = computed(() => {
  if (!scores.value.length) return null
  const avg = scores.value.reduce((a, b) => a + Number(b), 0) / scores.value.length
  return avg % 1 === 0 ? avg.toFixed(0) : avg.toFixed(1)
})

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}.${m}.${y}`
}

function onLogged(updatedWine) {
  currentWine.value = updatedWine
  showDrinkModal.value = false
  emit('updated', updatedWine)
}
</script>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: #f5f6fa;
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  padding-top: max(12px, env(safe-area-inset-top));
  background: #8B1A1A;
  flex-shrink: 0;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  padding: 8px 4px;
  min-height: 44px;
}
.back-arrow { font-size: 1.2rem; }

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.wine-heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.wine-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.25;
}
.wine-vintage {
  font-size: 1rem;
  color: #888;
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.info-item {
  background: white;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.info-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #aaa;
  font-weight: 600;
}
.info-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2c3e50;
}

.tastings-section { display: flex; flex-direction: column; gap: 12px; }
.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #999;
  font-weight: 700;
}

.tastings-aggregate {
  background: white;
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-family: monospace;
}
.aggregate-formula { font-size: 1rem; color: #555; }
.aggregate-avg { font-size: 1.25rem; font-weight: 700; color: #8B1A1A; }

.tastings-list { display: flex; flex-direction: column; gap: 8px; }
.tasting-card {
  background: white;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.tasting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tasting-date { font-size: 0.875rem; color: #888; }
.tasting-score { font-size: 0.95rem; font-weight: 700; color: #2c3e50; }
.tasting-notes { font-size: 0.9rem; color: #444; line-height: 1.45; }
.tasting-fault { font-size: 0.875rem; color: #c0392b; }

.no-tastings {
  background: white;
  border-radius: 10px;
  padding: 20px 16px;
  text-align: center;
  color: #aaa;
  font-size: 0.9rem;
}

.detail-footer {
  padding: 12px 16px;
  padding-bottom: max(20px, env(safe-area-inset-bottom));
  background: white;
  border-top: 1px solid #e8e8e8;
  flex-shrink: 0;
}
.btn-drink {
  width: 100%;
  padding: 16px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  min-height: 56px;
}
.btn-drink:active:not(:disabled) { background: #6d1414; }
.btn-drink:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
