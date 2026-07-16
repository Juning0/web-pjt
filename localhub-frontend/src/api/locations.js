import { apiFetch } from './client'

export function listLocations({ category, keyword, sort, page = 1, size = 20 } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (keyword) params.set('keyword', keyword)
  if (sort) params.set('sort', sort)
  params.set('page', String(page))
  params.set('size', String(size))
  return apiFetch(`/api/locations?${params.toString()}`)
}

export function getLocation(contentId) {
  return apiFetch(`/api/locations/${encodeURIComponent(contentId)}`)
}

const LIST_ALL_PAGE_SIZE = 100
const LIST_ALL_MAX_PAGES = 20 // 최대 2,000건까지 — 지도에 전부 표시해도 무리 없는 상한선

// 지도는 필터에 맞는 장소를 전부 보여줘야 해서, 총 개수만큼 페이지를 이어서 가져온다.
export async function listAllLocations({ category, keyword } = {}) {
  const first = await listLocations({ category, keyword, page: 1, size: LIST_ALL_PAGE_SIZE })
  const totalPages = Math.min(
    Math.ceil(first.total / LIST_ALL_PAGE_SIZE) || 1,
    LIST_ALL_MAX_PAGES,
  )

  const restPages = []
  for (let page = 2; page <= totalPages; page += 1) restPages.push(page)

  const rest = await Promise.all(
    restPages.map((page) => listLocations({ category, keyword, page, size: LIST_ALL_PAGE_SIZE })),
  )

  return [first.items, ...rest.map((response) => response.items)].flat()
}
