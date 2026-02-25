<template>
  <div class="flex justify-center items-center" :class="containerClass">
    <div
      class="border-4 rounded-full animate-spin"
      :class="[sizeClass, colorClass]"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: { type: String, default: 'md' },    // sm | md | lg
  color: { type: String, default: 'emerald' },
  fullPage: { type: Boolean, default: false },
})

const sizeClass = computed(() => ({
  sm: 'w-6 h-6 border-2',
  md: 'w-10 h-10 border-4',
  lg: 'w-16 h-16 border-4',
}[props.size]))

const colorClass = computed(() => `border-${props.color}-100 border-t-${props.color}-600`)

const containerClass = computed(() => props.fullPage ? 'min-h-[60vh]' : 'py-10')
</script>
