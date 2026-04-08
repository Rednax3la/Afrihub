import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const role = computed(() => user.value?.role || 'student')
  const isAdmin = computed(() => role.value === 'admin')
  const isTutor = computed(() => role.value === 'tutor')
  const isStudent = computed(() => role.value === 'student')

  async function register(name, email, password, location = '') {
    loading.value = true
    try {
      const { data } = await authApi.register({ name, email, password, location })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      return { success: true }
    } catch (err) {
      return { success: false, message: err.response?.data?.detail || 'Registration failed' }
    } finally {
      loading.value = false
    }
  }

  async function registerTutor(payload) {
    loading.value = true
    try {
      const { data } = await authApi.registerTutor(payload)
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      return { success: true }
    } catch (err) {
      return { success: false, message: err.response?.data?.detail || 'Registration failed' }
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    try {
      const { data } = await authApi.login({ email, password })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      return { success: true, role: data.user.role }
    } catch (err) {
      return { success: false, message: err.response?.data?.detail || 'Invalid credentials' }
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const { data } = await userApi.getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  async function refreshUser() {
    await fetchMe()
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, loading, isLoggedIn, role, isAdmin, isTutor, isStudent, register, registerTutor, login, fetchMe, refreshUser, logout }
})
