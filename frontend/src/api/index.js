import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to splash on 401
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
  completeLesson: (lessonId, score) =>
    api.post(`/lessons/${lessonId}/complete?score=${score}`),
}

export default api
