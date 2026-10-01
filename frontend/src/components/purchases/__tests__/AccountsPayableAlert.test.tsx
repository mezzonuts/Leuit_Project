import { render, screen, within } from '@testing-library/react'
import AccountsPayableAlert from '../AccountsPayableAlert'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
  formatDate: vi.fn((date: string) => date),
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
}))

const mockAlerts = [
  {
    id: 1,
    supplier_name: 'PT ABC',
    total_unpaid: 2500000,
    nearest_due_date: '2026-10-05',
    days_until_due: 4,
    purchase_count: 3,
  },
  {
    id: 2,
    supplier_name: 'PT XYZ',
    total_unpaid: 1800000,
    nearest_due_date: '2026-10-03',
    days_until_due: 2,
    purchase_count: 2,
  },
]

describe('AccountsPayableAlert', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders empty state when no alerts', () => {
    render(<AccountsPayableAlert alerts={[]} />)
    expect(screen.getByText('Tidak Ada Hutang')).toBeInTheDocument()
    expect(screen.getByText('Semua pembelian kredit sudah dilunasi. 🎉')).toBeInTheDocument()
  })

  it('renders summary cards', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    expect(screen.getByText('Total Hutang Belum Bayar')).toBeInTheDocument()
    expect(screen.getByText('Jatuh Tempo ≤ 3 Hari')).toBeInTheDocument()
    expect(screen.getByText('Jumlah Suplier')).toBeInTheDocument()
  })

  it('renders urgent count', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    expect(screen.getByText('1')).toBeInTheDocument() // 1 supplier with days_until_due <= 3
  })

  it('renders supplier count', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    const card = screen.getByText('Jumlah Suplier').parentElement
    expect(within(card!).getByText('2')).toBeInTheDocument() // 2 suppliers
  })

  it('renders supplier names', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    expect(screen.getByText('PT ABC')).toBeInTheDocument()
    expect(screen.getByText('PT XYZ')).toBeInTheDocument()
  })

  it('renders days until due', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    expect(screen.getByText('4 hari')).toBeInTheDocument()
    expect(screen.getByText('2 hari')).toBeInTheDocument()
  })

  it('renders action hint', () => {
    render(<AccountsPayableAlert alerts={mockAlerts} />)
    expect(screen.getByText(/Klik menu/i)).toBeInTheDocument()
  })
})
