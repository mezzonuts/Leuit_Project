import { useEffect, useRef, useState } from 'react'
import { X, Camera, Loader2 } from 'lucide-react'

interface BarcodeCameraModalProps {
  onClose: () => void
  onScan: (code: string) => void
}

export default function BarcodeCameraModal({ onClose, onScan }: BarcodeCameraModalProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const scanTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>()
  const [hasPermission, setHasPermission] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
        })

        if (cancelled) {
          stream.getTracks().forEach(track => track.stop())
          return
        }

        streamRef.current = stream
        setHasPermission(true)
      } catch {
        if (!cancelled) {
          setError('Tidak dapat mengakses kamera. Pastikan izin kamera diberikan.')
        }
      }
    }

    void initCamera()

    return () => {
      cancelled = true

      if (scanTimeoutRef.current) {
        clearTimeout(scanTimeoutRef.current)
        scanTimeoutRef.current = undefined
      }

      streamRef.current?.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!hasPermission || !videoRef.current || !streamRef.current) {
      return
    }

    const video = videoRef.current
    const stream = streamRef.current

    const startScanning = async () => {
      video.srcObject = stream
      await video.play()

      if (!('BarcodeDetector' in window)) {
        setError(
          'Barcode Detection API tidak didukung di browser ini. Gunakan HTTPS atau localhost.',
        )
        return
      }

      const detector = new window.BarcodeDetector({
        formats: [
          'ean_13',
          'ean_8',
          'upc_a',
          'upc_e',
          'code_128',
          'code_39',
          'qr_code',
        ],
      })

      const scan = async () => {
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
          scanTimeoutRef.current = setTimeout(() => void scan(), 100)
          return
        }

        try {
          const barcodes = await detector.detect(video)

          if (barcodes.length > 0) {
            onScan(barcodes[0].rawValue)
            onClose()
            return
          }
        } catch {
          // Ignore transient detection errors.
        }

        scanTimeoutRef.current = setTimeout(() => void scan(), 100)
      }

      void scan()
    }

    void startScanning()

    return () => {
      if (scanTimeoutRef.current) {
        clearTimeout(scanTimeoutRef.current)
        scanTimeoutRef.current = undefined
      }
    }
  }, [hasPermission, onClose, onScan])

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-8 text-center">
          <Camera className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Tidak Dapat Mengakses Kamera
          </h3>
          <p className="text-gray-600 mb-6">{error}</p>
          <button onClick={onClose} className="btn-primary">
            Tutup
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
    >
      <div className="relative w-full max-w-lg bg-white rounded-xl shadow-xl overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-white/90 shadow-lg"
          aria-label="Tutup kamera"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="aspect-video bg-black relative overflow-hidden">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            playsInline
            muted
          />

          {!hasPermission && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-white">
              <Loader2 className="h-10 w-10 animate-spin mx-auto text-primary-600 mb-4" />
              <p className="text-gray-600">Memuat kamera...</p>
            </div>
          )}

          {hasPermission && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-3/4 h-16 border-2 border-white/50 rounded-lg relative">
                <div className="absolute -top-2 left-1/2 -translate-x-1/2 bg-white px-2 text-xs text-gray-600 font-medium">
                  Arahkan barcode ke sini
                </div>
                <div className="absolute inset-0 border-2 border-primary-500/50 rounded-lg animate-pulse" />
              </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-gray-50 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-600">
            Pindai barcode/QR code kemasan bahan baku
          </p>
          <ul className="text-xs text-gray-500 mt-1 space-y-0.5">
            <li>EAN-13</li>
            <li>EAN-8</li>
            <li>UPC-A</li>
            <li>UPC-E</li>
            <li>Code 128</li>
            <li>Code 39</li>
            <li>QR Code</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Type augmentation for BarcodeDetector API
declare global {
  interface Window {
    BarcodeDetector: new (options: BarcodeDetectorOptions) => BarcodeDetector
  }

  interface BarcodeDetectorOptions {
    formats?: string[]
  }

  interface BarcodeDetector {
    detect(source: VideoFrame | HTMLVideoElement | ImageBitmap): Promise<DetectedBarcode[]>
  }

  interface DetectedBarcode {
    rawValue: string
    format: string
    boundingBox: DOMRectReadOnly
    cornerPoints: ReadonlyArray<DOMPoint>
  }
}