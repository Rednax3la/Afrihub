// Client-side image downscaling, so a 4 MB phone photo isn't shipped whole
// over a mobile connection just to be shown at 112px.

const DEFAULT_MAX = 512

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => { URL.revokeObjectURL(url); resolve(img) }
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('Could not read that image.')) }
    img.src = url
  })
}

/**
 * Returns a File no larger than `max` px on its longest edge.
 * Falls back to the original file if the browser can't process it (e.g. HEIC),
 * letting the server produce the authoritative error message.
 */
export async function downscaleImage(file, max = DEFAULT_MAX) {
  if (!file?.type?.startsWith('image/') || file.type === 'image/gif') return file
  if (typeof document === 'undefined' || typeof createImageBitmap === 'undefined') return file

  try {
    const img = await loadImage(file)
    const longest = Math.max(img.width, img.height)
    if (!longest) return file
    if (longest <= max) return file

    const scale = max / longest
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(img.width * scale)
    canvas.height = Math.round(img.height * scale)
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)

    // PNG keeps transparency; everything else is cheaper as JPEG.
    const type = file.type === 'image/png' ? 'image/png' : 'image/jpeg'
    const blob = await new Promise(resolve => canvas.toBlob(resolve, type, 0.85))
    if (!blob) return file

    const ext = type === 'image/png' ? 'png' : 'jpg'
    const name = (file.name || 'avatar').replace(/\.[^.]+$/, '') + '.' + ext
    return new File([blob], name, { type, lastModified: Date.now() })
  } catch {
    return file
  }
}
