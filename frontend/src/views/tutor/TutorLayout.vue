<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar -->
    <aside class="hidden lg:flex flex-col fixed left-0 top-0 h-screen w-64 bg-white border-r border-slate-100 z-40">
      <!-- Logo -->
      <div class="px-6 py-5 border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-emerald-800 rounded-xl flex items-center justify-center shrink-0">
            <span class="material-icons-outlined text-white text-lg">menu_book</span>
          </div>
          <div>
            <p class="text-slate-900 font-bold text-sm leading-tight">Vernaculearn</p>
            <p class="text-emerald-600 text-xs font-semibold">Tutor Portal</p>
          </div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-0.5">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all"
          :class="$route.path.startsWith(item.to)
            ? 'bg-emerald-50 text-emerald-900'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'"
        >
          <span class="material-icons-outlined text-xl">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- Tutor status + user -->
      <div class="p-4 border-t border-slate-100">
        <div v-if="auth.user?.tutor_status === 'active'" class="flex items-center gap-1.5 bg-emerald-50 px-3 py-2 rounded-xl mb-3">
          <span class="material-icons-outlined text-emerald-600 text-sm">verified</span>
          <span class="text-xs font-bold text-emerald-700">Active Tutor</span>
        </div>
        <div v-if="auth.user?.voice_character" class="flex items-center gap-1.5 bg-purple-50 px-3 py-2 rounded-xl mb-3">
          <span class="material-icons-outlined text-purple-600 text-sm">record_voice_over</span>
          <span class="text-xs font-bold text-purple-700">{{ auth.user.voice_character }}</span>
        </div>
        <div class="flex items-center gap-3 px-2 py-2 mb-2">
          <img
            :src="auth.user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.name || 'T')}&background=065F46&color=fff&rounded=true`"
            class="w-8 h-8 rounded-full object-cover border-2 border-emerald-100"
          />
          <div class="flex-1 min-w-0">
            <p class="font-bold text-slate-900 text-sm truncate">{{ auth.user?.name }}</p>
            <p class="text-xs text-slate-400 truncate">{{ auth.user?.email }}</p>
          </div>
        </div>
        <button @click="handleLogout" class="w-full flex items-center gap-2 px-4 py-2.5 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-slate-800 text-sm font-semibold transition-all">
          <span class="material-icons-outlined text-lg">logout</span> Sign out
        </button>
      </div>
    </aside>

    <!-- Mobile top bar -->
    <div class="lg:hidden fixed top-0 left-0 right-0 h-14 bg-white border-b border-slate-100 z-40 flex items-center px-4 gap-3">
      <button @click="mobileOpen = !mobileOpen" class="text-slate-700">
        <span class="material-icons-outlined">menu</span>
      </button>
      <span class="text-slate-900 font-bold text-sm">Tutor Portal</span>
    </div>

    <!-- Mobile drawer -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="lg:hidden fixed inset-0 z-50 flex">
        <div class="absolute inset-0 bg-black/40" @click="mobileOpen = false" />
        <aside class="relative w-64 bg-white h-full flex flex-col border-r border-slate-100">
          <div class="px-6 py-5 border-b border-slate-100">
            <p class="text-slate-900 font-bold">Vernaculearn — Tutor</p>
          </div>
          <nav class="flex-1 px-3 py-4 space-y-0.5">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              @click="mobileOpen = false"
              class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all"
              :class="$route.path.startsWith(item.to) ? 'bg-emerald-50 text-emerald-900' : 'text-slate-500 hover:bg-slate-50'"
            >
              <span class="material-icons-outlined text-xl">{{ item.icon }}</span>
              {{ item.label }}
            </RouterLink>
          </nav>
          <div class="p-4 border-t border-slate-100">
            <button @click="handleLogout" class="w-full flex items-center gap-2 px-4 py-2.5 rounded-2xl text-slate-500 hover:bg-slate-50 text-sm font-semibold">
              <span class="material-icons-outlined">logout</span> Sign out
            </button>
          </div>
        </aside>
      </div>
    </Transition>

    <!-- Main -->
    <main class="flex-1 lg:pl-64 pt-14 lg:pt-0 min-h-screen">
      <!-- Pending approval banner -->
      <div v-if="auth.user?.tutor_status === 'pending'"
        class="bg-amber-50 border-b border-amber-200 px-6 py-3 flex items-center gap-3"
      >
        <span class="material-icons-outlined text-amber-600">pending</span>
        <p class="text-sm text-amber-800 font-medium">
          Your tutor account is <strong>pending approval</strong>. An admin will review your application shortly.
        </p>
      </div>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const mobileOpen = ref(false)

const navItems = [
  { to: '/tutor/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { to: '/tutor/content', icon: 'edit_note', label: 'My Content' },
  { to: '/tutor/profile', icon: 'person', label: 'My Profile' },
]

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.drawer-enter-active, .drawer-leave-active { transition: opacity 0.2s ease; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }
</style>
