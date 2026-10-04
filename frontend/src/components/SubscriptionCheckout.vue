<template>
  <div class="space-y-4">
    <p v-if="checking" role="status">Checking purchase availability?</p>
    <p v-else-if="!available.mpesa && !googleReady" role="status">Purchases are currently unavailable. Please try again after payment setup is complete.</p>
    <label v-if="available.mpesa" class="block text-sm font-semibold">M-Pesa phone number
      <input v-model="phone" type="tel" autocomplete="tel" placeholder="0712345678" :disabled="busy" class="mt-2 w-full rounded-2xl border border-slate-200 bg-white p-3 text-slate-900" />
    </label>
    <button v-if="available.mpesa" @click="payMpesa" :disabled="busy" class="w-full rounded-2xl bg-amber-500 text-[#003B5C] py-4 font-bold disabled:opacity-50">{{ busy ? 'Waiting for payment...' : 'Subscribe with M-Pesa' }}</button>
    <div v-show="googleReady" ref="googleButton" :class="busy ? 'pointer-events-none opacity-50' : ''"></div>
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
const checking = ref(true)
const available = ref({ mpesa: false, google_pay: false })
const googleReady = ref(false)
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
onMounted(async () => {
  try {
    const { data } = await paymentApi.availability()
    if (disposed) return
    available.value = data
    const matches = data.google_pay_environment === (import.meta.env.VITE_GOOGLE_PAY_ENVIRONMENT || 'TEST')
    if (props.allowGoogle && data.google_pay && matches && await googlePay.isReady()) {
      if (!disposed && googleButton.value) {
        googleButton.value.replaceChildren(googlePay.createButton(payGoogle))
        googleReady.value = true
      }
    }
  } catch { error.value = 'Unable to check payment availability. Please try again later.' }
  finally { checking.value = false }
})
onUnmounted(() => { disposed = true; clearTimeout(pollTimer) })
</script>
