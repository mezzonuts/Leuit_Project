import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import PurchaseEntryDrawer from '../PurchaseEntryDrawer'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { post: vi.fn() },
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({
    drawerData: { mode: 'create', suppliers: [], ingredients: [] },
  })),
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
}))

const renderDrawer = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <PurchaseEntryDrawer onClose={vi.fn()} />
    </QueryClientProvider>
  )
}

describe('PurchaseEntryDrawer', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders title', () => {
    renderDrawer()
    expect(screen.getByText('Catat Pembelian Baru')).toBeInTheDocument()
  })

  it('renders close button', () => {
    renderDrawer()
    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('renders form fields', () => {
    renderDrawer()
    expect(screen.getByText('Tanggal Pembelian *')).toBeInTheDocument()
    expect(screen.getByText('Bahan Baku *')).toBeInTheDocument()
    expect(screen.getByText('Suplier *')).toBeInTheDocument()
    expect(screen.getByText('Jumlah *')).toBeInTheDocument()
    expect(screen.getByText('Total Biaya (Rp) *')).toBeInTheDocument()
    expect(screen.getByText('Metode Pembayaran *')).toBeInTheDocument()
  })

  it('renders payment method options', () => {
    renderDrawer()
    expect(screen.getByText('Cash (Tunai)')).toBeInTheDocument()
    expect(screen.getByText('Kredit / Tempo')).toBeInTheDocument()
  })

  it('renders action buttons', () => {
    renderDrawer()
    expect(screen.getByText('Batal')).toBeInTheDocument()
    expect(screen.getByText(/Simpan Pembelian/i)).toBeInTheDocument()
  })

  it('shows cash info message', () => {
    renderDrawer()
    expect(screen.getByText(/Pembayaran Cash/i)).toBeInTheDocument()
  })

  it('does not show due date fields initially', () => {
    renderDrawer()
    expect(screen.queryByText('Jatuh Tempo *')).not.toBeInTheDocument()
  })

  it('does not show payment status initially', () => {
    renderDrawer()
    expect(screen.queryByText('Status Pembayaran')).not.toBeInTheDocument()
  })
})
