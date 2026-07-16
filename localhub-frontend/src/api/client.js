const DEFAULT_API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'https://localhub-backend-kvly.onrender.com'
).replace(/\/$/, '')

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${DEFAULT_API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    let detail = ''
    try {
      const payload = await response.json()
      detail = payload.detail ? `: ${typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)}` : ''
    } catch {
      // The error response is not JSON. The status code is enough for the user message.
    }
    throw new Error(`요청에 실패했어요 (${response.status})${detail}`)
  }

  if (response.status === 204) return null
  return response.json()
}
