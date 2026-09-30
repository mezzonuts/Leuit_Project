import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from '../Sidebar'
import { vi, describe, it, expect, beforeEach } from 'vitest'

const renderSidebar = (props = {}) => {
  return render(
    <MemoryRouter>
      <Sidebar
        isOpen={true}
        onToggle={vi.fn()}
        mobileOpen={false}
        onMobileClose={vi.fn()}
        {...props}
      />
    </MemoryRouter>
  )
}

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders LEUIT logo when open', () => {
    renderSidebar()

    expect(screen.getByText('LEUIT')).toBeInTheDocument()
  })

  it('does not render LEUIT logo text when collapsed', () => {
    renderSidebar({ isOpen: false })

    expect(screen.queryByText('LEUIT')).not.toBeInTheDocument()
  })

  it('renders all navigation items', () => {
    renderSidebar()

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Kelola Stok')).toBeInTheDocument()
    expect(screen.getByText('Resep & Menu')).toBeInTheDocument()
    expect(screen.getByText('Pembelian')).toBeInTheDocument()
    expect(screen.getByText('Sinkronisasi')).toBeInTheDocument()
  })

  it('shows navigation item labels when open', () => {
    renderSidebar({ isOpen: true })

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('hides navigation item labels when collapsed', () => {
    renderSidebar({ isOpen: false })

    // When collapsed, labels are in title attribute, not visible text
    const dashboardLink = screen.getByTitle('Dashboard')
    expect(dashboardLink).toBeInTheDocument()
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
  })

  it('shows toggle button with correct aria labels', () => {
    renderSidebar({ isOpen: true })

    const toggleButton = screen.getByLabelText('Tutup sidebar')
    expect(toggleButton).toBeInTheDocument()

    renderSidebar({ isOpen: false })
    const openButton = screen.getByLabelText('Buka sidebar')
    expect(openButton).toBeInTheDocument()
  })

  it('toggles sidebar when button clicked', () => {
    const onToggle = vi.fn()
    renderSidebar({ isOpen: true, onToggle })

    const toggleButton = screen.getByLabelText('Tutup sidebar')
    fireEvent.click(toggleButton)

    expect(onToggle).toHaveBeenCalled()
  })

  it('renders footer with version when open', () => {
    renderSidebar({ isOpen: true })

    expect(screen.getByText('LEUIT v1.0.0')).toBeInTheDocument()
  })

  it('does not render footer when collapsed', () => {
    renderSidebar({ isOpen: false })

    expect(screen.queryByText('LEUIT v1.0.0')).not.toBeInTheDocument()
  })

  it('has correct aria-label for navigation', () => {
    renderSidebar()

    const nav = screen.getByLabelText('Menu navigasi')
    expect(nav).toBeInTheDocument()
  })

  it('renders icons for each navigation item', () => {
    renderSidebar({ isOpen: false })

    const icons = screen.getAllByTestId('nav-icon')
    expect(icons.length).toBeGreaterThan(0)
  })

  it('calls onMobileClose when navigation item clicked on mobile', () => {
    const onMobileClose = vi.fn()
    renderSidebar({ mobileOpen: true, onMobileClose })

    fireEvent.click(screen.getByText('Dashboard'))

    expect(onMobileClose).toHaveBeenCalled()
  })
})