<template>
  <section class="min-h-screen bg-[#FDFCFB] flex items-center justify-center p-6">
    <div class="w-full max-w-lg">
      <!-- Back -->
      <RouterLink to="/" class="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-800 font-semibold text-sm mb-8 transition-colors">
        <span class="material-icons-outlined text-lg">arrow_back</span> Back
      </RouterLink>

      <!-- Header -->
      <div class="mb-8">
        <div class="w-12 h-12 bg-emerald-900 rounded-2xl flex items-center justify-center mb-4">
          <span class="material-icons-outlined text-white text-2xl">school</span>
        </div>
        <h1 class="text-3xl font-bold text-slate-900 leading-tight">Apply as a Tutor</h1>
        <p class="text-slate-500 mt-2">Join our team of expert tutors and help learners connect with African languages.</p>
      </div>

      <!-- Info banner -->
      <div class="bg-amber-50 border border-amber-200 rounded-2xl px-4 py-3 flex gap-3 mb-6">
        <span class="material-icons-outlined text-amber-600 text-lg shrink-0 mt-0.5">info</span>
        <p class="text-sm text-amber-800">Applications are reviewed by our team. Once approved, you'll gain access to the tutor portal to upload lessons.</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="submit" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Full Name</label>
            <input v-model="form.name" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors" placeholder="Your full name" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Email</label>
            <input v-model="form.email" type="email" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors" placeholder="you@example.com" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Password</label>
            <input v-model="form.password" type="password" required minlength="6" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors" placeholder="Min. 6 characters" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Location</label>
            <input v-model="form.location" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors" placeholder="City, Country" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Languages You Can Teach</label>
          <!-- Tag chips -->
          <div v-if="form.languages_taught.length" class="flex flex-wrap gap-2 mb-2">
            <span
              v-for="lang in form.languages_taught"
              :key="lang"
              class="inline-flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold px-3 py-1.5 rounded-full"
            >
              {{ lang }}
              <button type="button" @click="removeLanguage(lang)" class="text-emerald-500 hover:text-red-500 transition-colors leading-none">&times;</button>
            </span>
          </div>
          <!-- Input row -->
          <div class="flex gap-2">
            <input
              v-model="languageInput"
              @keydown.enter.prevent="addLanguage"
              @keydown.comma.prevent="addLanguage"
              class="flex-1 border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
              placeholder="e.g. Kikuyu, Luo, Shona — press Enter to add"
            />
            <button type="button" @click="addLanguage" class="px-4 py-3 bg-emerald-900 text-white text-sm font-bold rounded-2xl hover:bg-emerald-800 transition-colors">Add</button>
          </div>
          <p class="text-xs text-slate-400 mt-1.5">Type any African language and press Enter or Add. You can add multiple.</p>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Primary Region</label>
          <select v-model="form.region" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors">
            <option value="">Select the region your language(s) belong to</option>
            <option value="West Africa">West Africa</option>
            <option value="East Africa">East Africa</option>
            <option value="Southern Africa">Southern Africa</option>
            <option value="North Africa">North Africa</option>
            <option value="Central Africa">Central Africa</option>
          </select>
          <p class="text-xs text-slate-400 mt-1.5">Helps learners discover your language via the region filter.</p>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Voice Character Name <span class="text-slate-300">(Optional)</span></label>
          <input v-model="form.voice_character" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors" placeholder="e.g. Amara, Juma…" />
          <p class="text-xs text-slate-400 mt-1.5">This is the in-app character name learners will see in your lessons.</p>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Bio</label>
          <textarea v-model="form.bio" rows="3" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 transition-colors resize-none" placeholder="Tell us about your language background and teaching experience…"></textarea>
        </div>

        <!-- Error -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-2xl px-4 py-3 text-sm text-red-700 font-medium">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="auth.loading || !form.languages_taught.length"
          class="w-full py-4 rounded-2xl bg-emerald-900 text-white font-bold text-base shadow-lg shadow-emerald-900/15 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          {{ auth.loading ? 'Submitting…' : 'Submit Application' }}
        </button>
      </form>

      <p class="text-center text-sm text-slate-500 mt-6">
        Already have an account?
        <RouterLink to="/login" class="font-bold text-emerald-700 hover:text-emerald-900">Sign in</RouterLink>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const languageInput = ref('')

const form = ref({
  name: '',
  email: '',
  password: '',
  location: '',
  region: '',
  languages_taught: [],
  voice_character: '',
  bio: '',
})

function addLanguage() {
  const val = languageInput.value.trim().replace(/,$/, '')
  if (val && !form.value.languages_taught.includes(val)) {
    form.value.languages_taught.push(val)
  }
  languageInput.value = ''
}

function removeLanguage(lang) {
  form.value.languages_taught = form.value.languages_taught.filter(l => l !== lang)
}

async function submit() {
  error.value = ''
  const result = await auth.registerTutor(form.value)
  if (result.success) {
    router.push('/tutor/dashboard')
  } else {
    error.value = result.message
  }
}
</script>
