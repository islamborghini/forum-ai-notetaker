import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useSessions } from './useSessions'
import { MOCK_SESSIONS } from '../fixtures/sessions.js'

describe('useSessions', () => {
  it('starts in loading state', () => {
    const { result } = renderHook(() => useSessions())
    expect(result.current.loading).toBe(true)
    expect(result.current.sessions).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('populates mock sessions after delay', async () => {
    const { result } = renderHook(() => useSessions())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.sessions).toEqual(MOCK_SESSIONS)
    expect(result.current.error).toBeNull()
  })

  it('returns 5 mock sessions', async () => {
    const { result } = renderHook(() => useSessions())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.sessions).toHaveLength(5)
  })
})
