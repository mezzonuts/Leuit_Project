import { Clock, DollarSign, CreditCard, MessageCircle } from 'lucide-react'
import { formatRupiah, formatDate } from '@/utils/formatters'
import { createWhatsAppReminderLink } from '@/utils/whatsapp'
import { cn } from '@/utils/formatters'

interface AccountsPayableAlertProps {
  alerts: any[]
}

export default function AccountsPayableAlert({ alerts }: AccountsPayableAlertProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-12">
        <CreditCard className="h-12 w-12 mx-auto text-green-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-1">Tidak Ada Hutang</h3>
        <p className="text-gray-500">Semua pembelian kredit sudah dilunasi. 🎉</p>
      </div>
    )
  }

  const totalUnpaid = alerts.reduce((sum, a) => sum + a.total_unpaid, 0)
  const urgentCount = alerts.filter(a => a.days_until_due <= 3).length

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card p-4 bg-danger-50 border-l-4 border-danger-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-danger-100 rounded-lg"><DollarSign className="h-5 w-5 text-danger-600" /></div>
            <div>
              <p className="text-sm text-danger-700">Total Hutang Belum Bayar</p>
              <p className="text-2xl font-bold text-danger-900">{formatRupiah(totalUnpaid)}</p>
            </div>
          </div>
        </div>
        <div className="card p-4 bg-warning-50 border-l-4 border-warning-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-warning-100 rounded-lg"><Clock className="h-5 w-5 text-warning-600" /></div>
            <div>
              <p className="text-sm text-warning-700">Jatuh Tempo ≤ 3 Hari</p>
              <p className="text-2xl font-bold text-warning-900">{urgentCount}</p>
            </div>
          </div>
        </div>
        <div className="card p-4 bg-blue-50 border-l-4 border-blue-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg"><CreditCard className="h-5 w-5 text-blue-600" /></div>
            <div>
              <p className="text-sm text-blue-700">Jumlah Suplier</p>
              <p className="text-2xl font-bold text-blue-900">{alerts.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full" role="table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Suplier</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Hutang</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jatuh Tempo Terdekat</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hari Tersisa</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jumlah Transaksi</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {alerts.map((alert) => (
                <tr key={alert.id} className={cn('hover:bg-gray-50', alert.days_until_due <= 3 && 'bg-warning-50/50')}>
                  <td className="px-4 py-3 font-medium text-gray-900">{alert.supplier_name}</td>
                  <td className="px-4 py-3 text-right font-medium text-gray-900">{formatRupiah(alert.total_unpaid)}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(alert.nearest_due_date)}</td>
                  <td className="px-4 py-3">
                    <span className={cn('badge', alert.days_until_due <= 0 ? 'badge-danger' : alert.days_until_due <= 3 ? 'badge-warning' : 'badge-info')}>
                      {alert.days_until_due <= 0
                        ? `Terlambat ${Math.abs(alert.days_until_due)} hari`
                        : alert.days_until_due === 1
                        ? 'Besok'
                        : `${alert.days_until_due} hari`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600">{alert.purchase_count}</td>
                  <td className="px-4 py-3">
                    <span className={cn('badge', alert.days_until_due <= 0 ? 'badge-danger' : alert.days_until_due <= 3 ? 'badge-warning' : 'badge-info')}>
                      {alert.days_until_due <= 0 ? 'TERLAMBAT' : alert.days_until_due <= 3 ? 'URGENT' : 'NORMAL'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {alert.phone_whatsapp && (
                      <a
                        href={createWhatsAppReminderLink(alert.phone_whatsapp, alert.supplier_name, alert.total_unpaid, alert.days_until_due)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 btn-secondary text-sm"
                      >
                        <MessageCircle className="h-3.5 w-3.5" />
                        WhatsApp
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Action hint */}
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Klik menu <span className="font-medium">Pembelian → Daftar Pembelian</span> untuk melunasi hutang (tombol <span className="font-medium text-green-600">Bayar</span> pada transaksi CREDIT UNPAID).
          </p>
        </div>
      </div>
    </div>
  )
}