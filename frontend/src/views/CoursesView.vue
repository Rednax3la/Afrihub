<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <header class="px-6 pt-6 pb-2 sticky top-0 bg-[#FDFCFB]/80 backdrop-blur-md z-20">
        <h3 class="text-2xl font-bold text-slate-900">Explore Languages</h3>
        <p class="text-slate-500 text-sm mt-1">50+ African vernaculars, taught by native tutors.</p>
      </header>

      <!-- Search -->
      <div class="px-6 py-3">
        <div class="flex items-center bg-white border border-slate-200 rounded-2xl px-4 py-3 gap-3">
          <span class="material-icons-outlined text-slate-400">search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search languages..."
            class="flex-1 outline-none text-slate-700 bg-transparent placeholder-slate-400"
          />
        </div>
      </div>

      <!-- Region Filter -->
      <div class="px-6 py-3 overflow-x-auto whitespace-nowrap flex gap-3 no-scrollbar">
        <button
          v-for="region in regions"
          :key="region"
          @click="activeRegion = region"
          class="px-4 py-2 rounded-xl text-sm font-semibold transition-all"
          :class="activeRegion === region
            ? 'bg-[#003B5C] text-white'
            : 'bg-white border border-slate-200 text-slate-600'"
        >
          {{ region }}
        </button>
      </div>

      <!-- Currently Learning -->
      <div v-if="auth.user?.active_languages?.length" class="px-6 mt-4 mb-2">
        <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">Currently Learning</h4>
        <div class="space-y-3">
          <RouterLink
            v-for="lang in activeLangs"
            :key="lang.id"
            to="/dashboard"
            class="flex items-center gap-4 bg-white border border-slate-100 rounded-3xl p-4 shadow-sm"
          >
            <div
              class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold text-white"
              :style="{ backgroundColor: colorMap[lang.color] || '#003B5C' }"
            >
              {{ lang.flag_emoji }}
            </div>
            <div class="flex-1">
              <h5 class="font-bold text-slate-900">{{ lang.name }}</h5>
              <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                <div class="bg-[#00A3C1] h-full w-1/5"></div>
              </div>
            </div>
            <span class="text-xs font-bold text-[#00A3C1]">CONTINUE →</span>
          </RouterLink>
        </div>
      </div>

      <!-- All Languages -->
      <div class="px-6 mt-6">
        <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">All Languages</h4>

        <div v-if="content.loading" class="flex justify-center py-10">
          <div class="w-8 h-8 border-4 border-[#A7FFEB] border-t-[#00A3C1] rounded-full animate-spin"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="lang in filteredLanguages"
            :key="lang.id"
            class="bg-white border border-slate-100 rounded-3xl p-5 shadow-sm overflow-hidden relative"
          >

            <div class="flex items-start gap-4">
              <div
                class="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shrink-0"
                :style="{ backgroundColor: `${colorMap[lang.color]}20` }"
              >
                {{ lang.flag_emoji }}
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h5 class="font-bold text-slate-900 text-lg">{{ lang.name }}</h5>
                  <span class="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-medium">{{ lang.country }}</span>
                </div>
                <p class="text-slate-500 text-sm mt-1 leading-relaxed">{{ lang.description }}</p>
                <div class="flex items-center gap-2 mt-3">
                  <span class="material-icons-outlined text-slate-400 text-sm">people</span>
                  <span class="text-xs text-slate-400 font-medium">{{ lang.speaker_count }} speakers</span>
                </div>
              </div>
            </div>

            <div class="mt-4">
              <button
                v-if="!isEnrolled(lang.id)"
                @click="enroll(lang)"
                class="w-full py-3 rounded-2xl font-bold text-sm transition-all active:scale-95 bg-[#003B5C] text-white shadow-md shadow-[#003B5C]/10"
              >
                + Start Learning
              </button>
              <RouterLink
                v-else
                to="/dashboard"
                class="block w-full py-3 rounded-2xl font-bold text-sm text-center bg-[#A7FFEB]/30 text-[#003B5C] border border-[#00A3C1]/30"
              >
                Continue Learning →
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Verified Tutors -->
      <div v-if="tutors.length" class="px-6 mt-10 mb-4">
        <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">Our Tutors</h4>
        <div class="space-y-3">
          <div v-for="tutor in tutors" :key="tutor.id"
            class="bg-white border border-slate-100 rounded-3xl p-4 flex items-center gap-4 shadow-sm"
          >
            <img
              :src="tutor.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=003B5C&color=fff&rounded=true&size=128`"
              class="w-14 h-14 rounded-2xl object-cover shrink-0"
            />
            <div class="flex-1 min-w-0">
              <p class="text-[10px] font-bold text-amber-600 tracking-wider uppercase">
                Verified Tutor · {{ tutor.languages_taught?.join(', ') || '' }}
              </p>
              <h5 class="font-bold text-slate-900">{{ tutor.name }}</h5>
              <p v-if="tutor.bio" class="text-xs text-slate-500 truncate">{{ tutor.bio }}</p>
            </div>
            <span class="material-icons-outlined text-[#00A3C1] shrink-0">verified</span>
          </div>
        </div>
      </div>
    </div>

    <BottomNav />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useContentStore } from '@/stores/content'
import { tutorApi } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const content = useContentStore()
const searchQuery = ref('')
const activeRegion = ref('All')
const tutors = ref([])

const regions = ['All', 'West Africa', 'East Africa', 'Southern Africa', 'North Africa']

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

const filteredLanguages = computed(() => {
  return content.languages.filter((l) => {
    const matchesSearch = l.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesRegion = activeRegion.value === 'All' || l.region === activeRegion.value
    return matchesSearch && matchesRegion
  })
})

const activeLangs = computed(() =>
  content.languages.filter((l) => auth.user?.active_languages?.includes(l.id))
)

function isEnrolled(langId) {
  return auth.user?.active_languages?.includes(langId)
}

async function enroll(lang) {
  await content.enrollInLanguage(lang.id)
  await auth.fetchMe()
  content.selectLanguage(lang.id)
}

onMounted(async () => {
  await content.fetchLanguages()
  try {
    const { data } = await tutorApi.listActiveTutors()
    tutors.value = data
  } catch { /* tutors section remains empty */ }
})
</script>
