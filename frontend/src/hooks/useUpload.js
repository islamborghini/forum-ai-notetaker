import { useReducer, useCallback, useRef } from 'react'
import {
  MAX_FILE_SIZE_BYTES,
  ACCEPTED_MIME_TYPES,
} from '../constants/index.js'

const initialState = {
  phase: 'idle',
  file: null,
  progress: 0,
  sessionId: null,
  error: null,
}

function uploadReducer(state, action) {
  switch (action.type) {
    case 'FILE_SELECTED':
      return { ...initialState, phase: 'file-selected', file: action.file }
    case 'FILE_INVALID':
      return { ...initialState, phase: 'error', error: action.error }
    case 'RESET':
      // FILE_REMOVED and CANCEL both collapse to initial state; abort is handled by cancel()
      return { ...initialState }
    case 'UPLOAD_START':
      return { ...state, phase: 'preparing', error: null }
    case 'UPLOAD_PROGRESS':
      return { ...state, phase: 'uploading', progress: action.progress }
    case 'SUCCESS':
      return { ...state, phase: 'success', sessionId: action.sessionId }
    case 'ERROR':
      return { ...state, phase: 'error', error: action.error }
    case 'RETRY':
      return { ...state, phase: 'file-selected', error: null, progress: 0 }
    default:
      return state
  }
}

export function useUpload() {
  const [state, dispatch] = useReducer(uploadReducer, initialState)
  const activeUploadRef = useRef(null)

  const selectFile = useCallback((file) => {
    if (!ACCEPTED_MIME_TYPES.includes(file.type)) {
      dispatch({ type: 'FILE_INVALID', error: 'Unsupported format. Use .mp4, .webm, or .mov.' })
      return
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const sizeMB = Math.round(file.size / 1024 / 1024)
      dispatch({ type: 'FILE_INVALID', error: `File is ${sizeMB} MB — the limit is 500 MB.` })
      return
    }
    dispatch({ type: 'FILE_SELECTED', file })
  }, [])

  const removeFile = useCallback(() => dispatch({ type: 'RESET' }), [])

  const cancel = useCallback(() => {
    activeUploadRef.current?.abort()
    activeUploadRef.current = null
    dispatch({ type: 'RESET' })
  }, [])

  const retry = useCallback(() => dispatch({ type: 'RETRY' }), [])

  const startUpload = useCallback(async (uploadFn) => {
    dispatch({ type: 'UPLOAD_START' })
    try {
      const uploadPromise = uploadFn((pct) => {
        dispatch({ type: 'UPLOAD_PROGRESS', progress: pct })
      })
      activeUploadRef.current = uploadPromise
      const result = await uploadPromise
      activeUploadRef.current = null
      dispatch({ type: 'SUCCESS', sessionId: result.id })
    } catch (err) {
      activeUploadRef.current = null
      if (err.message !== 'Upload cancelled') {
        dispatch({ type: 'ERROR', error: err.message })
      }
    }
  }, [])

  return { ...state, selectFile, removeFile, cancel, retry, startUpload }
}
