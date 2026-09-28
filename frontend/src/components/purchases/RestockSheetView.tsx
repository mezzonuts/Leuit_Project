import { CheckCircle, AlertCircle, Truck, DollarSign } from 'lucide-react'
import { formatRupiah, formatNumber, cn } from '@/utils/formatters'

interface RestockSheetViewProps {
  data: any
}

export default function RestockSheetView({ data }: RestockSheetViewProps) {
  if (!data || !data.items?.length) {
    return (
      <div className="text-center py-12">
        <Truck className="h-12 w-12 mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500">Belum ada rekomendasi restock.</p>
        <p className="text-sm text-gray-400 mt-1">Pastikan data stok & penjualan sudah di-sinkronkan.</p>
      </div>
    )
  }

  const items = data.items
  const totalEstimatedCost = items.reduce((sum: number, item: any) => sum + item.estimated_cost, 0)

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card p-4 bg-blue-50 border-l-4 border-blue-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg"><Truck className="h-5 w-5 text-blue-600" /></div>
            <div>
              <p className="text-sm text-blue-700">Total Item Direkomendasikan</p>
              <p className="text-2xl font-bold text-blue-900">{items.length}</p>
            </div>
          </div>
        </div>
        <div className="card p-4 bg-green-50 border-l-4 border-green-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg"><DollarSign className="h-5 w-5 text-green-600" /></div>
            <div>
              <p className="text-sm text-green-700">Estimasi Biaya Total</p>
              <p className="text-2xl font-bold text-green-900">{formatRupiah(totalEstimatedCost)}</p>
            </div>
          </div>
        </div>
        <div className="card p-4 bg-warning-50 border-l-4 border-warning-500">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-warning-100 rounded-lg"><AlertCircle className="h-5 w-5 text-warning-600" /></div>
            <div>
              <p className="text-sm text-warning-700">Prioritas Tinggi</p>
              <p className="text-2xl font-bold text-warning-900">
                {items.filter((i: any) => i.priority === 'high').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full" role="table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prioritas</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan Baku</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Stok Saat Ini</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Prediksi 7 Hari</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Safety Stock</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Order Qty</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Est. Biaya</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Suplier</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {items.map((item: any) => (
                <tr key={item.ingredient_id} className={cn('hover:bg-gray-50', item.priority === 'high' && 'bg-danger-50/30')}>
                  <td className="px-4 py-3">
                    <span className={cn('badge', item.priority === 'high' ? 'badge-danger' : item.priority === 'medium' ? 'badge-warning' : 'badge-success')}>
                      {item.priority === 'high' ? 'Tinggi' : item.priority === 'medium' ? 'Sedang' : 'Rendah'}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">{item.ingredient_name}</td>
                  <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.current_stock)} {item.unit}</td>
                  <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.predicted_consumption_7d)} {item.unit}</td>
                  <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.safety_stock)} {item.unit}</td>
                  <td className="px-4 py-3 text-right font-medium text-primary-600">{formatNumber(item.recommended_order_qty)} {item.unit}</td>
                  <td className="px-4 py-3 text-right font-medium text-gray-900">{formatRupiah(item.estimated_cost)}</td>
                  <td className="px-4 py-3 text-gray-600">{item.supplier_name || '-'}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{item.lead_time_days} hari</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Notes */}
      <div className="card p-4 bg-gray-50">
        <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-green-600" />
          Catatan:
        </h4>
        <ul className="space-y-1 text-sm text-gray-600">
          <li>â€¢ Prediksi berbasis 30 hari historis + cuaca BMKG Bandung</li>
          <li>â€¢ Safety stock = lead time Ã— rata-rata harian + buffer</li>
          <li>â€¢ Prioritas Tinggi: stok { "\x3C" } safety stock + lead time</li>
          <li>â€¢ Cek ketersediaan suplier sebelum memesan</li>
        </ul>
      </div>
    </div>
  )
}



