import { useRef, useState } from 'react'
import { ACCEPTED_FILE_TYPES, ACCEPTED_MIME_TYPES } from '../../constants/index.js'
import { DropZoneDisplay } from './DropZoneDisplay'
import styles from './DropZone.module.css'

const ACCEPT_ATTR = [...ACCEPTED_FILE_TYPES, ...ACCEPTED_MIME_TYPES].join(',')

/**
 * @param {{ onFile: (file: File) => void }} props
 */
export function DropZone({ onFile }) {
  const inputRef = useRef(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [isDragInvalid, setIsDragInvalid] = useState(false)

  function handleDragOver(e) {
    e.preventDefault()
    const file = e.dataTransfer.items?.[0]
    setIsDragOver(true)
    setIsDragInvalid(file ? !ACCEPTED_MIME_TYPES.includes(file.type) : false)
  }

  function handleDragLeave(e) {
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragOver(false)
      setIsDragInvalid(false)
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragOver(false)
    setIsDragInvalid(false)
    const file = e.dataTransfer.files?.[0]
    if (file) onFile(file)
  }

  function handleInputChange(e) {
    const file = e.target.files?.[0]
    if (file) onFile(file)
    e.target.value = ''
  }

  return (
    <button
      type="button"
      className={styles.wrapper}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      aria-label="Upload recording — click or drag and drop"
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT_ATTR}
        className={styles.hiddenInput}
        onChange={handleInputChange}
        tabIndex={-1}
      />
      <DropZoneDisplay isDragOver={isDragOver} isDragInvalid={isDragInvalid} />
    </button>
  )
}
