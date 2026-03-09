import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useUpload } from './useUpload'

const validFile = new File(['content'], 'lecture.mp4', { type: 'video/mp4' })
const invalidTypeFile = new File(['content'], 'notes.pdf', { type: 'application/pdf' })
const oversizedFile = new File(['x'.repeat(100)], 'big.mp4', { type: 'video/mp4' })
Object.defineProperty(oversizedFile, 'size', { value: 600 * 1024 * 1024 })

describe('useUpload initial state', () => {
  it('starts in idle phase', () => {
    const { result } = renderHook(() => useUpload())
    expect(result.current.phase).toBe('idle')
    expect(result.current.file).toBeNull()
    expect(result.current.progress).toBe(0)
    expect(result.current.error).toBeNull()
    expect(result.current.sessionId).toBeNull()
  })
})

describe('useUpload file selection', () => {
  it('transitions to file-selected on valid file', () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(validFile))
    expect(result.current.phase).toBe('file-selected')
    expect(result.current.file).toBe(validFile)
    expect(result.current.error).toBeNull()
  })

  it('transitions to error on invalid mime type', () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(invalidTypeFile))
    expect(result.current.phase).toBe('error')
    expect(result.current.error).toMatch(/unsupported/i)
  })

  it('transitions to error on oversized file', () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(oversizedFile))
    expect(result.current.phase).toBe('error')
    expect(result.current.error).toMatch(/500 MB/i)
  })
})

describe('useUpload file removal', () => {
  it('returns to idle on removeFile', () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(validFile))
    act(() => result.current.removeFile())
    expect(result.current.phase).toBe('idle')
    expect(result.current.file).toBeNull()
  })
})

describe('useUpload retry', () => {
  it('returns to file-selected from error, retaining file', async () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(validFile))

    // Trigger an error via a failing startUpload
    await act(async () => {
      await result.current.startUpload(() => Promise.reject(new Error('Network error')))
    })

    expect(result.current.phase).toBe('error')
    expect(result.current.error).toBe('Network error')

    act(() => result.current.retry())
    expect(result.current.phase).toBe('file-selected')
    expect(result.current.file).toBe(validFile)
    expect(result.current.error).toBeNull()
  })
})

describe('useUpload progress', () => {
  it('transitions through preparing → uploading → success', async () => {
    const { result } = renderHook(() => useUpload())
    act(() => result.current.selectFile(validFile))

    let capturedOnProgress
    const resolveRef = { current: null }

    const uploadFn = (onProgress) => {
      capturedOnProgress = onProgress
      return new Promise((resolve) => { resolveRef.current = resolve })
    }

    // Kick off upload without awaiting
    const startPromise = result.current.startUpload(uploadFn)

    // Let microtasks settle — phase should be 'preparing'
    await act(async () => {})
    expect(result.current.phase).toBe('preparing')

    // Fire a progress update
    act(() => capturedOnProgress(42))
    expect(result.current.phase).toBe('uploading')
    expect(result.current.progress).toBe(42)

    // Resolve the upload
    await act(async () => {
      resolveRef.current({ id: 'sess-1' })
      await startPromise
    })
    expect(result.current.phase).toBe('success')
    expect(result.current.sessionId).toBe('sess-1')
  })
})
