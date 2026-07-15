import { apiFetch } from './client'

export function createPost(payload) {
  return apiFetch('/api/posts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
