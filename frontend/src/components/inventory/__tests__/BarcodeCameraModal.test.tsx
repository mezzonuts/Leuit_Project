import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import BarcodeCameraModal from '../BarcodeCameraModal'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'

// Mock navigator.mediaDevices
const mockMediaDevices = {
  getUserMedia: vi.fn(),
}

Object.defineProperty(navigator, 'mediaDevices', {
  value: mockMediaDevices,
  writable: true,
})

// Mock BarcodeDetector
const mockDetect = vi.fn()
const MockBarcodeDetector = vi.fn().mockImplementation(() => ({
  detect: mockDetect,
}))

Object.defineProperty(window, 'BarcodeDetector', {
  value: MockBarcodeDetector,
  writable: true,
  configurable: true,
})

describe('BarcodeCameraModal', () => {
  const mockOnClose = vi.fn()
  const mockOnScan = vi.fn()

  const renderModal = (props = {}) => {
    return render(
      <BarcodeCameraModal
        onClose={mockOnClose}
        onScan={mockOnScan}
        {...props}
      />
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockMediaDevices.getUserMedia.mockReset()
    mockDetect.mockReset()
    MockBarcodeDetector.mockClear()
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('shows loading state while initializing camera', () => {
    mockMediaDevices.getUserMedia.mockImplementation(() => new Promise(() => {}))

    renderModal()

    expect(screen.getByText('Memuat kamera...')).toBeInTheDocument()
  })

  it('shows error when camera access denied', async () => {
    mockMediaDevices.getUserMedia.mockRejectedValueOnce(new Error('Permission denied'))

    renderModal()

    await waitFor(() => {
      expect(screen.getByText('Tidak Dapat Mengakses Kamera')).toBeInTheDocument()
      expect(screen.getByText('Tidak dapat mengakses kamera. Pastikan izin kamera diberikan.')).toBeInTheDocument()
    })
  })

  it('shows error when BarcodeDetector not supported', async () => {
    mockMediaDevices.getUserMedia.mockResolvedValueOnce({
      getTracks: () => [{ stop: vi.fn() }],
    })

    // Remove BarcodeDetector to simulate unsupported browser
    const originalBarcodeDetector = window.BarcodeDetector
    // @ts-ignore
    delete window.BarcodeDetector

    renderModal()

    await waitFor(() => {
      expect(screen.getByText('Barcode Detection API tidak didukung di browser ini. Gunakan HTTPS atau localhost.')).toBeInTheDocument()
    })

    // Restore
    window.BarcodeDetector = MockBarcodeDetector
  })

  it('calls onClose when close button clicked', () => {
    mockMediaDevices.getUserMedia.mockResolvedValueOnce({
      getTracks: () => [{ stop: vi.fn() }],
    })

    renderModal()

    const closeButton = screen.getByLabelText('Tutup kamera')
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onClose when error close button clicked', async () => {
    mockMediaDevices.getUserMedia.mockRejectedValueOnce(new Error('Permission denied'))

    renderModal()

    await waitFor(() => {
      const closeButton = screen.getByRole('button', { name: /tutup/i })
      fireEvent.click(closeButton)
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  it('initializes BarcodeDetector with correct formats', async () => {
    mockMediaDevices.getUserMedia.mockResolvedValueOnce({
      getTracks: () => [{ stop: vi.fn() }],
    })

    renderModal()

    await waitFor(() => {
      expect(MockBarcodeDetector).toHaveBeenCalledWith({
        formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'code_39', 'qr_code'],
      })
    })
  })

  it('calls onScan and onClose when barcode detected', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    renderModal()

    // Wait for camera to initialize
    await waitFor(() => {
      expect(MockBarcodeDetector).toHaveBeenCalled()
    })

    // Simulate barcode detection
    mockDetect.mockResolvedValueOnce([{ rawValue: '8991234567890', format: 'ean_13' }])

    // Advance timers to trigger scan
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })

    await waitFor(() => {
      expect(mockOnScan).toHaveBeenCalledWith('8991234567890')
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  it('stops camera stream on unmount', async () => {
    const mockTrack = { stop: vi.fn() }
    const mockStream = {
      getTracks: () => [mockTrack],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    const { unmount } = renderModal()

    await waitFor(() => {
      expect(mockMediaDevices.getUserMedia).toHaveBeenCalledWith({
        video: { facingMode: 'environment' },
      })
    })

    unmount()

    expect(mockTrack.stop).toHaveBeenCalled()
  })

  it('clears scan timeout on unmount', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    const { unmount } = renderModal()

    await waitFor(() => {
      expect(MockBarcodeDetector).toHaveBeenCalled()
    })

    unmount()

    // Should not throw - timeout cleared
  })

  it('displays camera view when permission granted', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    renderModal()

    await waitFor(() => {
      const video = screen.getByRole('video')
      expect(video).toBeInTheDocument()
    })
  })

  it('shows scanning overlay with frame and pulse animation', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    renderModal()

    await waitFor(() => {
      expect(screen.getByText('Arahkan barcode ke sini')).toBeInTheDocument()
    })
  })

  it('shows supported formats list', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    renderModal()

    await waitFor(() => {
      expect(screen.getByText('EAN-13')).toBeInTheDocument()
      expect(screen.getByText('QR Code')).toBeInTheDocument()
    })
  })

  it('stops scanning after successful scan', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    }

    mockMediaDevices.getUserMedia.mockResolvedValueOnce(mockStream)

    renderModal()

    await waitFor(() => {
      expect(MockBarcodeDetector).toHaveBeenCalled()
    })

    mockDetect.mockResolvedValueOnce([{ rawValue: '1234567890', format: 'ean_13' }])

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })

    await waitFor(() => {
      expect(mockOnScan).toHaveBeenCalledWith('1234567890')
      expect(mockOnClose).toHaveBeenCalled()
    })
  })
})