<template>
  <div class="table-wrap">
    <div v-if="loading" class="loading">Loading wines…</div>
    <AgGridVue
      v-else
      class="ag-theme-alpine"
      :columnDefs="columnDefs"
      :rowData="wines"
      :defaultColDef="defaultColDef"
      :getRowStyle="getRowStyle"
      rowSelection="single"
      @row-clicked="e => $emit('select', e.data)"
      style="width:100%; height:100%;"
    />
  </div>
</template>

<script setup>
import { AgGridVue } from 'ag-grid-vue3'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { URGENCY_LABEL, URGENCY_STYLE, STATUS_STYLE } from '../utils/urgency'

const props = defineProps({
  wines:      { type: Array,  default: () => [] },
  loading:    { type: Boolean, default: false },
  selectedId: { type: String, default: null }
})

defineEmits(['select'])

const gbp = v => v != null ? `£${Number(v).toFixed(0)}` : ''

const columnDefs = [
  { field: 'name',             headerName: 'Wine',       flex: 3,   minWidth: 200 },
  { field: 'vintage',          headerName: 'Vintage',    width: 88  },
  { field: 'category',         headerName: 'Category',   flex: 1.5, minWidth: 130 },
  { field: 'sub_region',       headerName: 'Sub-Region', flex: 1.5, minWidth: 130 },
  { field: 'merchant',         headerName: 'Merchant',   width: 115 },
  { field: 'storage_location', headerName: 'Location',   width: 140 },
  { field: 'bottle_count',     headerName: 'Btl',        width: 65,  type: 'numericColumn' },
  {
    field: 'cost_per_bottle',
    headerName: '£ Cost/btl',
    width: 110,
    type: 'numericColumn',
    valueFormatter: p => gbp(p.value)
  },
  {
    field: 'value_per_bottle',
    headerName: '£ Value/btl',
    width: 110,
    type: 'numericColumn',
    valueFormatter: p => gbp(p.value)
  },
  {
    headerName: 'Score',
    width: 100,
    type: 'numericColumn',
    valueGetter: p => p.data?.tasting_summary?.avg ?? null,
    valueFormatter: p => {
      const s = p.data?.tasting_summary
      if (!s) return ''
      return `${s.avg} ★ ×${s.count}`
    },
  },
  { field: 'window_start', headerName: 'Start', width: 75 },
  { field: 'window_mid',   headerName: 'Mid',   width: 75 },
  { field: 'window_end',   headerName: 'End',   width: 75 },
  {
    field: 'urgency',
    headerName: 'Urgency',
    width: 145,
    valueFormatter: p => URGENCY_LABEL[p.value] || p.value || '',
    cellStyle: p => URGENCY_STYLE[p.value] || {}
  },
  {
    field: 'status',
    headerName: 'Status',
    width: 135,
    valueFormatter: p => (p.value || '').replace(/_/g, ' '),
    cellStyle: p => STATUS_STYLE[p.value] || {}
  },
]

const defaultColDef = {
  sortable: true,
  resizable: true,
  filter: true,
  floatingFilter: true,
}

const getRowStyle = p => p.data?.id === props.selectedId
  ? { background: '#f0e6ff', fontWeight: '600' }
  : {}
</script>

<style scoped>
.table-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  font-size: 1.1rem;
}
</style>
