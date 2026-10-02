import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import OutletSwitcher from '../OutletSwitcher'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        items: [
          { id: 1, name: 'Cafe A', is_active: true },
          { id: 2, name: 'Cafe B', is_active: true },
        ],
      },
    }),
  },
}))

vi.mock('@/stores', () => ({
  useOutletStore: vi.fn(() => ({
    current_outlet_id: null,
    outlets: [
      { id: 1, name: 'Cafe A', is_active: true },
      { id: 2, name: 'Cafe B', is_active: true },
    ],
    setCurrentOutlet: vi.fn(),
    setOutlets: vi.fn(),
  })),
}))

const renderSwitcher = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <OutletSwitcher />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('OutletSwitcher', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders outlet select dropdown', () => {
    renderSwitcher()
    expect(screen.getByLabelText('Pilih outlet')).toBeInTheDocument()
  })

  it('shows "Semua Outlet" option', () => {
    renderSwitcher()
    expect(screen.getByText('Semua Outlet')).toBeInTheDocument()
  })

  it('shows outlet names in dropdown', () => {
    renderSwitcher()
    expect(screen.getByText('Cafe A')).toBeInTheDocument()
    expect(screen.getByText('Cafe B')).toBeInTheDocument()
  })

  it('renders Store icon', () => {
    const { container } = renderSwitcher()
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})
