import { render, screen } from '@testing-library/react'
import CriticalAlertsSection from '../CriticalAlertsSection'
import { describe, it, expect } from 'vitest'
import type { CriticalAlertItem } from '@/types'

const mockAlerts: CriticalAlertItem[] = [
  {
    id: 1,
    type: 'stock_low',
    name: 'Susu Segar',
    message: 'Stok 15 ml di bawah threshold 50 ml',
    severity: 'high',
  },
  {
    id: 2,
    type: 'expiry',
    name: 'Tepung Terigu',
    message: 'Basi dalam 2 hari',
    severity: 'medium',
  },
]

describe('CriticalAlertsSection', () => {
  it('renders empty state when no alerts', () => {
    render(<CriticalAlertsSection alerts={[]} />)
    expect(screen.getByText('Tidak ada peringatan kritis saat ini')).toBeInTheDocument()
  })

  it('renders alert count in header', () => {
    render(<CriticalAlertsSection alerts={mockAlerts} />)
    expect(screen.getByText('Peringatan Kritis (2)')).toBeInTheDocument()
  })

  it('renders alert name', () => {
    render(<CriticalAlertsSection alerts={mockAlerts} />)
    expect(screen.getByText('Susu Segar')).toBeInTheDocument()
    expect(screen.getByText('Tepung Terigu')).toBeInTheDocument()
  })

  it('renders alert message', () => {
    render(<CriticalAlertsSection alerts={mockAlerts} />)
    expect(screen.getByText('Stok 15 ml di bawah threshold 50 ml')).toBeInTheDocument()
  })

  it('renders high severity badge', () => {
    render(<CriticalAlertsSection alerts={mockAlerts} />)
    expect(screen.getByText('Tinggi')).toBeInTheDocument()
  })

  it('renders medium severity badge', () => {
    render(<CriticalAlertsSection alerts={mockAlerts} />)
    expect(screen.getByText('Sedang')).toBeInTheDocument()
  })

  it('renders single alert', () => {
    render(<CriticalAlertsSection alerts={[mockAlerts[0]]} />)
    expect(screen.getByText('Peringatan Kritis (1)')).toBeInTheDocument()
  })
})
