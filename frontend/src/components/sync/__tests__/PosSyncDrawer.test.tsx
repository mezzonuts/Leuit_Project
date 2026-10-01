import { render, screen } from '@testing-library/react'
import PosSyncDrawer from '../PosSyncDrawer'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { post: vi.fn() },
}))

vi.mock('@/utils/formatters', () => ({
  cn: (...args: any[]) => args.filter(Boolean).join(' '),
  formatDate: vi.fn((date: string) => date),
}))

const renderDrawer = () => {
  return render(<PosSyncDrawer onClose={vi.fn()} />)
}

describe('PosSyncDrawer', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders title', () => {
    renderDrawer()
    expect(screen.getByText('Upload CSV Kasir')).toBeInTheDocument()
  })

  it('renders close button', () => {
    renderDrawer()
    expect(screen.getByLabelText('Tutup')).toBeInTheDocument()
  })

  it('renders drag-drop zone', () => {
    renderDrawer()
    expect(screen.getByText('Seret & Lepas File CSV')).toBeInTheDocument()
  })

  it('renders supported formats', () => {
    renderDrawer()
    expect(screen.getByText('Format: Moka POS, Majoo, Olsera')).toBeInTheDocument()
  })

  it('renders file input', () => {
    const { container } = renderDrawer()
    const fileInput = container.querySelector('input[type="file"]')
    expect(fileInput).toBeInTheDocument()
  })

  it('does not show uploading state initially', () => {
    renderDrawer()
    expect(screen.queryByText('Memproses CSV...')).not.toBeInTheDocument()
  })

  it('does not show result initially', () => {
    renderDrawer()
    expect(screen.queryByText('Sinkronisasi Berhasil')).not.toBeInTheDocument()
  })
})
