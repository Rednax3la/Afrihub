import { defineStore } from 'pinia'
import { ref } from 'vue'
import { adminApi } from '@/api'

export const useAdminStore = defineStore('admin', () => {
  const stats = ref(null)
  const users = ref([])
  const tutors = ref([])
  const languages = ref([])
  const units = ref([])
  const lessons = ref([])
  const loading = ref(false)

  async function fetchStats() {
    const { data } = await adminApi.getStats()
    stats.value = data
  }

  async function fetchUsers() {
    loading.value = true
    try {
      const { data } = await adminApi.listUsers()
      users.value = data
    } finally { loading.value = false }
  }

  async function updateUser(id, payload) {
    const { data } = await adminApi.updateUser(id, payload)
    const idx = users.value.findIndex(u => u.id === id)
    if (idx !== -1) users.value[idx] = data
    return data
  }

  async function deleteUser(id) {
    await adminApi.deleteUser(id)
    users.value = users.value.filter(u => u.id !== id)
  }

  async function fetchTutors() {
    loading.value = true
    try {
      const { data } = await adminApi.listTutors()
      tutors.value = data
    } finally { loading.value = false }
  }

  async function approveTutor(id) {
    const { data } = await adminApi.approveTutor(id)
    const idx = tutors.value.findIndex(t => t.id === id)
    if (idx !== -1) tutors.value[idx] = data
    return data
  }

  async function suspendTutor(id) {
    const { data } = await adminApi.suspendTutor(id)
    const idx = tutors.value.findIndex(t => t.id === id)
    if (idx !== -1) tutors.value[idx] = data
    return data
  }

  async function fetchLanguages() {
    const { data } = await adminApi.listLanguages()
    languages.value = data
  }

  async function createLanguage(payload) {
    const { data } = await adminApi.createLanguage(payload)
    languages.value.push(data)
    return data
  }

  async function updateLanguage(id, payload) {
    const { data } = await adminApi.updateLanguage(id, payload)
    const idx = languages.value.findIndex(l => l.id === id)
    if (idx !== -1) languages.value[idx] = data
    return data
  }

  async function deleteLanguage(id) {
    await adminApi.deleteLanguage(id)
    languages.value = languages.value.filter(l => l.id !== id)
  }

  async function fetchUnits(languageId = null) {
    const { data } = await adminApi.listUnits(languageId)
    units.value = data
  }

  async function createUnit(payload) {
    const { data } = await adminApi.createUnit(payload)
    units.value.push(data)
    return data
  }

  async function updateUnit(id, payload) {
    const { data } = await adminApi.updateUnit(id, payload)
    const idx = units.value.findIndex(u => u.id === id)
    if (idx !== -1) units.value[idx] = data
    return data
  }

  async function deleteUnit(id) {
    await adminApi.deleteUnit(id)
    units.value = units.value.filter(u => u.id !== id)
  }

  async function fetchLessons(unitId = null) {
    const { data } = await adminApi.listLessons(unitId)
    lessons.value = data
  }

  async function createLesson(payload) {
    const { data } = await adminApi.createLesson(payload)
    lessons.value.push(data)
    return data
  }

  async function updateLesson(id, payload) {
    const { data } = await adminApi.updateLesson(id, payload)
    const idx = lessons.value.findIndex(l => l.id === id)
    if (idx !== -1) lessons.value[idx] = data
    return data
  }

  async function deleteLesson(id) {
    await adminApi.deleteLesson(id)
    lessons.value = lessons.value.filter(l => l.id !== id)
  }

  return {
    stats, users, tutors, languages, units, lessons, loading,
    fetchStats, fetchUsers, updateUser, deleteUser,
    fetchTutors, approveTutor, suspendTutor,
    fetchLanguages, createLanguage, updateLanguage, deleteLanguage,
    fetchUnits, createUnit, updateUnit, deleteUnit,
    fetchLessons, createLesson, updateLesson, deleteLesson,
  }
})
