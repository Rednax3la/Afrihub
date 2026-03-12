<template>
  <button
    @click="toggle"
    class="flex items-center gap-2 px-4 py-2.5 rounded-2xl font-semibold text-sm transition-all select-none"
    :class="playing
      ? 'bg-emerald-900 text-white shadow-lg shadow-emerald-900/20'
      : 'bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100'"
  >
    <span class="material-icons-outlined text-xl">
      {{ playing ? 'pause_circle' : 'play_circle' }}
    </span>
    <span>{{ playing ? 'Playing…' : label }}</span>

    <!-- Animated bars when playing -->
    <div v-if="playing" class="flex items-end gap-0.5 h-4">
      <span v-for="i in 3" :key="i"
        class="w-0.5 bg-white rounded-full animate-bounce"
        :style="{ height: `${[60, 100, 75][i-1]}%`, animationDelay: `${(i-1) * 0.15}s` }"
      />
    </div>
  </button>
</template>

<script setup>
import { ref, onUnmounted, watch } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  label: { type: String, default: 'Play Audio' },
})

const playing = ref(false)
let audio = null

function toggle() {
  if (!props.src) return
  if (!audio) audio = new Audio(props.src)

  if (playing.value) {
    audio.pause()
    playing.value = false
  } else {
    audio.play()
    playing.value = true
    audio.onended = () => { playing.value = false }
  }
}

watch(() => props.src, () => {
  if (audio) { audio.pause(); audio = null }
  playing.value = false
})

onUnmounted(() => {
  if (audio) { audio.pause(); audio = null }
})
</script>
