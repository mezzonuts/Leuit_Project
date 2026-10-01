import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import RecipeDrawer from '../RecipeDrawer'
import { useUIStore } from '@/stores'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { post: vi.fn(), put: vi.fn() },
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({
    drawerData: { mode: 'create', menu: null, ingredients: [] },
  })),
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
}))

const renderDrawer = (drawerData: any = { mode: 'create', menu: null, ingredients: [] }) => {
  vi.mocked(useUIStore).mockReturnValue({ drawerData } as any)

  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <RecipeDrawer onClose={vi.fn()} />
    </QueryClientProvider>
  )
}

describe('RecipeDrawer', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders create mode title', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText('Tambah Menu Baru')).toBeInTheDocument()
  })

  it('renders edit mode title', () => {
    renderDrawer({ mode: 'edit', menu: { name: 'Kopi', sale_price: 25000, recipes: [] }, ingredients: [] })
    expect(screen.getByText('Edit Menu & Resep')).toBeInTheDocument()
  })

  it('renders close button', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('renders form fields', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText('Nama Menu *')).toBeInTheDocument()
    expect(screen.getByText('Harga Jual (Rp) *')).toBeInTheDocument()
    expect(screen.getByText('POS Item ID')).toBeInTheDocument()
  })

  it('renders recipe items section', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText('Komposisi Resep (BOM)')).toBeInTheDocument()
  })

  it('renders add ingredient button', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText(/Tambah Bahan/i)).toBeInTheDocument()
  })

  it('renders cost summary', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText('Total HPP per Porsi:')).toBeInTheDocument()
  })

  it('renders action buttons', () => {
    renderDrawer({ mode: 'create', menu: null, ingredients: [] })
    expect(screen.getByText('Batal')).toBeInTheDocument()
    expect(screen.getByText(/Buat Menu/i)).toBeInTheDocument()
  })

  it('shows edit button text in edit mode', () => {
    renderDrawer({ mode: 'edit', menu: { name: 'Kopi', sale_price: 25000, recipes: [] }, ingredients: [] })
    expect(screen.getByText(/Update Menu/i)).toBeInTheDocument()
  })
})
