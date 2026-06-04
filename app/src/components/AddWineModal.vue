<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>Add New Wine</h2>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <div class="col">
          <section class="section">
            <h3>Identity</h3>
            <div class="field">
              <label>Wine name <span class="req">*</span></label>
              <input v-model="form.name" type="text" placeholder="e.g. Brane Cantenac" />
            </div>
            <div class="field-row">
              <div class="field">
                <label>Category</label>
                <select v-model="form.category">
                  <option value="">— select —</option>
                  <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
              <div class="field">
                <label>Vintage</label>
                <input v-model="form.vintage" type="text" placeholder="2019 or NV" />
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Sub-region</label>
                <input v-model="form.sub_region" type="text" placeholder="e.g. Margaux, Meursault" />
              </div>
              <div class="field">
                <label>Country</label>
                <input v-model="form.super_region" type="text" placeholder="e.g. France" />
              </div>
            </div>
            <div class="field">
              <label>Grape variety</label>
              <input v-model="form.grape_variety" type="text" placeholder="e.g. Cabernet Sauvignon" />
            </div>
          </section>

          <section class="section">
            <h3>Purchase</h3>
            <div class="field-row">
              <div class="field">
                <label>Status</label>
                <select v-model="form.status">
                  <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>
              <div class="field">
                <label>Merchant</label>
                <select v-model="form.merchant" @change="onMerchantChange">
                  <option value="">— select —</option>
                  <option v-for="m in MERCHANTS" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Storage location</label>
                <select v-model="form.storage_location">
                  <option value="">— select —</option>
                  <option v-for="loc in STORAGE_LOCATIONS" :key="loc" :value="loc">{{ loc }}</option>
                </select>
              </div>
              <div class="field">
                <label>Bottles <span class="req">*</span></label>
                <input v-model.number="form.bottle_count" type="number" min="1" placeholder="6" />
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Format</label>
                <select v-model="form.bottle_format">
                  <option value="75cl">75cl</option>
                  <option value="150cl">150cl (Magnum)</option>
                  <option value="300cl">300cl (Double Mag)</option>
                </select>
              </div>
              <div class="field">
                <label>Cost/btl (£)</label>
                <input v-model.number="form.cost_per_bottle" type="number" step="0.01" min="0" placeholder="0.00" />
              </div>
            </div>
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
        </div>

        <div class="col">
          <section class="section">
            <h3>Drinking Window</h3>
            <div class="field-row">
              <div class="field">
                <label>Start</label>
                <input v-model="form.window_start" type="text" placeholder="NOW or year" />
              </div>
              <div class="field">
                <label>Mid</label>
                <input v-model="form.window_mid" type="text" placeholder="year" />
              </div>
              <div class="field">
                <label>End</label>
                <input v-model="form.window_end" type="text" placeholder="year" />
              </div>
            </div>
            <div class="urgency-badge" :style="urgencyStyle">{{ urgencyLabel }}</div>
          </section>

          <section class="section">
            <h3>Notes</h3>
            <div class="field">
              <textarea v-model="form.notes" rows="4" placeholder="Any notes…" />
            </div>
          </section>
        </div>
      </div>

      <div class="modal-footer">
        <span v-if="error" class="error-msg">{{ error }}</span>
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="save" :disabled="saving || !valid">
          {{ saving ? 'Saving…' : 'Add Wine' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { supabase } from '../supabase'
import { calcUrgency, URGENCY_LABEL, URGENCY_STYLE, STORAGE_LOCATIONS, MERCHANTS, CATEGORIES, STATUSES } from '../utils/urgency'

const emit = defineEmits(['close', 'saved'])

const saving = ref(false)
const error  = ref('')

const MERCHANT_TO_LOCATION = {
  'BBR':           'BBR Bond',
  'Justerini':     'Justerini Bond',
  'IG':            'IG Bond',
  'Fine and Rare': 'Fine and Rare',
  'Hatton Edwards':'Hatton Edwards',
  'Lay Wheeler':   'Lay Wheeler',
  'Robertson':     'Robertson Bond',
}

const form = ref({
  name: '', category: '', sub_region: '', super_region: '', grape_variety: '', vintage: '',
  status: 'in_storage', merchant: '', storage_location: '', bottle_count: null,
  bottle_format: '75cl', cost_per_bottle: null,
  invoice_no: '', invoice_date: '', delivery_date: '', expected_delivery: '',
  window_start: '', window_mid: '', window_end: '', notes: '',
})

function onMerchantChange() {
  const loc = MERCHANT_TO_LOCATION[form.value.merchant]
  if (loc) form.value.storage_location = loc
}

const valid = computed(() =>
  form.value.name.trim() &&
  form.value.bottle_count > 0
)

const urgency      = computed(() => calcUrgency(form.value.window_end, form.value.window_mid))
const urgencyLabel = computed(() => URGENCY_LABEL[urgency.value] || '—')
const urgencyStyle = computed(() => URGENCY_STYLE[urgency.value] || { background: '#f0f0f0', color: '#555' })

async function save() {
  saving.value = true
  error.value  = ''

  const vintage = parseInt(form.value.vintage)

  const payload = {
    name:              form.value.name.trim(),
    category:          form.value.category          || null,
    sub_region:        form.value.sub_region         || null,
    super_region:      form.value.super_region        || null,
    grape_variety:     form.value.grape_variety       || null,
    vintage:           isNaN(vintage) ? null : vintage,
    status:            form.value.status,
    merchant:          form.value.merchant           || null,
    storage_location:  form.value.storage_location   || null,
    bottle_count:      form.value.bottle_count,
    bottle_format:     form.value.bottle_format,
    cost_per_bottle:   form.value.cost_per_bottle    || null,
    invoice_no:        form.value.invoice_no         || null,
    invoice_date:      form.value.invoice_date       || null,
    delivery_date:     form.value.delivery_date      || null,
    expected_delivery: form.value.expected_delivery  || null,
    window_start:      form.value.window_start       || null,
    window_mid:        form.value.window_mid         || null,
    window_end:        form.value.window_end         || null,
    notes:             form.value.notes              || null,
    urgency:           urgency.value,
    paid:              !['ordered'].includes(form.value.status),
  }

  const { data, error: err } = await supabase
    .from('wines')
    .insert(payload)
    .select()
    .single()

  saving.value = false
  if (err) { error.value = err.message; return }
  emit('saved', data)
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 780px;
  max-width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}
.modal-header h2 { font-size: 1rem; font-weight: 600; }
.btn-close { border: none; background: none; font-size: 1.1rem; cursor: pointer; color: #888; }

.modal-body {
  display: flex; gap: 20px;
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}
.col { flex: 1; display: flex; flex-direction: column; gap: 16px; }

.section h3 { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #999; margin-bottom: 8px; }

.field { display: flex; flex-direction: column; gap: 3px; }
.field label { font-size: 0.75rem; color: #666; }
.req { color: #c62828; }
.field input, .field select, .field textarea {
  padding: 5px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.85rem;
  font-family: inherit;
}
.field textarea { resize: vertical; }
.field-row { display: flex; gap: 8px; }
.field-row .field { flex: 1; }

.urgency-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.modal-footer {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 8px; padding: 12px 20px;
  border-top: 1px solid #e0e0e0;
  background: #f9f9f9;
}
.error-msg { font-size: 0.8rem; color: #c62828; margin-right: auto; }

.btn-primary {
  padding: 7px 18px; background: #8B1A1A; color: white;
  border: none; border-radius: 4px; font-size: 0.875rem;
  cursor: pointer; font-weight: 500;
}
.btn-primary:hover:not(:disabled) { background: #a02020; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  padding: 7px 14px; background: white; border: 1px solid #ccc;
  border-radius: 4px; font-size: 0.875rem; cursor: pointer; color: #555;
}
.btn-secondary:hover { background: #f5f5f5; }
</style>
