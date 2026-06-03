<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-sheet">
      <div class="sheet-handle"></div>

      <div class="sheet-header">
        <h2>Log a bottle</h2>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>

      <div class="sheet-body">
        <div class="field">
          <label>Date</label>
          <input v-model="form.drunk_at" type="date" />
        </div>

        <div class="field">
          <label>Score</label>
          <div class="score-grid">
            <button
              v-for="n in 10"
              :key="n"
              class="score-btn"
              :class="{ selected: form.score === n }"
              @click="form.score = n"
              type="button"
            >{{ n }}</button>
          </div>
        </div>

        <div class="field fault-field">
          <label class="fault-label">
            <span>Fault</span>
            <div class="toggle-wrap">
              <input
                id="fault-toggle"
                v-model="form.fault"
                type="checkbox"
                class="toggle-input"
              />
              <label for="fault-toggle" class="toggle-track">
                <span class="toggle-thumb"></span>
              </label>
            </div>
          </label>
          <input
            v-if="form.fault"
            v-model="form.fault_note"
            type="text"
            placeholder="Describe the fault…"
            class="fault-note-input"
          />
        </div>

        <div class="field">
          <label>Notes</label>
          <textarea
            v-model="form.notes"
            rows="3"
            placeholder="Tasting notes…"
          ></textarea>
        </div>
      </div>

      <div class="sheet-footer">
        <p v-if="error" class="error">{{ error }}</p>
        <button
          class="btn-log"
          @click="submit"
          :disabled="submitting"
        >
          {{ submitting ? 'Logging…' : 'Log bottle' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { supabase } from '../supabase'

const props = defineProps({
  wine: { type: Object, required: true }
})
const emit = defineEmits(['close', 'logged'])

const today = new Date().toISOString().split('T')[0]

const form = ref({
  drunk_at:   today,
  score:      null,
  fault:      false,
  fault_note: '',
  notes:      '',
})

const submitting = ref(false)
const error      = ref('')

async function submit() {
  error.value = ''
  submitting.value = true

  try {
    const { error: insertErr } = await supabase.from('tastings').insert({
      wine_id:    props.wine.id,
      drunk_at:   form.value.drunk_at,
      score:      form.value.score,
      fault:      form.value.fault,
      fault_note: form.value.fault ? (form.value.fault_note || null) : null,
      notes:      form.value.notes || null,
    })

    if (insertErr) throw insertErr

    const newCount = (props.wine.bottle_count || 0) - 1
    const update = { bottle_count: newCount }
    if (newCount <= 0) update.status = 'consumed'

    const { error: updateErr } = await supabase
      .from('wines')
      .update(update)
      .eq('id', props.wine.id)

    if (updateErr) throw updateErr

    emit('logged', { ...props.wine, ...update })
  } catch (err) {
    error.value = err.message || 'Something went wrong'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: flex-end;
  z-index: 200;
}

.modal-sheet {
  background: white;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.sheet-handle {
  width: 40px;
  height: 4px;
  background: #ddd;
  border-radius: 2px;
  margin: 12px auto 0;
  flex-shrink: 0;
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  flex-shrink: 0;
}
.sheet-header h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #2c3e50;
}
.btn-close {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #888;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sheet-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.field > label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #888;
}
.field input[type="date"],
.field textarea {
  padding: 12px 14px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  outline: none;
  background: #fafafa;
  -webkit-appearance: none;
  width: 100%;
}
.field input[type="date"]:focus,
.field textarea:focus {
  border-color: #8B1A1A;
  background: white;
}
.field textarea { resize: none; }

/* Score grid */
.score-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.score-btn {
  height: 52px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  background: #fafafa;
  font-size: 1.1rem;
  font-weight: 600;
  color: #444;
  cursor: pointer;
  transition: background 0.1s, border-color 0.1s, color 0.1s;
}
.score-btn.selected {
  background: #8B1A1A;
  border-color: #8B1A1A;
  color: white;
}
.score-btn:active { opacity: 0.75; }

/* Fault toggle */
.fault-field { gap: 10px; }
.fault-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #888;
  cursor: default;
}
.toggle-wrap { position: relative; }
.toggle-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}
.toggle-track {
  display: flex;
  align-items: center;
  width: 50px;
  height: 28px;
  background: #e0e0e0;
  border-radius: 14px;
  cursor: pointer;
  transition: background 0.2s;
  padding: 3px;
}
.toggle-input:checked + .toggle-track {
  background: #8B1A1A;
}
.toggle-thumb {
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-input:checked + .toggle-track .toggle-thumb {
  transform: translateX(22px);
}
.fault-note-input {
  padding: 12px 14px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  outline: none;
  background: #fafafa;
  width: 100%;
}
.fault-note-input:focus {
  border-color: #8B1A1A;
  background: white;
}

.sheet-footer {
  padding: 12px 20px 20px;
  flex-shrink: 0;
  border-top: 1px solid #f0f0f0;
}
.error {
  color: #c0392b;
  font-size: 0.875rem;
  margin-bottom: 10px;
}
.btn-log {
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
.btn-log:active:not(:disabled) { background: #6d1414; }
.btn-log:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
