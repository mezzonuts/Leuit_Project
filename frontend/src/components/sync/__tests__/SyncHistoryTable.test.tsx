import { render, screen } from '@testing-library/react'
import SyncHistoryTable from '../SyncHistoryTable'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/utils/formatters', () => ({
  formatDate: vi.fn((date: string) => date),
  formatDateTime: vi.fn((date: string) => date),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
}))

const mockHistory = [
  {
    id: 1,
    file_name: 'sales_jan.csv',
    uploaded_at: '2026-01-15T10:00:00Z',
    total_rows_read: 100,
    new_rows_inserted: 90,
    duplicate_rows_skipped: 10,
    reconciled_stock_items: 5,
    date_range_start: '2026-01-01',
    date_range_end: '2026-01-31',
  },
  {
    id: 2,
    file_name: 'sales_feb.csv',
    uploaded_at: '2026-02-15T10:00:00Z',
    total_rows_read: 80,
    new_rows_inserted: 75,
    duplicate_rows_skipped: 5,
    reconciled_stock_items: 3,
    date_range_start: '2026-02-01',
    date_range_end: '2026-02-28',
  },
]

describe('SyncHistoryTable', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders empty state when no history', () => {
    render(<SyncHistoryTable history={[]} />)
    expect(screen.getByText('Belum ada riwayat sinkronisasi')).toBeInTheDocument()
  })

  it('renders table headers', () => {
    render(<SyncHistoryTable history={mockHistory} />)
    expect(screen.getByText('Tanggal Upload')).toBeInTheDocument()
    expect(screen.getByText('File')).toBeInTheDocument()
    expect(screen.getByText('Total Baris')).toBeInTheDocument()
    expect(screen.getByText('Baru')).toBeInTheDocument()
    expect(screen.getByText('Duplikat')).toBeInTheDocument()
    expect(screen.getByText('Bahan Sync')).toBeInTheDocument()
    expect(screen.getByText('Periode Data')).toBeInTheDocument()
    expect(screen.getByText('Aksi')).toBeInTheDocument()
  })

  it('renders file names', () => {
    render(<SyncHistoryTable history={mockHistory} />)
    expect(screen.getByText('sales_jan.csv')).toBeInTheDocument()
    expect(screen.getByText('sales_feb.csv')).toBeInTheDocument()
  })

  it('renders row counts', () => {
    render(<SyncHistoryTable history={mockHistory} />)
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('90')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getAllByText('5').length).toBe(2)
  })

  it('renders second row data', () => {
    render(<SyncHistoryTable history={mockHistory} />)
    expect(screen.getByText('sales_feb.csv')).toBeInTheDocument()
    expect(screen.getByText('80')).toBeInTheDocument()
    expect(screen.getByText('75')).toBeInTheDocument()
  })

  it('renders action buttons', () => {
    render(<SyncHistoryTable history={mockHistory} />)
    expect(screen.getAllByTitle('Detail').length).toBe(2)
    expect(screen.getAllByTitle('Ekspor Detail').length).toBe(2)
  })

  it('renders single history item', () => {
    render(<SyncHistoryTable history={[mockHistory[0]]} />)
    expect(screen.getByText('sales_jan.csv')).toBeInTheDocument()
    expect(screen.queryByText('sales_feb.csv')).not.toBeInTheDocument()
  })
})
