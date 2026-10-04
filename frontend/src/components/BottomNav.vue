<template>
  <nav class="md:hidden fixed bottom-0 left-0 right-0 glass border-t border-slate-100 px-2 py-3 grid grid-cols-5 items-center z-30">
    <RouterLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      :aria-label="item.label || item.to.slice(1)"
      class="min-w-0 flex flex-col items-center gap-1 text-slate-400 transition-colors"
      :class="{ 'text-[#003B5C] font-bold': isNavigationActive($route.path, item.to) }"
    >
      <span class="material-icons-outlined">{{ item.icon }}</span>
      <span class="text-[10px] leading-tight">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
import { studentNavigation as navItems, isNavigationActive } from '@/utils/navigation'
</script>
