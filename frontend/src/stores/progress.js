import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useProgressStore = defineStore('progress', () => {
  const summary = ref(null)       // full /progress/me response
  const lessonCache = ref({})     // { [lesson_id]: { completed, score, attempts } }
  const loading = ref(false)

  async function fetchMyProgress() {
    loading.value = true
    try {
      const { data } = await api.get('/progress/me')
      summary.value = data
      lessonCache.value = data.lesson_progress ?? {}
    } finally {
      loading.value = false
    }
  }

  async function fetchLessonProgress(lessonId) {
    if (lessonCache.value[lessonId]) return lessonCache.value[lessonId]
    const { data } = await api.get(`/progress/me/lesson/${lessonId}`)
    lessonCache.value[lessonId] = data
    return data
  }

  function isCompleted(lessonId) {
    return lessonCache.value[lessonId]?.completed ?? false
  }

  return { summary, lessonCache, loading, fetchMyProgress, fetchLessonProgress, isCompleted }
})
