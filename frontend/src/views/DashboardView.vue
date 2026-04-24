<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <div class="max-w-2xl mx-auto">

      <!-- Header -->
      <header class="px-6 pt-6 pb-2 flex justify-between items-center sticky top-0 bg-[#FDFCFB]/80 backdrop-blur-md z-20">
        <div class="flex items-center gap-2">
          <img src="/Vernaculearn logo.png" alt="Vernaculearn" class="h-7 w-auto" />
          <span class="text-lg font-bold tracking-tight text-[#003B5C]">Vernaculearn</span>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex items-center bg-amber-50 px-3 py-1.5 rounded-full border border-amber-100">
            <span class="material-icons-outlined text-amber-600 text-sm">local_fire_department</span>
            <span class="text-amber-700 font-bold ml-1 text-sm">{{ progressStore.summary?.streak ?? auth.user?.streak ?? 0 }}</span>
          </div>
          <RouterLink to="/profile" class="w-10 h-10 rounded-full border-2 border-[#A7FFEB] p-0.5">
            <img
              :src="auth.user?.avatar_url || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(auth.user?.name || 'User') + '&background=003B5C&color=fff&rounded=true'"
              class="w-full h-full rounded-full object-cover"
            />
          </RouterLink>
        </div>
      </header>

      <!-- ── LANDING VIEW (no language selected) ───────────────────────── -->
      <template v-if="!activeLangId">

        <!-- Currently Learning -->
        <div v-if="learningLangs.length" class="px-6 pt-6">
          <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">Currently Learning</h4>
          <div class="space-y-3">
            <button
              v-for="lang in learningLangs"
              :key="lang.language_id"
              @click="openLearningPath(lang.language_id)"
              class="w-full flex items-center gap-4 bg-white border border-slate-100 rounded-3xl p-4 shadow-sm active:scale-[0.98] transition-transform text-left"
            >
              <div
                class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shrink-0"
                :style="{ backgroundColor: colorMap[langMeta(lang.language_id).color] || '#003B5C' }"
              >
                {{ langMeta(lang.language_id).flag_emoji }}
              </div>
              <div class="flex-1 min-w-0">
                <h5 class="font-bold text-slate-900">{{ lang.language_name }}</h5>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                  <div
                    class="bg-[#00A3C1] h-full transition-all duration-700"
                    :style="{ width: `${lang.percent_complete}%` }"
                  ></div>
                </div>
                <p class="text-xs text-slate-400 mt-1">{{ lang.percent_complete }}% complete</p>
              </div>
              <span class="text-xs font-bold text-[#00A3C1] shrink-0">CONTINUE →</span>
            </button>
          </div>
        </div>

        <!-- Language Picker -->
        <div class="px-6 pt-8 pb-8">
          <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">
            {{ learningLangs.length ? 'Pick Another Language' : 'Pick a Language' }}
          </h4>

          <div v-if="content.loading" class="flex justify-center py-10">
            <div class="w-8 h-8 border-4 border-[#A7FFEB] border-t-[#00A3C1] rounded-full animate-spin"></div>
          </div>

          <div v-else class="grid grid-cols-2 gap-3">
            <button
              v-for="lang in pickerLangs"
              :key="lang.id"
              @click="startLang(lang)"
              class="flex items-center gap-3 bg-white border border-slate-100 rounded-2xl px-4 py-4 shadow-sm active:scale-95 transition-transform text-left"
            >
              <span class="text-2xl shrink-0">{{ lang.flag_emoji }}</span>
              <span class="font-bold text-sm text-slate-800 leading-tight truncate">{{ lang.name }}</span>
            </button>
          </div>
        </div>

      </template>

      <!-- ── LEARNING PATH VIEW (language selected) ─────────────────────── -->
      <template v-else>

        <!-- Back + Language Header -->
        <div class="px-6 pt-4 pb-2 flex items-center gap-3">
          <button
            @click="activeLangId = null"
            class="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center shrink-0 active:scale-90 transition-transform"
          >
            <span class="material-icons-outlined text-slate-700 text-xl">arrow_back</span>
          </button>
          <div>
            <p class="text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase">Learning Path</p>
            <h3 class="text-lg font-bold text-[#003B5C] leading-tight">{{ activeLangName }}</h3>
          </div>
          <div class="ml-auto text-2xl">{{ langMeta(activeLangId).flag_emoji }}</div>
        </div>

        <!-- Loading -->
        <div v-if="content.loading || progressStore.loading" class="flex justify-center py-20">
          <div class="w-10 h-10 border-4 border-[#A7FFEB] border-t-[#00A3C1] rounded-full animate-spin"></div>
        </div>

        <!-- Units + Lessons -->
        <main v-else-if="content.units.length" class="p-6">
          <div v-for="(unit, uIdx) in content.units" :key="unit.id" class="mb-12">

            <!-- Unit Card -->
            <div class="bg-[#A7FFEB]/30 rounded-[2.5rem] p-6 mb-12 border border-[#00A3C1]/20 shadow-sm">
              <div class="flex justify-between items-start mb-4">
                <div class="flex-1 min-w-0 mr-4">
                  <span class="text-[10px] font-bold tracking-[0.2em] text-[#003B5C] uppercase bg-[#A7FFEB]/60 px-3 py-1 rounded-full">Unit {{ uIdx + 1 }}</span>
                  <h4 class="text-2xl font-bold text-[#003B5C] mt-2">{{ unit.title }}</h4>
                  <p class="text-[#003B5C]/60 text-sm">{{ unit.subtitle }}</p>
                </div>
                <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-sm shrink-0">
                  <span class="material-icons-outlined text-[#003B5C]">{{ unit.icon }}</span>
                </div>
              </div>
              <div class="w-full bg-white/50 h-2 rounded-full overflow-hidden">
                <div
                  class="bg-[#00A3C1] h-full transition-all duration-700"
                  :style="{ width: `${unitProgressPct(unit)}%` }"
                ></div>
              </div>
              <p class="text-xs text-[#003B5C]/60 mt-1.5">
                {{ unitCompletedCount(unit) }} / {{ unit.lessons?.length ?? 0 }} lessons
              </p>
            </div>

            <!-- Lesson Nodes -->
            <div class="flex flex-col items-center gap-12 relative">
              <div
                v-for="(lesson, lIdx) in unit.lessons ?? []"
                :key="lesson.id"
                class="relative"
              >
                <!-- Connector line -->
                <div
                  v-if="lIdx < (unit.lessons?.length ?? 0) - 1"
                  class="absolute left-1/2 bottom-[-48px] w-0.5 h-10 bg-slate-200 -translate-x-1/2 z-[-1]"
                ></div>

                <!-- Completed -->
                <RouterLink v-if="progressStore.isCompleted(lesson.id)" :to="`/lesson/${lesson.id}`" class="group flex flex-col items-center cursor-pointer">
                  <div class="w-20 h-20 bg-[#00A3C1] rounded-3xl rotate-45 flex items-center justify-center shadow-xl shadow-[#00A3C1]/20 group-active:scale-90 transition-transform">
                    <span class="material-icons-outlined text-white -rotate-45 text-3xl">check</span>
                  </div>
                  <p class="text-center mt-4 font-bold text-slate-800">{{ lesson.title }}</p>
                  <span class="mt-1 text-[10px] font-bold text-[#00A3C1] uppercase tracking-wider">Redo</span>
                </RouterLink>

                <!-- Active / Current -->
                <RouterLink v-else-if="lesson.id === currentLessonId" :to="`/lesson/${lesson.id}`" class="group flex flex-col items-center cursor-pointer">
                  <div class="relative w-24 h-24 bg-white border-4 border-[#003B5C] rounded-[2rem] rotate-45 flex items-center justify-center shadow-xl shadow-slate-200 group-active:scale-90 transition-transform">
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                      :class="lesson.lesson_type === 'reading' ? 'bg-teal-50' : 'bg-[#A7FFEB]/50'"
                    >
                      <span class="material-icons-outlined -rotate-45 text-3xl"
                        :class="lesson.lesson_type === 'reading' ? 'text-teal-600' : 'text-[#003B5C]'"
                      >{{ lesson.lesson_type === 'reading' ? 'menu_book' : 'chat_bubble' }}</span>
                    </div>
                    <div class="absolute -top-2 -right-2 text-white text-[10px] font-bold px-2 py-1 rounded-lg -rotate-45 shadow-md"
                      :class="lesson.lesson_type === 'reading' ? 'bg-teal-500' : 'bg-amber-500'"
                    >{{ lesson.lesson_type === 'reading' ? 'READ' : 'NOW' }}</div>
                  </div>
                  <p class="text-center mt-6 font-bold text-slate-800">{{ lesson.title }}</p>
                </RouterLink>

                <!-- Locked -->
                <RouterLink v-else :to="`/lesson/${lesson.id}`" class="group flex flex-col items-center opacity-50">
                  <div class="w-20 h-20 bg-slate-200 rounded-3xl rotate-45 flex items-center justify-center group-active:scale-90 transition-transform">
                    <span class="material-icons-outlined text-slate-500 -rotate-45 text-2xl">
                      {{ lesson.lesson_type === 'reading' ? 'menu_book' : 'lock' }}
                    </span>
                  </div>
                  <p class="text-center mt-4 font-medium text-slate-500">{{ lesson.title }}</p>
                </RouterLink>
              </div>
            </div>

          </div>
        </main>

        <div v-else class="text-center py-20 px-6">
          <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">language</span>
          <p class="text-slate-400 font-medium">No lessons available yet for this language.</p>
        </div>

      </template>
    </div>

    <BottomNav />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useContentStore } from '@/stores/content'
import { useProgressStore } from '@/stores/progress'
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const content = useContentStore()
const progressStore = useProgressStore()

// Which language's path is open (null = landing page)
const activeLangId = ref(null)

const colorMap = {
  emerald: '#003B5C',
  blue: '#1E40AF',
  amber: '#B45309',
  red: '#B91C1C',
  purple: '#7C3AED',
  pink: '#BE185D',
  orange: '#C2410C',
  teal: '#0F766E',
  cyan: '#0E7490',
  indigo: '#4338CA',
}

// Quick lookup: language id → full language object
const langMap = computed(() => {
  const m = {}
  for (const l of content.languages) m[l.id] = l
  return m
})

function langMeta(langId) {
  return langMap.value[langId] ?? { flag_emoji: '🌍', color: 'emerald' }
}

const activeLangName = computed(() => langMap.value[activeLangId.value]?.name ?? '')

// Only show a language as "currently learning" once the first lesson is done
const learningLangs = computed(() =>
  (progressStore.summary?.languages ?? []).filter(l => l.completed_lessons > 0)
)

// Show all languages except those where at least one lesson is completed
const startedIds = computed(() => new Set(learningLangs.value.map(l => l.language_id)))
const pickerLangs = computed(() =>
  content.languages.filter(l => !startedIds.value.has(l.id))
)

const currentLessonId = computed(() => {
  for (const unit of content.units) {
    for (const lesson of unit.lessons ?? []) {
      if (!progressStore.isCompleted(lesson.id)) return lesson.id
    }
  }
  return null
})

function unitCompletedCount(unit) {
  return (unit.lessons ?? []).filter(l => progressStore.isCompleted(l.id)).length
}

function unitProgressPct(unit) {
  const lessons = unit.lessons ?? []
  if (!lessons.length) return 0
  return Math.round((unitCompletedCount(unit) / lessons.length) * 100)
}

async function openLearningPath(langId) {
  activeLangId.value = langId
  await content.selectLanguage(langId)
}

async function startLang(lang) {
  // Enroll if not already enrolled
  if (!auth.user?.active_languages?.includes(lang.id)) {
    await content.enrollInLanguage(lang.id)
    await auth.fetchMe()
    await progressStore.fetchMyProgress()
  }
  await openLearningPath(lang.id)
}

onMounted(async () => {
  await content.fetchLanguages()
  await progressStore.fetchMyProgress()
})
</script>
