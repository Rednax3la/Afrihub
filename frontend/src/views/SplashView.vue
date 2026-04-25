<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col relative overflow-hidden">

    <!-- Decorative blobs -->
    <div class="pointer-events-none select-none absolute -top-32 -right-32 w-[500px] h-[500px] bg-[#A7FFEB] rounded-full blur-[100px] opacity-50"></div>
    <div class="pointer-events-none select-none absolute -bottom-40 -left-32 w-[420px] h-[420px] bg-[#00E5FF] rounded-full blur-[100px] opacity-20"></div>

    <!-- Nav -->
    <nav class="relative z-10 flex items-center justify-between px-6 md:px-16 pt-8">
      <div class="flex items-center gap-2">
        <img src="/Vernaculearn logo.png" alt="Vernaculearn" class="h-9 w-auto" />
        <span class="text-xl font-bold tracking-tight text-[#003B5C] hidden sm:inline">Vernaculearn</span>
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
    <div class="relative z-10 pb-8 flex flex-col items-center gap-4">
      <RouterLink
        to="/register/tutor"
        class="text-sm text-slate-400 hover:text-[#00A3C1] font-semibold transition-colors"
      >
        Are you a native speaker? Apply as a Tutor →
      </RouterLink>

      <!-- Social icons -->
      <div class="flex items-center gap-5">
        <!-- Instagram -->
        <a href="https://instagram.com/vernaculearn.africa" target="_blank" rel="noopener" aria-label="Instagram" class="text-slate-300 hover:text-[#E1306C] transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
          </svg>
        </a>
        <!-- X (Twitter) -->
        <a href="https://x.com/vernaculearn" target="_blank" rel="noopener" aria-label="X" class="text-slate-300 hover:text-slate-800 transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
        </a>
        <!-- TikTok -->
        <a href="https://tiktok.com/@vernaculearn.africa" target="_blank" rel="noopener" aria-label="TikTok" class="text-slate-300 hover:text-slate-800 transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.85a8.18 8.18 0 004.78 1.52V6.92a4.85 4.85 0 01-1.01-.23z"/>
          </svg>
        </a>
      </div>

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
