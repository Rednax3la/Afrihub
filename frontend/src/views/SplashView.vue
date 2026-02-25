<template>
  <section class="min-h-screen flex flex-col justify-between p-8 relative overflow-hidden bg-[#FDFCFB]">
    <div class="blob w-64 h-64 bg-emerald-500 rounded-full -top-10 -left-10"></div>
    <div class="blob w-64 h-64 bg-amber-500 rounded-full bottom-20 -right-10"></div>

    <div class="mt-20">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-12 h-12 bg-emerald-800 rounded-2xl flex items-center justify-center">
          <span class="material-icons-outlined text-white">menu_book</span>
        </div>
        <h1 class="text-2xl font-bold tracking-tight text-emerald-950">Afrihub</h1>
      </div>
      <h2 class="text-5xl font-bold serif leading-tight mb-6">
        Learn the pulse of <span class="text-emerald-700 italic">Africa.</span>
      </h2>
      <p class="text-lg text-slate-600 leading-relaxed max-w-xs">
        Master vernacular languages with curriculum-backed content from native schools.
      </p>
    </div>

    <div class="space-y-4 mb-8">
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
    </div>
  </section>
</template>
