import { ref, onMounted } from 'vue'
import { userApi } from '@/api'
import { useAuthStore } from '@/stores/auth'

function decodeKey(value) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/')
  return Uint8Array.from(atob(base64 + '='.repeat((4 - base64.length % 4) % 4)), c => c.charCodeAt(0))
}
export function usePushNotifications() {
  const auth = useAuthStore()
  const isSupported = !!(window.isSecureContext && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window)
  const isSubscribed = ref(false)
  async function registration() {
    let reg = await navigator.serviceWorker.getRegistration('/')
    if (!reg) reg = await navigator.serviceWorker.register('/sw.js')
    if (reg.active) return reg
    return Promise.race([
      navigator.serviceWorker.ready,
      new Promise((_, reject) => setTimeout(() => reject(new Error('Offline support could not start. Reload and try again.')), 15000)),
    ])
  }
  onMounted(async () => {
    if (!isSupported) return
    try {
      const reg = await navigator.serviceWorker.getRegistration('/')
      isSubscribed.value = !!(reg && await reg.pushManager.getSubscription() && auth.user?.push_enabled)
    } catch { isSubscribed.value = false }
  })
  async function subscribe() {
    if (!isSupported) throw new Error('Push notifications are not supported in this browser.')
    const permission = await Notification.requestPermission()
    if (permission !== 'granted') throw new Error('Allow notifications in your browser settings to enable reminders.')
    const { data } = await userApi.getVapidPublicKey()
    const reg = await registration()
    let subscription = await reg.pushManager.getSubscription()
    if (!subscription) subscription = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: decodeKey(data.public_key) })
    await userApi.savePushSubscription(subscription.toJSON())
    isSubscribed.value = true
    await auth.refreshUser()
  }
  async function unsubscribe() {
    if (!isSupported) return
    await userApi.removePushSubscription()
    const reg = await navigator.serviceWorker.getRegistration('/')
    const subscription = await reg?.pushManager.getSubscription()
    if (subscription) await subscription.unsubscribe()
    isSubscribed.value = false
    await auth.refreshUser()
  }
  return { isSupported, isSubscribed, subscribe, unsubscribe }
}
