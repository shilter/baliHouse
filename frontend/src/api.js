function getApiKey() {
  return localStorage.getItem('api_key') || ''
}

function getAccessToken() {
  return localStorage.getItem('access_token') || ''
}

export function saveAuth({ access_token, refresh_token, api_key, member }) {
  if (access_token) localStorage.setItem('access_token', access_token)
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token)
  if (api_key)       localStorage.setItem('api_key', api_key)
  if (member)        localStorage.setItem('member', JSON.stringify(member))
}

export function clearAuth() {
  ['access_token', 'refresh_token', 'api_key', 'member'].forEach((k) =>
    localStorage.removeItem(k)
  )
}

export function getMemberFromStorage() {
  try {
    const raw = localStorage.getItem('member')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/**
 * For leads endpoints — sends x-api-key received from the backend at login.
 */
export function apiFetch(path, options = {}) {
  return fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': getApiKey(),
      ...(options.headers || {}),
    },
  })
}

/**
 * For member endpoints — sends JWT Bearer token.
 */
export function authFetch(path, options = {}) {
  const token = getAccessToken()
  return fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })
}