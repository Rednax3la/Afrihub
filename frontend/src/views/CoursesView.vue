<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom">
    <!-- Header -->
    <header class="p-6 pb-2 sticky top-0 bg-[#FDFCFB]/80 backdrop-blur-md z-20">
      <h3 class="text-2xl font-bold text-slate-900">Explore Languages</h3>
      <p class="text-slate-500 text-sm mt-1">50+ African vernaculars, curriculum-backed.</p>
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
          ? 'bg-emerald-900 text-white'
          : 'bg-white border border-slate-200 text-slate-600'"
      >
        {{ region }}
      </button>
    </div>

    <!-- Your Active Languages -->
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
            :style="{ backgroundColor: colorMap[lang.color] || '#065F46' }"
          >
            {{ lang.flag_emoji }}
          </div>
          <div class="flex-1">
            <h5 class="font-bold text-slate-900">{{ lang.name }}</h5>
            <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
              <div class="bg-emerald-500 h-full w-1/5"></div>
            </div>
          </div>
          <span class="text-xs font-bold text-emerald-700">CONTINUE →</span>
        </RouterLink>
      </div>
    </div>

    <!-- All Languages -->
    <div class="px-6 mt-6">
      <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">All Languages</h4>

      <div v-if="content.loading" class="flex justify-center py-10">
        <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
      </div>

      <div class="space-y-4">
        <div
          v-for="lang in filteredLanguages"
          :key="lang.id"
          class="bg-white border border-slate-100 rounded-3xl p-5 shadow-sm overflow-hidden relative"
        >
          <!-- Premium badge -->
          <div v-if="!lang.is_free && !auth.user?.is_premium"
            class="absolute top-0 right-0 bg-amber-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-2xl"
          >
            PREMIUM
          </div>

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
              :disabled="!lang.is_free && !auth.user?.is_premium"
              class="w-full py-3 rounded-2xl font-bold text-sm transition-all active:scale-95"
              :class="lang.is_free || auth.user?.is_premium
                ? 'bg-emerald-900 text-white shadow-md shadow-emerald-900/10'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
            >
              {{ lang.is_free || auth.user?.is_premium ? '+ Start Learning' : '🔒 Premium Only' }}
            </button>
            <RouterLink
              v-else
              to="/dashboard"
              class="block w-full py-3 rounded-2xl font-bold text-sm text-center bg-emerald-50 text-emerald-800 border border-emerald-200"
            >
              Continue Learning →
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Partner Schools -->
    <div class="px-6 mt-10 mb-4">
      <h4 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-4">Partner Schools</h4>
      <div class="space-y-3">
        <div v-for="school in partnerSchools" :key="school.name"
          class="bg-white border border-slate-100 rounded-3xl p-4 flex items-center gap-4 shadow-sm"
        >
          <img :src="school.img" class="w-14 h-14 rounded-2xl object-cover shrink-0" />
          <div class="flex-1">
            <p class="text-[10px] font-bold text-amber-600 tracking-wider">OFFICIAL PARTNER</p>
            <h5 class="font-bold text-slate-900">{{ school.name }}</h5>
            <p class="text-xs text-slate-500">{{ school.curriculum }}</p>
          </div>
          <span class="material-icons-outlined text-emerald-500">verified</span>
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
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const content = useContentStore()
const searchQuery = ref('')
const activeRegion = ref('All')

const regions = ['All', 'West Africa', 'East Africa', 'Southern Africa', 'North Africa']

const colorMap = {
  emerald: '#065F46',
  blue: '#1E40AF',
  amber: '#B45309',
  red: '#B91C1C',
}

const partnerSchools = [
  {
    name: 'Lagos Academy of Arts',
    curriculum: 'Yoruba – Units 1–4',
    img: 'https://images.pexels.com/photos/1007066/pexels-photo-1007066.jpeg?auto=compress&cs=tinysrgb&w=200',
  },
  {
    name: 'Nairobi Language Institute',
    curriculum: 'Swahili – All Units',
    img: 'https://images.pexels.com/photos/256490/pexels-photo-256490.jpeg?auto=compress&cs=tinysrgb&w=200',
  },
]

const filteredLanguages = computed(() => {
  return content.languages.filter((l) =>
    l.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const activeLangs = computed(() =>
  content.languages.filter((l) => auth.user?.active_languages?.includes(l.id))
)

function isEnrolled(langId) {
  return auth.user?.active_languages?.includes(langId)
}

async function enroll(lang) {
  await content.enrollInLanguage(lang.id)
  await auth.fetchMe() // refresh user to update active_languages
  content.selectLanguage(lang.id)
}

onMounted(() => content.fetchLanguages())
</script>
