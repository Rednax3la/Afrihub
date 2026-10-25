<template>
  <div class="p-6 lg:p-8 max-w-5xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Review Queue</h1>
      <p class="text-slate-500 text-sm mt-0.5">Review and approve scraped or submitted content before it goes live.</p>
    </div>

    <!-- Stats bar -->
    <div v-if="stats" class="flex flex-wrap gap-3 mb-6">
      <div class="bg-amber-50 border border-amber-100 rounded-2xl px-4 py-3 flex items-center gap-2">
        <span class="material-icons-outlined text-amber-500">pending</span>
        <span class="font-bold text-amber-800">{{ stats.total }} pending</span>
      </div>
      <div v-if="stats.audio_pending" class="bg-red-50 border border-red-100 rounded-2xl px-4 py-3 flex items-center gap-2">
        <span class="material-icons-outlined text-red-500">mic</span>
        <span class="font-bold text-red-800">{{ stats.audio_pending }} recording{{ stats.audio_pending === 1 ? '' : 's' }}</span>
      </div>
      <div
        v-for="(count, lang) in stats.by_language"
        :key="lang"
        class="bg-white border border-slate-100 rounded-2xl px-4 py-3 text-sm font-semibold text-slate-700 capitalize"
      >
        {{ lang }}: {{ count }}
      </div>
    </div>

    <!-- Tutor-submitted recordings. Only an admin can publish these; approving
         is what writes audio_url onto the question. -->
    <section v-if="audioQueue.length" class="mb-10">
      <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Tutor recordings ({{ audioQueue.length }})
      </h2>
      <div class="space-y-3">
        <div v-for="item in audioQueue" :key="item._id" class="bg-white rounded-3xl border border-slate-100 shadow-sm p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <span class="text-[10px] font-bold bg-sky-100 text-sky-700 px-2 py-0.5 rounded-full">TUTOR AUDIO</span>
                <span class="text-[10px] font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full capitalize">{{ item.language_id }}</span>
              </div>
              <p class="font-bold text-slate-900">{{ item.prompt || '(no prompt)' }}</p>
              <p v-if="item.native_text" class="text-sm text-slate-400 italic">{{ item.native_text }}</p>
              <p class="mt-1 text-xs text-slate-400">
                {{ item.lesson_title }} · {{ item.unit_id }} · submitted by
                <span class="font-semibold text-slate-600">{{ item.tutor_name }}</span>
              </p>
            </div>
            <div class="flex gap-2 shrink-0">
              <button
                :disabled="processing[item._id]"
                class="px-3 py-1.5 rounded-xl text-xs font-bold bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50"
                @click="doRejectAudio(item)"
              >Reject</button>
              <button
                :disabled="processing[item._id]"
                class="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-900 text-white hover:bg-emerald-800 disabled:opacity-50"
                @click="doApproveAudio(item)"
              >{{ processing[item._id] ? '…' : 'Approve' }}</button>
            </div>
          </div>
          <div class="mt-3">
            <AudioPlayer :src="item.audio_url" label="Listen before approving" />
          </div>
        </div>
      </div>
    </section>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!hasItems" class="bg-white rounded-3xl border border-dashed border-slate-200 p-16 text-center">
      <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">check_circle</span>
      <p class="text-slate-400 font-medium">No items pending review. All caught up!</p>
    </div>

    <template v-else>
      <div v-for="(lessons, lang) in queue" :key="lang" class="mb-10">
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 capitalize">{{ lang }} ({{ lessons.length }})</h2>
        <div class="space-y-4">
          <div v-for="lesson in lessons" :key="lesson.id" class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
            <!-- Lesson header -->
            <div class="p-5 flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2 mb-1">
                  <p class="font-bold text-slate-900">{{ lesson.title }}</p>
                  <span v-if="lesson.source === 'tutor'" class="text-[10px] font-bold bg-sky-100 text-sky-700 px-2 py-0.5 rounded-full">TUTOR</span>
                  <span v-else-if="isScraped(lesson)" class="text-[10px] font-bold bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">SCRAPED</span>
                </div>
                <p class="text-xs text-slate-400">
                  {{ lesson.questions?.length ?? 0 }} questions · {{ lesson.unit_id }}
                  <template v-if="lesson.tutor_name"> · by <span class="font-semibold text-slate-600">{{ lesson.tutor_name }}</span></template>
                </p>
              </div>
              <div class="flex gap-2 shrink-0">
                <button
                  @click="toggleExpand(lesson.id)"
                  class="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 text-slate-600 hover:bg-slate-50"
                >
                  {{ expanded[lesson.id] ? 'Hide' : 'Preview' }}
                </button>
                <button
                  @click="doReject(lesson.id)"
                  :disabled="processing[lesson.id]"
                  class="px-3 py-1.5 rounded-xl text-xs font-bold bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50"
                >
                  Reject
                </button>
                <button
                  @click="doApprove(lesson.id)"
                  :disabled="processing[lesson.id]"
                  class="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-900 text-white hover:bg-emerald-800 disabled:opacity-50"
                >
                  {{ processing[lesson.id] ? '…' : 'Approve' }}
                </button>
              </div>
            </div>

            <!-- Question preview -->
            <div v-if="expanded[lesson.id]" class="border-t border-slate-100 px-5 py-4 bg-slate-50">
              <div v-if="lesson.cultural_note" class="bg-amber-50 rounded-2xl p-3 mb-3 text-sm">
                <p class="font-bold text-amber-700 text-xs uppercase mb-1">Cultural Note — {{ lesson.cultural_note_title }}</p>
                <p class="text-slate-600">{{ lesson.cultural_note }}</p>
              </div>
              <div v-for="(q, qi) in lesson.questions ?? []" :key="q.id" class="mb-3 last:mb-0">
                <p class="text-xs font-bold text-slate-400 mb-1">Q{{ qi + 1 }} · {{ q.type }}</p>
                <p class="text-sm text-slate-700 font-medium mb-1">{{ q.prompt }}</p>
                <AudioPlayer v-if="q.audio_url" :src="q.audio_url" label="Play audio" class="mb-2" />
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="opt in q.options"
                    :key="opt.id"
                    class="text-xs px-2 py-0.5 rounded-lg"
                    :class="opt.id === q.correct_answer_id ? 'bg-emerald-100 text-emerald-700 font-bold' : 'bg-slate-100 text-slate-500'"
                  >
                    {{ opt.id }}) {{ opt.text }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useToastStore } from '@/stores/toast'
import AudioPlayer from '@/components/AudioPlayer.vue'

const toast = useToastStore()
const loading = ref(true)
const queue = ref({})
const audioQueue = ref([])
const stats = ref(null)
const expanded = ref({})
const processing = ref({})

const hasItems = computed(() =>
  Object.values(queue.value).some(l => l.length) || audioQueue.value.length > 0
)

// Historic documents used "scraped"; the pipeline writes "scraper".
const isScraped = lesson => ['scraper', 'scraped'].includes(lesson.source)

async function load() {
  loading.value = true
  try {
    const [qRes, sRes, aRes] = await Promise.all([
      adminApi.getReviewQueue(),
      adminApi.getReviewStats(),
      adminApi.getAudioReviewQueue(),
    ])
    queue.value = qRes.data
    stats.value = sRes.data
    audioQueue.value = aRes.data
  } catch {
    toast.error('Failed to load review queue')
  } finally {
    loading.value = false
  }
}

async function doApproveAudio(item) {
  processing.value[item._id] = true
  try {
    await adminApi.approveAudio(item._id)
    toast.success('Recording approved and attached to the question')
    await load()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Failed to approve recording')
  } finally {
    processing.value[item._id] = false
  }
}

async function doRejectAudio(item) {
  const reason = prompt('Reason for rejecting this recording? (the tutor will see this)')
  if (reason === null) return
  processing.value[item._id] = true
  try {
    await adminApi.rejectAudio(item._id, reason.trim() || null)
    toast.success('Recording rejected')
    await load()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Failed to reject recording')
  } finally {
    processing.value[item._id] = false
  }
}

function toggleExpand(id) {
  expanded.value[id] = !expanded.value[id]
}

async function doApprove(id) {
  processing.value[id] = true
  try {
    await adminApi.approveLesson(id)
    toast.success('Lesson approved and published')
    await load()
  } catch {
    toast.error('Failed to approve lesson')
  } finally {
    processing.value[id] = false
  }
}

async function doReject(id) {
  const reason = prompt('Reason for rejecting this lesson? (the tutor will see this)')
  if (reason === null) return
  processing.value[id] = true
  try {
    await adminApi.rejectLesson(id, reason.trim() || null)
    toast.success('Lesson rejected')
    await load()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Failed to reject lesson')
  } finally {
    processing.value[id] = false
  }
}

onMounted(load)
</script>
