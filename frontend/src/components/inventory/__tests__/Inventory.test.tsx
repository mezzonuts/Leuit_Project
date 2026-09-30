import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import Inventory from '../Inventory'
import { useUIStore } from '@/stores'

// Mock dependencies
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val) => `Rp ${val.toLocaleString('id-ID')}`),
  formatNumber: vi.fn((val) => val.toLocaleString('id-ID')),
  getStockRatio: vi.fn((current, min) => min > 0 ? Math.round((current / min) * 100) : 100),
  getStockStatus: vi.fn((ratio) => ratio >= 150 ? 'safe' : ratio >= 100 ? 'warning' : 'danger'),
  getStockStatusColor: vi.fn((status) => status === 'safe' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-danger-600'),
  getStockProgressColor: vi.fn((ratio) => ratio >= 100 ? 'bg-green-500' : ratio >= 50 ? 'bg-yellow-500' : 'bg-danger-500'),
  daysUntilExpiry: vi.fn(() => 30),
}))

vi.mock('@/utils/exportCsv', () => ({
  downloadValuationCSV: vi.fn(),
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({
    openDrawer: vi.fn(),
    closeDrawer: vi.fn(),
    activeDrawer: null,
  })),
}))

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [], total: 0, page: 1, page_size: 100, total_pages: 1 } }),
    delete: vi.fn().mockResolvedValue({}),
  },
}))

const mockIngredients = [
  {
    id: 1,
    name: 'Susu Segar',
    barcode_sku: '8991234567890',
    unit: 'ml',
    current_stock: 100,
    min_stock_threshold: 20,
    cost_per_unit: 8000,
    shelf_life_days: 7,
    is_active: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    name: 'Gula Pasir',
    barcode_sku: '8991234567891',
    unit: 'gram',
    current_stock: 5,
    min_stock_threshold: 50,
    cost_per_unit: 12000,
    shelf_life_days: 365,
    is_active: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 3,
    name: 'Tepung Terigu',
    barcode_sku: '',
    unit: 'gram',
    current_stock: 1000,
    min_stock_threshold: 100,
    cost_per_unit: 8000,
    shelf_life_days: 180,
    is_active: false,
    created_at: new Date().toISOString(),
  },
]

const renderInventory = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Inventory />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Inventory', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('renders page title and description', () => {
    renderInventory()

    expect(screen.getByText('Kelola Stok')).toBeInTheDocument()
    expect(screen.getByText('Master bahan baku, barcode scanner, stock opname & threshold')).toBeInTheDocument()
  })

  it('renders action buttons: Export CSV, Tambah Bahan', () => {
    renderInventory()

    expect(screen.getByRole('button', { name: /ekspor csv/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^tambah bahan$/i })).toBeInTheDocument()
  })

  it('renders search input with placeholder', () => {
    renderInventory()

    expect(screen.getByPlaceholderText('Cari nama bahan atau barcode...')).toBeInTheDocument()
  })

  it('renders show inactive checkbox', () => {
    renderInventory()

    expect(screen.getByText('Tampilkan yang diarsipkan')).toBeInTheDocument()
    expect(screen.getByRole('checkbox')).toBeInTheDocument()
  })

  it('renders table with correct headers', () => {
    renderInventory()

    expect(screen.getByText('Bahan')).toBeInTheDocument()
    expect(screen.getByText('Barcode/SKU')).toBeInTheDocument()
    expect(screen.getByText('Stok')).toBeInTheDocument()
    expect(screen.getByText('Progress')).toBeInTheDocument()
    expect(screen.getByText('HPP')).toBeInTheDocument()
    expect(screen.getByText('Kadaluwarsa')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
    expect(screen.getByText('Aksi')).toBeInTheDocument()
  })

  it('shows empty state when no ingredients', () => {
    renderInventory()

    expect(screen.getByText('Belum ada data bahan baku')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /tambah bahan pertama/i })).toBeInTheDocument()
  })

  it('renders ingredient rows when data exists', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      expect(screen.getByText('Susu Segar')).toBeInTheDocument()
      expect(screen.getByText('Gula Pasir')).toBeInTheDocument()
      expect(screen.getByText('Tepung Terigu')).toBeInTheDocument()
    })
  })

  it('renders barcode with code styling when present', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      expect(screen.getByText('8991234567890')).toBeInTheDocument()
      expect(screen.getByText('8991234567891')).toBeInTheDocument()
    })
  })

  it('shows "-" for empty barcode', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      expect(screen.getByText('-')).toBeInTheDocument()
    })
  })

  it('renders stock with unit and min threshold', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      expect(screen.getByText('100 ml')).toBeInTheDocument()
      expect(screen.getByText('Min: 20')).toBeInTheDocument()
    })
  })

  it('renders progress bar with correct percentage', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      expect(screen.getByText('500%')).toBeInTheDocument() // 100/20 * 100
    })
  })

  it('renders HPP with Rupiah format', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      const hppElements = screen.getAllByText(/Rp\s*8\.000/)
      expect(hppElements.length).toBeGreaterThanOrEqual(1)
    })
  })

  it('shows expiry badge for expiring soon items', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      const expiryTexts = screen.getAllByText(/30 hari/)
      expect(expiryTexts.length).toBeGreaterThanOrEqual(1)
    })
  })

  it('shows active/archived status badge', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      const activeBadges = screen.getAllByText('Aktif')
      const archivedBadges = screen.getAllByText('Diarsipkan')
      expect(activeBadges.length).toBe(2)
      expect(archivedBadges.length).toBe(1)
    })
  })

  it('renders action buttons for each row', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      // Check action icons exist (one per row = 3 rows)
      const opnameButtons = screen.getAllByTitle('Stock Opname')
      const scanButtons = screen.getAllByTitle('Scan Barcode')
      const editButtons = screen.getAllByTitle('Edit')
      const deleteButtons = screen.getAllByTitle('Arsipkan')

      expect(opnameButtons.length).toBe(3)
      expect(scanButtons.length).toBe(3)
      expect(editButtons.length).toBe(3)
      expect(deleteButtons.length).toBe(3)
    })
  })

  it('filters by search term', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Cari nama bahan atau barcode...')
      fireEvent.change(searchInput, { target: { value: 'Susu' } })
      expect(searchInput).toHaveValue('Susu')
    })
  })

  it('toggles show inactive filter', async () => {
    const { api } = await import('@/services/api')
    vi.mocked(api.get).mockResolvedValueOnce({ data: { items: mockIngredients, total: 3, page: 1, page_size: 100, total_pages: 1 } })

    renderInventory()

    await waitFor(() => {
      const checkbox = screen.getByRole('checkbox')
      fireEvent.click(checkbox)
      expect(checkbox).toBeChecked()
    })
  })
})