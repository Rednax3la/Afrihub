<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 max-w-sm w-full px-4">
      <TransitionGroup name="toast">
        <div
          v-for="toast in store.toasts"
          :key="toast.id"
          class="flex items-start gap-3 px-4 py-3.5 rounded-2xl shadow-lg cursor-pointer select-none"
          :class="{
            'bg-[#003B5C] text-white': toast.type === 'success',
            'bg-red-600 text-white': toast.type === 'error',
            'bg-slate-800 text-white': toast.type === 'info',
          }"
          @click="store.dismiss(toast.id)"
        >
          <span class="material-icons-outlined text-lg mt-0.5 shrink-0">
            {{ toast.type === 'success' ? 'check_circle' : toast.type === 'error' ? 'cancel' : 'info' }}
          </span>
          <p class="text-sm font-semibold leading-snug">{{ toast.message }}</p>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'
const store = useToastStore()
</script>

<style scoped>
.toast-enter-active { transition: all 0.25s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to   { opacity: 0; transform: translateX(100%); }
</style>
