<template>
  <div class="space-y-4">
    <label class="block text-sm font-semibold">M-Pesa phone number
      <input v-model="phone" type="tel" autocomplete="tel" placeholder="0712345678" :disabled="busy" class="mt-2 w-full rounded-2xl border border-slate-200 bg-white p-3 text-slate-900" />
    </label>
    <button @click="payMpesa" :disabled="busy" class="w-full rounded-2xl bg-amber-500 text-[#003B5C] py-4 font-bold disabled:opacity-50">{{ busy ? 'Waiting for payment...' : 'Subscribe with M-Pesa' }}</button>
    <div v-if="allowGoogle" ref="googleButton" :class="busy ? 'pointer-events-none opacity-50' : ''"></div>
    <p v-if="message" role="status" class="text-sm">{{ message }}</p>
    <p v-if="error" role="alert" class="text-sm text-red-500">{{ error }}</p>
    <button v-if="pendingCheckout && !busy" @click="checkPayment" class="text-sm underline">Check M-Pesa payment status</button>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { paymentApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useGooglePay } from '@/composables/useGooglePay'
const props = defineProps({ tier: { type: String, required: true }, allowGoogle: { type: Boolean, default: true } })
const emit = defineEmits(['activated'])
const auth = useAuthStore()
const googlePay = useGooglePay()
const phone = ref('')
const busy = ref(false)
const message = ref('')
const error = ref('')
const googleButton = ref(null)
const pendingCheckout = ref('')
let disposed = false
let googleTimer
let pollTimer
let polls = 0
async function activated() {
  pendingCheckout.value = ''
  message.value = 'Subscription activated. Enjoy your lessons!'
  await auth.refreshUser()
  navigator.serviceWorker?.controller?.postMessage({ type: 'CLEAR_API_CACHE' })
  emit('activated')
}
async function payGoogle() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  message.value = ''
  const tier = props.tier
  try {
    const token = await googlePay.requestPayment(tier === 'yearly' ? 12999 : 1299, tier === 'yearly' ? 'Yearly access' : 'Monthly access')
    await paymentApi.googlePay(token, tier)
    await activated()
  } catch (err) {
    if (err.statusCode !== 'CANCELED') error.value = err.response?.data?.detail || err.message || 'Google Pay could not complete the payment.'
  } finally { busy.value = false }
}
async function checkPayment() {
  if (disposed || !pendingCheckout.value) return
  busy.value = true
  try {
    const { data } = await paymentApi.mpesaStatus(pendingCheckout.value)
    if (disposed) return
    if (data.status === 'completed') { await activated(); busy.value = false; return }
    if (data.status === 'failed') {
      pendingCheckout.value = ''
      throw new Error('Payment was cancelled or failed. Please try again.')
    }
    if (++polls < 24) pollTimer = setTimeout(checkPayment, 5000)
    else { busy.value = false; message.value = 'Payment is still pending. You can check its status again.' }
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Could not check payment status.'
    busy.value = false
  }
}
async function payMpesa() {
  if (busy.value) return
  error.value = ''
  message.value = ''
  const normalized = phone.value.replace(/[\s-]/g, '')
  if (!/^(?:\+?254|0)[17]\d{8}$/.test(normalized)) {
    error.value = 'Enter a valid Kenyan M-Pesa phone number.'
    return
  }
  busy.value = true
  try {
    const { data } = await paymentApi.stkPush(normalized, props.tier)
    pendingCheckout.value = data.checkout_request_id
    message.value = data.message
    polls = 0
    pollTimer = setTimeout(checkPayment, 5000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not start M-Pesa payment.'
    busy.value = false
  }
}
onMounted(() => {
  if (!props.allowGoogle) return
  let attempts = 0
  const setup = async () => {
    if (disposed) return
    if (await googlePay.isReady()) {
      if (!disposed && googleButton.value) googleButton.value.replaceChildren(googlePay.createButton(payGoogle))
    } else if (++attempts < 20) googleTimer = setTimeout(setup, 500)
  }
  setup()
})
onUnmounted(() => { disposed = true; clearTimeout(googleTimer); clearTimeout(pollTimer) })
</script>
