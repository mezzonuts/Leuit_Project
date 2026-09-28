import { forwardRef } from 'react'
import { formatRupiah, formatNumber, getStockRatio, getStockStatus, getStockStatusColor, getStockProgressColor, daysUntilExpiry } from '@/utils/formatters'
import type { StockHealthItem } from '@/types'

interface StockHealthTableProps {
  items: StockHealthItem[]
}

const StockHealthTable = forwardRef<HTMLDivElement, StockHealthTableProps>(
  ({ items }, ref) => {
    const sortedItems = [...items].sort((a, b) => {
      const statusOrder = { danger: 0, warning: 1, safe: 2 }
      return statusOrder[a.status] - statusOrder[b.status]
    })

    return (
      <div ref={ref} className="card overflow-hidden">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Kesehatan Stok</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full" role="table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Stok</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kadaluwarsa</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sortedItems.map((item) => {
                const ratio = getStockRatio(item.current_stock, item.min_stock_threshold)
                const status = getStockStatus(ratio)
                const progressColor = getStockProgressColor(ratio)
                const daysLeft = daysUntilExpiry(item.shelf_life_days)
                const isExpiringSoon = daysLeft <= 3 && daysLeft >= 0
                const isExpired = daysLeft < 0

                return (
                  <tr key={item.id} className={`hover:bg-gray-50 ${status === 'danger' ? 'bg-danger-50/50' : ''}`}>
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        {item.barcode_sku && (
                          <p className="text-xs text-gray-500 font-mono">{item.barcode_sku}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {formatNumber(item.current_stock)} {item.unit}
                      </div>
                      <div className="text-xs text-gray-500">
                        Threshold: {formatNumber(item.min_stock_threshold)} {item.unit}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${progressColor} transition-all duration-300`}
                            style={{ width: `${Math.min(ratio, 200)}%` }}
                            role="progressbar"
                            aria-valuenow={ratio}
                            aria-valuemin={0}
                            aria-valuemax={200}
                            aria-label={`Stok ${ratio}% dari threshold`}
                          />
                        </div>
                        <span className={`text-xs font-medium ${getStockStatusColor(status)} whitespace-nowrap`}>
                          {ratio}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {isExpired ? (
                        <span className="badge badge-danger flex items-center gap-1">
                          <span className="animate-pulse">⏰</span>
                          Kadaluarsa {Math.abs(daysLeft)} hari lalu
                        </span>
                      ) : isExpiringSoon ? (
                        <span className="badge badge-danger flex items-center gap-1 animate-pulse">
                          ⏰ Basi dalam {daysLeft} hari
                        </span>
                      ) : (
                        <span className="text-sm text-gray-600">{daysLeft} hari</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {items.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            Tidak ada data bahan baku
          </div>
        )}
      </div>
    )
  }
)

StockHealthTable.displayName = 'StockHealthTable'

export default StockHealthTable