import { render, screen, fireEvent } from '@testing-library/react'
import AccessibleModal from '../AccessibleModal'
import { vi, describe, it, expect } from 'vitest'

describe('AccessibleModal', () => {
  const onClose = vi.fn()

  const renderModal = (isOpen = true) => (
    <AccessibleModal isOpen={isOpen} onClose={onClose} title="Test Modal">
      <p>Modal content</p>
    </AccessibleModal>
  )

  it('renders when open', () => {
    render(renderModal(true))
    expect(screen.getByText('Test Modal')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(renderModal(false))
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument()
  })

  it('has role dialog', () => {
    render(renderModal(true))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('has aria-modal', () => {
    render(renderModal(true))
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('has aria-label', () => {
    render(renderModal(true))
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-label', 'Test Modal')
  })

  it('close button has aria-label', () => {
    render(renderModal(true))
    expect(screen.getByLabelText('Tutup dialog')).toBeInTheDocument()
  })

  it('calls onClose on close button click', () => {
    render(renderModal(true))
    fireEvent.click(screen.getByLabelText('Tutup dialog'))
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose on Escape key', () => {
    render(renderModal(true))
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
  })

  it('renders children', () => {
    render(renderModal(true))
    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })
})
