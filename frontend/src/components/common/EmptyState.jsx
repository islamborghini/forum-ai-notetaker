import { Button } from './Button'
import { DocumentIcon } from '../icons/DocumentIcon'
import styles from './EmptyState.module.css'

export function EmptyState({
  heading = 'No recordings yet',
  subtitle = 'Upload a recording to get started.',
  ctaLabel,
  onCta,
}) {
  return (
    <div className={styles.emptyState}>
      <span className={styles.icon}>
        <DocumentIcon />
      </span>
      <h2 className={styles.heading}>{heading}</h2>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      {ctaLabel && onCta && (
        <Button onClick={onCta}>{ctaLabel}</Button>
      )}
    </div>
  )
}
