import { useState, useEffect } from 'react'
import { MOCK_SESSIONS } from '../fixtures/sessions.js'

export function useSessions() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => {
      setSessions(MOCK_SESSIONS)
      setLoading(false)
    }, 600)
    return () => clearTimeout(t)
  }, [])

  return { sessions, loading, error: null }
}
