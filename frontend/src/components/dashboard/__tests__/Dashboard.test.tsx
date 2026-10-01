import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
  },
}))

vi.mock('@/utils/exportCsv', () => ({
  downloadValuationCSV: vi.fn(),
}))

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
  formatDate: vi.fn((date: string) => date),
  getStockRatio: vi.fn((current: number, min: number) => min > 0 ? Math.round((current / min) * 100) : 100),
  getStockStatus: vi.fn((ratio: number) => ratio >= 150 ? 'safe' : ratio >= 100 ? 'warning' : 'danger'),
  getStockStatusColor: vi.fn((status: string) => status === 'safe' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-danger-600'),
  getStockProgressColor: vi.fn((ratio: number) => ratio >= 100 ? 'bg-green-500' : ratio >= 50 ? 'bg-yellow-500' : 'bg-danger-500'),
  daysUntilExpiry: vi.fn(() => 30),
}))

const renderDashboard = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders page title', () => {
    renderDashboard()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders subtitle', () => {
    renderDashboard()
    expect(screen.getByText('Pusat pantau stok, valuasi aset & peringatan kritis')).toBeInTheDocument()
  })

  it('renders export button', () => {
    renderDashboard()
    expect(screen.getByRole('button', { name: /ekspor valuasi csv/i })).toBeInTheDocument()
  })

  it('renders metric cards section', () => {
    renderDashboard()
    expect(screen.getByText('Total Valuasi Aset')).toBeInTheDocument()
    expect(screen.getByText('Stok Rendah')).toBeInTheDocument()
    expect(screen.getByText('Segera Kadaluwarsa')).toBeInTheDocument()
  })

  it('renders chart section', () => {
    renderDashboard()
    expect(screen.getByText('Tren Konsumsi 30 Hari')).toBeInTheDocument()
  })

  it('renders alerts section', () => {
    renderDashboard()
    expect(screen.getByText('Peringatan Kritis')).toBeInTheDocument()
  })

  it('renders stock health table', () => {
    renderDashboard()
    expect(screen.getByText('Kesehatan Stok')).toBeInTheDocument()
  })

  it('disables export button when no valuation data', () => {
    renderDashboard()
    const exportButton = screen.getByRole('button', { name: /ekspor valuasi csv/i })
    expect(exportButton).toBeDisabled()
  })
})
