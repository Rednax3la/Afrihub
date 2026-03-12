import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tutorApi } from '@/api'

export const useTutorStore = defineStore('tutor', () => {
  const units = ref([])
  const lessons = ref([])
  const loading = ref(false)

  async function fetchContent() {
    loading.value = true
    try {
      const { data } = await tutorApi.getMyContent()
      units.value = data.units
      lessons.value = data.lessons
    } finally {
      loading.value = false
    }
  }

  async function createUnit(payload) {
    const { data } = await tutorApi.createUnit(payload)
    units.value.push(data)
    return data
  }

  async function updateUnit(id, payload) {
    const { data } = await tutorApi.updateUnit(id, payload)
    const idx = units.value.findIndex(u => u.id === id)
    if (idx !== -1) units.value[idx] = data
    return data
  }

  async function createLesson(payload) {
    const { data } = await tutorApi.createLesson(payload)
    lessons.value.push(data)
    return data
  }

  async function updateLesson(id, payload) {
    const { data } = await tutorApi.updateLesson(id, payload)
    const idx = lessons.value.findIndex(l => l.id === id)
    if (idx !== -1) lessons.value[idx] = data
    return data
  }

  async function deleteLesson(id) {
    await tutorApi.deleteLesson(id)
    lessons.value = lessons.value.filter(l => l.id !== id)
  }

  return { units, lessons, loading, fetchContent, createUnit, updateUnit, createLesson, updateLesson, deleteLesson }
})
