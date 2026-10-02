import { useState } from 'react'
import { generateMenuQRUrl, getMenuUrlForOutlet } from '@/utils/qrcode'
import { QrCode, Printer, Copy, Check } from 'lucide-react'
import { useOutletStore } from '@/stores'

export default function MenuQRPage() {
  const [copied, setCopied] = useState(false)
  const { current_outlet_id } = useOutletStore()

  const menuUrl = getMenuUrlForOutlet(current_outlet_id, '')
  const qrUrl = generateMenuQRUrl(menuUrl)

  const copyLink = () => {
    navigator.clipboard.writeText(menuUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="card text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <QrCode className="h-6 w-6 text-primary-600" />
          <h1 className="text-xl font-semibold">QR Code Menu</h1>
        </div>
        
        <div className="bg-white p-4 rounded-lg border inline-block">
          <img
            src={qrUrl}
            alt="QR Code Menu"
            className="w-64 h-64 mx-auto"
          />
        </div>
        
        <p className="text-sm text-gray-600 mt-4 mb-2">
          Scan untuk melihat menu digital
        </p>
        
        <div className="flex items-center gap-2 mb-4">
          <input
            type="text"
            value={menuUrl}
            readOnly
            className="form-input text-sm flex-1"
            aria-label="URL menu"
          />
          <button
            onClick={copyLink}
            className="btn-secondary flex items-center gap-1"
            aria-label="Salin link"
          >
            {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => window.print()}
            className="btn-secondary flex-1 flex items-center justify-center gap-1"
          >
            <Printer className="h-4 w-4" />
            Cetak QR
          </button>
        </div>
      </div>
    </div>
  )
}
