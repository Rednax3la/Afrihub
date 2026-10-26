<template>
  <div class="flex min-w-0 flex-1 items-center gap-1" role="tablist" aria-label="Lesson questions">
    <button
      v-for="(question, index) in questions"
      :key="question.id ?? index"
      type="button"
      role="tab"
      :aria-selected="index === current"
      :aria-label="`Question ${index + 1}${props.isAnswered(question.id) ? ' (answered)' : ''}`"
      class="relative h-1.5 min-w-0 flex-1 rounded-full transition-colors"
      :class="segmentClass(question, index)"
      @click="emit('select', index)"
    >
      <!-- Invisible 40px-tall hit area keeps the thin bar thumb-friendly. -->
      <span class="absolute inset-x-0 -top-5 h-10"></span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  questions: { type: Array, required: true },
  // -1 on the review step, where no single question is current.
  current: { type: Number, default: 0 },
  isAnswered: { type: Function, required: true },
})
const emit = defineEmits(['select'])

function segmentClass(question, index) {
  if (index === props.current) return 'bg-[#003B5C]'
  if (props.isAnswered(question.id)) return 'bg-[#00A3C1]'
  return 'bg-slate-200 hover:bg-slate-300'
}
</script>
