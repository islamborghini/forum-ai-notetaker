import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.stubEnv('VITE_API_URL', 'http://localhost:5000')

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

const { api } = await import('./client.js')

describe('api.getSessions', () => {
  beforeEach(() => mockFetch.mockClear())

  it('calls GET /sessions', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ([{ id: '1', filename: 'test.mp4' }]),
    })
    const result = await api.getSessions()
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:5000/sessions',
      expect.objectContaining({})
    )
    expect(result).toEqual([{ id: '1', filename: 'test.mp4' }])
  })

  it('throws with server message on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: 'Server error' }),
    })
    await expect(api.getSessions()).rejects.toThrow('Server error')
  })

  it('throws generic message when no body message', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({}),
    })
    await expect(api.getSessions()).rejects.toThrow('Request failed: HTTP 404')
  })
})

describe('api.getTranscript', () => {
  beforeEach(() => mockFetch.mockClear())

  it('calls GET /sessions/:id/transcript', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ transcript: [] }),
    })
    await api.getTranscript('abc123')
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:5000/sessions/abc123/transcript',
      expect.objectContaining({})
    )
  })
})
