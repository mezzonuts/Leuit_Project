import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import PublicMenuPage from '../PublicMenuPage'
import { vi, describe, it, expect } from 'vitest'

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        items: [
          { id: 1, name: 'Kopi Susu', sale_price: 25000, ingredient_count: 3, is_active: true },
          { id: 2, name: 'Teh Manis', sale_price: 15000, ingredient_count: 2, is_active: true },
        ],
        total: 2,
      },
    }),
  },
}))

vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
}))

const renderPage = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <PublicMenuPage />
    </QueryClientProvider>
  )
}

describe('PublicMenuPage', () => {
  it('renders title', async () => {
    renderPage()
    expect(await screen.findByText('Menu Kami')).toBeInTheDocument()
  })

  it('renders menu items', async () => {
    renderPage()
    expect(await screen.findByText('Kopi Susu')).toBeInTheDocument()
    expect(await screen.findByText('Teh Manis')).toBeInTheDocument()
  })

  it('renders prices', async () => {
    renderPage()
    expect(await screen.findByText('Rp 25.000')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    renderPage()
    expect(screen.getByText(/Memuat menu/i)).toBeInTheDocument()
  })
})
