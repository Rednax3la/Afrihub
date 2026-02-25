import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contentApi, userApi } from '@/api'

export const useContentStore = defineStore('content', () => {
  const languages = ref([])
  const activeLanguageId = ref(null)
  const units = ref([])
  const currentLesson = ref(null)
  const loading = ref(false)

  async function fetchLanguages() {
    loading.value = true
    try {
      const { data } = await contentApi.getLanguages()
      languages.value = data
    } finally {
      loading.value = false
    }
  }

  async function selectLanguage(languageId) {
    activeLanguageId.value = languageId
    await fetchUnits(languageId)
  }

  async function fetchUnits(languageId) {
    loading.value = true
    try {
      const { data } = await contentApi.getUnits(languageId)
      units.value = data
    } finally {
      loading.value = false
    }
  }

  async function loadLesson(lessonId) {
    loading.value = true
    try {
      const { data } = await contentApi.getLesson(lessonId)
      currentLesson.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function enrollInLanguage(languageId) {
    await userApi.enrollLanguage(languageId)
    if (!activeLanguageId.value) {
      await selectLanguage(languageId)
    }
  }

  return {
    languages,
    activeLanguageId,
    units,
    currentLesson,
    loading,
    fetchLanguages,
    selectLanguage,
    fetchUnits,
    loadLesson,
    enrollInLanguage,
  }
})
