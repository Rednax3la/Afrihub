import test from 'node:test'
import assert from 'node:assert/strict'
import vm from 'node:vm'
import { readFile } from 'node:fs/promises'
import { webcrypto } from 'node:crypto'

const code = await readFile(new URL('../public/sw.js', import.meta.url), 'utf8')
function worker() {
  const handlers = {}
  const stores = new Map()
  const notifications = []
  const key = request => typeof request === 'string' ? new URL(request, 'https://app.test').href : request.url || request.href
  let network = async () => new Response('network')
  const caches = {
    keys: async () => [...stores.keys()],
    delete: async name => stores.delete(name),
    open: async name => {
      if (!stores.has(name)) stores.set(name, new Map())
      const entries = stores.get(name)
      return {
        match: async request => entries.get(key(request))?.clone(),
        put: async (request, response) => entries.set(key(request), response.clone()),
        delete: async request => entries.delete(key(request)),
        addAll: async urls => { for (const url of urls) entries.set(key(url), await network(url)) },
      }
    },
  }
  const self = {
    location: { origin: 'https://app.test' },
    addEventListener: (name, handler) => { handlers[name] = handler },
    clients: { claim: async () => {}, matchAll: async () => [], openWindow: async () => {} },
    registration: { showNotification: async (title, options) => notifications.push({ title, ...options }) },
  }
  vm.runInNewContext(code, { self, caches, fetch: (...args) => network(...args), crypto: webcrypto, TextEncoder, URL, Response, Uint8Array })
  return {
    caches, stores, notifications,
    network: fn => { network = fn },
    async event(name, event = {}) {
      let promise
      handlers[name]({ ...event, waitUntil: p => { promise = p }, respondWith: p => { promise = p } })
      return promise
    },
  }
}
const apiRequest = token => new Request('https://api.test/api/users/me', { headers: { Authorization: 'Bearer ' + token } })

test('API fallback is isolated by login and does not replace a server denial', async () => {
  const sw = worker()
  sw.network(async () => new Response('Alice'))
  assert.equal(await (await sw.event('fetch', { request: apiRequest('alice') })).text(), 'Alice')
  sw.network(async () => { throw new Error('offline') })
  assert.equal(await (await sw.event('fetch', { request: apiRequest('alice') })).text(), 'Alice')
  assert.equal((await sw.event('fetch', { request: apiRequest('bob') })).status, 503)
  sw.network(async () => new Response('Locked', { status: 403 }))
  assert.equal((await sw.event('fetch', { request: apiRequest('alice') })).status, 403)
  sw.network(async () => { throw new Error('offline') })
  assert.equal((await sw.event('fetch', { request: apiRequest('alice') })).status, 503)
})

test('writes never enter the offline cache', async () => {
  const sw = worker()
  const result = await sw.event('fetch', { request: new Request('https://api.test/api/payments/google-pay', { method: 'POST', body: '{}' }) })
  assert.equal(result, undefined)
  assert.equal(sw.stores.size, 0)
})

test('install preloads the app shell and nested Vite chunks', async () => {
  const sw = worker()
  sw.network(async request => {
    const path = new URL(request.url || request.href || request, 'https://app.test').pathname
    if (path === '/assets/main.js') return new Response('import("./Dashboard.js"); const a=["assets/lesson.css"]')
    if (path.endsWith('.js') || path.endsWith('.css')) return new Response('/* asset */')
    return new Response('<script src="/assets/main.js"></script>')
  })
  await sw.event('install')
  const cache = await sw.caches.open('vernaculearn-static-v1')
  for (const path of ['/', '/dashboard', '/courses', '/lesson', '/assets/main.js', '/assets/Dashboard.js', '/assets/lesson.css']) assert.ok(await cache.match(path), path)
})

test('logout clears API caches and activation deletes obsolete app caches only', async () => {
  const sw = worker()
  await sw.caches.open('vernaculearn-static-v0')
  await sw.caches.open('other-application')
  await sw.event('fetch', { request: apiRequest('alice') })
  await sw.event('activate')
  assert.ok(!sw.stores.has('vernaculearn-static-v0'))
  assert.ok(sw.stores.has('other-application'))
  await sw.event('message', { data: { type: 'CLEAR_API_CACHE' } })
  assert.ok(![...sw.stores.keys()].some(name => name.startsWith('vernaculearn-api-')))
})

test('push messages display title and body', async () => {
  const sw = worker()
  await sw.event('push', { data: { json: () => ({ title: 'Review', body: 'Time to learn' }) } })
  assert.equal(sw.notifications[0].title, 'Review')
  assert.equal(sw.notifications[0].body, 'Time to learn')
})
