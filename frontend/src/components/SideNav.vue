<template>
  <aside class="hidden md:flex flex-col fixed left-0 top-0 h-screen w-64 bg-white border-r border-slate-100 z-40">
    <!-- Logo -->
    <div class="p-6 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-emerald-800 rounded-xl flex items-center justify-center shrink-0">
          <span class="material-icons-outlined text-white text-xl">menu_book</span>
        </div>
        <span class="text-lg font-bold text-emerald-950 tracking-tight">Vernaculearn</span>
      </div>
    </div>

    <!-- Nav Items -->
    <nav class="flex-1 px-3 py-2 space-y-1">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-4 py-3 rounded-2xl font-semibold text-sm transition-all"
        :class="$route.path === item.to
          ? 'bg-emerald-50 text-emerald-900'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'"
      >
        <span class="material-icons-outlined text-xl">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- User Stats -->
    <div v-if="auth.user" class="p-4 border-t border-slate-100">
      <div class="flex items-center gap-3 px-2 py-2 mb-3">
        <img
          :src="auth.user.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user.name || 'U')}&background=065F46&color=fff&rounded=true`"
          class="w-9 h-9 rounded-full object-cover border-2 border-emerald-100"
        />
        <div class="flex-1 min-w-0">
          <p class="font-bold text-slate-900 text-sm truncate">{{ auth.user.name }}</p>
          <p class="text-xs text-slate-400 truncate">{{ auth.user.email }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <div class="flex-1 flex items-center gap-1.5 bg-amber-50 rounded-xl px-3 py-2">
          <span class="material-icons-outlined text-amber-500 text-sm">local_fire_department</span>
          <span class="font-bold text-amber-700 text-sm">{{ auth.user.streak ?? 0 }}</span>
        </div>
        <div class="flex-1 flex items-center gap-1.5 bg-emerald-50 rounded-xl px-3 py-2">
          <span class="material-icons-outlined text-emerald-600 text-sm">bolt</span>
          <span class="font-bold text-emerald-700 text-sm">{{ auth.user.xp ?? 0 }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const navItems = [
  { to: '/dashboard', icon: 'home', label: 'Home' },
  { to: '/courses', icon: 'map', label: 'Courses' },
  { to: '/subscription', icon: 'workspace_premium', label: 'Premium' },
  { to: '/profile', icon: 'person', label: 'Profile' },
]
</script>
