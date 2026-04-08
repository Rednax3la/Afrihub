<template>
  <nav class="md:hidden fixed bottom-0 left-0 right-0 glass border-t border-slate-100 px-8 py-4 flex justify-between items-center z-30">
    <RouterLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      class="flex flex-col items-center gap-1 text-slate-400 transition-colors"
      :class="{ 'text-[#003B5C] font-bold': $route.path === item.to }"
    >
      <span class="material-icons-outlined">{{ item.icon }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
const navItems = [
  { to: '/dashboard', icon: 'home' },
  { to: '/courses', icon: 'map' },
  { to: '/leaderboard', icon: 'emoji_events' },
  { to: '/subscription', icon: 'workspace_premium' },
  { to: '/profile', icon: 'person' },
]
</script>
