<template>
  <div class="p-6 lg:p-8 max-w-2xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">My Profile</h1>
      <p class="text-slate-500 text-sm mt-0.5">How learners see you on the platform</p>
    </div>

    <!-- Avatar & name card -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 mb-6 flex items-center gap-5">
      <img
        :src="auth.user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(auth.user?.name || 'T')}&background=065F46&color=fff&rounded=true&size=128`"
        class="w-20 h-20 rounded-2xl object-cover border-2 border-slate-100"
      />
      <div>
        <h2 class="text-xl font-bold text-slate-900">{{ auth.user?.name }}</h2>
        <p class="text-slate-500 text-sm">{{ auth.user?.email }}</p>
        <div class="flex gap-2 mt-2 flex-wrap">
          <span class="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">
            {{ auth.user?.tutor_status === 'active' ? '✓ Active Tutor' : auth.user?.tutor_status }}
          </span>
          <span v-if="auth.user?.voice_character" class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-bold">
            🎙 {{ auth.user.voice_character }}
          </span>
        </div>
      </div>
    </div>

    <!-- Edit form -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6">
      <h3 class="font-bold text-slate-900 mb-5">Edit Profile</h3>
      <form @submit.prevent="save" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Display Name</label>
          <input v-model="form.name" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Location</label>
          <input v-model="form.location" placeholder="e.g. Lagos, Nigeria" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Bio</label>
          <textarea v-model="form.bio" rows="3" placeholder="Tell learners about yourself and your teaching background..." class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 resize-none"></textarea>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Avatar URL</label>
          <input v-model="form.avatar_url" placeholder="https://..." class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Voice Character Name</label>
          <input v-model="form.voice_character" placeholder="e.g. Amara" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          <p class="text-xs text-slate-400 mt-1.5">This is the character name learners will see in lessons you create.</p>
        </div>
        <button type="submit" :disabled="saving" class="w-full py-4 rounded-2xl bg-emerald-900 text-white font-bold text-sm disabled:opacity-50 mt-2">
          {{ saving ? 'Saving…' : 'Save Changes' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { tutorApi } from '@/api'

const auth = useAuthStore()
const toast = useToastStore()
const saving = ref(false)

const form = ref({
  name: '',
  location: '',
  bio: '',
  avatar_url: '',
  voice_character: '',
})

onMounted(() => {
  form.value = {
    name: auth.user?.name || '',
    location: auth.user?.location || '',
    bio: auth.user?.bio || '',
    avatar_url: auth.user?.avatar_url || '',
    voice_character: auth.user?.voice_character || '',
  }
})

async function save() {
  saving.value = true
  try {
    const { data } = await tutorApi.updateMyProfile(form.value)
    auth.user = data
    toast.success('Profile updated')
  } catch {
    toast.error('Failed to update profile')
  } finally {
    saving.value = false
  }
}
</script>
