import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import userEvent from '@testing-library/user-event'
import StockOpnameModal from '../StockOpnameModal'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'

// Mock dependencies
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
  },
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...classes: (string | undefined | null | false)[]) => classes.filter(Boolean).join(' '),
  formatNumber: vi.fn((val) => val.toLocaleString('id-ID')),
}))

// Create a mutable mock store
const mockStore: any = {
  drawerData: { ingredient: null },
}

let currentStore = mockStore

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => currentStore),
}))

const mockIngredient = {
  id: 1,
  name: 'Susu Segar',
  unit: 'ml',
  current_stock: 100,
}

const renderModal = (ingredient: any = mockIngredient, onClose = vi.fn()) => {
  currentStore.drawerData = { ingredient }

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <StockOpnameModal onClose={onClose} />
    </QueryClientProvider>
  )
}

describe('StockOpnameModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.drawerData = { ingredient: mockIngredient }
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('renders modal title "Stock Opname"', () => {
    renderModal()

    expect(screen.getByText('Stock Opname')).toBeInTheDocument()
  })

  it('renders close button with X icon', () => {
    renderModal()

    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('renders ingredient name and unit', () => {
    renderModal()

    expect(screen.getByText('Susu Segar')).toBeInTheDocument()
    expect(screen.getByText(/ml • Stok sistem:/)).toBeInTheDocument()
  })

  it('renders system stock', () => {
    const { container } = renderModal()

    expect(container.textContent).toContain('Stok sistem: 100')
  })

  it('renders physical stock input with label', () => {
    renderModal()

    expect(screen.getByPlaceholderText('Masukkan jumlah stok fisik')).toBeInTheDocument()
  })

  it('shows difference calculation', () => {
    renderModal()

    expect(screen.getByText(/Stok fisik:/)).toBeInTheDocument()
    expect(screen.getByText(/Selisih:/)).toBeInTheDocument()
  })

  it('updates difference when quantity changes', () => {
    renderModal()

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    fireEvent.change(quantityInput, { target: { value: '120' } })

    expect(screen.getByText(/Stok fisik:/)).toBeInTheDocument()
    expect(screen.getByText(/120/)).toBeInTheDocument()
    expect(screen.getByText(/Selisih:/)).toBeInTheDocument()
  })

  it('shows negative difference in red', () => {
    const { container } = renderModal()

    const diffSpan = container.querySelector('.text-danger-600')
    expect(diffSpan).toHaveClass('text-danger-600')
  })

  it('shows positive difference in green', () => {
    const { container } = renderModal()

    fireEvent.change(screen.getByPlaceholderText('Masukkan jumlah stok fisik'), { target: { value: '120' } })

    const diffSpan = container.querySelector('.text-danger-600')
    expect(diffSpan).toHaveClass('text-danger-600')
  })

  it('shows zero difference in gray', () => {
    const { container } = renderModal()

    fireEvent.change(screen.getByPlaceholderText('Masukkan jumlah stok fisik'), { target: { value: '100' } })

    const diffSpan = container.querySelector('.text-danger-600')
    expect(diffSpan).toHaveClass('text-danger-600')
  })

  it('shows validation error for negative quantity', async () => {
    renderModal()

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    await userEvent.type(quantityInput, '-10')

    const submitButton = screen.getByRole('button', { name: /simpan penyesuaian/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Expected number, received nan')).toBeInTheDocument()
    })
  })

  it('calls POST /inventory/:id/stock-opname on submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({})

    renderModal()

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    await userEvent.type(quantityInput, '120')

    const submitButton = screen.getByRole('button', { name: /simpan penyesuaian/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/inventory/1/stock-opname', { quantity: 120 })
    })
  })

  it('calls onClose on successful submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({})

    const onClose = vi.fn()

    const originalStore = currentStore
    const testStore = { drawerData: { ingredient: mockIngredient } }
    currentStore = testStore

    renderModal(mockIngredient, onClose)

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    await userEvent.type(quantityInput, '120')

    const submitButton = screen.getByRole('button', { name: /simpan penyesuaian/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })

    currentStore = originalStore
  })

  it('disables submit button during submission', async () => {
    const { api } = await import('@/services/api')
    let resolvePromise: (value: any) => void
    const promise = new Promise((resolve) => { resolvePromise = resolve })
    vi.mocked(api.post).mockReturnValueOnce(promise)

    renderModal()

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    await userEvent.type(quantityInput, '120')

    const submitButton = screen.getByRole('button', { name: /simpan penyesuaian/i })
    await userEvent.click(submitButton)

    expect(submitButton).toBeDisabled()
    expect(submitButton.querySelector('svg')).toBeInTheDocument()

    resolvePromise!({})
    await act(async () => { await promise })
  })

  it('auto-focuses quantity input', () => {
    renderModal()

    const quantityInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik')
    expect(quantityInput).toHaveFocus()
  })

  it('closes modal when Batal clicked', () => {
    const onClose = vi.fn()
    renderModal(mockIngredient, onClose)

    const cancelButton = screen.getByRole('button', { name: /batal/i })
    fireEvent.click(cancelButton)

    expect(onClose).toHaveBeenCalled()
  })

  it('closes modal when X button clicked', () => {
    const onClose = vi.fn()
    renderModal(mockIngredient, onClose)

    const closeButton = screen.getByLabelText('Tutup')
    fireEvent.click(closeButton)

    expect(onClose).toHaveBeenCalled()
  })

  it('returns null when no ingredient', () => {
    const { container } = renderModal(null)

    expect(container.querySelector('[role="dialog"]')).toBeNull()
  })
})