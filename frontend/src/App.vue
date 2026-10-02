<template>
  <div class="min-h-screen bg-[#FDFCFB]">
    <div v-if="isOffline" role="status" class="sticky top-0 z-50 bg-amber-50 px-4 py-2 text-center text-xs text-amber-900 md:pl-64">You're offline &mdash; showing cached content</div>
    <SideNav v-if="auth.isLoggedIn && auth.isStudent" />
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
    <Toast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import SideNav from '@/components/SideNav.vue'
import Toast from '@/components/Toast.vue'

import { useOffline } from '@/composables/useOffline'
const { isOffline } = useOffline()

const auth = useAuthStore()
onMounted(() => auth.fetchMe())
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
