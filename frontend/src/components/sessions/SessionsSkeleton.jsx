import styles from './SessionsSkeleton.module.css'

function SkeletonRow() {
  return (
    <div className={styles.skeletonRow}>
      <div className={styles.left}>
        <div className={`${styles.titleBar} ${styles.shimmer}`} />
        <div className={`${styles.metaBar} ${styles.shimmer}`} />
      </div>
      <div className={`${styles.badgeBar} ${styles.shimmer}`} />
    </div>
  )
}

export function SessionsSkeleton() {
  return (
    <div role="status" aria-label="Loading sessions" aria-busy="true" className={styles.container}>
      <SkeletonRow />
      <SkeletonRow />
      <SkeletonRow />
    </div>
  )
}
