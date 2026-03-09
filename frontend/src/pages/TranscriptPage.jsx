import { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { PageLayout } from '../components/layout/PageLayout'
import { Panel } from '../components/layout/Panel'
import { TranscriptCard } from '../components/transcript/TranscriptCard'
import { TranscriptSkeleton } from '../components/transcript/TranscriptSkeleton'
import { StatusBadge } from '../components/common/StatusBadge'
import { useTranscript } from '../hooks/useTranscript'
import { normalizeStatus, formatMeta, formatSessionName } from '../utils/index.js'
import { POLL_INTERVAL_MS } from '../constants/index.js'
import styles from './TranscriptPage.module.css'

export function TranscriptPage() {
  const { id } = useParams()
  const { data, loading, error, refetch } = useTranscript(id)

  const session = data
    ? {
        ...data,
        name: formatSessionName(data.filename),
        status: normalizeStatus(data.status),
      }
    : null

  const transcript = data?.segments ?? []
  const isProcessing = session?.status === 'processing'

  useEffect(() => {
    if (!isProcessing) return
    const interval = setInterval(refetch, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [isProcessing, refetch])

  return (
    <PageLayout>
      <div className={styles.wrapper}>
        <Link to="/sessions" className={styles.backLink}>
          <span aria-hidden="true">←</span> Sessions
        </Link>

        <Panel marginTop="0px" maxWidth="672px">
          {loading && !session && <TranscriptSkeleton />}

          {error && (
            <div className={styles.errorBox}>{error}</div>
          )}

          {session && (
            <>
              <div className={styles.headerRow}>
                <h2 className={styles.sessionTitle}>{session.name || 'Recording'}</h2>
                <StatusBadge status={session.status} />
              </div>
              <p className={styles.sessionMeta}>{formatMeta(session)}</p>

              {session.status === 'processing' && (
                <div className={styles.processingBox}>
                  <div className={styles.processingDot} />
                  <div className={styles.processingTextGroup}>
                    <p className={styles.processingTitle}>Transcription in progress…</p>
                    <p className={styles.processingSubtitle}>This usually takes a few minutes. Checking automatically.</p>
                  </div>
                </div>
              )}

              {session.status === 'error' && (
                <div className={styles.errorBox}>Failed to process this recording.</div>
              )}

              {session.status === 'transcribed' && (
                <div className={styles.transcriptList}>
                  {transcript.map((entry, index) => (
                    <TranscriptCard key={entry.timestamp ?? index} entry={entry} />
                  ))}
                </div>
              )}
            </>
          )}
        </Panel>
      </div>
    </PageLayout>
  )
}
