<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col md:items-center md:justify-center p-8 md:p-0">
    <div class="w-full md:max-w-md md:bg-white md:rounded-[2.5rem] md:shadow-xl md:shadow-slate-100 md:p-12">
      <button @click="$router.back()" class="w-10 h-10 flex items-center justify-center text-slate-400 mb-8 md:mb-6">
        <span class="material-icons-outlined">arrow_back</span>
      </button>

      <div class="mb-10">
        <h2 class="text-3xl font-bold serif text-emerald-950 mb-2">Welcome back</h2>
        <p class="text-slate-500">Continue your language journey.</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
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
            placeholder="••••••••"
            required
            class="w-full p-4 rounded-2xl border border-slate-200 bg-white text-slate-800 outline-none focus:border-emerald-400 transition-colors"
          />
        </div>

        <p v-if="error" class="text-red-500 text-sm font-medium">{{ error }}</p>

        <button
          type="submit"
          :disabled="auth.loading"
          class="w-full bg-emerald-900 text-white py-5 rounded-3xl font-bold text-lg shadow-lg shadow-emerald-900/20 active:scale-95 transition-transform mt-4 disabled:opacity-60"
        >
          {{ auth.loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <p class="text-center text-slate-500 mt-8">
        Don't have an account?
        <RouterLink to="/register" class="text-emerald-700 font-semibold">Sign up</RouterLink>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const error = ref('')
const form = ref({ email: '', password: '' })

async function handleLogin() {
  error.value = ''
  const result = await auth.login(form.value.email, form.value.password)
  if (result.success) {
    if (result.role === 'admin') router.push('/admin/dashboard')
    else if (result.role === 'tutor') router.push('/tutor/dashboard')
    else router.push('/dashboard')
  } else {
    error.value = result.message
  }
}
</script>
