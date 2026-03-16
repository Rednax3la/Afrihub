<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col relative overflow-hidden">

    <!-- Decorative blobs -->
    <div class="pointer-events-none select-none absolute -top-32 -right-32 w-[500px] h-[500px] bg-emerald-100 rounded-full blur-[100px] opacity-60"></div>
    <div class="pointer-events-none select-none absolute -bottom-40 -left-32 w-[420px] h-[420px] bg-amber-100 rounded-full blur-[100px] opacity-50"></div>

    <!-- Nav -->
    <nav class="relative z-10 flex items-center justify-between px-6 md:px-16 pt-8">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-emerald-900 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-900/20">
          <span class="material-icons-outlined text-white text-xl">menu_book</span>
        </div>
        <span class="text-xl font-bold tracking-tight text-slate-900">Vernaculearn</span>
      </div>
      <RouterLink
        to="/login"
        class="text-base font-semibold text-slate-500 hover:text-slate-900 transition-colors"
      >Sign in</RouterLink>
    </nav>

    <!-- Hero -->
    <div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-12 md:py-20">

      <!-- Badge -->
      <div class="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-full px-4 py-1.5 mb-8">
        <span class="text-base">🌍</span>
        <span class="text-base font-semibold text-emerald-800">Authentic lessons from native tutors</span>
      </div>

      <!-- Headline -->
      <h1 class="text-6xl md:text-8xl font-bold text-slate-900 leading-[1.05] mb-8 max-w-4xl">
        Learn the pulse<br />of
        <span class="text-emerald-700 italic">Africa.</span>
      </h1>

      <!-- Sub -->
      <p class="text-xl md:text-2xl text-slate-500 leading-relaxed max-w-2xl mb-12">
        Master vernacular languages — Kikuyu, Yoruba, Swahili, Zulu and hundreds more — one lesson at a time.
      </p>

      <!-- CTAs -->
      <div class="flex flex-col sm:flex-row gap-4 w-full max-w-xs sm:max-w-none sm:justify-center">
        <RouterLink
          to="/register"
          class="bg-emerald-900 text-white px-10 py-5 rounded-2xl font-bold text-lg shadow-xl shadow-emerald-900/20 hover:bg-emerald-800 active:scale-95 transition-all"
        >
          Start Learning
        </RouterLink>
        <RouterLink
          to="/login"
          class="bg-white border border-slate-200 text-slate-800 px-10 py-5 rounded-2xl font-bold text-lg hover:border-slate-300 active:scale-95 transition-all"
        >
          I have an account
        </RouterLink>
      </div>

      <!-- Feature pills -->
      <div class="flex flex-wrap gap-3 justify-center mt-14 max-w-2xl">
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-emerald-600">verified</span> Native speaker tutors
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-amber-500">local_fire_department</span> Daily streaks
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-100 rounded-full px-5 py-3 text-base text-slate-600 font-medium shadow-sm">
          <span class="material-icons-outlined text-emerald-600">headphones</span> Audio-first lessons
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
        class="text-sm text-slate-400 hover:text-emerald-700 font-semibold transition-colors"
      >
        Are you a native speaker? Apply as a Tutor →
      </RouterLink>
      <p class="text-xs text-slate-300">© 2026 Vernaculearn</p>
    </div>

  </section>
</template>

<script setup>
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
