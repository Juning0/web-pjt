export function formatEventDate(value) {
  if (!/^\d{8}$/.test(value || '')) return value || ''
  return `${value.slice(0, 4)}.${value.slice(4, 6)}.${value.slice(6, 8)}`
}

export function eventDateLabel(place) {
  if (!place?.start_date && !place?.end_date) return ''
  if (place.start_date === place.end_date || !place.end_date) {
    return formatEventDate(place.start_date)
  }
  return `${formatEventDate(place.start_date)} ~ ${formatEventDate(place.end_date)}`
}
