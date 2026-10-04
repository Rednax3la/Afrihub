<template>
  <section class="min-h-screen bg-[#FDFCFB] safe-bottom md:pl-64">
    <main class="max-w-3xl mx-auto p-6 pb-28">
      <div class="flex items-center gap-3 mb-3"><span class="material-icons-outlined text-3xl text-[#00A3C1]">explore</span><h1 class="text-3xl font-bold text-[#003B5C]">Explore</h1></div>
      <p class="text-slate-500 mb-8">Discover more ways to connect with language and culture.</p>
      <div class="grid sm:grid-cols-2 gap-4">
        <article v-for="feature in exploreFeatures" :key="feature.name" class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
          <span class="material-icons-outlined text-3xl text-[#003B5C] bg-[#A7FFEB]/30 rounded-2xl p-3 mb-4">{{ feature.icon }}</span>
          <h2 class="text-xl font-bold text-slate-900">{{ feature.name }}</h2>
          <p class="text-sm text-slate-500 mt-2 mb-4">{{ feature.description }}</p>
          <RouterLink v-if="feature.to" :to="feature.to" class="inline-block font-semibold text-[#007F96] underline">Open dictionary</RouterLink>
          <span v-else class="inline-block text-xs font-semibold rounded-full bg-slate-100 text-slate-500 px-3 py-1">Coming soon</span>
        </article>
      </div>
    </main>
    <BottomNav />
  </section>
</template>
<script setup>
import BottomNav from '@/components/BottomNav.vue'
import { exploreFeatures } from '@/utils/navigation'
</script>
