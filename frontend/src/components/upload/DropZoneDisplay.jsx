import { cn } from '../../utils/index.js'
import { MAX_FILE_SIZE_BYTES, ACCEPTED_FILE_TYPES } from '../../constants/index.js'
import { formatFileSize } from '../../utils/index.js'
import styles from './DropZoneDisplay.module.css'

const MAX_SIZE_LABEL = formatFileSize(MAX_FILE_SIZE_BYTES)
const FORMAT_LABEL = ACCEPTED_FILE_TYPES.map((ext) => ext.slice(1).toUpperCase()).join(', ')

/**
 * @param {{ isDragOver: boolean, isDragInvalid: boolean }} props
 */
export function DropZoneDisplay({ isDragOver, isDragInvalid }) {
  const isAccepting = isDragOver && !isDragInvalid

  return (
    <div className={cn(styles.dropzone, isAccepting && styles.accepting, isDragInvalid && styles.rejecting)}>
      <div className={styles.visualIndicator}>
        <div className={styles.crosshairX} />
        <div className={styles.crosshairY} />
        <div className={styles.centerDot} />
      </div>

      <div className={styles.textContent}>
        <h2 className={styles.primaryInstruction}>
          {isAccepting ? 'Release to upload' : isDragInvalid ? 'Invalid format' : 'Drag file here'}
        </h2>

        <div className={styles.secondaryInstruction}>
          {!isDragOver && (
            <span className={styles.orText}>or click to browse</span>
          )}
        </div>
      </div>

      <div className={styles.footerSpecs}>
        <span>AUDIO / VIDEO</span>
        <span className={styles.dot}>•</span>
        <span>{FORMAT_LABEL}</span>
        <span className={styles.dot}>•</span>
        <span>MAX {MAX_SIZE_LABEL}</span>
      </div>
    </div>
  )
}
