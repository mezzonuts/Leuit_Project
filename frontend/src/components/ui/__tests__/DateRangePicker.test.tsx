import { render, screen, fireEvent } from '@testing-library/react'
import DateRangePicker from '../DateRangePicker'
import { vi, describe, it, expect } from 'vitest'

describe('DateRangePicker', () => {
  const onChange = vi.fn()

  const defaultProps = {
    startDate: '2026-01-01',
    endDate: '2026-01-31',
    onChange,
  }

  it('renders date inputs', () => {
    render(<DateRangePicker {...defaultProps} />)
    expect(screen.getByLabelText('Tanggal mulai')).toBeInTheDocument()
    expect(screen.getByLabelText('Tanggal selesai')).toBeInTheDocument()
  })

  it('renders date values', () => {
    render(<DateRangePicker {...defaultProps} />)
    expect(screen.getByLabelText('Tanggal mulai')).toHaveValue('2026-01-01')
    expect(screen.getByLabelText('Tanggal selesai')).toHaveValue('2026-01-31')
  })

  it('opens preset dropdown on button click', () => {
    render(<DateRangePicker {...defaultProps} />)
    fireEvent.click(screen.getByLabelText('Pilih rentang tanggal'))
    expect(screen.getByText('7 Hari')).toBeInTheDocument()
    expect(screen.getByText('30 Hari')).toBeInTheDocument()
  })

  it('calls onChange with preset dates', () => {
    render(<DateRangePicker {...defaultProps} />)
    fireEvent.click(screen.getByLabelText('Pilih rentang tanggal'))
    fireEvent.click(screen.getByText('7 Hari'))
    expect(onChange).toHaveBeenCalled()
  })

  it('calls onChange when date input changes', () => {
    render(<DateRangePicker {...defaultProps} />)
    fireEvent.change(screen.getByLabelText('Tanggal mulai'), {
      target: { value: '2026-02-01' },
    })
    expect(onChange).toHaveBeenCalledWith('2026-02-01', '2026-01-31')
  })
})
