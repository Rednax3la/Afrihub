<template>
  <div>
    <label :for="id" class="block text-sm font-semibold text-slate-600 mb-2">{{ label }}</label>
    <div class="flex items-center rounded-2xl border border-slate-200 bg-white focus-within:border-emerald-500">
      <input :id="id" :name="id" :value="modelValue" :type="visible ? 'text' : 'password'"
        :autocomplete="autocomplete" required :aria-describedby="showRequirements ? `${id}-requirements` : undefined"
        class="min-w-0 flex-1 p-4 rounded-2xl text-slate-800 outline-none"
        @input="$emit('update:modelValue', $event.target.value)" />
      <button type="button" :aria-controls="id" :aria-pressed="visible"
        :aria-label="`${visible ? 'Hide' : 'Show'} ${label.toLowerCase()}`"
        class="px-3 py-4 text-sm font-semibold text-emerald-800 rounded-xl focus-visible:outline focus-visible:outline-2"
        @click="visible = !visible">{{ visible ? 'Hide' : 'Show' }}</button>
    </div>
    <ul v-if="showRequirements" :id="`${id}-requirements`" aria-live="polite" class="mt-2 text-xs space-y-1">
      <li v-for="item in requirements" :key="item.label" :class="item.met ? 'text-emerald-800' : 'text-slate-600'">
        <span class="sr-only">{{ item.met ? 'Met:' : 'Needed:' }}</span>
        <span aria-hidden="true">{{ item.met ? '✓' : '○' }}</span> {{ item.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { passwordRequirements } from '@/utils/passwords'
const props = defineProps({
  id: { type: String, required: true },
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Password' },
  autocomplete: { type: String, default: 'new-password' },
  showRequirements: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])
const visible = ref(false)
const requirements = computed(() => passwordRequirements(props.modelValue))
</script>
