import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api',
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
  completeLesson: (lessonId, score) => api.post(`/lessons/${lessonId}/complete?score=${score}`),
}

// ── Progress ───────────────────────────────────────────────────────────────────
export const progressApi = {
  getMyProgress: () => api.get('/progress/me'),
  getLessonProgress: (lessonId) => api.get(`/progress/me/lesson/${lessonId}`),
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
  createLesson: (data) => api.post('/tutors/me/lessons', data),
  updateLesson: (id, data) => api.patch(`/tutors/me/lessons/${id}`, data),
  deleteLesson: (id) => api.delete(`/tutors/me/lessons/${id}`),
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
