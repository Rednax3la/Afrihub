<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <header class="px-6 pt-6 pb-2 sticky top-0 bg-[#FDFCFB]/80 backdrop-blur-md z-20">
        <h3 class="text-xl font-bold text-slate-900">Leaderboard</h3>
        <p class="text-slate-500 font-medium text-sm">Top learners this week</p>
      </header>

      <!-- Language Selector -->
      <div class="px-6 py-4 overflow-x-auto whitespace-nowrap flex gap-4 no-scrollbar">
        <button
          v-for="lang in content.languages"
          :key="lang.id"
          @click="selectLang(lang.id)"
          class="inline-flex items-center px-5 py-3 rounded-2xl gap-2 transition-all"
          :class="selectedLanguageId === lang.id
            ? 'bg-emerald-900 text-white shadow-lg shadow-emerald-900/10'
            : 'bg-white border border-slate-200 text-slate-600'"
        >
          <span class="text-base">{{ lang.flag_emoji }}</span>
          <span class="text-sm font-bold tracking-widest uppercase">{{ lang.name }}</span>
        </button>
      </div>

      <main class="px-4 pb-24">
        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-20">
          <div class="w-10 h-10 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
        </div>

        <!-- Empty -->
        <div v-else-if="!entries.length" class="text-center py-20">
          <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">leaderboard</span>
          <p class="text-slate-400 font-medium">No learners yet for this language.</p>
        </div>

        <!-- List -->
        <div v-else class="space-y-3">
          <!-- Top 3 podium-style -->
          <div v-for="(entry, idx) in entries" :key="entry.id"
            class="flex items-center gap-4 px-5 py-4 rounded-3xl border transition-all"
            :class="[
              entry.id === auth.user?._id || entry.id === currentUserId
                ? 'bg-emerald-50 border-emerald-200 shadow-sm'
                : 'bg-white border-slate-100',
              idx === 0 ? 'ring-2 ring-amber-300' : ''
            ]"
          >
            <!-- Rank -->
            <div class="w-9 text-center shrink-0">
              <span v-if="idx === 0" class="text-2xl">🥇</span>
              <span v-else-if="idx === 1" class="text-2xl">🥈</span>
              <span v-else-if="idx === 2" class="text-2xl">🥉</span>
              <span v-else class="text-base font-bold text-slate-400">#{{ idx + 1 }}</span>
            </div>

            <!-- Avatar -->
            <img
              :src="entry.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(entry.name)}&background=065F46&color=fff&rounded=true&size=80`"
              class="w-11 h-11 rounded-full object-cover shrink-0 border-2"
              :class="entry.id === currentUserId ? 'border-emerald-500' : 'border-slate-100'"
            />

            <!-- Name -->
            <div class="flex-1 min-w-0">
              <p class="font-bold text-slate-900 truncate">
                {{ entry.name }}
                <span v-if="entry.id === currentUserId" class="text-xs text-emerald-700 font-bold ml-1">(you)</span>
              </p>
              <div class="flex items-center gap-1 mt-0.5">
                <span class="material-icons-outlined text-amber-500 text-xs">local_fire_department</span>
                <span class="text-xs text-slate-500 font-medium">{{ entry.streak }} day streak</span>
              </div>
            </div>

            <!-- XP -->
            <div class="text-right shrink-0">
              <p class="font-bold text-emerald-700 text-base">{{ entry.xp.toLocaleString() }}</p>
              <p class="text-xs text-slate-400 font-bold uppercase tracking-wide">XP</p>
            </div>
          </div>
        </div>
      </main>
    </div>

    <BottomNav />
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useContentStore } from '@/stores/content'
import { contentApi } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const content = useContentStore()

const selectedLanguageId = ref(null)
const entries = ref([])
const loading = ref(false)

// Normalize user ID for comparison (MongoDB ObjectId can be nested)
const currentUserId = computed(() => {
  const u = auth.user
  if (!u) return null
  return u._id?.$oid ?? u._id ?? u.id ?? null
})

async function fetchLeaderboard(langId) {
  if (!langId) return
  loading.value = true
  try {
    const { data } = await contentApi.getLeaderboard(langId)
    entries.value = data
  } catch {
    entries.value = []
  } finally {
    loading.value = false
  }
}

function selectLang(id) {
  selectedLanguageId.value = id
}

watch(selectedLanguageId, (id) => fetchLeaderboard(id))

onMounted(async () => {
  await content.fetchLanguages()
  const firstLang = auth.user?.active_languages?.[0] ?? content.languages[0]?.id
  if (firstLang) selectLang(firstLang)
})
</script>
