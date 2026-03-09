import styles from './TranscriptSkeleton.module.css'

const ROWS = [
  { width: 'long' },
  { width: 'medium' },
  { width: 'short' },
  { width: 'long' },
  { width: 'medium' },
  { width: 'short' },
  { width: 'long' },
  { width: 'medium' },
]

export function TranscriptSkeleton() {
  return (
    <div className={styles.container} role="status" aria-label="Loading transcript" aria-busy="true">
      {ROWS.map((row, i) => (
        <div key={i} className={styles.skeletonRow}>
          <div className={`${styles.tsBar} ${styles.shimmer}`} />
          <div className={`${styles.textBar} ${styles[row.width]} ${styles.shimmer}`} />
        </div>
      ))}
    </div>
  )
}
