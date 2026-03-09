import { cn } from '../../utils/index.js'
import styles from './StatusBadge.module.css'

const CONFIG = {
  transcribed: { label: 'Transcribed', mod: styles.transcribed, spinner: false },
  complete:    { label: 'Transcribed', mod: styles.transcribed, spinner: false },
  processing:  { label: 'Processing',  mod: styles.processing,  spinner: true  },
  queued:      { label: 'Queued',      mod: styles.processing,  spinner: true  },
  error:       { label: 'Error',       mod: styles.error,       spinner: false },
}

export function StatusBadge({ status }) {
  const config = CONFIG[status]
  if (!config) {
    if (import.meta.env.DEV) {
      console.warn(`[StatusBadge] Unknown status: "${status}"`)
    }
  }
  const resolved = config ?? CONFIG.processing
  return (
    <span className={cn(styles.badge, resolved.mod)} aria-label={resolved.label}>
      {resolved.spinner
        ? <span className={styles.spinner} aria-hidden="true" />
        : <span className={styles.dot} aria-hidden="true" />
      }
      {resolved.label}
    </span>
  )
}
