<template>
  <section class="min-h-screen bg-slate-50 safe-bottom md:pl-64">
    <div class="max-w-2xl mx-auto">
      <!-- Hero card -->
      <div class="bg-white p-8 pt-16 pb-12 md:pt-10 rounded-b-[3rem] shadow-sm relative overflow-hidden">
        <div class="blob w-40 h-40 bg-emerald-100 rounded-full -top-10 -right-10"></div>

        <div class="flex flex-col items-center">
          <div class="relative mb-4">
            <img
              :src="auth.user?.avatar_url || avatarUrl"
              class="w-28 h-28 rounded-full object-cover border-4 border-emerald-50"
            />
            <div class="absolute bottom-0 right-0 w-8 h-8 bg-emerald-600 rounded-full border-4 border-white flex items-center justify-center cursor-pointer">
              <span class="material-icons-outlined text-white text-[12px]">edit</span>
            </div>
          </div>
          <h2 class="text-2xl font-bold text-slate-900">{{ auth.user?.name }}</h2>
          <p class="text-slate-500 font-medium flex items-center gap-1 mt-1">
            <span class="material-icons-outlined text-sm">location_on</span>
            {{ auth.user?.location || 'Somewhere in Africa 🌍' }}
          </p>

          <!-- Stats -->
          <div class="flex gap-4 mt-8 w-full">
            <div class="flex-1 text-center bg-slate-50 p-4 rounded-3xl">
              <p class="text-2xl font-bold text-slate-900">{{ auth.user?.xp ?? 0 }}</p>
              <p class="text-xs text-slate-500 font-bold tracking-wider uppercase">XP</p>
            </div>
            <div class="flex-1 text-center bg-slate-50 p-4 rounded-3xl">
              <p class="text-2xl font-bold text-slate-900">{{ auth.user?.streak ?? 0 }}</p>
              <p class="text-xs text-slate-500 font-bold tracking-wider uppercase">Streak</p>
            </div>
            <div class="flex-1 text-center bg-slate-50 p-4 rounded-3xl">
              <p class="text-2xl font-bold text-slate-900">{{ earnedBadgeCount }}</p>
              <p class="text-xs text-slate-500 font-bold tracking-wider uppercase">Badges</p>
            </div>
          </div>

          <!-- Earned Badges Row -->
          <div v-if="earnedBadgeIcons.length" class="flex gap-2 mt-4 flex-wrap justify-center">
            <span
              v-for="icon in earnedBadgeIcons"
              :key="icon"
              class="text-2xl w-11 h-11 flex items-center justify-center bg-slate-50 rounded-2xl border border-slate-100"
              :title="icon"
            >{{ icon }}</span>
          </div>
        </div>
      </div>

      <div class="p-6">
        <!-- Active Courses -->
        <h4 class="text-sm font-bold text-slate-400 mb-4 tracking-widest uppercase">My Courses</h4>

        <div v-if="progressLangs.length" class="space-y-4 mb-8">
          <div v-for="lang in progressLangs" :key="lang.language_id"
            class="bg-white p-5 rounded-3xl flex items-center gap-4 shadow-sm border border-slate-100"
          >
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-xl bg-slate-50">
              {{ lang.flag_emoji }}
            </div>
            <div class="flex-1">
              <h5 class="font-bold">{{ lang.language_name }}</h5>
              <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                <div class="bg-emerald-600 h-full transition-all duration-700" :style="{ width: `${lang.percent_complete}%` }"></div>
              </div>
            </div>
            <span class="text-sm font-bold text-emerald-700">{{ lang.percent_complete }}%</span>
          </div>
        </div>

        <div v-else class="bg-white rounded-3xl p-6 text-center border border-slate-100 shadow-sm mb-8">
          <span class="material-icons-outlined text-3xl text-slate-300 mb-2 block">language</span>
          <p class="text-slate-400 text-sm">No languages yet.</p>
          <RouterLink to="/courses" class="text-emerald-700 font-semibold text-sm mt-1 block">Browse courses →</RouterLink>
        </div>

        <!-- Settings -->
        <h4 class="text-sm font-bold text-slate-400 mb-4 tracking-widest uppercase">Settings</h4>
        <div class="bg-white rounded-[2rem] overflow-hidden shadow-sm border border-slate-100">
          <div class="p-5 flex justify-between items-center border-b border-slate-50">
            <div class="flex items-center gap-4">
              <span class="material-icons-outlined text-slate-400">notifications</span>
              <span class="font-medium">Learning Reminders</span>
            </div>
            <div
              @click="reminders = !reminders"
              class="w-12 h-6 rounded-full p-1 relative cursor-pointer transition-colors"
              :class="reminders ? 'bg-emerald-600' : 'bg-slate-200'"
            >
              <div class="w-4 h-4 bg-white rounded-full absolute top-1 transition-all" :class="reminders ? 'right-1' : 'left-1'"></div>
            </div>
          </div>

          <RouterLink to="/subscription" class="p-5 flex justify-between items-center border-b border-slate-50 cursor-pointer">
            <div class="flex items-center gap-4">
              <span class="material-icons-outlined text-amber-500">workspace_premium</span>
              <span class="font-medium text-amber-600">
                {{ auth.user?.is_premium ? 'Vernaculearn Premium ✓' : 'Upgrade to Premium' }}
              </span>
            </div>
            <span class="material-icons-outlined text-slate-300">chevron_right</span>
          </RouterLink>

          <button @click="logout" class="w-full p-5 flex justify-between items-center cursor-pointer">
            <div class="flex items-center gap-4 text-red-500">
              <span class="material-icons-outlined">logout</span>
              <span class="font-medium">Log Out</span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <BottomNav />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProgressStore } from '@/stores/progress'
import { contentApi } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const progressStore = useProgressStore()
const router = useRouter()
const reminders = ref(true)
const allBadges = ref([])

const avatarUrl = computed(() =>
  `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.name || 'U')}&background=065F46&color=fff&rounded=true&size=200`
)

// Per-language progress from the progress store
const progressLangs = computed(() => progressStore.summary?.languages ?? [])

// Earned badges
const earnedBadgeCount = computed(() => auth.user?.earned_badges?.length ?? 0)
const earnedBadgeIcons = computed(() => {
  const earned = new Set(auth.user?.earned_badges ?? [])
  return allBadges.value
    .filter(b => earned.has(b.id))
    .map(b => b.icon)
})

function logout() {
  auth.logout()
  router.push('/')
}

onMounted(async () => {
  await Promise.all([
    progressStore.fetchMyProgress(),
    contentApi.getBadges().then(({ data }) => { allBadges.value = data }).catch(() => {}),
  ])
})
</script>
