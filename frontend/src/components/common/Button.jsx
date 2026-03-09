import styles from './Button.module.css'

export function Button({ children, variant = 'primary', onClick, disabled, type = 'button', className }) {
  const classes = [styles.button, styles[variant], className].filter(Boolean).join(' ')
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={classes}
    >
      {children}
    </button>
  )
}
