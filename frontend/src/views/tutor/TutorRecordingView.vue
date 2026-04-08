<template>
  <div class="p-6 lg:p-8 max-w-4xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Recording Queue</h1>
      <p class="text-slate-500 text-sm mt-0.5">
        <span v-if="loading">Loading…</span>
        <span v-else-if="queue.total_pending === 0">All caught up — no recordings needed.</span>
        <span v-else>{{ queue.total_pending }} phrase{{ queue.total_pending === 1 ? '' : 's' }} need your voice</span>
      </p>
    </div>

    <!-- Session progress -->
    <div v-if="sessionTotal > 0" class="bg-emerald-50 border border-emerald-100 rounded-3xl p-4 mb-6 flex items-center gap-4">
      <div class="flex-1">
        <p class="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1">Session progress</p>
        <div class="h-2 bg-emerald-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-emerald-500 rounded-full transition-all duration-300"
            :style="{ width: `${Math.round((sessionRecorded / sessionTotal) * 100)}%` }"
          ></div>
        </div>
      </div>
      <span class="text-sm font-bold text-emerald-800 shrink-0">{{ sessionRecorded }} / {{ sessionTotal }} recorded</span>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!queue.lessons?.length" class="bg-white rounded-3xl border border-dashed border-slate-200 p-12 text-center">
      <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">mic</span>
      <p class="text-slate-400 font-medium">No recordings needed right now</p>
    </div>

    <!-- Grouped by language -->
    <div v-else class="space-y-6">
      <div v-for="(lessons, lang) in groupedByLanguage" :key="lang">
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 capitalize">{{ lang }}</h2>
        <div class="space-y-3">
          <div v-for="item in lessons" :key="item.lesson_id" class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
            <!-- Lesson header -->
            <button
              class="w-full flex items-center gap-4 p-5 text-left hover:bg-slate-50 transition-colors"
              @click="toggleLesson(item.lesson_id)"
            >
              <div class="w-10 h-10 bg-red-50 rounded-2xl flex items-center justify-center shrink-0">
                <span class="material-icons-outlined text-red-500">mic</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-slate-900">{{ item.lesson_title }}</p>
                <p class="text-xs text-slate-400 mt-0.5">Unit: {{ item.unit_id }} · {{ item.needs_recording }} of {{ item.total_questions }} questions need audio</p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                  {{ pendingForLesson(item) }} remaining
                </span>
                <span class="material-icons-outlined text-slate-400 text-base transition-transform" :class="expandedLessons.has(item.lesson_id) ? 'rotate-180' : ''">expand_more</span>
              </div>
            </button>

            <!-- Questions list -->
            <div v-if="expandedLessons.has(item.lesson_id)" class="border-t border-slate-100 divide-y divide-slate-50">
              <div
                v-for="q in item.questions"
                :key="q.question_id"
                class="p-5"
                :class="submittedSet.has(`${item.lesson_id}:${q.question_id}`) ? 'bg-emerald-50/50' : ''"
              >
                <!-- Question text -->
                <div class="mb-3">
                  <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 mr-2">{{ q.type.replace('_', ' ') }}</span>
                  <p class="text-lg font-bold text-slate-900 mt-2 leading-snug">{{ q.prompt }}</p>
                  <p v-if="q.native_text" class="text-sm text-slate-400 mt-0.5 italic">{{ q.native_text }}</p>
                </div>

                <!-- Submitted state -->
                <div v-if="submittedSet.has(`${item.lesson_id}:${q.question_id}`)" class="flex items-center gap-3">
                  <span class="material-icons-outlined text-emerald-600">check_circle</span>
                  <span class="text-sm font-semibold text-emerald-700">Recording submitted</span>
                  <AudioPlayer :src="submittedUrls[`${item.lesson_id}:${q.question_id}`]" label="Preview" />
                </div>

                <!-- Upload state -->
                <div v-else>
                  <FileUpload
                    :model-value="pendingUrls[`${item.lesson_id}:${q.question_id}`] || ''"
                    type="audio"
                    @update:model-value="(url) => onAudioUploaded(item.lesson_id, q.question_id, url)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { tutorApi } from '@/api'
import { useToastStore } from '@/stores/toast'
import FileUpload from '@/components/FileUpload.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'

const toast = useToastStore()
const loading = ref(true)
const queue = ref({ total_pending: 0, lessons: [] })
const expandedLessons = reactive(new Set())
const submittedSet = reactive(new Set())
const submittedUrls = reactive({})
const pendingUrls = reactive({})

const sessionTotal = ref(0)
const sessionRecorded = ref(0)

const groupedByLanguage = computed(() => {
  const groups = {}
  for (const item of (queue.value.lessons ?? [])) {
    const lang = item.language_id || 'unknown'
    if (!groups[lang]) groups[lang] = []
    groups[lang].push(item)
  }
  return groups
})

function pendingForLesson(item) {
  const submitted = item.questions.filter(q =>
    submittedSet.has(`${item.lesson_id}:${q.question_id}`)
  ).length
  return item.needs_recording - submitted
}

function toggleLesson(id) {
  if (expandedLessons.has(id)) {
    expandedLessons.delete(id)
  } else {
    expandedLessons.add(id)
  }
}

async function onAudioUploaded(lessonId, questionId, url) {
  if (!url) return
  const key = `${lessonId}:${questionId}`
  pendingUrls[key] = url
  try {
    await tutorApi.submitRecording(lessonId, questionId, url)
    submittedSet.add(key)
    submittedUrls[key] = url
    sessionRecorded.value++
    toast.success('Recording submitted')
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to submit recording')
    delete pendingUrls[key]
  }
}

onMounted(async () => {
  try {
    const { data } = await tutorApi.getRecordingQueue()
    queue.value = data
    sessionTotal.value = data.total_pending
  } catch {
    toast.error('Failed to load recording queue')
  } finally {
    loading.value = false
  }
})
</script>
