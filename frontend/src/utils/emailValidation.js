// Client-side sign-up email hints. The backend remains the source of truth —
// this only catches obvious mistakes before a round trip.

// Mirrors backend/services/email_validation.py::TYPO_DOMAINS
export const TYPO_DOMAINS = {
  'gmial.com': 'gmail.com',
  'gmal.com': 'gmail.com',
  'gamil.com': 'gmail.com',
  'gmai.com': 'gmail.com',
  'gmail.co': 'gmail.com',
  'gmaill.com': 'gmail.com',
  'gnail.com': 'gmail.com',
  'yaho.com': 'yahoo.com',
  'yahooo.com': 'yahoo.com',
  'yhoo.com': 'yahoo.com',
  'hotmial.com': 'hotmail.com',
  'hotmai.com': 'hotmail.com',
  'hotmil.com': 'hotmail.com',
  'hotnail.com': 'hotmail.com',
  'outlok.com': 'outlook.com',
  'outllok.com': 'outlook.com',
  'iclod.com': 'icloud.com',
  'icloud.co': 'icloud.com',
}

const EMAIL_RE = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/

export function normalizeEmail(email) {
  return (email || '').trim().toLowerCase()
}

export function domainOf(email) {
  const value = normalizeEmail(email)
  return value.includes('@') ? value.slice(value.lastIndexOf('@') + 1) : ''
}

/** Returns an error string to show inline, or '' when the address looks fine. */
export function emailError(email) {
  const value = normalizeEmail(email)
  if (!value) return ''
  if (!EMAIL_RE.test(value)) return 'Enter a valid email address, like you@example.com'
  const suggestion = TYPO_DOMAINS[domainOf(value)]
  if (suggestion) return `Did you mean ${suggestion}?`
  return ''
}
