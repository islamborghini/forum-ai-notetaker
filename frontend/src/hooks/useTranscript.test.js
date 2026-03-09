import { describe, it, expect } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useTranscript } from './useTranscript'

describe('useTranscript', () => {
  it('starts in loading state', () => {
    const { result } = renderHook(() => useTranscript('1'))
    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('populates data for a known session id', async () => {
    const { result } = renderHook(() => useTranscript('1'))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.id).toBe('1')
    expect(result.current.data.status).toBe('transcribed')
    expect(result.current.error).toBeNull()
  })

  it('sets error for unknown session id', async () => {
    const { result } = renderHook(() => useTranscript('999'))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('Session not found')
    expect(result.current.data).toBeNull()
  })

  it('returns processing status for session 3', async () => {
    const { result } = renderHook(() => useTranscript('3'))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data.status).toBe('processing')
  })

  it('exposes refetch to reload data', async () => {
    const { result } = renderHook(() => useTranscript('1'))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).not.toBeNull()
    await act(async () => { result.current.refetch() })
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data.id).toBe('1')
  })
})
