<template>
  <div class="p-6 lg:p-8 max-w-4xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Review Queue</h1>
      <p class="text-slate-500 text-sm mt-0.5">Review pending content for the languages you teach.</p>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="!hasItems" class="bg-white rounded-3xl border border-dashed border-slate-200 p-16 text-center">
      <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">check_circle</span>
      <p class="text-slate-400 font-medium">No items to review right now.</p>
    </div>

    <template v-else>
      <div v-for="(lessons, lang) in queue" :key="lang" class="mb-10">
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 capitalize">{{ lang }} ({{ lessons.length }})</h2>
        <div class="space-y-4">
          <div v-for="lesson in lessons" :key="lesson.id" class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
            <div class="p-5 flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <p class="font-bold text-slate-900">{{ lesson.title }}</p>
                  <span v-if="lesson.source === 'scraped'" class="text-[10px] font-bold bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">SCRAPED</span>
                </div>
                <p class="text-xs text-slate-400">{{ lesson.questions?.length ?? 0 }} questions · {{ lesson.unit_id }}</p>
              </div>
              <div class="flex gap-2 shrink-0">
                <button @click="toggleExpand(lesson.id)" class="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 text-slate-600 hover:bg-slate-50">
                  {{ expanded[lesson.id] ? 'Hide' : 'Preview' }}
                </button>
                <button @click="doReject(lesson.id)" :disabled="processing[lesson.id]" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50">
                  Reject
                </button>
                <button @click="doApprove(lesson.id)" :disabled="processing[lesson.id]" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-900 text-white hover:bg-emerald-800 disabled:opacity-50">
                  {{ processing[lesson.id] ? '…' : 'Approve' }}
                </button>
              </div>
            </div>

            <div v-if="expanded[lesson.id]" class="border-t border-slate-100 px-5 py-4 bg-slate-50">
              <div v-if="lesson.cultural_note" class="bg-amber-50 rounded-2xl p-3 mb-3 text-sm">
                <p class="font-bold text-amber-700 text-xs uppercase mb-1">Cultural Note — {{ lesson.cultural_note_title }}</p>
                <p class="text-slate-600">{{ lesson.cultural_note }}</p>
              </div>
              <div v-for="(q, qi) in lesson.questions ?? []" :key="q.id" class="mb-3 last:mb-0">
                <p class="text-xs font-bold text-slate-400 mb-1">Q{{ qi + 1 }} · {{ q.type }}</p>
                <p class="text-sm text-slate-700 font-medium mb-1">{{ q.prompt }}</p>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="opt in q.options" :key="opt.id" class="text-xs px-2 py-0.5 rounded-lg"
                    :class="opt.id === q.correct_answer_id ? 'bg-emerald-100 text-emerald-700 font-bold' : 'bg-slate-100 text-slate-500'">
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
import { tutorApi } from '@/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const loading = ref(true)
const queue = ref({})
const expanded = ref({})
const processing = ref({})

const hasItems = computed(() => Object.values(queue.value).some(l => l.length))

async function load() {
  loading.value = true
  try {
    const { data } = await tutorApi.getReviewQueue()
    queue.value = data
  } catch {
    toast.error('Failed to load review queue')
  } finally {
    loading.value = false
  }
}

function toggleExpand(id) { expanded.value[id] = !expanded.value[id] }

async function doApprove(id) {
  processing.value[id] = true
  try {
    await tutorApi.approveReview(id)
    toast.success('Lesson approved')
    await load()
  } catch {
    toast.error('Failed to approve')
  } finally { processing.value[id] = false }
}

async function doReject(id) {
  if (!confirm('Reject this lesson?')) return
  processing.value[id] = true
  try {
    await tutorApi.rejectReview(id)
    toast.success('Lesson rejected')
    await load()
  } catch {
    toast.error('Failed to reject')
  } finally { processing.value[id] = false }
}

onMounted(load)
</script>
