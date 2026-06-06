<template>
  <div class="panel">
    <div class="panel-header">
      <div class="panel-title">
        <span class="panel-name">{{ wine.name }}</span>
        <span class="panel-vintage">{{ wine.vintage || 'NV' }}</span>
      </div>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>

    <div class="panel-body">
      <section class="section">
        <h3>Status & Location</h3>
        <div class="field">
          <label>Status</label>
          <select v-model="form.status">
            <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </div>
        <div class="field">
          <label>Storage location</label>
          <select v-model="form.storage_location">
            <option value="">— select —</option>
            <option v-for="loc in STORAGE_LOCATIONS" :key="loc" :value="loc">{{ loc }}</option>
          </select>
        </div>
      </section>

      <section class="section">
        <h3>Identity</h3>
        <div class="field-row">
          <div class="field">
            <label>Vintage</label>
            <input v-model.number="form.vintage" type="number" placeholder="e.g. 2015" />
          </div>
          <div class="field">
            <label>Grape variety</label>
            <input v-model="form.grape_variety" type="text" placeholder="e.g. Pinot Noir" />
          </div>
        </div>
        <div class="field">
          <label>Country</label>
          <input v-model="form.super_region" type="text" placeholder="e.g. France" />
        </div>
      </section>

      <section class="section">
        <h3>Purchase & Delivery</h3>
        <div class="field-row">
          <div class="field">
            <label>Invoice no.</label>
            <input v-model="form.invoice_no" type="text" />
          </div>
          <div class="field">
            <label>Invoice date</label>
            <input v-model="form.invoice_date" type="date" />
          </div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Delivery date</label>
            <input v-model="form.delivery_date" type="date" />
          </div>
          <div class="field">
            <label>Expected delivery</label>
            <input v-model="form.expected_delivery" type="text" placeholder="e.g. 2027 Q1" />
          </div>
        </div>
      </section>

      <section class="section" v-if="form.status === 'listed' || form.status === 'pending_listing'">
        <h3>Listing</h3>
        <div class="field">
          <label>Asking price per bottle (£)</label>
          <input v-model.number="form.value_per_bottle" type="number" step="0.01" min="0" />
        </div>
      </section>

      <section class="section" v-if="form.status === 'sold'">
        <h3>Sale</h3>
        <div class="field">
          <label>Sold price per bottle (£)</label>
          <input v-model.number="form.sold_price_per_bottle" type="number" step="0.01" min="0" />
        </div>
        <div class="field">
          <label>Sold date</label>
          <input v-model="form.sold_at" type="date" />
        </div>
        <div class="field">
          <label>Sold via</label>
          <input v-model="form.sold_via" type="text" placeholder="BBR, Justerini, private…" />
        </div>
      </section>

      <section class="section">
        <h3>Drinking Window</h3>
        <div class="field-row">
          <div class="field">
            <label>Start</label>
            <input v-model="form.window_start" type="text" placeholder="NOW or year" />
          </div>
          <div class="field">
            <label>Mid</label>
            <input v-model="form.window_mid" type="text" placeholder="NOW or year" />
          </div>
          <div class="field">
            <label>End</label>
            <input v-model="form.window_end" type="text" placeholder="year" />
          </div>
        </div>
        <div class="urgency-badge" :style="urgencyStyle">
          {{ urgencyLabel }}
        </div>
      </section>

      <section class="section">
        <h3>Valuation</h3>
        <div class="field-row">
          <div class="field">
            <label>Cost/btl (£)</label>
            <input :value="wine.cost_per_bottle" disabled type="number" />
          </div>
          <div class="field">
            <label>Value/btl (£)</label>
            <input v-model.number="form.value_per_bottle" type="number" step="0.01" min="0" />
          </div>
        </div>
        <div class="field-row info-row" v-if="wine.bottle_count">
          <span>{{ wine.bottle_count }} bottles</span>
          <span v-if="form.value_per_bottle">
            Total value: <strong>£{{ Math.round(form.value_per_bottle * wine.bottle_count).toLocaleString() }}</strong>
          </span>
          <span v-if="wine.cost_per_bottle && form.value_per_bottle">
            P&amp;L: <strong :class="pnl >= 0 ? 'positive' : 'negative'">
              £{{ Math.round(pnl).toLocaleString() }}
            </strong>
          </span>
        </div>
      </section>

      <section class="section">
        <h3>Working notes</h3>
        <div class="field">
          <textarea v-model="form.working_notes" rows="2" placeholder="e.g. possible sale, possible delivery…" />
        </div>
      </section>

      <section class="section">
        <h3>Notes</h3>
        <div class="field">
          <textarea v-model="form.notes" rows="3" placeholder="Any notes…" />
        </div>
      </section>

      <section class="section">
        <h3>Tastings</h3>
        <div v-if="tastingsLoading" class="tastings-loading">Loading…</div>
        <div v-else-if="tastings.length">
          <div class="tastings-aggregate">
            <span class="agg-formula">{{ aggregateFormula }}</span>
            <span class="agg-equals"> = </span>
            <strong class="agg-avg">{{ avgScore }}</strong>
          </div>
          <div class="tasting-list">
            <div v-for="t in tastings" :key="t.id" class="tasting-row">
              <span class="t-date">{{ formatDate(t.drunk_at) }}</span>
              <span class="t-score">{{ t.score != null ? t.score + '/10' : '—' }}</span>
              <span v-if="t.fault" class="t-fault" :title="t.fault_note">🚫</span>
              <span class="t-notes">{{ t.notes || '' }}</span>
            </div>
          </div>
        </div>
        <p v-else class="no-tastings">No tastings recorded yet</p>
      </section>
    </div>

    <div class="panel-footer">
      <span v-if="saved" class="saved-msg">Saved</span>
      <span v-if="error" class="error-msg">{{ error }}</span>
      <button class="btn-secondary" @click="$emit('close')">Cancel</button>
      <button class="btn-primary" @click="save" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { supabase } from '../supabase'
import { calcUrgency, URGENCY_LABEL, URGENCY_STYLE, STORAGE_LOCATIONS, STATUSES } from '../utils/urgency'

const props = defineProps({ wine: Object })
const emit  = defineEmits(['close', 'saved'])

const saving          = ref(false)
const saved           = ref(false)
const error           = ref('')
const tastings        = ref([])
const tastingsLoading = ref(false)

const form = ref(toForm(props.wine))

watch(() => props.wine, w => {
  form.value = toForm(w)
  if (w?.id) loadTastings(w.id)
})

async function loadTastings(wineId) {
  tastingsLoading.value = true
  tastings.value = []
  const { data, error: err } = await supabase
    .from('tastings')
    .select('*')
    .eq('wine_id', wineId)
    .order('drunk_at', { ascending: false })
  tastingsLoading.value = false
  if (!err) tastings.value = data || []
}

const tastingScores = computed(() =>
  tastings.value.map(t => t.score).filter(s => s != null).map(Number)
)

const aggregateFormula = computed(() => {
  if (!tastingScores.value.length) return ''
  return tastingScores.value.join('+') + '/' + tastingScores.value.length
})

const avgScore = computed(() => {
  if (!tastingScores.value.length) return null
  const avg = tastingScores.value.reduce((a, b) => a + b, 0) / tastingScores.value.length
  return avg % 1 === 0 ? avg.toFixed(0) : avg.toFixed(1)
})

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}.${m}.${y}`
}

// Load tastings on first mount
if (props.wine?.id) loadTastings(props.wine.id)

function toForm(w) {
  return {
    vintage:              w.vintage               ?? null,
    status:               w.status               || 'in_storage',
    storage_location:     w.storage_location      || '',
    grape_variety:        w.grape_variety          || '',
    super_region:         w.super_region           || '',
    invoice_no:           w.invoice_no             || '',
    invoice_date:         w.invoice_date           || '',
    delivery_date:        w.delivery_date          || '',
    expected_delivery:    w.expected_delivery      || '',
    value_per_bottle:     w.value_per_bottle      ?? null,
    sold_price_per_bottle:w.sold_price_per_bottle ?? null,
    sold_at:              w.sold_at               || '',
    sold_via:             w.sold_via              || '',
    window_start:         w.window_start          || '',
    window_mid:           w.window_mid            || '',
    window_end:           w.window_end            || '',
    working_notes:        w.working_notes          || '',
    notes:                w.notes                 || '',
  }
}

const urgency      = computed(() => calcUrgency(form.value.window_end, form.value.window_mid))
const urgencyLabel = computed(() => URGENCY_LABEL[urgency.value] || '—')
const urgencyStyle = computed(() => URGENCY_STYLE[urgency.value] || { background: '#f0f0f0', color: '#555' })

const pnl = computed(() =>
  (form.value.value_per_bottle - props.wine.cost_per_bottle) * (props.wine.bottle_count || 0)
)

async function save() {
  saving.value = true
  error.value  = ''
  saved.value  = false

  const payload = {
    vintage:              form.value.vintage               || null,
    status:               form.value.status,
    storage_location:     form.value.storage_location     || null,
    grape_variety:        form.value.grape_variety         || null,
    super_region:         form.value.super_region          || null,
    invoice_no:           form.value.invoice_no            || null,
    invoice_date:         form.value.invoice_date          || null,
    delivery_date:        form.value.delivery_date         || null,
    expected_delivery:    form.value.expected_delivery     || null,
    value_per_bottle:     form.value.value_per_bottle      || null,
    sold_price_per_bottle:form.value.sold_price_per_bottle || null,
    sold_at:              form.value.sold_at               || null,
    sold_via:             form.value.sold_via              || null,
    window_start:         form.value.window_start          || null,
    window_mid:           form.value.window_mid            || null,
    window_end:           form.value.window_end            || null,
    working_notes:        form.value.working_notes         || null,
    notes:                form.value.notes                 || null,
    urgency:              urgency.value,
  }

  const { data, error: err } = await supabase
    .from('wines')
    .update(payload)
    .eq('id', props.wine.id)
    .select()
    .single()

  saving.value = false
  if (err) { error.value = err.message; return }
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
  emit('saved', data)
}
</script>

<style scoped>
.panel {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-left: 1px solid #e0e0e0;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f9f9f9;
  gap: 8px;
}
.panel-title { display: flex; flex-direction: column; gap: 2px; }
.panel-name  { font-weight: 600; font-size: 0.95rem; line-height: 1.3; }
.panel-vintage { font-size: 0.8rem; color: #888; }
.btn-close   { border: none; background: none; font-size: 1.1rem; cursor: pointer; color: #888; flex-shrink: 0; }

.panel-body  { flex: 1; overflow-y: auto; padding: 12px 16px; display: flex; flex-direction: column; gap: 16px; }

.section h3  { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #999; margin-bottom: 8px; }

.field       { display: flex; flex-direction: column; gap: 3px; }
.field label { font-size: 0.75rem; color: #666; }
.field input, .field select, .field textarea {
  padding: 5px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: inherit;
}
.field input:disabled { background: #f5f5f5; color: #888; }
.field textarea { resize: vertical; }

.field-row   { display: flex; gap: 8px; }
.field-row .field { flex: 1; }

.info-row    { font-size: 0.8rem; color: #555; align-items: center; flex-wrap: wrap; gap: 12px; }
.positive    { color: #2e7d32; }
.negative    { color: #c62828; }

.urgency-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.panel-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid #e0e0e0;
  background: #f9f9f9;
}
.saved-msg  { font-size: 0.8rem; color: #2e7d32; margin-right: auto; }
.error-msg  { font-size: 0.8rem; color: #c62828; margin-right: auto; }

.btn-primary {
  padding: 6px 16px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary:hover:not(:disabled) { background: #a02020; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 6px 14px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  color: #555;
}
.btn-secondary:hover { background: #f5f5f5; }

.tastings-loading { font-size: 0.8rem; color: #aaa; }

.tastings-aggregate {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-bottom: 8px;
  font-family: monospace;
  font-size: 0.85rem;
}
.agg-formula { color: #666; }
.agg-equals  { color: #999; }
.agg-avg     { font-size: 1rem; color: #8B1A1A; }

.tasting-list { display: flex; flex-direction: column; gap: 4px; }

.tasting-row {
  display: grid;
  grid-template-columns: 70px 48px 20px 1fr;
  gap: 6px;
  align-items: start;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.78rem;
}
.tasting-row:last-child { border-bottom: none; }
.t-date  { color: #888; white-space: nowrap; }
.t-score { font-weight: 600; color: #2c3e50; }
.t-fault { font-size: 0.75rem; cursor: default; }
.t-notes { color: #555; white-space: pre-wrap; word-break: break-word; }

.no-tastings { font-size: 0.8rem; color: #aaa; }
</style>
