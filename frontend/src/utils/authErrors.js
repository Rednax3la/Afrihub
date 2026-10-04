export function authError(error, fallback = 'The request could not be completed.') {
  if (!error.response) return 'Cannot reach the server. Check your connection and try again.'
  const status = error.response.status
  if (status >= 500) return 'The service is temporarily unavailable. Please try again later.'
  if (status === 401) return 'Invalid email or password.'
  const detail = error.response.data?.detail
  if (Array.isArray(detail)) return detail.map(item => item.msg).join(' ')
  return typeof detail === 'string' ? detail : fallback
}
