<template>
  <div class="ms-wrap" ref="root">
    <button
      class="ms-trigger"
      :class="{ active: modelValue.length > 0 }"
      @click="open = !open"
    >
      {{ triggerLabel }}
      <span class="ms-caret">▾</span>
    </button>

    <div v-if="open" class="ms-dropdown">
      <label class="ms-option ms-all">
        <input type="checkbox" :checked="allSelected" :indeterminate="someSelected" @change="toggleAll" />
        <span>All</span>
      </label>
      <hr class="ms-divider" />
      <label v-for="opt in options" :key="opt.value" class="ms-option">
        <input type="checkbox" :value="opt.value" :checked="modelValue.includes(opt.value)" @change="toggle(opt.value)" />
        <span>{{ opt.label }}</span>
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  placeholder: { type: String, required: true },
  options:     { type: Array,  required: true },
  modelValue:  { type: Array,  default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const root = ref(null)

const allSelected  = computed(() => props.modelValue.length === 0)
const someSelected = computed(() => props.modelValue.length > 0 && props.modelValue.length < props.options.length)

const triggerLabel = computed(() => {
  if (props.modelValue.length === 0) return props.placeholder
  if (props.modelValue.length === 1) {
    const opt = props.options.find(o => o.value === props.modelValue[0])
    return opt ? opt.label : props.modelValue[0]
  }
  return `${props.placeholder} (${props.modelValue.length})`
})

function toggle(value) {
  const current = [...props.modelValue]
  const idx = current.indexOf(value)
  if (idx === -1) current.push(value)
  else current.splice(idx, 1)
  emit('update:modelValue', current)
}

function toggleAll() {
  emit('update:modelValue', [])
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<style scoped>
.ms-wrap {
  position: relative;
}

.ms-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
  color: #444;
  white-space: nowrap;
}
.ms-trigger.active {
  border-color: #8B1A1A;
  color: #8B1A1A;
  background: #fff5f5;
}
.ms-caret { font-size: 0.7rem; color: #999; }

.ms-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  z-index: 200;
  padding: 4px 0;
  max-height: 280px;
  overflow-y: auto;
}

.ms-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  color: #2c3e50;
  user-select: none;
}
.ms-option:hover { background: #f5f5f5; }
.ms-option.ms-all { font-weight: 600; color: #555; }
.ms-option input[type="checkbox"] { cursor: pointer; accent-color: #8B1A1A; }

.ms-divider { margin: 4px 0; border: none; border-top: 1px solid #eee; }
</style>
