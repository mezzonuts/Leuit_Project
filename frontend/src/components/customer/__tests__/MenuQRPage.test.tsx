import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import MenuQRPage from '../MenuQRPage'
import { vi, describe, it, expect } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { get: vi.fn().mockResolvedValue({ data: { items: [] } }) },
}))

vi.mock('@/utils/qrcode', () => ({
  generateMenuQRUrl: vi.fn(() => 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=test'),
  getMenuUrlForOutlet: vi.fn(() => 'http://localhost:5173/menu'),
}))

vi.mock('@/stores', () => ({
  useOutletStore: vi.fn(() => ({ current_outlet_id: null })),
}))

const renderPage = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MenuQRPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('MenuQRPage', () => {
  it('renders title', () => {
    renderPage()
    expect(screen.getByText('QR Code Menu')).toBeInTheDocument()
  })

  it('renders QR code image', () => {
    renderPage()
    expect(screen.getByAltText('QR Code Menu')).toBeInTheDocument()
  })

  it('renders URL input', () => {
    renderPage()
    expect(screen.getByLabelText('URL menu')).toBeInTheDocument()
  })

  it('renders copy button', () => {
    renderPage()
    expect(screen.getByLabelText('Salin link')).toBeInTheDocument()
  })

  it('renders print button', () => {
    renderPage()
    expect(screen.getByText('Cetak QR')).toBeInTheDocument()
  })
})
