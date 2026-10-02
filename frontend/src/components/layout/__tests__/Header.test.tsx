import { render, screen, fireEvent } from '@testing-library/react'
import Header from '../Header'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Create a mutable mock store
const mockStore: {
  licenseGraceDays: number | null
} = {
  licenseGraceDays: null,
}

vi.mock('@/stores', () => ({
  useUIStore: vi.fn(() => mockStore),
}))

vi.mock('../OutletSwitcher', () => ({ default: () => null }))

const renderHeader = (props = {}) => {
  return render(<Header onMenuClick={vi.fn()} title="Test Page" {...props} />)
}

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.licenseGraceDays = null
  })

  it('renders page title', () => {
    renderHeader({ title: 'Dashboard' })

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders mobile menu button', () => {
    renderHeader()

    const menuButton = screen.getByLabelText('Buka menu')
    expect(menuButton).toBeInTheDocument()
  })

  it('calls onMenuClick when mobile menu button clicked', () => {
    const onMenuClick = vi.fn()
    renderHeader({ onMenuClick })

    const menuButton = screen.getByLabelText('Buka menu')
    fireEvent.click(menuButton)

    expect(onMenuClick).toHaveBeenCalled()
  })

  it('does not show license grace banner when licenseGraceDays is null', () => {
    mockStore.licenseGraceDays = null

    renderHeader()

    expect(screen.queryByText('Lisensi berakhir')).not.toBeInTheDocument()
  })

  it('does not show license grace banner when licenseGraceDays > 3', () => {
    mockStore.licenseGraceDays = 5

    renderHeader()

    expect(screen.queryByText('Lisensi berakhir')).not.toBeInTheDocument()
  })

  it('shows license grace banner when licenseGraceDays <= 3', () => {
    mockStore.licenseGraceDays = 2

    renderHeader()

    expect(screen.getByText(/Lisensi berakhir dalam 2 hari/)).toBeInTheDocument()
  })

  it('shows license grace banner when licenseGraceDays = 3', () => {
    mockStore.licenseGraceDays = 3

    renderHeader()

    expect(screen.getByText(/Lisensi berakhir dalam 3 hari/)).toBeInTheDocument()
  })

  it('shows license grace banner when licenseGraceDays = 1', () => {
    mockStore.licenseGraceDays = 1

    renderHeader()

    expect(screen.getByText(/Lisensi berakhir dalam 1 hari/)).toBeInTheDocument()
  })

  it('shows database status indicator', () => {
    mockStore.licenseGraceDays = null

    renderHeader()

    expect(screen.getByText('Database Terbuka')).toBeInTheDocument()
  })

  it('has correct styling for grace period badge', () => {
    mockStore.licenseGraceDays = 1

    const { container } = renderHeader()

    const badge = container.querySelector('[class*="bg-warning-50"]')
    expect(badge).toBeInTheDocument()
  })

  it('has correct styling for database status badge', () => {
    mockStore.licenseGraceDays = null

    const { container } = renderHeader()

    const badge = container.querySelector('[class*="bg-green-50"]')
    expect(badge).toBeInTheDocument()
  })
})