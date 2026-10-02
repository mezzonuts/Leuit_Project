import { render, screen } from '@testing-library/react'
import SkipNav from '../SkipNav'
import { describe, it, expect } from 'vitest'

describe('SkipNav', () => {
  it('renders skip link', () => {
    render(<SkipNav />)
    expect(screen.getByText('Lewati ke konten utama')).toBeInTheDocument()
  })

  it('links to main content', () => {
    render(<SkipNav />)
    const link = screen.getByText('Lewati ke konten utama')
    expect(link).toHaveAttribute('href', '#main-content')
  })

  it('is initially hidden (sr-only)', () => {
    const { container } = render(<SkipNav />)
    const link = container.querySelector('a')
    expect(link).toHaveClass('sr-only')
  })
})
