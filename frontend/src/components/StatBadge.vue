<template>
  <div class="flex items-center px-3 py-1.5 rounded-full border" :class="containerClass">
    <span class="material-icons-outlined text-sm" :class="iconClass">{{ icon }}</span>
    <span class="font-bold ml-1 text-sm" :class="textClass">{{ value }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'streak' },  // 'streak' | 'xp' | 'hearts'
  value: { type: [Number, String], required: true },
})

const config = {
  streak:  { icon: 'local_fire_department', bg: 'bg-amber-50 border-amber-100', icon: 'text-amber-600', text: 'text-amber-700' },
  xp:      { icon: 'bolt',                 bg: 'bg-emerald-50 border-emerald-100', icon: 'text-emerald-600', text: 'text-emerald-700' },
  hearts:  { icon: 'favorite',             bg: 'bg-red-50 border-red-100', icon: 'text-red-500', text: 'text-red-600' },
}

const icon         = computed(() => ({ streak: 'local_fire_department', xp: 'bolt', hearts: 'favorite' }[props.type]))
const containerClass = computed(() => config[props.type]?.bg ?? config.streak.bg)
const iconClass    = computed(() => config[props.type]?.icon ?? config.streak.icon)
const textClass    = computed(() => config[props.type]?.text ?? config.streak.text)
</script>
