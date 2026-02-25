<template>
  <div class="bg-white border border-slate-100 rounded-3xl p-5 shadow-sm overflow-hidden relative">
    <!-- Premium badge -->
    <div
      v-if="!language.is_free && !isPremiumUser"
      class="absolute top-0 right-0 bg-amber-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-2xl"
    >
      PREMIUM
    </div>

    <div class="flex items-start gap-4">
      <div
        class="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shrink-0"
        :style="{ backgroundColor: bgColor }"
      >
        {{ language.flag_emoji }}
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-2 flex-wrap">
          <h5 class="font-bold text-slate-900 text-lg">{{ language.name }}</h5>
          <span class="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-medium">
            {{ language.country }}
          </span>
        </div>
        <p class="text-slate-500 text-sm mt-1 leading-relaxed">{{ language.description }}</p>
        <div class="flex items-center gap-2 mt-3">
          <span class="material-icons-outlined text-slate-400 text-sm">people</span>
          <span class="text-xs text-slate-400 font-medium">{{ language.speaker_count }} speakers</span>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  language: { type: Object, required: true },
  isPremiumUser: { type: Boolean, default: false },
})

const colorMap = {
  emerald: '#065F46',
  blue: '#1E40AF',
  amber: '#B45309',
  red: '#B91C1C',
}

const bgColor = computed(() => {
  const hex = colorMap[props.language.color] ?? '#065F46'
  return `${hex}20`  // 12% opacity hex trick
})
</script>
