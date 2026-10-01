import { render, screen } from '@testing-library/react'
import ValuationMetricCard from '../ValuationMetricCard'
import { vi, describe, it, expect } from 'vitest'

// Mock formatters
vi.mock('@/utils/formatters', () => ({
  formatRupiah: vi.fn((val: number) => `Rp ${val.toLocaleString('id-ID')}`),
}))

describe('ValuationMetricCard', () => {
  const defaultProps = {
    title: 'Total Valuasi Aset',
    value: 5000000,
    icon: <span data-testid="icon">💰</span>,
    iconColor: 'text-green-600',
    bgColor: 'bg-green-50',
  }

  it('renders title correctly', () => {
    render(<ValuationMetricCard {...defaultProps} />)
    expect(screen.getByText('Total Valuasi Aset')).toBeInTheDocument()
  })

  it('renders formatted value', () => {
    render(<ValuationMetricCard {...defaultProps} />)
    expect(screen.getByText('Rp 5.000.000')).toBeInTheDocument()
  })

  it('renders icon', () => {
    render(<ValuationMetricCard {...defaultProps} />)
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(<ValuationMetricCard {...defaultProps} subtitle="20 bahan aktif" />)
    expect(screen.getByText('20 bahan aktif')).toBeInTheDocument()
  })

  it('hides subtitle when not provided', () => {
    render(<ValuationMetricCard {...defaultProps} />)
    expect(screen.queryByText('20 bahan aktif')).not.toBeInTheDocument()
  })

  it('renders zero value correctly', () => {
    render(<ValuationMetricCard {...defaultProps} value={0} />)
    expect(screen.getByText('Rp 0')).toBeInTheDocument()
  })

  it('applies custom colors', () => {
    const { container } = render(<ValuationMetricCard {...defaultProps} />)
    expect(container.querySelector('.bg-green-50')).toBeInTheDocument()
  })
})
