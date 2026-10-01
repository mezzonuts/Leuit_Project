import { render, screen } from '@testing-library/react'
import RestockSheetView from '../RestockSheetView'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
}))

const mockData = {
  items: [
    {
      ingredient_id: 1,
      ingredient_name: 'Susu Segar',
      current_stock: 50,
      unit: 'ml',
      predicted_consumption_7d: 200,
      safety_stock: 100,
      recommended_order_qty: 300,
      estimated_cost: 2400000,
      supplier_name: 'PT ABC',
      lead_time_days: 2,
      priority: 'high',
    },
    {
      ingredient_id: 2,
      ingredient_name: 'Gula Pasir',
      current_stock: 200,
      unit: 'gram',
      predicted_consumption_7d: 150,
      safety_stock: 80,
      recommended_order_qty: 100,
      estimated_cost: 1200000,
      supplier_name: 'PT XYZ',
      lead_time_days: 3,
      priority: 'medium',
    },
  ],
}

describe('RestockSheetView', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders empty state when no data', () => {
    render(<RestockSheetView data={null} />)
    expect(screen.getByText('Belum ada rekomendasi restock.')).toBeInTheDocument()
  })

  it('renders empty state when items empty', () => {
    render(<RestockSheetView data={{ items: [] }} />)
    expect(screen.getByText('Belum ada rekomendasi restock.')).toBeInTheDocument()
  })

  it('renders summary cards', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('Total Item Direkomendasikan')).toBeInTheDocument()
    expect(screen.getByText('Estimasi Biaya Total')).toBeInTheDocument()
    expect(screen.getByText('Prioritas Tinggi')).toBeInTheDocument()
  })

  it('renders item count in summary', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('renders high priority count', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('Tinggi')).toBeInTheDocument()
  })

  it('renders ingredient names', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('Susu Segar')).toBeInTheDocument()
    expect(screen.getByText('Gula Pasir')).toBeInTheDocument()
  })

  it('renders supplier names', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('PT ABC')).toBeInTheDocument()
  })

  it('renders lead time', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('2 hari')).toBeInTheDocument()
  })

  it('renders notes section', () => {
    render(<RestockSheetView data={mockData} />)
    expect(screen.getByText('Catatan:')).toBeInTheDocument()
  })
})
