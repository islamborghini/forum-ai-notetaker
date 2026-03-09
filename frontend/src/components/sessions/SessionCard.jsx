import { useNavigate } from 'react-router-dom'
import { StatusBadge } from '../common/StatusBadge'
import { cn, normalizeStatus, formatDate, formatDuration, formatSessionName } from '../../utils/index.js'
import styles from './SessionCard.module.css'

export function SessionCard({ session }) {
  const navigate = useNavigate()
  const status = normalizeStatus(session.status)
  const isClickable = status === 'transcribed'
  const isProcessing = status === 'processing'

  function handleClick() {
    if (isClickable) navigate(`/sessions/${session.id}`)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  return (
    <div
      className={cn(styles.sessionRow, isClickable && styles.clickable, isProcessing && styles.processing)}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      aria-label={isClickable ? `View transcript for ${formatSessionName(session.filename)}` : undefined}
      aria-disabled={isProcessing ? true : undefined}
    >
      <div className={styles.left}>
        <div className={styles.title}>{formatSessionName(session.filename)}</div>
        <div className={styles.meta}>
          <span>{formatDate(session.created_at)}</span>
          {session.duration_seconds != null && (
            <><span className={styles.dot}>·</span><span>{formatDuration(session.duration_seconds)}</span></>
          )}
          {session.word_count != null && (
            <><span className={styles.dot}>·</span><span>~{session.word_count.toLocaleString()} words</span></>
          )}
        </div>
      </div>
      <div className={styles.right}>
        <StatusBadge status={status} />
      </div>
    </div>
  )
}
