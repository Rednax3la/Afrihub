const pending = new Map()
export function loadScript(src) {
  if (pending.has(src)) return pending.get(src)
  const promise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.referrerPolicy = 'no-referrer'
    const timer = setTimeout(() => { script.remove(); pending.delete(src); reject(new Error('Service took too long to load. Try again.')) }, 15000)
    script.onload = () => { clearTimeout(timer); resolve() }
    script.onerror = () => { clearTimeout(timer); script.remove(); pending.delete(src); reject(new Error('Service could not load. Check your connection.')) }
    document.head.appendChild(script)
  })
  pending.set(src, promise)
  return promise
}
