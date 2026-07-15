import { apiFetch } from './client'

export function listLocations({ category, keyword, page = 1, size = 20 } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (keyword) params.set('keyword', keyword)
  params.set('page', String(page))
  params.set('size', String(size))
  return apiFetch(`/api/locations?${params.toString()}`)
}

export function getLocation(contentId) {
  return apiFetch(`/api/locations/${encodeURIComponent(contentId)}`)
}
