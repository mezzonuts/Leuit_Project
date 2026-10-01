import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import userEvent from '@testing-library/user-event'
import IngredientDrawer from '../IngredientDrawer'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'

// Mock dependencies
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
    put: vi.fn(),
  },
}))

// Create a mutable mock store
const mockStore = {
  drawerData: null,
}

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => mockStore),
}))

const mockIngredient = {
  id: 1,
  barcode_sku: '8991234567890',
  name: 'Susu Segar',
  unit: 'ml',
  cost_per_unit: 8000,
  shelf_life_days: 7,
  current_stock: 100,
  min_stock_threshold: 20,
  lead_time_days: 1,
  is_active: true,
}

const renderDrawer = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <IngredientDrawer onClose={vi.fn()} />
    </QueryClientProvider>
  )
}

describe('IngredientDrawer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockStore.drawerData = null
  })

  afterEach(() => {
    vi.resetModules()
  })

  const setDrawerData = (drawerData: any) => {
    mockStore.drawerData = drawerData
  }

  it('renders "Tambah Bahan Baru" title in create mode', () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    expect(screen.getByText('Tambah Bahan Baru')).toBeInTheDocument()
  })

  it('renders "Edit Bahan" title in edit mode', () => {
    setDrawerData({ mode: 'edit', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.getByText('Edit Bahan')).toBeInTheDocument()
  })

  it('renders "Stock Opname" title in opname mode', () => {
    setDrawerData({ mode: 'opname', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.getByText('Stock Opname')).toBeInTheDocument()
  })

  it('renders close button with X icon', () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('renders all form fields in create/edit mode', () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    expect(screen.getByPlaceholderText('Contoh: Susu Segar Lembang 1L')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Scan atau ketik manual')).toBeInTheDocument()
    expect(screen.getByRole('combobox')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contoh: 12000')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contoh: 7')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contoh: 1')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contoh: 50')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contoh: 10')).toBeInTheDocument()
  })

  it('hides stock and threshold fields in opname mode', () => {
    setDrawerData({ mode: 'opname', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.queryByPlaceholderText('Contoh: 50')).not.toBeInTheDocument()
    expect(screen.queryByPlaceholderText('Contoh: 10')).not.toBeInTheDocument()
    expect(screen.getByPlaceholderText('Masukkan jumlah stok fisik yang dihitung')).toBeInTheDocument()
  })

  it('populates form with ingredient data in edit mode', () => {
    setDrawerData({ mode: 'edit', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.getByPlaceholderText('Contoh: Susu Segar Lembang 1L')).toHaveValue('Susu Segar')
    expect(screen.getByPlaceholderText('Scan atau ketik manual')).toHaveValue('8991234567890')
    expect(screen.getByRole('combobox')).toHaveValue('ml')
    expect(screen.getByPlaceholderText('Contoh: 12000')).toHaveValue(8000)
    expect(screen.getByPlaceholderText('Contoh: 7')).toHaveValue(7)
    expect(screen.getByPlaceholderText('Contoh: 50')).toHaveValue(100)
    expect(screen.getByPlaceholderText('Contoh: 10')).toHaveValue(20)
  })

  it('sets stock to 0 in opname mode', () => {
    setDrawerData({ mode: 'opname', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.getByPlaceholderText('Masukkan jumlah stok fisik yang dihitung')).toHaveValue(0)
  })

  it('shows validation error for empty name', async () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Nama bahan wajib diisi')).toBeInTheDocument()
    })
  })

  it('shows validation error for negative cost', async () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const costInput = screen.getByPlaceholderText('Contoh: 12000')
    await userEvent.clear(costInput)
    fireEvent.change(costInput, { target: { value: '-10' } })

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/HPP harus/)).toBeInTheDocument()
    })
  })

  it('shows validation error for shelf_life_days < 1', async () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const shelfLifeInput = screen.getByPlaceholderText('Contoh: 7')
    await userEvent.clear(shelfLifeInput)
    fireEvent.change(shelfLifeInput, { target: { value: '0' } })

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/Masa simpan minimal/)).toBeInTheDocument()
    })
  })

  it('shows validation error for negative stock', async () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const stockInput = screen.getByPlaceholderText('Contoh: 50')
    await userEvent.clear(stockInput)
    fireEvent.change(stockInput, { target: { value: '-10' } })

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Stok tidak boleh negatif')).toBeInTheDocument()
    })
  })

  it('shows validation error for negative threshold', async () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const thresholdInput = screen.getByPlaceholderText('Contoh: 10')
    await userEvent.clear(thresholdInput)
    fireEvent.change(thresholdInput, { target: { value: '-5' } })

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Threshold tidak boleh negatif')).toBeInTheDocument()
    })
  })

  it('calls POST /inventory on create submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({})

    
    setDrawerData({ mode: 'create' })
    renderDrawer()

    await userEvent.type(screen.getByPlaceholderText('Contoh: Susu Segar Lembang 1L'), 'Test Bahan')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 12000'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 12000'), '10000')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 7'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 7'), '30')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 50'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 50'), '50')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 10'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 10'), '10')

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/inventory', expect.objectContaining({
        name: 'Test Bahan',
        cost_per_unit: 10000,
        shelf_life_days: 30,
        current_stock: 50,
        min_stock_threshold: 10,
        unit: 'gram',
        barcode_sku: '',
        lead_time_days: 1,
      }))
    })
  })

  it('calls PUT /inventory/:id on edit submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.put).mockResolvedValueOnce({})

    
    setDrawerData({ mode: 'edit', ingredient: mockIngredient })
    renderDrawer()

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/inventory/1', expect.any(Object))
    })
  })

  it('calls POST /inventory/:id/stock-opname on opname submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({})

    
    setDrawerData({ mode: 'opname', ingredient: mockIngredient })
    renderDrawer()

    const stockInput = screen.getByPlaceholderText('Masukkan jumlah stok fisik yang dihitung')
    await userEvent.clear(stockInput)
    await userEvent.type(stockInput, '150')

    const submitButton = screen.getByRole('button', { name: /simpan penyesuaian/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/inventory/1/stock-opname', { quantity: 150 })
    })
  })

  it('calls onClose on successful submit', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.post).mockResolvedValueOnce({})

    
    

    setDrawerData({ mode: 'create' })

    const onClose = vi.fn()
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <IngredientDrawer onClose={onClose} />
      </QueryClientProvider>
    )

    await userEvent.type(screen.getByPlaceholderText('Contoh: Susu Segar Lembang 1L'), 'Test')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 12000'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 12000'), '10000')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 7'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 7'), '30')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 50'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 50'), '50')
    await userEvent.clear(screen.getByPlaceholderText('Contoh: 10'))
    await userEvent.type(screen.getByPlaceholderText('Contoh: 10'), '10')

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })

  it('disables submit button during submission', async () => {
    const { api } = await import('@/services/api')
    let resolvePromise: (value: any) => void
    const promise = new Promise((resolve) => { resolvePromise = resolve })
    vi.mocked(api.post).mockReturnValueOnce(promise)

    
    setDrawerData({ mode: 'create' })
    renderDrawer()

    await userEvent.type(screen.getByPlaceholderText('Contoh: Susu Segar Lembang 1L'), 'Test')
    await userEvent.type(screen.getByPlaceholderText('Contoh: 12000'), '10000')
    await userEvent.type(screen.getByPlaceholderText('Contoh: 7'), '30')
    await userEvent.type(screen.getByPlaceholderText('Contoh: 50'), '50')
    await userEvent.type(screen.getByPlaceholderText('Contoh: 10'), '10')

    const submitButton = screen.getByRole('button', { name: /simpan/i })
    await act(async () => {
      await userEvent.click(submitButton)
    })

    expect(submitButton).toBeDisabled()
    expect(screen.getByRole('status')).toBeInTheDocument() // Loader/spinner

    resolvePromise!({})
    await act(async () => { await promise })
  })

  it('shows camera button next to barcode input', () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const cameraButton = screen.getByRole('button', { name: /scan barcode/i })
    expect(cameraButton).toBeInTheDocument()
  })

  it('shows opname help text in opname mode', () => {
    setDrawerData({ mode: 'opname', ingredient: mockIngredient })
    renderDrawer()

    expect(screen.getByText('Sistem akan menghitung selisih otomatis dari stok sistem.')).toBeInTheDocument()
  })

  it('closes drawer when Batal clicked', () => {
    
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const cancelButton = screen.getByRole('button', { name: /batal/i })
    fireEvent.click(cancelButton)
  })

  it('closes drawer when X button clicked', () => {
    setDrawerData({ mode: 'create' })
    renderDrawer()

    const closeButton = screen.getByLabelText('Tutup')
    fireEvent.click(closeButton)
  })
})