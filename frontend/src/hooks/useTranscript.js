import { useState, useEffect, useCallback, useRef } from 'react'
import { MOCK_TRANSCRIPTS } from '../fixtures/transcripts.js'

export function useTranscript(sessionId) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const initialFetch = useRef(true)

  const fetchData = useCallback(() => {
    // Only show loading spinner on the initial fetch, not on background polls
    if (initialFetch.current) {
      setLoading(true)
    }
    setError(null)

    const t = setTimeout(() => {
      const mock = MOCK_TRANSCRIPTS[sessionId]
      if (mock) {
        setData(mock)
      } else {
        setError('Session not found')
      }
      setLoading(false)
      initialFetch.current = false
    }, 500)

    return () => clearTimeout(t)
  }, [sessionId])

  useEffect(() => {
    initialFetch.current = true
    return fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}
