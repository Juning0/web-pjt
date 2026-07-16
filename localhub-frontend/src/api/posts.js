import { apiFetch } from './client'

export function listPosts({
  category,
  keyword,
  sort = 'latest',
  page = 1,
  size = 10,
  locationId,
} = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (keyword) params.set('keyword', keyword)
  if (locationId) params.set('location_id', locationId)
  params.set('sort', sort)
  params.set('page', String(page))
  params.set('size', String(size))
  return apiFetch(`/api/posts?${params.toString()}`)
}

export function getPost(postId) {
  return apiFetch(`/api/posts/${postId}`)
}

export function createPost(payload) {
  return apiFetch('/api/posts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updatePost(postId, payload) {
  return apiFetch(`/api/posts/${postId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deletePost(postId, password) {
  return apiFetch(`/api/posts/${postId}/delete`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
}

export function createComment(postId, { content, password }) {
  return apiFetch(`/api/posts/${postId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content, password }),
  })
}

export function deleteComment(commentId, password) {
  return apiFetch(`/api/posts/comments/${commentId}/delete`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
}

const LIST_ALL_PAGE_SIZE = 50
const LIST_ALL_MAX_PAGES = 20 // 최대 1,000건까지 — 게시판 전체를 클라이언트에서 필터/정렬하기 위한 상한선

// 게시판은 카테고리 다중 선택 + 키워드 검색을 클라이언트에서 처리하므로, 전체 목록을 이어서 가져온다.
export async function listAllPosts() {
  const first = await listPosts({ page: 1, size: LIST_ALL_PAGE_SIZE })
  const totalPages = Math.min(
    Math.ceil(first.total / LIST_ALL_PAGE_SIZE) || 1,
    LIST_ALL_MAX_PAGES,
  )

  const restPages = []
  for (let page = 2; page <= totalPages; page += 1) restPages.push(page)

  const rest = await Promise.all(
    restPages.map((page) => listPosts({ page, size: LIST_ALL_PAGE_SIZE })),
  )

  return [first.items, ...rest.map((response) => response.items)].flat()
}
