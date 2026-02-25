<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col items-center justify-center p-8 text-center">
    <div class="blob w-48 h-48 bg-emerald-300 rounded-full -top-10 -left-10 absolute"></div>
    <div class="blob w-48 h-48 bg-amber-300 rounded-full bottom-10 -right-10 absolute"></div>

    <div class="relative z-10">
      <div class="w-24 h-24 bg-emerald-50 rounded-3xl mx-auto mb-6 flex items-center justify-center">
        <span class="material-icons-outlined text-5xl text-emerald-400">explore_off</span>
      </div>
      <h1 class="text-6xl font-bold serif text-emerald-900 mb-3">404</h1>
      <h2 class="text-2xl font-bold text-slate-800 mb-3">Page not found</h2>
      <p class="text-slate-500 max-w-xs mb-10">
        Looks like you've wandered off the path. Let's get you back to learning.
      </p>
      <RouterLink
        to="/dashboard"
        class="inline-block bg-emerald-900 text-white px-8 py-4 rounded-2xl font-bold shadow-lg shadow-emerald-900/20 active:scale-95 transition-transform"
      >
        Back to Dashboard
      </RouterLink>
    </div>
  </section>
</template>
