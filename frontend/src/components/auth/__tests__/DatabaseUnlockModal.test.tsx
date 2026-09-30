import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DatabaseUnlockModal from '../DatabaseUnlockModal'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock dependencies
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
  },
}))

vi.mock('@/stores', () => ({
  useSecurityStore: vi.fn(() => ({
    is_locked: true,
    role: 'UNAUTHENTICATED',
    unlock: vi.fn(),
  })),
}))

const mockOnUnlock = vi.fn()

describe('DatabaseUnlockModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockOnUnlock.mockClear()
    localStorage.clear()
  })

  it('renders modal with correct title and description', () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    expect(screen.getByText('Database Terkunci')).toBeInTheDocument()
    expect(screen.getByText('Masukkan PIN Owner atau Developer Recovery Key untuk melanjutkan')).toBeInTheDocument()
  })

  it('renders Owner PIN and Developer Key toggle buttons', () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    expect(screen.getByText('Owner PIN')).toBeInTheDocument()
    expect(screen.getByText('Developer Key')).toBeInTheDocument()
  })

  it('shows Owner PIN mode by default', () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'password')
    expect(input).toHaveAttribute('inputmode', 'numeric')
  })

  it('switches to Developer Key mode when clicked', () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    fireEvent.click(screen.getByText('Developer Key'))

    const input = screen.getByPlaceholderText('Masukkan Developer Recovery Key')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('inputmode', 'text')
  })

  it('shows validation error when passkey is too short', async () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, '123')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('PIN minimal 4 digit')).toBeInTheDocument()
    })
  })

  it('toggles password visibility', async () => {
    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    expect(input).toHaveAttribute('type', 'password')

    const toggleButton = screen.getByLabelText('Tampilkan PIN')
    await userEvent.click(toggleButton)

    expect(input).toHaveAttribute('type', 'text')

    await userEvent.click(toggleButton)
    expect(input).toHaveAttribute('type', 'password')
  })

  it('calls onUnlock on successful API response', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({ data: { success: true, role: 'OWNER', message: 'Unlocked' } })

    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, '123456')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/unlock', {
        passkey: '123456',
        is_developer: false,
      })
      expect(mockOnUnlock).toHaveBeenCalled()
      expect(localStorage.getItem('leuit_passkey')).toBe('123456')
    })
  })

  it('shows error message on failed API response', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({ data: { success: false, message: 'PIN salah' } })

    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, 'wrong')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('PIN salah')).toBeInTheDocument()
    })
    expect(mockOnUnlock).not.toHaveBeenCalled()
  })

  it('shows network error message on API exception', async () => {
    const { api } = await import('@/services/api')
    // Throw an error without response.detail to trigger fallback message
    vi.mocked(api.post).mockRejectedValueOnce(new Error('Network error'))

    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, '123456')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Gagal membuka database. Coba lagi.')).toBeInTheDocument()
    })
  })

  it('disables submit button during submission', async () => {
    const { api } = await import('@/services/api')
    let resolvePromise: (value: any) => void
    const promise = new Promise((resolve) => { resolvePromise = resolve })
    vi.mocked(api.post).mockReturnValueOnce(promise)

    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, '123456')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await act(async () => {
      await userEvent.click(submitButton)
    })

    expect(submitButton).toBeDisabled()
    expect(screen.getByText('Membuka Database...')).toBeInTheDocument()

    resolvePromise!({ data: { success: true } })
    await act(async () => {
      await promise
    })
  })

  it('saves passkey to localStorage on success', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({ data: { success: true, role: 'OWNER', message: 'Unlocked' } })

    render(<DatabaseUnlockModal onUnlock={mockOnUnlock} />)

    const input = screen.getByPlaceholderText('Masukkan 6-digit Owner PIN')
    await userEvent.type(input, 'secret123')

    const submitButton = screen.getByRole('button', { name: /buka database/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(localStorage.getItem('leuit_passkey')).toBe('secret123')
    })
  })
})