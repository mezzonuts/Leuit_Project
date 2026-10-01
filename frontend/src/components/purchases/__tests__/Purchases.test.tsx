import { render, screen, fireEvent, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Purchases from '../Purchases'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn((url: string) =>
      Promise.resolve({ data: url.includes('payables') ? [] : { items: [] } })
    ),
    post: vi.fn(),
  },
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({ openDrawer: vi.fn(), closeDrawer: vi.fn(), activeDrawer: null })),
}))

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
  formatDate: vi.fn((date: string) => date),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
}))

const renderPurchases = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <Purchases />
    </QueryClientProvider>
  )
}

describe('Purchases', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders page title', () => {
    renderPurchases()
    expect(screen.getByText('Pembelian Stok')).toBeInTheDocument()
  })

  it('renders subtitle', () => {
    renderPurchases()
    expect(screen.getByText('Catat belanja Cash vs Kredit/Tempo + Hutang Suplier')).toBeInTheDocument()
  })

  it('renders tab buttons', () => {
    renderPurchases()
    const nav = screen.getByRole('navigation', { name: 'Tab navigasi' })
    expect(within(nav).getByText(/Daftar Pembelian/i)).toBeInTheDocument()
    expect(within(nav).getByText(/Rekomendasi Restock/i)).toBeInTheDocument()
    expect(within(nav).getByText(/Hutang Suplier/i)).toBeInTheDocument()
  })

  it('shows empty state when no purchases', () => {
    renderPurchases()
    expect(screen.getByText('Belum ada catatan pembelian.')).toBeInTheDocument()
  })

  it('switches to restock tab', () => {
    renderPurchases()
    fireEvent.click(screen.getByText(/Rekomendasi Restock/i))
    expect(screen.getByText('Belum ada rekomendasi restock.')).toBeInTheDocument()
  })

  it('switches to payables tab', () => {
    renderPurchases()
    const nav = screen.getByRole('navigation', { name: 'Tab navigasi' })
    fireEvent.click(within(nav).getByText(/Hutang Suplier/i))
    expect(screen.getByText('Tidak Ada Hutang')).toBeInTheDocument()
  })

  it('renders Catat Pembelian button', () => {
    renderPurchases()
    expect(screen.getByText(/Catat Pembelian/i)).toBeInTheDocument()
  })
})
