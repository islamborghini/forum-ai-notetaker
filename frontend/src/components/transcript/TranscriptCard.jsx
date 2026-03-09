import styles from './TranscriptCard.module.css'

export function TranscriptCard({ entry }) {
  return (
    <div className={styles.row}>
      <span className={styles.timestamp}>{entry.timestamp}</span>
      <p className={styles.text}>{entry.text}</p>
    </div>
  )
}
