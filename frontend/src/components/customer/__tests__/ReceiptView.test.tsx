import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ReceiptView from '../ReceiptView'
import { vi, describe, it, expect } from 'vitest'

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        transaction_id: 1,
        date: '2026-01-15T10:00:00Z',
        items: [
          { id: 1, name: 'Kopi Susu', quantity: 2, subtotal: 50000 },
        ],
        total: 50000,
      },
    }),
  },
}))

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
}))

const renderReceipt = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ReceiptView transactionId={1} />
    </QueryClientProvider>
  )
}

describe('ReceiptView', () => {
  it('renders loading state initially', () => {
    renderReceipt()
    expect(screen.getByText(/Memuat struk/i)).toBeInTheDocument()
  })

  it('renders receipt content', async () => {
    renderReceipt()
    expect(await screen.findByText('LEUIT')).toBeInTheDocument()
  })

  it('renders item details', async () => {
    renderReceipt()
    expect(await screen.findByText(/Kopi Susu/)).toBeInTheDocument()
  })

  it('renders total', async () => {
    renderReceipt()
    expect(await screen.findByText('Total')).toBeInTheDocument()
  })

  it('renders print button', async () => {
    renderReceipt()
    expect(await screen.findByText('Cetak')).toBeInTheDocument()
  })

  it('renders share button', async () => {
    renderReceipt()
    expect(await screen.findByText('Share')).toBeInTheDocument()
  })
})
