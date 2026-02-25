<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom">
    <!-- Header -->
    <header class="p-6 pb-2 flex justify-between items-center sticky top-0 bg-[#FDFCFB]/80 backdrop-blur-md z-20">
      <div>
        <p class="text-slate-500 font-medium">Moni, {{ firstName }} 👋</p>
        <h3 class="text-xl font-bold">Your Progress</h3>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center bg-amber-50 px-3 py-1.5 rounded-full border border-amber-100">
          <span class="material-icons-outlined text-amber-600 text-sm">local_fire_department</span>
          <span class="text-amber-700 font-bold ml-1 text-sm">{{ auth.user?.streak ?? 0 }}</span>
        </div>
        <RouterLink to="/profile" class="w-10 h-10 rounded-full border-2 border-emerald-100 p-0.5">
          <img
            :src="auth.user?.avatar_url || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(auth.user?.name || 'User') + '&background=065F46&color=fff&rounded=true'"
            class="w-full h-full rounded-full object-cover"
          />
        </RouterLink>
      </div>
    </header>

    <!-- Language Selector -->
    <div class="px-6 py-4 overflow-x-auto whitespace-nowrap flex gap-4 no-scrollbar">
      <button
        v-for="lang in content.languages"
        :key="lang.id"
        @click="content.selectLanguage(lang.id)"
        class="inline-flex items-center px-5 py-3 rounded-2xl gap-2 transition-all"
        :class="content.activeLanguageId === lang.id
          ? 'bg-emerald-900 text-white shadow-lg shadow-emerald-900/10'
          : 'bg-white border border-slate-200 text-slate-600'"
      >
        <span class="text-base">{{ lang.flag_emoji }}</span>
        <span class="text-sm font-bold tracking-widest uppercase">{{ lang.name }}</span>
      </button>
    </div>

    <!-- Learning Path -->
    <main class="p-6">
      <div v-if="content.loading" class="flex justify-center py-20">
        <div class="w-10 h-10 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
      </div>

      <template v-else-if="content.units.length">
        <div v-for="(unit, uIdx) in content.units" :key="unit.id" class="mb-12">
          <!-- Unit Card -->
          <div class="bg-emerald-50 rounded-[2.5rem] p-6 mb-12 border border-emerald-100 shadow-sm">
            <div class="flex justify-between items-start mb-4">
              <div>
                <span class="text-[10px] font-bold tracking-[0.2em] text-emerald-800 uppercase bg-emerald-200/50 px-3 py-1 rounded-full">Unit {{ uIdx + 1 }}</span>
                <h4 class="text-2xl font-bold text-emerald-950 mt-2">{{ unit.title }}</h4>
                <p class="text-emerald-800/70 text-sm">{{ unit.subtitle }}</p>
              </div>
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-sm">
                <span class="material-icons-outlined text-emerald-900">{{ unit.icon }}</span>
              </div>
            </div>
            <div class="w-full bg-white/50 h-2 rounded-full overflow-hidden">
              <div class="bg-emerald-600 h-full w-1/3 transition-all duration-700"></div>
            </div>
          </div>

          <!-- Lesson Nodes -->
          <div class="flex flex-col items-center gap-12 relative">
            <div
              v-for="(lesson, lIdx) in unit.lessons ?? []"
              :key="lesson.id"
              class="relative"
            >
              <div
                v-if="lIdx < (unit.lessons?.length ?? 0) - 1"
                class="absolute left-1/2 bottom-[-48px] w-0.5 h-10 bg-slate-200 -translate-x-1/2 z-[-1]"
              ></div>

              <!-- Completed -->
              <RouterLink v-if="lIdx === 0" :to="`/lesson/${lesson.id}`" class="group flex flex-col items-center cursor-pointer">
                <div class="w-20 h-20 bg-emerald-600 rounded-3xl rotate-45 flex items-center justify-center shadow-xl shadow-emerald-600/20 group-active:scale-90 transition-transform">
                  <span class="material-icons-outlined text-white -rotate-45 text-3xl">check</span>
                </div>
                <p class="text-center mt-4 font-bold text-slate-800">{{ lesson.title }}</p>
              </RouterLink>

              <!-- Active -->
              <RouterLink v-else-if="lIdx === 1" :to="`/lesson/${lesson.id}`" class="group flex flex-col items-center cursor-pointer">
                <div class="relative w-24 h-24 bg-white border-4 border-emerald-600 rounded-[2rem] rotate-45 flex items-center justify-center shadow-xl shadow-slate-200 group-active:scale-90 transition-transform">
                  <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center">
                    <span class="material-icons-outlined text-emerald-900 -rotate-45 text-3xl">chat_bubble</span>
                  </div>
                  <div class="absolute -top-2 -right-2 bg-amber-500 text-white text-[10px] font-bold px-2 py-1 rounded-lg -rotate-45 shadow-md">NOW</div>
                </div>
                <p class="text-center mt-6 font-bold text-slate-800">{{ lesson.title }}</p>
              </RouterLink>

              <!-- Locked -->
              <div v-else class="flex flex-col items-center opacity-40">
                <div class="w-20 h-20 bg-slate-200 rounded-3xl rotate-45 flex items-center justify-center">
                  <span class="material-icons-outlined text-slate-500 -rotate-45 text-2xl">lock</span>
                </div>
                <p class="text-center mt-4 font-medium text-slate-500">{{ lesson.title }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="text-center py-20">
        <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">language</span>
        <p class="text-slate-400 font-medium">Select a language to see your path</p>
      </div>
    </main>

    <BottomNav />
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useContentStore } from '@/stores/content'
import BottomNav from '@/components/BottomNav.vue'

const auth = useAuthStore()
const content = useContentStore()

const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'Learner')

onMounted(async () => {
  await content.fetchLanguages()
  // Default to first enrolled language or first available
  const firstLang = auth.user?.active_languages?.[0] ?? content.languages.value?.[0]?.id
  if (firstLang) await content.selectLanguage(firstLang)
  else if (content.languages.length) await content.selectLanguage(content.languages[0].id)
})
</script>
