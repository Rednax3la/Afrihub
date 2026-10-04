<template>
  <div class="min-h-screen bg-[#FDFCFB]">
    <div v-if="isOffline" role="status" class="sticky top-0 z-50 bg-amber-50 px-4 py-2 text-center text-xs text-amber-900 md:pl-64">You're offline &mdash; showing cached content</div>
    <SideNav v-if="auth.isLoggedIn && auth.isStudent" />
    <div v-if="update" role="status" class="fixed top-3 right-3 z-50 rounded-2xl bg-white p-4 shadow-lg border">
      A new version is ready. <button @click="refreshApp" class="text-[#007F96] font-bold underline">Refresh when ready</button>
    </div>
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
    <Toast />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import SideNav from '@/components/SideNav.vue'
import Toast from '@/components/Toast.vue'

import { useOffline } from '@/composables/useOffline'
const { isOffline } = useOffline()

const auth = useAuthStore()
const update = ref(null)
const onUpdate = event => { update.value = event.detail }
onMounted(() => window.addEventListener('app-update', onUpdate))
onUnmounted(() => window.removeEventListener('app-update', onUpdate))
function refreshApp() {
  navigator.serviceWorker.addEventListener('controllerchange', () => window.location.reload(), { once: true })
  update.value?.waiting?.postMessage({ type: 'ACTIVATE_UPDATE' })
}
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
