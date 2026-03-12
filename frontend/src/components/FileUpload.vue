<template>
  <div>
    <!-- Existing URL display -->
    <div v-if="modelValue" class="flex items-center gap-2 mb-2 bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5">
      <span class="material-icons-outlined text-emerald-600 text-lg">{{ type === 'audio' ? 'audiotrack' : 'image' }}</span>
      <span class="text-xs text-slate-600 flex-1 truncate font-mono">{{ modelValue }}</span>
      <button type="button" @click="$emit('update:modelValue', '')" class="text-slate-400 hover:text-red-500 transition-colors">
        <span class="material-icons-outlined text-base">close</span>
      </button>
    </div>

    <!-- Upload zone -->
    <label
      class="flex flex-col items-center justify-center gap-2 p-4 rounded-2xl border-2 border-dashed cursor-pointer transition-all"
      :class="dragging
        ? 'border-emerald-500 bg-emerald-50'
        : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <input type="file" class="sr-only" :accept="accept" @change="onFileChange" />

      <div v-if="uploading" class="flex items-center gap-2 text-emerald-700">
        <div class="w-4 h-4 border-2 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
        <span class="text-sm font-semibold">Uploading…</span>
      </div>
      <template v-else>
        <span class="material-icons-outlined text-2xl text-slate-400">{{ type === 'audio' ? 'upload_file' : 'add_photo_alternate' }}</span>
        <span class="text-xs text-slate-500 text-center">
          {{ modelValue ? 'Replace file' : `Upload ${type}` }} · drag & drop or click
        </span>
        <span class="text-xs text-slate-400">{{ type === 'audio' ? 'MP3, WAV, OGG, M4A · max 15 MB' : 'JPG, PNG, WebP · max 15 MB' }}</span>
      </template>
    </label>

    <!-- Or paste URL -->
    <div class="flex items-center gap-2 mt-2">
      <div class="flex-1 h-px bg-slate-100"></div>
      <span class="text-xs text-slate-400">or paste URL</span>
      <div class="flex-1 h-px bg-slate-100"></div>
    </div>
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="`https://example.com/file.${type === 'audio' ? 'mp3' : 'jpg'}`"
      class="mt-2 w-full border border-slate-200 rounded-2xl px-4 py-2.5 text-xs focus:outline-none focus:border-emerald-400 font-mono"
    />

    <p v-if="error" class="mt-1.5 text-xs text-red-500 font-medium">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { uploadApi } from '@/api'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  modelValue: { type: String, default: '' },
  type: { type: String, default: 'image' }, // 'audio' | 'image'
})
const emit = defineEmits(['update:modelValue'])

const toast = useToastStore()
const dragging = ref(false)
const uploading = ref(false)
const error = ref('')

const accept = computed(() =>
  props.type === 'audio' ? 'audio/*' : 'image/*'
)

async function upload(file) {
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const fn = props.type === 'audio' ? uploadApi.audio : uploadApi.image
    const { data } = await fn(file)
    emit('update:modelValue', data.url)
    toast.success('File uploaded')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
    dragging.value = false
  }
}

function onFileChange(e) { upload(e.target.files[0]) }
function onDrop(e) { upload(e.dataTransfer.files[0]) }
</script>
