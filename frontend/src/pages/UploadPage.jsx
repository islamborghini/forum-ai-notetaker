import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../components/layout/PageLayout'
import { DropZone } from '../components/upload/DropZone'
import { Button } from '../components/common/Button'
import { useUpload } from '../hooks/useUpload'
import { api } from '../api/client.js'
import { UPLOAD_SUCCESS_DELAY } from '../constants/index.js'
import { formatFileSize } from '../utils/index.js'
import styles from './UploadPage.module.css'

export function UploadPage() {
  const navigate = useNavigate()
  const upload = useUpload()
  const { phase, file, progress, error, sessionId } = upload

  useEffect(() => {
    const handler = (e) => { e.preventDefault(); e.returnValue = '' }
    if (phase === 'uploading' || phase === 'preparing') {
      window.addEventListener('beforeunload', handler)
    }
    return () => window.removeEventListener('beforeunload', handler)
  }, [phase])

  useEffect(() => {
    if (phase === 'success') {
      const timer = setTimeout(
        () => navigate(`/sessions/${sessionId}`, { replace: true }),
        UPLOAD_SUCCESS_DELAY,
      )
      return () => clearTimeout(timer)
    }
  }, [phase, sessionId, navigate])

  function handleUpload() {
    if (!file) return
    upload.startUpload((onProgress) => api.uploadRecording(file, onProgress))
  }

  return (
    <PageLayout>
      <div className={styles.splitLayout}>
        {/* Left side: Canvas/Editorial Header */}
        <div className={styles.editorialCanvas}>
          <div className={styles.canvasContent}>
            <h1 className={styles.headline}>
              Upload a<br />
              class recording.
            </h1>
            <p className={styles.subhead}>
              Drop a Forum session recording and we'll transcribe it automatically — notes available to your whole course within minutes.
            </p>
            <div className={styles.metadata}>
              <span>FORUM AI NOTETAKER &copy; {new Date().getFullYear()}</span>
            </div>
          </div>
        </div>

        {/* Right side: The Drop Zone */}
        <div className={styles.uploadZoneContainer}>
          {phase === 'success' ? (
            <div className={styles.successState}>
              <div className={styles.successIconWrapper}>
                <svg viewBox="0 0 24 24" fill="none" className={styles.minimalCheck}>
                  <path d="M4 12L9 17L20 6" stroke="currentColor" strokeWidth="1" strokeLinecap="square" />
                </svg>
              </div>
              <h2 className={styles.successText}>Transcribing...</h2>
              <div className={styles.successProgressLine} />
            </div>
          ) : (
            <div className={styles.dropZoneWrapper}>
              {(phase === 'idle' || phase === 'error') && (
                <DropZone onFile={upload.selectFile} />
              )}

              {(phase === 'file-selected' || phase === 'preparing' || phase === 'uploading') && file && (
                <div className={styles.activeUploadState}>
                  <div className={styles.fileDetails}>
                    <h3 className={styles.fileName}>{file.name}</h3>
                    <span className={styles.fileSize}>{formatFileSize(file.size)}</span>
                  </div>

                  {phase === 'uploading' ? (
                    <div className={styles.uploadingInterface}>
                      <div className={styles.massiveCounter}>
                        {Math.round(progress)}<span className={styles.percentSymbol}>%</span>
                      </div>
                      <div className={styles.progressTrack}>
                        <div className={styles.progressFill} style={{ width: `${progress}%` }} />
                      </div>
                      <Button variant="ghost" onClick={upload.cancel}>Cancel</Button>
                    </div>
                  ) : (
                    <div className={styles.actionBlock}>
                      <div className={styles.readyIndicator}>File recognized. Ready to process.</div>
                      <div className={styles.actionButtons}>
                        <Button variant="ghost" onClick={upload.removeFile}>Discard</Button>
                        <Button variant="primary" onClick={handleUpload}>Process file</Button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {phase === 'error' && error && (
                <div className={styles.errorText}>
                  {error}
                  <Button variant="ghost" onClick={upload.removeFile}>Clear error</Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  )
}
