import { render, screen } from '@testing-library/react'
import StockHealthTable from '../StockHealthTable'
import { vi, describe, it, expect } from 'vitest'
import type { StockHealthItem } from '@/types'

// Mock formatters
vi.mock('@/utils/formatters', () => ({
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
  getStockRatio: vi.fn((current: number, min: number) => min > 0 ? Math.round((current / min) * 100) : 100),
  getStockStatus: vi.fn((ratio: number) => ratio >= 150 ? 'safe' : ratio >= 100 ? 'warning' : 'danger'),
  getStockStatusColor: vi.fn((status: string) => status === 'safe' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-danger-600'),
  getStockProgressColor: vi.fn((ratio: number) => ratio >= 100 ? 'bg-green-500' : ratio >= 50 ? 'bg-yellow-500' : 'bg-danger-500'),
  daysUntilExpiry: vi.fn(() => 30),
}))

const mockItems: StockHealthItem[] = [
  {
    id: 1,
    name: 'Susu Segar',
    barcode_sku: '8991234567890',
    current_stock: 100,
    min_stock_threshold: 20,
    unit: 'ml',
    shelf_life_days: 7,
    days_until_expiry: 30,
    stock_ratio: 500,
    status: 'safe',
    cost_per_unit: 8000,
    valuation: 800000,
  },
  {
    id: 2,
    name: 'Gula Pasir',
    barcode_sku: '',
    current_stock: 5,
    min_stock_threshold: 50,
    unit: 'gram',
    shelf_life_days: 365,
    days_until_expiry: 365,
    stock_ratio: 10,
    status: 'danger',
    cost_per_unit: 15000,
    valuation: 75000,
  },
]

describe('StockHealthTable', () => {
  it('renders empty state when no items', () => {
    render(<StockHealthTable items={[]} />)
    expect(screen.getByText('Tidak ada data bahan baku')).toBeInTheDocument()
  })

  it('renders table headers', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getByText('Bahan')).toBeInTheDocument()
    expect(screen.getByText('Stok')).toBeInTheDocument()
    expect(screen.getByText('Progress')).toBeInTheDocument()
    expect(screen.getByText('Kadaluwarsa')).toBeInTheDocument()
  })

  it('renders ingredient names', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getByText('Susu Segar')).toBeInTheDocument()
    expect(screen.getByText('Gula Pasir')).toBeInTheDocument()
  })

  it('renders barcode when present', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getByText('8991234567890')).toBeInTheDocument()
  })

  it('does not render barcode when empty', () => {
    render(<StockHealthTable items={[mockItems[1]]} />)
    expect(screen.queryByText('8991234567890')).not.toBeInTheDocument()
    expect(screen.queryByText('font-mono')).not.toBeInTheDocument()
  })

  it('renders stock with unit', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getByText('100 ml')).toBeInTheDocument()
  })

  it('renders threshold information', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getByText('Threshold: 20 ml')).toBeInTheDocument()
  })

  it('renders progress bar', () => {
    render(<StockHealthTable items={mockItems} />)
    const progressBars = screen.getAllByRole('progressbar')
    expect(progressBars.length).toBeGreaterThan(0)
  })

  it('renders expiry days', () => {
    render(<StockHealthTable items={mockItems} />)
    expect(screen.getAllByText('30 hari').length).toBeGreaterThan(0)
  })
})
