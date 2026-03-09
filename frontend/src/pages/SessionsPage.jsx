import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../components/layout/PageLayout'
import { Panel } from '../components/layout/Panel'
import { SessionCard } from '../components/sessions/SessionCard'
import { SessionsSkeleton } from '../components/sessions/SessionsSkeleton'
import { EmptyState } from '../components/common/EmptyState'
import { useSessions } from '../hooks/useSessions'
import styles from './SessionsPage.module.css'

export function SessionsPage() {
  const navigate = useNavigate()
  const { sessions, loading, error } = useSessions()

  const recordingCount = sessions.length
  const subtitle = loading
    ? 'Loading recordings…'
    : `${recordingCount} ${recordingCount === 1 ? 'recording' : 'recordings'}`

  return (
    <PageLayout>
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Sessions</h1>
        {!error && <p className={styles.pageSubtitle}>{subtitle}</p>}
      </div>

      <Panel maxWidth="640px" marginTop="0">
        {error && (
          <p className={styles.error}>Failed to load sessions: {error}</p>
        )}

        <div className={styles.sessionList}>
          {loading && <SessionsSkeleton />}

          {!loading && !error && sessions.length === 0 && (
            <EmptyState
              heading="No sessions yet"
              subtitle="Upload a class recording and it will be transcribed automatically."
              ctaLabel="Upload a Recording"
              onCta={() => navigate('/upload')}
            />
          )}

          {!loading && !error && sessions.map((session) => (
            <SessionCard key={session.id} session={session} />
          ))}
        </div>
      </Panel>
    </PageLayout>
  )
}
