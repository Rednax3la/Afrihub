<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <main class="max-w-2xl mx-auto p-6 pb-28">
      <RouterLink to="/dashboard" class="inline-flex items-center gap-2 text-[#007F96] mb-6"><span class="material-icons-outlined">arrow_back</span>Back to learning</RouterLink>
      <h1 class="text-3xl font-bold text-[#003B5C]">Language foundations</h1>
      <p class="text-slate-500 mt-3">Start with writing, sounds and pronunciation before exploring the lessons.</p>
      <p v-if="loading" class="mt-8" role="status">Loading foundations…</p>
      <p v-else-if="error" role="alert" class="mt-8 text-red-700">{{ error }}</p>
      <div v-else-if="!modules.length" class="bg-white border rounded-3xl p-6 mt-8">
        <h2 class="font-bold">Coming soon</h2><p class="mt-2 text-slate-600">Foundations for this language are awaiting linguistic review and tutor recordings. You can continue with the existing lessons.</p>
      </div>
      <article v-for="module in modules" :key="module.id" class="bg-white border rounded-3xl p-6 mt-6">
        <h2 class="font-bold text-xl">{{ module.title }}</h2><p class="mt-3 whitespace-pre-line">{{ module.body }}</p>
        <div v-for="recording in module.recordings || []" :key="recording.audio_url" class="mt-4">
          <p>{{ recording.example }} · {{ recording.grapheme }}</p><AudioPlayer :src="recording.audio_url" label="Listen to tutor" />
        </div>
      </article>
    </main><BottomNav />
  </section>
</template>
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import BottomNav from '@/components/BottomNav.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
const route = useRoute()
const modules = ref([]), loading = ref(false), error = ref('')
let version = 0
watch(() => route.params.languageId, async id => {
  const request = ++version
  loading.value = true; error.value = ''; modules.value = []
  try {
    const { data } = await api.get(`/languages/${encodeURIComponent(id)}/foundations`)
    if (request === version) modules.value = data.modules
  } catch { if (request === version) error.value = 'Foundations could not load. Please try again later.' }
  finally { if (request === version) loading.value = false }
}, { immediate: true })
</script>
