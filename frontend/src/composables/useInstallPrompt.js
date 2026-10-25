import { ref } from 'vue'

// The browser can fire `beforeinstallprompt` before any component mounts, so the
// event is captured at module scope (imported from main.js) and replayed later.
const deferredPrompt = ref(null)
const promptAvailable = ref(false)

const DISMISS_KEY = 'install-prompt-dismissed-at'
const SESSION_KEY = 'install-prompt-shown'
const DISMISS_COOLDOWN_MS = 24 * 60 * 60 * 1000

export function isStandalone() {
  if (typeof window === 'undefined') return false
  return (
    window.matchMedia?.('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  )
}

export function isIos() {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent || ''
  // iPadOS 13+ reports as Macintosh but is touch-capable.
  return /iPad|iPhone|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)
}

function readTimestamp(key) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? Number(raw) || 0 : 0
  } catch {
    return 0
  }
}

/** True when the 24h cool-down after a dismissal has elapsed (or never dismissed). */
export function dismissalExpired() {
  const at = readTimestamp(DISMISS_KEY)
  return !at || Date.now() - at > DISMISS_COOLDOWN_MS
}

export function markDismissed() {
  try { localStorage.setItem(DISMISS_KEY, String(Date.now())) } catch { /* storage disabled */ }
}

export function markShownThisSession() {
  try { sessionStorage.setItem(SESSION_KEY, '1') } catch { /* storage disabled */ }
}

export function shownThisSession() {
  try { return sessionStorage.getItem(SESSION_KEY) === '1' } catch { return false }
}

export function clearDismissal() {
  try { localStorage.removeItem(DISMISS_KEY) } catch { /* storage disabled */ }
}

/** Registers the global listeners. Safe to call once from main.js. */
export function registerInstallListeners() {
  if (typeof window === 'undefined') return
  window.addEventListener('beforeinstallprompt', event => {
    // Suppress Chrome's mini-infobar so our own prompt controls the schedule.
    event.preventDefault()
    deferredPrompt.value = event
    promptAvailable.value = true
  })
  window.addEventListener('appinstalled', () => {
    deferredPrompt.value = null
    promptAvailable.value = false
    clearDismissal()
  })
}

export function useInstallPrompt() {
  async function install() {
    const event = deferredPrompt.value
    if (!event) return 'unavailable'
    deferredPrompt.value = null
    promptAvailable.value = false
    event.prompt()
    const { outcome } = await event.userChoice
    if (outcome !== 'accepted') markDismissed()
    return outcome
  }

  return { deferredPrompt, promptAvailable, install }
}
