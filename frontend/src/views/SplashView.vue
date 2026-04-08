<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col relative overflow-hidden">

    <!-- Decorative blobs -->
    <div class="pointer-events-none select-none absolute -top-32 -right-32 w-[500px] h-[500px] bg-[#A7FFEB] rounded-full blur-[100px] opacity-50"></div>
    <div class="pointer-events-none select-none absolute -bottom-40 -left-32 w-[420px] h-[420px] bg-[#00E5FF] rounded-full blur-[100px] opacity-20"></div>

    <!-- Nav -->
    <nav class="relative z-10 flex items-center justify-between px-6 md:px-16 pt-8">
      <div class="flex items-center gap-3">
        <img src="/Vernaculearn logo.png" alt="Vernaculearn" class="h-9 w-auto" />
      </div>
      <RouterLink
        to="/login"
        class="text-base font-semibold text-slate-500 hover:text-[#003B5C] transition-colors"
      >Sign in</RouterLink>
    </nav>

    <!-- Hero -->
    <div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-12 md:py-20">

      <!-- Badge -->
      <div class="inline-flex items-center gap-2 bg-[#A7FFEB]/50 border border-[#00A3C1]/30 rounded-full px-4 py-1.5 mb-8">
        <span class="text-base">🌍</span>
        <span class="text-base font-semibold text-[#003B5C]">Authentic lessons from native tutors</span>
      </div>

      <!-- Headline -->
      <h1 class="text-6xl md:text-8xl font-bold text-slate-900 leading-[1.05] mb-8 max-w-4xl">
        Learn the pulse<br />of
        <span class="text-[#00A3C1] italic">Africa.</span>
      </h1>

      <!-- Sub -->
      <p class="text-xl md:text-2xl text-slate-500 leading-relaxed max-w-2xl mb-12">
        Master vernacular languages — Kikuyu, Yoruba, Swahili, Zulu and hundreds more — one lesson at a time.
      </p>

      <!-- CTAs -->
      <div class="flex flex-col sm:flex-row gap-4 w-full max-w-xs sm:max-w-none sm:justify-center">
        <RouterLink
          to="/register"
          class="bg-[#003B5C] text-white px-10 py-5 rounded-2xl font-bold text-lg shadow-xl shadow-[#003B5C]/20 hover:bg-[#00A3C1] active:scale-95 transition-all"
        >
          Start Learning
        </RouterLink>
        <RouterLink
          to="/login"
          class="bg-white border border-slate-200 text-slate-800 px-10 py-5 rounded-2xl font-bold text-lg hover:border-[#00A3C1] active:scale-95 transition-all"
        >
          I have an account
        </RouterLink>
      </div>

      <!-- Waitlist email capture -->
      <div class="mt-12 w-full max-w-md">
        <p class="text-sm text-slate-400 mb-3">Works on 2G · Offline capable · Launching soon in your region</p>
        <div v-if="!waitlistSuccess" class="flex gap-2">
          <input
            v-model="waitlistEmail"
            type="email"
            placeholder="your@email.com"
            @keydown.enter="joinWaitlist"
            class="flex-1 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-[#00A3C1] transition-colors bg-white"
          />
          <button
            @click="joinWaitlist"
            :disabled="waitlistLoading"
            class="bg-[#003B5C] text-white px-5 py-3 rounded-xl font-bold text-sm active:scale-95 transition-all disabled:opacity-50"
          >
            {{ waitlistLoading ? '…' : 'Notify me' }}
          </button>
        </div>
        <div v-else class="flex items-center gap-2 justify-center text-[#003B5C] font-semibold text-sm">
          <span class="material-icons-outlined text-[#00A3C1]">check_circle</span>
          You're in! We'll notify you at launch.
        </div>
      </div>

      <!-- Feature pills -->
      <div class="flex flex-wrap gap-3 justify-center mt-14 max-w-2xl">
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-[#00A3C1]">verified</span> Native speaker tutors
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-amber-500">local_fire_department</span> Daily streaks
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-[#00A3C1]">headphones</span> Audio-first lessons
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-purple-500">language</span> 50+ languages
        </div>
      </div>

      <!-- Language showcase -->
      <div class="flex flex-wrap gap-2 justify-center mt-10 max-w-2xl opacity-60">
        <span v-for="lang in languages" :key="lang.name"
          class="text-sm font-semibold text-slate-500 bg-slate-100 rounded-full px-4 py-1.5">
          {{ lang.flag }} {{ lang.name }}
        </span>
      </div>
    </div>

    <!-- Footer -->
    <div class="relative z-10 pb-8 flex flex-col items-center gap-3">
      <RouterLink
        to="/register/tutor"
        class="text-sm text-slate-400 hover:text-[#00A3C1] font-semibold transition-colors"
      >
        Are you a native speaker? Apply as a Tutor →
      </RouterLink>
      <p class="text-xs text-slate-300">© 2026 Vernaculearn</p>
    </div>

  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { waitlistApi } from '@/api'

const waitlistEmail = ref('')
const waitlistLoading = ref(false)
const waitlistSuccess = ref(false)

onMounted(() => {
  waitlistSuccess.value = !!localStorage.getItem('vl_waitlist')
})

async function joinWaitlist() {
  const email = waitlistEmail.value.trim()
  if (!email || waitlistLoading.value) return
  waitlistLoading.value = true
  try {
    await waitlistApi.join(email)
    waitlistSuccess.value = true
    localStorage.setItem('vl_waitlist', email)
  } catch {
    // silent — still show success to avoid friction
    waitlistSuccess.value = true
    localStorage.setItem('vl_waitlist', email)
  } finally {
    waitlistLoading.value = false
  }
}

const languages = [
  { name: 'Kikuyu', flag: '🇰🇪' },
  { name: 'Yoruba', flag: '🇳🇬' },
  { name: 'Swahili', flag: '🌍' },
  { name: 'Zulu', flag: '🇿🇦' },
  { name: 'Amharic', flag: '🇪🇹' },
  { name: 'Igbo', flag: '🇳🇬' },
  { name: 'Hausa', flag: '🇳🇬' },
  { name: 'Shona', flag: '🇿🇼' },
  { name: 'Wolof', flag: '🇸🇳' },
  { name: 'Twi', flag: '🇬🇭' },
  { name: 'Luo', flag: '🇰🇪' },
  { name: 'Xhosa', flag: '🇿🇦' },
]
</script>
