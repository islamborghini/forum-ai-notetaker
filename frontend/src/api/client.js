if (!import.meta.env.VITE_API_URL) {
  throw new Error('VITE_API_URL is not set. Copy .env.example to .env and fill it in.')
}

const BASE_URL = import.meta.env.VITE_API_URL
const BODY_METHODS = new Set(['POST', 'PUT', 'PATCH'])

async function request(path, options = {}) {
  const method = (options.method ?? 'GET').toUpperCase()
  const headers = BODY_METHODS.has(method) ? { 'Content-Type': 'application/json' } : {}

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const error = new Error(body.message || `Request failed: HTTP ${response.status}`)
    error.status = response.status
    throw error
  }

  return response.json().catch(() => {
    throw new Error('Invalid JSON in server response')
  })
}

export function uploadRecording(file, onProgress) {
  const xhr = new XMLHttpRequest()

  const promise = new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append('file', file)

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText))
        } catch {
          reject(new Error('Invalid JSON in upload response'))
        }
      } else {
        const body = (() => { try { return JSON.parse(xhr.responseText) } catch { return {} } })()
        const error = new Error(body.message || `Upload failed: HTTP ${xhr.status}`)
        error.status = xhr.status
        reject(error)
      }
    })

    xhr.addEventListener('error', () => reject(new Error('Network error during upload')))
    xhr.addEventListener('abort', () => reject(new Error('Upload cancelled')))

    xhr.open('POST', `${BASE_URL}/upload`)
    xhr.send(formData)
  })

  promise.abort = () => xhr.abort()

  return promise
}

export const api = {
  uploadRecording,
  getSessions:   ()   => request('/sessions'),
  getTranscript: (id) => request(`/sessions/${id}/transcript`),
}
