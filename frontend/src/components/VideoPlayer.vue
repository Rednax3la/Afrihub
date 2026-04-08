<template>
  <div class="w-full">
    <!-- Video element -->
    <div class="relative bg-black rounded-t-[2rem] overflow-hidden" style="aspect-ratio: 16/9">
      <!-- Loading spinner -->
      <div v-if="videoLoading" class="absolute inset-0 flex items-center justify-center z-10">
        <div class="w-10 h-10 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
      </div>

      <!-- Error state -->
      <div v-if="videoError" class="absolute inset-0 flex flex-col items-center justify-center text-white/70 gap-2">
        <span class="material-icons-outlined text-4xl">videocam_off</span>
        <p class="text-sm font-medium">Video unavailable</p>
      </div>

      <video
        v-if="src"
        ref="videoEl"
        :src="src"
        controls
        class="w-full h-full object-contain"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onMetadata"
        @waiting="videoLoading = true"
        @canplay="videoLoading = false"
        @error="onError"
      ></video>

      <div v-if="!src" class="absolute inset-0 flex items-center justify-center text-white/40">
        <span class="material-icons-outlined text-5xl">play_circle</span>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="bg-slate-800 rounded-b-[2rem] px-5 py-3">
      <div class="flex items-center justify-between mb-1.5">
        <span class="text-xs font-semibold text-white/70">
          Watched: {{ watchedPercent }}%
          <span v-if="!progressMet" class="text-amber-400"> — watch to {{ Math.round(requiredProgress * 100) }}% to continue</span>
          <span v-else class="text-emerald-400"> — ready to continue!</span>
        </span>
        <span v-if="progressMet" class="material-icons-outlined text-emerald-400 text-base">check_circle</span>
      </div>

      <!-- Track -->
      <div class="relative h-2 bg-white/10 rounded-full overflow-visible">
        <!-- Filled portion (high-water mark) -->
        <div
          class="h-full rounded-full transition-all duration-200"
          :class="progressMet ? 'bg-emerald-400' : 'bg-emerald-500'"
          :style="{ width: `${watchedPercent}%` }"
        ></div>
        <!-- Threshold dashed marker -->
        <div
          class="absolute top-1/2 -translate-y-1/2 w-0.5 h-4 border-l-2 border-dashed border-amber-400"
          :style="{ left: `${requiredProgress * 100}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  requiredProgress: { type: Number, default: 0.75 },
  lessonId: { type: [String, Number], default: '' },
  questionId: { type: [String, Number], default: '' },
})

const emit = defineEmits(['progress-met'])

const videoEl = ref(null)
const videoLoading = ref(false)
const videoError = ref(false)
const duration = ref(0)
const highWaterMark = ref(0)   // 0–1 fraction of video watched
const progressMet = ref(false)

const storageKey = computed(() => `vp:${props.lessonId}:${props.questionId}`)

const watchedPercent = computed(() => Math.round(highWaterMark.value * 100))

function onMetadata() {
  duration.value = videoEl.value?.duration ?? 0
  videoLoading.value = false
}

function onTimeUpdate() {
  if (!duration.value) return
  const current = (videoEl.value?.currentTime ?? 0) / duration.value
  if (current > highWaterMark.value) {
    highWaterMark.value = current
    try {
      localStorage.setItem(storageKey.value, String(highWaterMark.value))
    } catch { /* storage full */ }
  }
  if (!progressMet.value && highWaterMark.value >= props.requiredProgress) {
    progressMet.value = true
    emit('progress-met')
  }
}

function onError() {
  videoLoading.value = false
  videoError.value = true
}

// Restore progress from localStorage on mount
onMounted(() => {
  const saved = localStorage.getItem(storageKey.value)
  if (saved) {
    const val = parseFloat(saved)
    if (!isNaN(val) && val > 0) {
      highWaterMark.value = val
      if (val >= props.requiredProgress) {
        progressMet.value = true
        emit('progress-met')
      }
    }
  }
})

// Reset when question changes
watch(() => props.questionId, () => {
  highWaterMark.value = 0
  progressMet.value = false
  videoError.value = false
  const saved = localStorage.getItem(storageKey.value)
  if (saved) {
    const val = parseFloat(saved)
    if (!isNaN(val) && val >= props.requiredProgress) {
      highWaterMark.value = val
      progressMet.value = true
      emit('progress-met')
    }
  }
})
</script>
