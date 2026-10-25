<template>
  <Transition name="fade">
    <div
      v-if="visible"
      role="dialog"
      aria-label="Install Vernaculearn"
      class="fixed inset-x-3 bottom-20 z-40 rounded-3xl border border-[#00A3C1]/20 bg-white p-4 shadow-xl shadow-slate-300/40 md:left-auto md:right-6 md:bottom-6 md:w-[22rem]"
    >
      <div class="flex items-start gap-3">
        <img src="/Vernaculearn logo.png" alt="" class="h-10 w-10 shrink-0 rounded-xl" />
        <div class="min-w-0 flex-1">
          <p class="font-bold text-[#003B5C]">Install Vernaculearn</p>
          <p v-if="iosHint" class="mt-1 text-sm text-slate-600">
            Tap <span class="font-semibold">Share</span>, then
            <span class="font-semibold">Add to Home Screen</span>.
          </p>
          <p v-else class="mt-1 text-sm text-slate-600">
            Add it to your home screen for faster access and offline lessons.
          </p>
        </div>
        <button
          aria-label="Dismiss install prompt"
          class="-mt-1 -mr-1 flex h-8 w-8 shrink-0 items-center justify-center text-slate-400"
          @click="dismiss"
        >
          <span class="material-icons-outlined text-lg">close</span>
        </button>
      </div>

      <div class="mt-3 flex gap-2">
        <button
          v-if="!iosHint"
          class="flex-1 rounded-2xl bg-[#003B5C] py-3 text-sm font-bold text-white active:scale-95 transition-transform"
          @click="accept"
        >
          Install
        </button>
        <button
          class="rounded-2xl bg-slate-100 px-4 py-3 text-sm font-bold text-slate-600"
          :class="iosHint ? 'flex-1' : ''"
          @click="dismiss"
        >
          Not now
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  useInstallPrompt, isStandalone, isIos,
  dismissalExpired, markDismissed, markShownThisSession, shownThisSession,
} from '@/composables/useInstallPrompt'

const route = useRoute()
const { promptAvailable, install } = useInstallPrompt()

const dismissedNow = ref(false)
const iosHint = ref(false)
const eligible = ref(false)

// Never interrupt staff workflows or a lesson in progress.
const routeAllows = computed(() => {
  const path = route.path || ''
  if (path.startsWith('/admin') || path.startsWith('/tutor')) return false
  if (route.name === 'lesson' || route.name === 'foundations') return false
  return true
})

const visible = computed(() =>
  eligible.value && routeAllows.value && !dismissedNow.value &&
  (iosHint.value || promptAvailable.value)
)

function evaluate() {
  if (isStandalone()) { eligible.value = false; return }
  // One appearance per browser session, and only once the 24h dismissal
  // cool-down has elapsed.
  if (shownThisSession() || !dismissalExpired()) { eligible.value = false; return }
  iosHint.value = isIos()
  eligible.value = true
}

function dismiss() {
  dismissedNow.value = true
  markDismissed()
  markShownThisSession()
}

async function accept() {
  markShownThisSession()
  const outcome = await install()
  if (outcome !== 'accepted') markDismissed()
  dismissedNow.value = true
}

// Mark the session as "shown" only once the card is actually on screen, so a
// user who starts inside a lesson still sees it after they leave.
watch(visible, isVisible => { if (isVisible) markShownThisSession() })

onMounted(evaluate)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; transform: translateY(0.5rem); }
</style>
