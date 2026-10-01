import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Sync from '../Sync'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { items: [] } }),
    post: vi.fn(),
  },
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({
    openDrawer: vi.fn(),
    closeDrawer: vi.fn(),
    activeDrawer: null,
  })),
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatDate: vi.fn((date: string) => date),
  formatDateTime: vi.fn((date: string) => date),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
}))

const renderSync = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <Sync />
    </QueryClientProvider>
  )
}

describe('Sync', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders page title', () => {
    renderSync()
    expect(screen.getByText('Sinkronisasi POS')).toBeInTheDocument()
  })

  it('renders subtitle', () => {
    renderSync()
    expect(screen.getByText(/Upload CSV kasir berkala/i)).toBeInTheDocument()
  })

  it('renders Upload CSV Baru button', () => {
    renderSync()
    expect(screen.getByText(/Upload CSV Baru/i)).toBeInTheDocument()
  })

  it('renders upload zone with drag-drop text', () => {
    renderSync()
    expect(screen.getByText('Seret & Lepas File CSV Kasir')).toBeInTheDocument()
  })

  it('renders upload zone aria-label', () => {
    renderSync()
    expect(screen.getByLabelText('Area upload CSV kasir')).toBeInTheDocument()
  })

  it('renders supported formats', () => {
    renderSync()
    expect(screen.getByText(/Moka POS/i)).toBeInTheDocument()
  })

  it('renders history section', () => {
    renderSync()
    expect(screen.getByText('Riwayat Sinkronisasi')).toBeInTheDocument()
  })

  it('renders empty history state', () => {
    renderSync()
    expect(screen.getByText('Belum ada riwayat sinkronisasi')).toBeInTheDocument()
  })

  it('renders column format hints', () => {
    renderSync()
    expect(screen.getByText('Order_ID')).toBeInTheDocument()
    expect(screen.getByText('Timestamp')).toBeInTheDocument()
    expect(screen.getByText('Item_Name')).toBeInTheDocument()
  })
})
