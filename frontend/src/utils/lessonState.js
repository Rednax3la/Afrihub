// In-lesson resume state, kept in sessionStorage and keyed by user + lesson so
// two accounts on one device never see each other's answers.

const PREFIX = 'lesson-state'
const MAX_AGE_MS = 24 * 60 * 60 * 1000

export function lessonStateKey(userId, lessonId) {
  return `${PREFIX}:${userId || 'anon'}:${lessonId}`
}

export function saveLessonState(userId, lessonId, state) {
  if (!lessonId) return
  try {
    sessionStorage.setItem(
      lessonStateKey(userId, lessonId),
      JSON.stringify({ ...state, savedAt: Date.now() })
    )
  } catch { /* storage full or disabled — resuming is best-effort */ }
}

export function loadLessonState(userId, lessonId) {
  if (!lessonId) return null
  try {
    const raw = sessionStorage.getItem(lessonStateKey(userId, lessonId))
    if (!raw) return null
    const parsed = JSON.parse(raw)
    // Safety expiry, in case a session is restored by the browser days later.
    if (!parsed?.savedAt || Date.now() - parsed.savedAt > MAX_AGE_MS) {
      clearLessonState(userId, lessonId)
      return null
    }
    return parsed
  } catch {
    return null
  }
}

export function clearLessonState(userId, lessonId) {
  try { sessionStorage.removeItem(lessonStateKey(userId, lessonId)) } catch { /* ignore */ }
}
