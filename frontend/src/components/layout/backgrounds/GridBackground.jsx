import styles from './GridBackground.module.css'

export function GridBackground() {
  return (
    <div className={styles.wrapper} aria-hidden="true">
      <div className={styles.gridPattern} />
      <div className={styles.radialMask} />
      <div className={styles.orbTop} />
      <div className={styles.orbBottom} />
    </div>
  )
}
