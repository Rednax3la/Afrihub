<template>
  <main class="min-h-screen bg-[#FDFCFB] flex items-center justify-center p-6">
    <section class="w-full max-w-md bg-white rounded-3xl p-6 shadow-sm">
      <h1 class="text-3xl font-bold text-emerald-950 mb-3">{{ resetting ? 'Reset password' : 'Forgot password?' }}</h1>
      <p v-if="!resetting" class="text-slate-600 mb-5">Enter the email you use to sign in. Reset links expire after 30 minutes.</p>
      <p v-if="resetting && !token" role="alert" class="text-red-700">Open the complete link from your email. If you refreshed this page, reopen the link.</p>
      <form v-if="!done && (!resetting || token)" class="space-y-4" @submit.prevent="submit">
        <div v-if="!resetting">
          <label for="recovery-email" class="block font-semibold mb-2">Email</label>
          <input id="recovery-email" v-model="email" name="email" type="email" autocomplete="email" required
            class="w-full p-4 border rounded-2xl" />
        </div>
        <template v-else>
          <PasswordInput id="reset-password" v-model="password" label="New password" show-requirements />
          <PasswordInput id="confirm-password" v-model="confirmation" label="Confirm new password" />
        </template>
        <p v-if="error" role="alert" class="text-red-700">{{ error }}</p>
        <button type="submit" :disabled="busy" class="w-full p-4 rounded-2xl bg-emerald-900 text-white font-bold disabled:opacity-60">
          {{ busy ? 'Please wait…' : resetting ? 'Reset password' : 'Request reset email' }}
        </button>
      </form>
      <p v-if="message" role="status" class="my-4 text-emerald-900">{{ message }}</p>
      <a v-if="resetting" href="/forgot-password" class="block mt-5 text-emerald-800 underline">Request another reset link</a>
      <a href="/login" class="block mt-5 text-emerald-800 underline">Return to sign in</a>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import PasswordInput from '@/components/PasswordInput.vue'
import { validNewPassword } from '@/utils/passwords'
import { authError } from '@/utils/authErrors'

const props = defineProps({ token: String, resetting: Boolean })
const email = ref(''), password = ref(''), confirmation = ref('')
const busy = ref(false), done = ref(false), error = ref(''), message = ref('')
async function submit() {
  error.value = ''
  if (props.resetting && !validNewPassword(password.value)) {
    error.value = 'Please meet all the password requirements.'
    return
  }
  if (props.resetting && password.value !== confirmation.value) {
    error.value = 'Passwords do not match.'
    return
  }
  busy.value = true
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 20000)
  try {
    const origin = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')
    const response = await fetch(`${origin}/api/auth/${props.resetting ? 'reset-password' : 'forgot-password'}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      cache: 'no-store', referrerPolicy: 'no-referrer', credentials: 'omit', signal: controller.signal,
      body: JSON.stringify(props.resetting ? { token: props.token, password: password.value } : { email: email.value }),
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw { response: { status: response.status, data } }
    message.value = data.message
    done.value = true
    password.value = confirmation.value = ''
    if (props.resetting) {
      localStorage.removeItem('token')
      navigator.serviceWorker?.controller?.postMessage({ type: 'CLEAR_API_CACHE' })
    }
  } catch (err) {
    error.value = authError(err)
  } finally {
    clearTimeout(timeout)
    busy.value = false
  }
}
</script>
