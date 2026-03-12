<template>
  <div class="p-6 lg:p-8 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Tutors</h1>
        <p class="text-slate-500 text-sm mt-0.5">Manage tutor applications and access</p>
      </div>
      <!-- Filter tabs -->
      <div class="flex gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="px-4 py-2 rounded-xl text-sm font-semibold transition-all"
          :class="activeTab === tab.key ? 'bg-emerald-900 text-white' : 'bg-white border border-slate-200 text-slate-600'"
        >
          {{ tab.label }}
          <span v-if="tab.key === 'pending' && pendingCount > 0"
            class="ml-1.5 bg-amber-500 text-white text-xs px-1.5 py-0.5 rounded-full">
            {{ pendingCount }}
          </span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="adminStore.loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
    </div>

    <!-- Tutor cards -->
    <div v-else class="space-y-3">
      <div
        v-for="tutor in filteredTutors"
        :key="tutor.id"
        class="bg-white rounded-3xl border border-slate-100 shadow-sm p-5"
      >
        <div class="flex items-start gap-4">
          <img
            :src="tutor.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=065F46&color=fff&rounded=true&size=128`"
            class="w-14 h-14 rounded-2xl object-cover border border-slate-100 shrink-0"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap mb-0.5">
              <h3 class="font-bold text-slate-900">{{ tutor.name }}</h3>
              <span
                class="text-xs font-bold px-2 py-0.5 rounded-full"
                :class="{
                  'bg-amber-100 text-amber-700': tutor.tutor_status === 'pending',
                  'bg-emerald-100 text-emerald-700': tutor.tutor_status === 'active',
                  'bg-red-100 text-red-600': tutor.tutor_status === 'suspended',
                }"
              >
                {{ tutor.tutor_status?.toUpperCase() }}
              </span>
              <span v-if="tutor.voice_character" class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-semibold">
                🎙 {{ tutor.voice_character }}
              </span>
            </div>
            <p class="text-sm text-slate-500">{{ tutor.email }}</p>
            <p v-if="tutor.bio" class="text-sm text-slate-600 mt-2 leading-relaxed">{{ tutor.bio }}</p>
            <div v-if="tutor.languages_taught?.length" class="flex gap-1.5 mt-2 flex-wrap">
              <span
                v-for="lang in tutor.languages_taught"
                :key="lang"
                class="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-semibold capitalize"
              >
                {{ lang }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 shrink-0">
            <button
              v-if="tutor.tutor_status === 'pending'"
              @click="approve(tutor)"
              :disabled="actionLoading === tutor.id"
              class="flex items-center gap-1.5 px-4 py-2 rounded-2xl bg-emerald-900 text-white text-sm font-bold hover:bg-emerald-800 disabled:opacity-50 transition-colors"
            >
              <span class="material-icons-outlined text-base">check</span>
              Approve
            </button>
            <button
              v-if="tutor.tutor_status === 'active'"
              @click="suspend(tutor)"
              :disabled="actionLoading === tutor.id"
              class="flex items-center gap-1.5 px-4 py-2 rounded-2xl bg-red-50 text-red-600 text-sm font-bold hover:bg-red-100 disabled:opacity-50 transition-colors border border-red-200"
            >
              <span class="material-icons-outlined text-base">block</span>
              Suspend
            </button>
            <button
              v-if="tutor.tutor_status === 'suspended'"
              @click="approve(tutor)"
              :disabled="actionLoading === tutor.id"
              class="flex items-center gap-1.5 px-4 py-2 rounded-2xl bg-emerald-50 text-emerald-700 text-sm font-bold hover:bg-emerald-100 border border-emerald-200 disabled:opacity-50"
            >
              <span class="material-icons-outlined text-base">restore</span>
              Reinstate
            </button>
          </div>
        </div>
      </div>

      <div v-if="!filteredTutors.length" class="bg-white rounded-3xl border border-slate-100 p-12 text-center">
        <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">school</span>
        <p class="text-slate-400 font-medium">No {{ activeTab }} tutors</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'

const adminStore = useAdminStore()
const toast = useToastStore()
const activeTab = ref('all')
const actionLoading = ref(null)

const tabs = [
  { key: 'all', label: 'All' },
  { key: 'pending', label: 'Pending' },
  { key: 'active', label: 'Active' },
  { key: 'suspended', label: 'Suspended' },
]

onMounted(() => adminStore.fetchTutors())

const pendingCount = computed(() => adminStore.tutors.filter(t => t.tutor_status === 'pending').length)

const filteredTutors = computed(() => {
  if (activeTab.value === 'all') return adminStore.tutors
  return adminStore.tutors.filter(t => t.tutor_status === activeTab.value)
})

async function approve(tutor) {
  actionLoading.value = tutor.id
  try {
    await adminStore.approveTutor(tutor.id)
    toast.success(`${tutor.name} approved as tutor`)
  } catch {
    toast.error('Failed to update tutor')
  } finally {
    actionLoading.value = null
  }
}

async function suspend(tutor) {
  actionLoading.value = tutor.id
  try {
    await adminStore.suspendTutor(tutor.id)
    toast.success(`${tutor.name}'s access suspended`)
  } catch {
    toast.error('Failed to update tutor')
  } finally {
    actionLoading.value = null
  }
}
</script>
