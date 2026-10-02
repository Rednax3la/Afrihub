<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <main class="max-w-2xl mx-auto p-6">
      <h1 class="text-3xl font-bold text-[#003B5C] mb-6">Dictionary</h1>
      <label for="word" class="block text-sm font-semibold mb-2">Find a word</label>
      <input id="word" v-model="query" type="search" maxlength="200" placeholder="Search words and translations" class="w-full border rounded-2xl p-4 focus:outline-[#00A3C1]" />
      <label for="language" class="block text-sm font-semibold mt-4 mb-2">Language</label>
      <select id="language" v-model="languageId" class="w-full border rounded-2xl p-3 bg-white">
        <option value="">All Languages</option>
        <option v-for="language in languages" :key="language.id" :value="language.id">{{ language.name }}</option>
      </select>
      <p v-if="error" role="alert" class="mt-6 text-red-600">{{ error }}</p>
      <p v-else-if="loading" role="status" class="mt-8 text-slate-500">Searching...</p>
      <div v-else-if="results.length" class="space-y-4 mt-6">
        <article v-for="(entry, index) in results" :key="`${entry.language_id}-${index}`" class="bg-white border border-slate-100 rounded-3xl p-5 shadow-sm">
          <p class="text-xs font-semibold text-[#00A3C1] mb-2">{{ entry.language_name }}</p>
          <h2 class="text-2xl font-bold text-[#003B5C]">{{ entry.native }}</h2>
          <p class="mt-1 text-slate-700">{{ entry.english }}</p>
          <p v-if="entry.pronunciation" class="text-sm text-slate-400 mt-2">{{ entry.pronunciation }}</p>
          <AudioPlayer v-if="entry.audio_url" :src="entry.audio_url" label="Listen" class="mt-3" />
        </article>
      </div>
      <p v-else class="text-center text-slate-500 py-16">{{ query.trim() ? 'No matching words found.' : 'Search for a word in any of your languages' }}</p>
    </main>
    <BottomNav />
  </section>
</template>
<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { contentApi, dictionaryApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import BottomNav from '@/components/BottomNav.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
const auth = useAuthStore()
const query = ref('')
const languageId = ref('')
const languages = ref([])
const results = ref([])
const loading = ref(false)
const error = ref('')
let timer
let requestId = 0
watch([query, languageId], () => {
  clearTimeout(timer)
  const id = ++requestId
  results.value = []
  error.value = ''
  loading.value = !!query.value.trim()
  if (!loading.value) return
  timer = setTimeout(async () => {
    try {
      const { data } = await dictionaryApi.search(query.value.trim(), languageId.value || undefined)
      if (id === requestId) results.value = data
    } catch (err) {
      if (id === requestId) error.value = err.response?.data?.detail || 'Could not search. Please try again.'
    } finally { if (id === requestId) loading.value = false }
  }, 400)
})
onMounted(async () => {
  try {
    const { data } = await contentApi.getLanguages()
    languages.value = data.filter(l => auth.user?.active_languages?.includes(l.id))
  } catch { error.value = 'Could not load your languages.' }
})
onUnmounted(() => { clearTimeout(timer); requestId++ })
</script>
