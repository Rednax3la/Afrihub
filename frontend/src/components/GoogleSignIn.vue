<template>
  <div class="mt-5">
    <button type="button" @click="signIn" :disabled="auth.loading" class="w-full border border-slate-200 bg-white p-4 rounded-2xl font-semibold text-slate-700 disabled:opacity-50">Continue with Google</button>
    <div ref="fallbackButton" class="flex justify-center mt-3"></div>
    <p v-if="error" role="alert" class="text-sm text-red-600 mt-2">{{ error }}</p>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const fallbackButton = ref(null)
function signIn() {
  error.value = ''
  const identity = window.google?.accounts?.id
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!identity || !clientId) {
    error.value = 'Google sign-in is unavailable. Please try again or use email.'
    return
  }
  identity.initialize({ client_id: clientId, callback: async response => {
    const result = await auth.loginWithGoogle(response.credential)
    if (result.success) {
      router.push(result.role === 'admin' ? '/admin/dashboard' : result.role === 'tutor' ? '/tutor/dashboard' : '/dashboard')
    } else error.value = result.message
  } })
  // A standard GIS button remains usable when One Tap is suppressed by the browser.
  identity.renderButton(fallbackButton.value, { theme: 'outline', size: 'large', text: 'continue_with' })
  identity.prompt()
}
</script>
