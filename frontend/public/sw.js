const STATIC_CACHE = 'vernaculearn-static-v3'
const API_PREFIX = 'vernaculearn-api-v2-'
const SHELL = ['/', '/dashboard', '/courses', '/lesson']

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(STATIC_CACHE)
    await cache.addAll(SHELL)
    // Cache only entry assets and static modulepreloads. Visited lazy routes are
    // cached on use; do not eagerly download every admin/tutor/learning chunk.
    const html = await (await cache.match('/')).text()
    const assets = [...html.matchAll(/(?:src|href)="([^"]+\.(?:js|css))"/g)].map(m => m[1])
    const seen = new Set()
    async function preload(path) {
      const url = new URL(path, self.location.origin)
      if (url.origin !== self.location.origin || seen.has(url.href)) return
      seen.add(url.href)
      const response = await fetch(url)
      if (!response.ok) throw new Error('Asset unavailable')
      await cache.put(url, response.clone())
    }
    await Promise.all(assets.map(preload))
  })())
})
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith('vernaculearn-') && name !== STATIC_CACHE && !name.startsWith(API_PREFIX)) await caches.delete(name)
    }
    await self.clients.claim()
  })())
})
async function apiCache(request) {
  const auth = request.headers.get('Authorization') || 'public'
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(auth))
  const key = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('')
  return caches.open(API_PREFIX + key)
}
self.addEventListener('message', event => {
  if (event.data?.type === 'ACTIVATE_UPDATE') self.skipWaiting()
  if (event.data?.type === 'CLEAR_API_CACHE') {
    event.waitUntil(caches.keys().then(names => Promise.all(names.filter(n => n.startsWith(API_PREFIX)).map(n => caches.delete(n)))))
  }
})
self.addEventListener('fetch', event => {
  const request = event.request
  const url = new URL(request.url)
  // Authentication and recovery must never use an offline response.
  if (url.pathname.startsWith('/api/auth/') || ['/reset-password', '/forgot-password', '/recovery.html'].includes(url.pathname.replace(/\/$/, ''))) {
    event.respondWith(fetch(request, { cache: 'no-store', referrerPolicy: 'no-referrer' }))
    return
  }
  // Writes and payments are never cached or replayed.
  if (request.method !== 'GET') return
  if (url.pathname.startsWith('/api/')) {
    event.respondWith((async () => {
      const cache = await apiCache(request)
      try {
        const response = await fetch(request)
        if (response.ok && !response.headers.get('Cache-Control')?.includes('no-store')) await cache.put(request, response.clone())
        else await cache.delete(request)
        return response
      } catch {
        return await cache.match(request) || new Response(JSON.stringify({ detail: 'This content is not available offline' }), {
          status: 503, headers: { 'Content-Type': 'application/json' },
        })
      }
    })())
    return
  }
  if (url.origin !== self.location.origin) return
  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try { return await fetch(request) } catch {
        const cache = await caches.open(STATIC_CACHE)
        return await cache.match(request) || await cache.match('/')
      }
    })())
  } else if (['script', 'style', 'image', 'font'].includes(request.destination)) {
    event.respondWith((async () => {
      const cache = await caches.open(STATIC_CACHE)
      const cached = await cache.match(request)
      if (cached) return cached
      const response = await fetch(request)
      if (response.ok && !response.headers.get('Cache-Control')?.includes('no-store')) await cache.put(request, response.clone())
      return response
    })())
  }
})
self.addEventListener('push', event => {
  let data = {}
  try { data = event.data?.json() || {} } catch { data.body = event.data?.text() }
  event.waitUntil(self.registration.showNotification(data.title || 'Vernaculearn', {
    body: data.body || '', icon: '/Vernaculearn logo.png', data: { url: '/dashboard' },
  }))
})
self.addEventListener('notificationclick', event => {
  event.notification.close()
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    for (const client of windows) {
      if (new URL(client.url).origin === self.location.origin) {
        await client.navigate('/dashboard')
        return client.focus()
      }
    }
    return self.clients.openWindow('/dashboard')
  })())
})
