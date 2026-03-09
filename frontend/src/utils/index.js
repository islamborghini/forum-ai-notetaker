export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}

const STATUS_MAP = {
  complete:    'transcribed',
  transcribed: 'transcribed',
  processing:  'processing',
  queued:      'queued',
  error:       'error',
}

export function normalizeStatus(status) {
  return STATUS_MAP[status] ?? status
}

export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1).replace(/\.0$/, '')} KB`
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1).replace(/\.0$/, '')} MB`
  return `${(bytes / 1024 ** 3).toFixed(1).replace(/\.0$/, '')} GB`
}

export function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatShortDate(isoString) {
  return new Date(isoString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

export function formatMeta(session) {
  if (!session) return ''
  const datePart = session.created_at ? formatShortDate(session.created_at) : ''
  const durationPart = session.duration_seconds != null ? formatDuration(session.duration_seconds) : ''
  if (datePart && durationPart) return `${datePart} · ${durationPart}`
  return datePart || durationPart
}

export function formatSessionName(filename) {
  const withoutExt = filename.replace(/\.[^/.]+$/, '')
  return withoutExt
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
