import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('renders transcribed status', () => {
    render(<StatusBadge status="transcribed" />)
    expect(screen.getByText(/transcribed/i)).toBeInTheDocument()
  })

  it('renders processing status', () => {
    render(<StatusBadge status="processing" />)
    expect(screen.getByText(/processing/i)).toBeInTheDocument()
  })

  it('renders error status', () => {
    render(<StatusBadge status="error" />)
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
