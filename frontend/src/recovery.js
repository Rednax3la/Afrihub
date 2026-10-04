import { createApp } from 'vue'
import PasswordRecoveryView from './views/PasswordRecoveryView.vue'
import './style.css'

// Keep the token only in this page's memory, not router history or browser storage.
const token = new URLSearchParams(window.location.hash.slice(1)).get('token') || ''
const resetting = window.location.pathname.replace(/\/$/, '') === '/reset-password'
window.history.replaceState(null, '', window.location.pathname)
createApp(PasswordRecoveryView, { token, resetting }).mount('#app')
