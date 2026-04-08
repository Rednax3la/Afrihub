import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/api` : '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(err)
  }
)

// ── Auth ───────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  registerTutor: (data) => api.post('/auth/register/tutor', data),
  login: (data) => api.post('/auth/login', data),
}

// ── Users ──────────────────────────────────────────────────────────────────────
export const userApi = {
  getMe: () => api.get('/users/me'),
  updateProfile: (data) => api.patch('/users/me', data),
  enrollLanguage: (languageId) => api.post(`/users/me/languages/${languageId}`),
}

// ── Languages & Content ────────────────────────────────────────────────────────
export const contentApi = {
  getLanguages: () => api.get('/languages'),
  getLanguage: (id) => api.get(`/languages/${id}`),
  getUnits: (languageId) => api.get(`/languages/${languageId}/units`),
  getLessons: (unitId) => api.get(`/units/${unitId}/lessons`),
  getLesson: (lessonId) => api.get(`/lessons/${lessonId}`),
  submitAnswer: (data) => api.post('/lessons/answer', data),
  // score + per-question results sent as JSON body (Gap 3)
  completeLesson: (lessonId, score, questionsAttempted = []) =>
    api.post(`/lessons/${lessonId}/complete`, { score, questions_attempted: questionsAttempted }),
  getCulturalNotes: (languageId) => api.get(`/languages/${languageId}/cultural-notes`),
  getLeaderboard: (languageId) => api.get(`/leaderboard/${languageId}`),
  getBadges: () => api.get('/badges'),
}

// ── Progress ───────────────────────────────────────────────────────────────────
export const progressApi = {
  getMyProgress: () => api.get('/progress/me'),
  getLessonProgress: (lessonId) => api.get(`/progress/me/lesson/${lessonId}`),
}

// ── TTS (2B) ───────────────────────────────────────────────────────────────────
export const ttsApi = {
  generate: (text, languageCode) => api.post('/tts/generate', { text, language_code: languageCode }),
}

// ── Admin ──────────────────────────────────────────────────────────────────────
export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  // Users
  listUsers: () => api.get('/admin/users'),
  updateUser: (id, data) => api.patch(`/admin/users/${id}`, data),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  // Tutors
  listTutors: () => api.get('/admin/tutors'),
  approveTutor: (id) => api.patch(`/admin/tutors/${id}/approve`),
  suspendTutor: (id) => api.patch(`/admin/tutors/${id}/suspend`),
  // Languages
  listLanguages: () => api.get('/admin/languages'),
  createLanguage: (data) => api.post('/admin/languages', data),
  updateLanguage: (id, data) => api.patch(`/admin/languages/${id}`, data),
  deleteLanguage: (id) => api.delete(`/admin/languages/${id}`),
  // Units
  listUnits: (languageId) => api.get(`/admin/units${languageId ? `?language_id=${languageId}` : ''}`),
  createUnit: (data) => api.post('/admin/units', data),
  updateUnit: (id, data) => api.patch(`/admin/units/${id}`, data),
  deleteUnit: (id) => api.delete(`/admin/units/${id}`),
  // Lessons
  listLessons: (unitId) => api.get(`/admin/lessons${unitId ? `?unit_id=${unitId}` : ''}`),
  createLesson: (data) => api.post('/admin/lessons', data),
  updateLesson: (id, data) => api.patch(`/admin/lessons/${id}`, data),
  deleteLesson: (id) => api.delete(`/admin/lessons/${id}`),
  // Review queue (2E)
  getReviewQueue: () => api.get('/admin/review-queue'),
  getReviewStats: () => api.get('/admin/review-queue/stats'),
  approveLesson: (id) => api.patch(`/admin/lessons/${id}/approve`),
  rejectLesson: (id) => api.patch(`/admin/lessons/${id}/reject`),
}

// ── Tutors ─────────────────────────────────────────────────────────────────────
export const tutorApi = {
  listActiveTutors: () => api.get('/tutors/'),
  getTutor: (id) => api.get(`/tutors/${id}`),
  getMyProfile: () => api.get('/tutors/me/profile'),
  updateMyProfile: (data) => api.patch('/tutors/me/profile', data),
  getMyContent: () => api.get('/tutors/me/content'),
  createUnit: (data) => api.post('/tutors/me/units', data),
  updateUnit: (id, data) => api.patch(`/tutors/me/units/${id}`, data),
  deleteUnit: (id) => api.delete(`/tutors/me/units/${id}`),
  createLesson: (data) => api.post('/tutors/me/lessons', data),
  updateLesson: (id, data) => api.patch(`/tutors/me/lessons/${id}`, data),
  deleteLesson: (id) => api.delete(`/tutors/me/lessons/${id}`),
  // Review queue (2E)
  getReviewQueue: () => api.get('/tutors/me/review-queue'),
  getReviewQueueCount: () => api.get('/tutors/me/review-queue/count'),
  approveReview: (lessonId) => api.patch(`/tutors/me/review/${lessonId}/approve`),
  rejectReview: (lessonId) => api.patch(`/tutors/me/review/${lessonId}/reject`),
  // Cultural notes (2C)
  createCulturalNote: (data) => api.post('/tutors/me/cultural-notes', data),
  updateCulturalNote: (id, data) => api.patch(`/tutors/me/cultural-notes/${id}`, data),
}

// ── Upload ─────────────────────────────────────────────────────────────────────
export const uploadApi = {
  audio: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/upload/audio', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  image: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/upload/image', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

export default api
