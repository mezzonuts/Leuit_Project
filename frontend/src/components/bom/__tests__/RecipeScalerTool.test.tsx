import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import RecipeScalerTool from '../RecipeScalerTool'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { get: vi.fn().mockResolvedValue({ data: { items: [] } }), post: vi.fn() },
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatNumber: vi.fn((val: number) => val.toLocaleString('id-ID')),
}))

const renderScaler = (ingredients: any[] = []) => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <RecipeScalerTool ingredients={ingredients} />
    </QueryClientProvider>
  )
}

describe('RecipeScalerTool', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders title', () => {
    renderScaler()
    expect(screen.getByText(/Simulasi Kebutuhan Bahan/i)).toBeInTheDocument()
  })

  it('renders menu select', () => {
    renderScaler()
    expect(screen.getByText('Menu *')).toBeInTheDocument()
  })

  it('renders target portions input', () => {
    renderScaler()
    expect(screen.getByText('Target Produksi (Porsi) *')).toBeInTheDocument()
  })

  it('renders calculate button', () => {
    renderScaler()
    expect(screen.getByText(/Hitung Kebutuhan/i)).toBeInTheDocument()
  })

  it('disables calculate button when no menu selected', () => {
    renderScaler()
    const button = screen.getByRole('button', { name: /Hitung Kebutuhan/i })
    expect(button).toBeDisabled()
  })

  it('shows empty menu option', () => {
    renderScaler()
    expect(screen.getByText('Pilih menu')).toBeInTheDocument()
  })

  it('does not show results initially', () => {
    renderScaler()
    expect(screen.queryByText(/Hasil Simulasi/i)).not.toBeInTheDocument()
  })
})
