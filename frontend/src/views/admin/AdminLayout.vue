<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar -->
    <aside class="hidden lg:flex flex-col fixed left-0 top-0 h-screen w-64 bg-emerald-950 z-40">
      <!-- Logo -->
      <div class="px-6 py-5 border-b border-emerald-900">
        <div class="flex items-center gap-3">
          <div class="shrink-0">
            <img src="/Vernaculearn logo.png" alt="Vernaculearn" class="h-7 w-auto" />
          </div>
          <div>
            <p class="text-white font-bold text-sm leading-tight">Vernaculearn</p>
            <p class="text-emerald-400 text-xs font-medium">Admin Portal</p>
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
            ? 'bg-emerald-800 text-white'
            : 'text-emerald-300 hover:bg-emerald-900 hover:text-white'"
        >
          <span class="material-icons-outlined text-xl">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- User -->
      <div class="p-4 border-t border-emerald-900">
        <div class="flex items-center gap-3 px-2 py-2 mb-2">
          <div class="w-8 h-8 rounded-full bg-emerald-400 flex items-center justify-center shrink-0">
            <span class="material-icons-outlined text-emerald-950 text-sm">admin_panel_settings</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-white text-sm truncate">{{ auth.user?.name }}</p>
            <p class="text-xs text-emerald-400 truncate">Administrator</p>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-2 px-4 py-2.5 rounded-2xl text-emerald-300 hover:bg-emerald-900 hover:text-white text-sm font-semibold transition-all"
        >
          <span class="material-icons-outlined text-lg">logout</span>
          Sign out
        </button>
      </div>
    </aside>

    <!-- Mobile top bar -->
    <div class="lg:hidden fixed top-0 left-0 right-0 h-14 bg-emerald-950 z-40 flex items-center px-4 gap-3">
      <button @click="mobileOpen = !mobileOpen" class="text-white">
        <span class="material-icons-outlined">menu</span>
      </button>
      <span class="text-white font-bold text-sm">Vernaculearn Admin</span>
    </div>

    <!-- Mobile drawer -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="lg:hidden fixed inset-0 z-50 flex">
        <div class="absolute inset-0 bg-black/50" @click="mobileOpen = false" />
        <aside class="relative w-64 bg-emerald-950 h-full flex flex-col">
          <div class="px-6 py-5 border-b border-emerald-900">
            <p class="text-white font-bold">Vernaculearn Admin</p>
          </div>
          <nav class="flex-1 px-3 py-4 space-y-0.5">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              @click="mobileOpen = false"
              class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all"
              :class="$route.path.startsWith(item.to)
                ? 'bg-emerald-800 text-white'
                : 'text-emerald-300 hover:bg-emerald-900 hover:text-white'"
            >
              <span class="material-icons-outlined text-xl">{{ item.icon }}</span>
              {{ item.label }}
            </RouterLink>
          </nav>
          <div class="p-4 border-t border-emerald-900">
            <button @click="handleLogout" class="w-full flex items-center gap-2 px-4 py-2.5 rounded-2xl text-emerald-300 hover:bg-emerald-900 text-sm font-semibold">
              <span class="material-icons-outlined">logout</span> Sign out
            </button>
          </div>
        </aside>
      </div>
    </Transition>

    <!-- Main content -->
    <main class="flex-1 lg:pl-64 pt-14 lg:pt-0 min-h-screen">
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
  { to: '/admin/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { to: '/admin/users', icon: 'people', label: 'Users' },
  { to: '/admin/tutors', icon: 'school', label: 'Tutors' },
  { to: '/admin/content', icon: 'library_books', label: 'Content CMS' },
  { to: '/admin/review', icon: 'rate_review', label: 'Review Queue' },
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
