import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BOM from '../BOM'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { get: vi.fn().mockResolvedValue({ data: { items: [] } }) },
}))

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => ({
    openDrawer: vi.fn(),
    closeDrawer: vi.fn(),
    activeDrawer: null,
  })),
}))

const renderBOM = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <BOM />
    </QueryClientProvider>
  )
}

describe('BOM', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders page title', () => {
    renderBOM()
    expect(screen.getByText('Resep & Menu')).toBeInTheDocument()
  })

  it('renders subtitle', () => {
    renderBOM()
    expect(screen.getByText('Bill of Materials & Recipe Scaler untuk simulasi porsi')).toBeInTheDocument()
  })

  it('renders tab buttons', () => {
    renderBOM()
    expect(screen.getByRole('button', { name: /Daftar Menu & Resep/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Recipe Scaler/i })).toBeInTheDocument()
  })

  it('shows empty state when no menus', () => {
    renderBOM()
    expect(screen.getByText('Belum ada menu. Buat menu pertama untuk memulai.')).toBeInTheDocument()
  })

  it('shows add menu button in empty state', () => {
    renderBOM()
    expect(screen.getAllByText(/Tambah Menu/i).length).toBeGreaterThan(0)
  })

  it('shows Tambah Menu button in header', () => {
    renderBOM()
    expect(screen.getAllByText(/Tambah Menu/i).length).toBeGreaterThan(0)
  })

  it('switches to scaler tab on click', () => {
    renderBOM()
    const scalerTab = screen.getByRole('button', { name: /Recipe Scaler/i })
    fireEvent.click(scalerTab)
    expect(screen.getByText(/Simulasi Kebutuhan Bahan/i)).toBeInTheDocument()
  })
})
