import { cn } from '../../utils/index.js'
import styles from './Panel.module.css'

export function Panel({
  children,
  maxWidth = '440px',
  marginTop = '40px',
  className,
}) {
  return (
    <div
      className={cn(styles.panel, className)}
      style={{ maxWidth, marginTop }}
    >
      {children}
    </div>
  )
}
