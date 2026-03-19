<template>
  <div v-if="keyboard" class="mt-2">
    <!-- Language note (Amharic / Swahili) -->
    <div v-if="keyboard.note && !keyboard.chars.length" class="flex items-start gap-2 bg-blue-50 border border-blue-100 rounded-xl px-3 py-2 text-xs text-blue-700">
      <span class="material-icons-outlined text-sm mt-0.5">info</span>
      <span>{{ keyboard.note }}</span>
    </div>

    <!-- Character buttons -->
    <div v-if="keyboard.chars.length" class="space-y-1.5">
      <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Special characters</p>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="char in keyboard.chars"
          :key="char"
          type="button"
          @click="insert(char)"
          class="px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-sm font-semibold hover:bg-emerald-50 hover:border-emerald-300 active:scale-95 transition-all"
        >
          {{ char }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { KEYBOARDS } from '@/data/keyboards'

const props = defineProps({
  languageCode: { type: String, default: '' },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'insert'])

const keyboard = computed(() => KEYBOARDS[props.languageCode] ?? null)

function insert(char) {
  emit('insert', char)
  // If parent passes a modelValue we can append to it
  if (props.modelValue !== undefined) {
    emit('update:modelValue', props.modelValue + char)
  }
}
</script>
