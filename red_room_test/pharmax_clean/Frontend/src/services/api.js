import { beginRequestLoading, endRequestLoading } from './globalLoading'

export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 20000)

function parseErrorMessage(body, status) {
  if (!body) return `Request failed (${status})`

  if (typeof body.detail === 'string' && body.detail.trim()) {
    return body.detail.trim()
  }

  if (Array.isArray(body.detail) && body.detail.length > 0) {
    return body.detail
      .map((item) => {
        const location = Array.isArray(item?.loc) ? item.loc.filter(Boolean).join(' > ') : ''
        const msg = String(item?.msg || '').trim()
        if (location && msg) return `${location}: ${msg}`
        return msg || 'Invalid input.'
      })
      .join(' | ')
  }

  if (typeof body.message === 'string' && body.message.trim()) {
    return body.message.trim()
  }

  return `Request failed (${status})`
}

/**
 * Thin fetch wrapper with automatic JSON handling and auth header injection.
 */
async function request(path, options = {}) {
  const token = localStorage.getItem('pharmax.token')
  const shouldTrack = options.silent !== true
  const requestLabel = options.loadingLabel || `${String(options.method || 'GET').toUpperCase()} ${path}`
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  if (shouldTrack) beginRequestLoading(requestLabel)

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    })

    if (res.status === 204) return null

    const body = await res.json().catch(() => null)

    if (!res.ok) {
      const message = parseErrorMessage(body, res.status)
      const err = new Error(message)
      err.status = res.status
      err.body = body
      throw err
    }

    return body
  } catch (err) {
    if (err?.name === 'AbortError') {
      const timeoutError = new Error(
        `Request timed out after ${Math.round(REQUEST_TIMEOUT_MS / 1000)}s. Check backend health or API URL.`,
      )
      timeoutError.status = 0
      throw timeoutError
    }
    throw err
  } finally {
    window.clearTimeout(timeoutId)
    if (shouldTrack) endRequestLoading(requestLabel)
  }
}

export const api = {
  get: (path, options = {}) => request(path, { method: 'GET', ...options }),
  post: (path, data = {}, options = {}) => request(path, { method: 'POST', body: JSON.stringify(data), ...options }),
  patch: (path, data = {}, options = {}) => request(path, { method: 'PATCH', body: JSON.stringify(data), ...options }),
  delete: (path, options = {}) => request(path, { method: 'DELETE', ...options }),
}
