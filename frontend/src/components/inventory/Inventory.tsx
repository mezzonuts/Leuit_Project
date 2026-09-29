import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Camera, Download, Package } from 'lucide-react'
import { api } from '@/services/api'
import { formatRupiah, formatNumber, getStockRatio, getStockStatus, getStockStatusColor, getStockProgressColor, daysUntilExpiry } from '@/utils/formatters'
import { downloadValuationCSV } from '@/utils/exportCsv'
import { useUIStore } from '@/stores'
import IngredientDrawer from './IngredientDrawer'
import BarcodeCameraModal from './BarcodeCameraModal'

export default function Inventory() {
  const queryClient = useQueryClient()
  const { openDrawer, closeDrawer, activeDrawer } = useUIStore()
  const [search, setSearch] = useState('')
  const [showInactive, setShowInactive] = useState(false)
  const [showCamera, setShowCamera] = useState(false)

  const { data: response } = useQuery({
    queryKey: ['ingredients', search, showInactive],
    queryFn: () => api.get('/inventory', { params: { search, active_only: !showInactive } }).then(res => res.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/inventory/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['ingredients'] }),
  })

  const handleEdit = (ingredient: any) => {
    openDrawer('ingredient', { mode: 'edit', ingredient })
  }

  const handleDelete = (id: number) => {
    if (confirm('Yakin ingin mengarsipkan bahan ini? (Soft delete)')) {
      deleteMutation.mutate(id)
    }
  }

  const handleNew = () => {
    openDrawer('ingredient', { mode: 'create' })
  }

  const handleOpname = (ingredient: any) => {
    openDrawer('ingredient', { mode: 'opname', ingredient })
  }

  const handleExport = () => {
    if (response?.items) {
      downloadValuationCSV(response.items)
    }
  }

  const items = response?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Kelola Stok</h1>
          <p className="text-gray-500 mt-1">Master bahan baku, barcode scanner, stock opname & threshold</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
            <Download className="h-4 w-4" />
            Ekspor CSV
          </button>
          <button onClick={handleNew} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Tambah Bahan
          </button>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Cari nama bahan atau barcode..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="input pl-10"
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={e => setShowInactive(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Tampilkan yang diarsipkan</span>
          </label>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full" role="table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Barcode/SKU</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Stok</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">HPP</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kadaluwarsa</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {items.map((item: any) => {
                const ratio = getStockRatio(item.current_stock, item.min_stock_threshold)
                const status = getStockStatus(ratio)
                const progressColor = getStockProgressColor(ratio)
                const daysLeft = daysUntilExpiry(item.shelf_life_days, item.created_at)
                const isExpiringSoon = daysLeft <= 3 && daysLeft >= 0
                const isExpired = daysLeft < 0

                return (
                  <tr key={item.id} className={`hover:bg-gray-50 ${!item.is_active ? 'opacity-50' : ''}`}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900">{item.name}</p>
                      <p className="text-xs text-gray-500">{item.unit}</p>
                    </td>
                    <td className="px-4 py-3">
                      {item.barcode_sku ? (
                        <code className="text-sm font-mono text-gray-700 bg-gray-100 px-2 py-0.5 rounded">{item.barcode_sku}</code>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="font-medium text-gray-900">{formatNumber(item.current_stock)} {item.unit}</div>
                      <div className="text-xs text-gray-500">Min: {formatNumber(item.min_stock_threshold)}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 max-w-xs h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${progressColor} transition-all`}
                            style={{ width: `${Math.min(ratio, 200)}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium ${getStockStatusColor(status)}`}>{ratio}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900">
                      {formatRupiah(item.cost_per_unit)}/{item.unit}
                    </td>
                    <td className="px-4 py-3">
                      {isExpired ? (
                        <span className="badge badge-danger animate-pulse">⏰ Kadaluarsa {Math.abs(daysLeft)} hri</span>
                      ) : isExpiringSoon ? (
                        <span className="badge badge-danger animate-pulse">⏰ {daysLeft} hari</span>
                      ) : (
                        <span className="text-sm text-gray-600">{daysLeft} hari</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${item.is_active ? 'badge-success' : 'badge-warning'}`}>
                        {item.is_active ? 'Aktif' : 'Diarsipkan'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleOpname(item)}
                          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                          title="Stock Opname"
                        >
                          <Package className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => setShowCamera(true)}
                          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                          title="Scan Barcode"
                        >
                          <Camera className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(item)}
                          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                          title="Edit"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-2 rounded-lg text-gray-500 hover:bg-danger-100 hover:text-danger-700"
                          title="Arsipkan"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {items.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <Package className="h-12 w-12 mx-auto text-gray-300 mb-2" />
            <p>Belum ada data bahan baku</p>
            <button onClick={handleNew} className="mt-2 btn-primary">
              <Plus className="h-4 w-4 mr-2" />
              Tambah Bahan Pertama
            </button>
          </div>
        )}
      </div>

      {/* Modals & Drawers */}
      {activeDrawer === 'ingredient' && <IngredientDrawer onClose={closeDrawer} />}
      {showCamera && (
        <BarcodeCameraModal
          onClose={() => setShowCamera(false)}
          onScan={(code) => {
            // Handle scanned code
            console.log('Scanned:', code)
          }}
        />
      )}
    </div>
  )
}