import { render, screen, fireEvent } from '@testing-library/react'
import SyncResultSummary from '../SyncResultSummary'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatDate: vi.fn((date: string) => date),
}))

const successResult = {
  new_inserted: 10,
  duplicates_skipped: 2,
  reconciled_stock_items: 5,
  date_range_start: '2026-01-01',
  date_range_end: '2026-01-31',
}

const emptyResult = {
  new_inserted: 0,
  duplicates_skipped: 5,
  reconciled_stock_items: 0,
  date_range_start: null,
  date_range_end: null,
}

describe('SyncResultSummary', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders success title', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText('Sinkronisasi Berhasil')).toBeInTheDocument()
  })

  it('renders empty title when no new data', () => {
    render(<SyncResultSummary result={emptyResult} onClose={vi.fn()} />)
    expect(screen.getByText('Tidak Ada Data Baru')).toBeInTheDocument()
  })

  it('renders new transactions count', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('renders duplicates count', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('renders reconciled items count', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('renders summary text', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText(/transaksi baru ditambahkan/i)).toBeInTheDocument()
  })

  it('renders close button', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('calls onClose when close clicked', () => {
    const onClose = vi.fn()
    render(<SyncResultSummary result={successResult} onClose={onClose} />)
    fireEvent.click(screen.getByLabelText('Tutup'))
    expect(onClose).toHaveBeenCalled()
  })

  it('renders date range when present', () => {
    render(<SyncResultSummary result={successResult} onClose={vi.fn()} />)
    expect(screen.getByText(/Periode/i)).toBeInTheDocument()
  })

  it('does not render date range when null', () => {
    render(<SyncResultSummary result={emptyResult} onClose={vi.fn()} />)
    expect(screen.queryByText(/Periode/i)).not.toBeInTheDocument()
  })
})
