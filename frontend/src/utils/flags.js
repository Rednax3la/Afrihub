// Build-time feature flags. Change the value in Vercel and redeploy.

function boolFlag(value, fallback = false) {
  if (value === undefined || value === null || value === '') return fallback
  return String(value).trim().toLowerCase() === 'true'
}

// Premium unit gating. Off by default while all lessons are open; the paywall
// UI is retained and comes back by setting VITE_PAYWALL_ENABLED=true (and the
// backend's PAYWALL_ENABLED to match).
export const PAYWALL_ENABLED = boolFlag(import.meta.env.VITE_PAYWALL_ENABLED, false)
