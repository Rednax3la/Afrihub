<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col md:flex-row">
    <!-- Left branding panel (desktop only) -->
    <div class="hidden md:flex flex-col justify-between w-1/2 bg-emerald-950 p-16 relative overflow-hidden">
      <div class="absolute top-0 right-0 w-80 h-80 bg-emerald-800 rounded-full blur-[120px] opacity-30 -mr-40 -mt-40"></div>
      <div class="absolute bottom-0 left-0 w-80 h-80 bg-amber-600 rounded-full blur-[120px] opacity-10 -ml-40 -mb-40"></div>

      <div class="flex items-center gap-3 relative">
        <div class="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center">
          <span class="material-icons-outlined text-white text-2xl">menu_book</span>
        </div>
        <span class="text-xl font-bold text-white tracking-tight">Vernaculearn</span>
      </div>

      <div class="relative">
        <h2 class="text-5xl font-bold serif text-white leading-tight mb-6">
          Learn the pulse of <span class="text-amber-400 italic">Africa.</span>
        </h2>
        <p class="text-emerald-200/70 text-lg leading-relaxed max-w-sm">
          Master vernacular languages with authentic lessons from native-speaking tutors.
        </p>
        <div class="flex gap-4 mt-10">
          <div class="flex items-center gap-2 bg-white/10 rounded-2xl px-4 py-3">
            <span class="material-icons-outlined text-amber-400 text-sm">language</span>
            <span class="text-white text-sm font-semibold">50+ Languages</span>
          </div>
          <div class="flex items-center gap-2 bg-white/10 rounded-2xl px-4 py-3">
            <span class="material-icons-outlined text-emerald-400 text-sm">people</span>
            <span class="text-white text-sm font-semibold">Native Tutors</span>
          </div>
        </div>
      </div>

      <p class="text-emerald-200/30 text-xs relative">© 2026 Vernaculearn</p>
    </div>

    <!-- Right / Mobile content -->
    <div class="flex-1 flex flex-col justify-between p-8 md:p-16 relative overflow-hidden">
      <div class="blob w-64 h-64 bg-emerald-500 rounded-full -top-10 -left-10"></div>
      <div class="blob w-64 h-64 bg-amber-500 rounded-full bottom-20 -right-10"></div>

      <!-- Mobile logo -->
      <div class="mt-12 md:hidden">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-12 h-12 bg-emerald-800 rounded-2xl flex items-center justify-center">
            <span class="material-icons-outlined text-white">menu_book</span>
          </div>
          <h1 class="text-2xl font-bold tracking-tight text-emerald-950">Vernaculearn</h1>
        </div>
        <h2 class="text-5xl font-bold serif leading-tight mb-6">
          Learn the pulse of <span class="text-emerald-700 italic">Africa.</span>
        </h2>
        <p class="text-lg text-slate-600 leading-relaxed max-w-xs">
          Master vernacular languages with authentic lessons from native-speaking tutors.
        </p>
      </div>

      <!-- Desktop heading -->
      <div class="hidden md:flex flex-col justify-center flex-1">
        <h2 class="text-4xl font-bold serif text-emerald-950 leading-tight mb-3">
          Begin your journey
        </h2>
        <p class="text-slate-500 text-lg mb-10">Connect with your heritage, one lesson at a time.</p>

        <div class="space-y-4 max-w-sm">
          <RouterLink
            to="/register"
            class="block w-full bg-emerald-900 text-white py-5 rounded-3xl font-semibold text-lg text-center shadow-xl shadow-emerald-900/20 active:scale-95 transition-transform"
          >
            Start Learning
          </RouterLink>
          <RouterLink
            to="/login"
            class="block w-full bg-white border border-slate-200 text-slate-800 py-5 rounded-3xl font-semibold text-lg text-center active:scale-95 transition-transform"
          >
            I already have an account
          </RouterLink>
          <RouterLink
            to="/register/tutor"
            class="block w-full text-center text-sm text-slate-400 hover:text-emerald-700 font-semibold py-2 transition-colors"
          >
            Apply as a Tutor →
          </RouterLink>
        </div>
      </div>

      <!-- Mobile CTA -->
      <div class="space-y-4 mb-8 md:hidden">
        <RouterLink
          to="/register"
          class="block w-full bg-emerald-900 text-white py-5 rounded-3xl font-semibold text-lg text-center shadow-xl shadow-emerald-900/20 active:scale-95 transition-transform"
        >
          Start Learning
        </RouterLink>
        <RouterLink
          to="/login"
          class="block w-full bg-white border border-slate-200 text-slate-800 py-5 rounded-3xl font-semibold text-lg text-center active:scale-95 transition-transform"
        >
          I already have an account
        </RouterLink>
        <RouterLink to="/register/tutor" class="block w-full text-center text-sm text-slate-400 font-semibold py-2">
          Apply as a Tutor →
        </RouterLink>
      </div>
    </div>
  </section>
</template>
