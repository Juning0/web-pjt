const DEFAULT_API_BASE_URL = (
  import.meta.env.VITE_CHAT_API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000'
).replace(/\/$/, '')

export async function requestChat({ message, history, mode, apiBaseUrl }) {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), 90_000)
  const baseUrl = (apiBaseUrl || DEFAULT_API_BASE_URL).replace(/\/$/, '')

  try {
    const response = await fetch(`${baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, mode }),
      signal: controller.signal,
    })

    if (!response.ok) {
  let detail = ''

  try {
    const payload = await response.json()

    if (typeof payload.detail === 'string') {
      detail = payload.detail
    } else if (Array.isArray(payload.detail)) {
      detail = payload.detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join(', ')
    }
  } catch {
    // JSON 응답이 아니면 상태 코드만 사용한다.
  }

  if (response.status === 429) {
    throw new Error(
      detail || '챗봇 요청 한도에 도달했어요. 잠시 후 다시 시도해 주세요.',
    )
  }

  throw new Error(
    `챗봇 서버 오류 (${response.status})${detail ? `: ${detail}` : ''}`,
  )
}

    return await response.json()
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('응답 시간이 길어 연결을 종료했어요. 잠시 후 다시 시도해 주세요.')
    }
    if (error instanceof TypeError) {
      throw new Error('챗봇 서버에 연결할 수 없어요. FastAPI 실행 상태와 주소를 확인해 주세요.')
    }
    throw error
  } finally {
    window.clearTimeout(timeoutId)
  }
}
