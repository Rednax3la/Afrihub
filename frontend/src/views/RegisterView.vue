<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col p-8">
    <button @click="$router.back()" class="w-10 h-10 flex items-center justify-center text-slate-400 mb-8">
      <span class="material-icons-outlined">arrow_back</span>
    </button>

    <div class="mb-10">
      <h2 class="text-3xl font-bold serif text-emerald-950 mb-2">Join Afrihub</h2>
      <p class="text-slate-500">Create your account and start learning.</p>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-4 flex-1">
      <div>
        <label class="block text-sm font-semibold text-slate-600 mb-2">Full Name</label>
        <input
          v-model="form.name"
          type="text"
          placeholder="Kwame Mensah"
          required
          class="w-full p-4 rounded-2xl border border-slate-200 bg-white text-slate-800 outline-none focus:border-emerald-400 transition-colors"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-slate-600 mb-2">Email</label>
        <input
          v-model="form.email"
          type="email"
          placeholder="you@example.com"
          required
          class="w-full p-4 rounded-2xl border border-slate-200 bg-white text-slate-800 outline-none focus:border-emerald-400 transition-colors"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-slate-600 mb-2">Password</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="At least 6 characters"
          required
          minlength="6"
          class="w-full p-4 rounded-2xl border border-slate-200 bg-white text-slate-800 outline-none focus:border-emerald-400 transition-colors"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-slate-600 mb-2">Location <span class="font-normal text-slate-400">(optional)</span></label>
        <input
          v-model="form.location"
          type="text"
          placeholder="Accra, Ghana"
          class="w-full p-4 rounded-2xl border border-slate-200 bg-white text-slate-800 outline-none focus:border-emerald-400 transition-colors"
        />
      </div>

      <p v-if="error" class="text-red-500 text-sm font-medium">{{ error }}</p>

      <button
        type="submit"
        :disabled="auth.loading"
        class="w-full bg-emerald-900 text-white py-5 rounded-3xl font-bold text-lg shadow-lg shadow-emerald-900/20 active:scale-95 transition-transform mt-4 disabled:opacity-60"
      >
        {{ auth.loading ? 'Creating account...' : 'Create Account' }}
      </button>
    </form>

    <p class="text-center text-slate-500 mt-8">
      Already have an account?
      <RouterLink to="/login" class="text-emerald-700 font-semibold">Sign in</RouterLink>
    </p>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const error = ref('')
const form = ref({ name: '', email: '', password: '', location: '' })

async function handleRegister() {
  error.value = ''
  const result = await auth.register(form.value.name, form.value.email, form.value.password, form.value.location)
  if (result.success) {
    router.push('/dashboard')
  } else {
    error.value = result.message
  }
}
</script>
