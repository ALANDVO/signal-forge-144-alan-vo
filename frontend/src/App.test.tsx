import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('shows loading state initially', () => {

    render(<App />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays health data when fetch succeeds', async () => {
    ;(global.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy', service: 'signal-forge' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy', database: 'connected' }),
      })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('API Healthy')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('API Healthy')).toBeInTheDocument()
    })

    expect(screen.getByText('Signal Forge')).toBeInTheDocument()
  })

  it('displays error when fetch fails', async () => {
    ;(global.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'))

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument()
    })

    expect(screen.getByText(/Network error/)).toBeInTheDocument()
  })
})