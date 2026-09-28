import { X, AlertTriangle } from 'lucide-react'
import { useUIStore } from '@/stores'

export default function LicenseGraceBanner() {
  const { licenseGraceDays, setLicenseGraceDays } = useUIStore()

  if (licenseGraceDays === null || licenseGraceDays > 3) return null

  const isExpired = licenseGraceDays <= 0
  const bgColor = isExpired ? 'bg-danger-50' : 'bg-warning-50'
  const textColor = isExpired ? 'text-danger-700' : 'text-warning-700'
  const borderColor = isExpired ? 'border-danger-200' : 'border-warning-200'
  const iconColor = isExpired ? 'text-danger-500' : 'text-warning-500'

  const message = isExpired
    ? 'Langganan telah kedaluwarsa. Fitur prediksi & cuaca dinonaktifkan. Mode read-only aktif.'
    : `Masa tenggang lisensi: ${licenseGraceDays} hari tersisa. Silakan perpanjang langganan.`

  return (
    <div
      className={`${bgColor} border-b ${borderColor} px-4 py-3`}
      role="alert"
      aria-live="polite"
    >
      <div className="max-w-7xl mx-auto flex items-center gap-3">
        <AlertTriangle className={`${iconColor} h-5 w-5 flex-shrink-0`} aria-hidden="true" />
        <p className={`${textColor} text-sm font-medium flex-1`}>{message}</p>
        {!isExpired && (
          <button
            onClick={() => setLicenseGraceDays(null)}
            className={`${textColor} hover:underline text-sm font-medium`}
          >
            Tutup
          </button>
        )}
        {isExpired && (
          <button
            onClick={() => setLicenseGraceDays(null)}
            className={`p-1 rounded hover:bg-white/50 ${textColor}`}
            aria-label="Tutup notifikasi"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}