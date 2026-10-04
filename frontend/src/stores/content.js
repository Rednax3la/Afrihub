import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contentApi, userApi } from '@/api'

export const useContentStore = defineStore('content', () => {
  const languages = ref([])
  const activeLanguageId = ref(null)
  const units = ref([])
  const currentLesson = ref(null)
  const loading = ref(false)

  let languageRequest
  let languagesAt = 0
  async function fetchLanguages() {
    if (languages.value.length && Date.now() - languagesAt < 300000) return
    if (languageRequest) return languageRequest
    languageRequest = contentApi.getLanguages().then(({ data }) => {
      languages.value = data
      languagesAt = Date.now()
    }).finally(() => { languageRequest = null })
    return languageRequest
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
