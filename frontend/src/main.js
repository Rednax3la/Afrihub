import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then(registration => {
      const announce = () => window.dispatchEvent(new CustomEvent('app-update', { detail: registration }))
      if (registration.waiting) announce()
      registration.addEventListener('updatefound', () => {
        registration.installing?.addEventListener('statechange', event => {
          if (event.target.state === 'installed' && navigator.serviceWorker.controller) announce()
        })
      })
    }).catch(() => console.warn('Offline mode registration failed'))
  })
}
