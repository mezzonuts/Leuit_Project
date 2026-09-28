import { Clock, Package, AlertTriangle } from 'lucide-react'
import { formatDate, daysUntilExpiry, getStockRatio, getStockStatus, getStockStatusColor, getStockProgressColor } from '@/utils/formatters'
import type { CriticalAlertItem } from '@/types'

interface CriticalAlertsSectionProps {
  alerts: CriticalAlertItem[]
}

export default function CriticalAlertsSection({ alerts }: CriticalAlertsSectionProps) {
  if (alerts.length === 0) {
    return (
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Peringatan Kritis</h2>
        <div className="text-center py-8 text-gray-500">
          <AlertTriangle className="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p>Tidak ada peringatan kritis saat ini</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-danger-500" />
        Peringatan Kritis ({alerts.length})
      </h2>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`flex items-start gap-3 p-3 rounded-lg border ${
              alert.severity === 'high'
                ? 'bg-danger-50 border-danger-200'
                : 'bg-warning-50 border-warning-200'
            }`}
          >
            <div className={`flex-shrink-0 p-2 rounded-full ${
              alert.type === 'expiry'
                ? 'bg-danger-100 text-danger-600'
                : 'bg-warning-100 text-warning-600'
            }`}>
              {alert.type === 'expiry' ? <Clock className="h-5 w-5" /> : <Package className="h-5 w-5" />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900">{alert.name}</p>
              <p className="text-sm text-gray-600 mt-0.5">{alert.message}</p>
            </div>
            <span className={`badge ${alert.severity === 'high' ? 'badge-danger' : 'badge-warning'}`}>
              {alert.severity === 'high' ? 'Tinggi' : 'Sedang'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}