const YEAR = new Date().getFullYear()

function toYear(val) {
  if (!val) return null
  if (val === 'NOW') return YEAR - 1
  const n = parseInt(val)
  return isNaN(n) ? null : n
}

export function calcUrgency(windowEnd, windowMid) {
  const endY = toYear(windowEnd)
  if (endY === null) return null
  if (endY < YEAR) return 'past_window'
  if (endY <= YEAR + 1) return 'closing_soon'
  const midY = toYear(windowMid)
  if (midY !== null && midY < YEAR) return 'near_midpoint'
  if (midY !== null && midY <= YEAR + 2) return 'approaching_midpoint'
  return 'hold'
}

export const URGENCY_LABEL = {
  past_window:          'Past window',
  closing_soon:         'Closing soon',
  near_midpoint:        'Near midpoint',
  approaching_midpoint: 'Approaching mid',
  hold:                 'Hold',
}

export const URGENCY_STYLE = {
  past_window:          { background: '#ffcccc', color: '#b71c1c' },
  closing_soon:         { background: '#ffe0b2', color: '#e65100' },
  near_midpoint:        { background: '#fff9c4', color: '#827717' },
  approaching_midpoint: { background: '#f9fbe7', color: '#558b2f' },
  hold:                 { background: '#f0f0f0', color: '#555'    },
}

export const STATUS_STYLE = {
  in_storage:      { background: '#e3f2fd', color: '#1565c0' },
  pending_listing: { background: '#fff3e0', color: '#e65100' },
  listed:          { background: '#fce4ec', color: '#880e4f' },
  sold:            { background: '#e8f5e9', color: '#2e7d32' },
  consumed:        { background: '#eeeeee', color: '#555'    },
}

export const STORAGE_LOCATIONS = [
  'BBR Bond', 'Justerini Bond', 'IG Bond',
  'Fine and Rare', 'Hatton Edwards', 'Lay Wheeler',
  'Robertson Bond', 'Vinotheque', 'Wien'
]

export const MERCHANTS = [
  'BBR', 'Justerini', 'IG', 'Fine and Rare',
  'Hatton Edwards', 'Lay Wheeler', 'Robertson', 'Other'
]

export const CATEGORIES = [
  'Bordeaux Red', 'Bordeaux White', 'Bordeaux Blend',
  'Burgundy - Red', 'Burgundy - White',
  'Champagne', 'Chardonnay', 'Other Red',
  'Piedmont', 'Pinot Noir', 'Port', 'Rhone',
  'Sauvignon Blanc', 'Sangiovese'
]
