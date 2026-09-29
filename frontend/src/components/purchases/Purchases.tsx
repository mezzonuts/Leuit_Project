import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, CreditCard, DollarSign, Package, Truck } from 'lucide-react'
import { api } from '@/services/api'
import { formatRupiah, formatDate, formatNumber } from '@/utils/formatters'
import { useUIStore } from '@/stores'
import PurchaseEntryDrawer from './PurchaseEntryDrawer'
import RestockSheetView from './RestockSheetView'
import AccountsPayableAlert from './AccountsPayableAlert'

export default function Purchases() {
  const queryClient = useQueryClient()
  const { openDrawer, closeDrawer, activeDrawer } = useUIStore()
  const [activeTab, setActiveTab] = useState<'list' | 'restock' | 'payables'>('list')

  const { data: purchases } = useQuery({
    queryKey: ['purchases'],
    queryFn: () => api.get('/purchases').then(res => res.data),
  })

  const { data: suppliers } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => api.get('/purchases/suppliers').then(res => res.data),
  })

  const { data: payables } = useQuery({
    queryKey: ['payables'],
    queryFn: () => api.get('/purchases/payables').then(res => res.data),
  })

  const { data: restockSheet } = useQuery({
    queryKey: ['restock-sheet'],
    queryFn: () => api.get('/purchases/restock-sheet').then(res => res.data),
  })

  const payMutation = useMutation({
    mutationFn: (id: number) => api.post(`/purchases/${id}/pay`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchases'] })
      queryClient.invalidateQueries({ queryKey: ['payables'] })
    },
  })

  const handleNew = () => {
    openDrawer('purchase', { mode: 'create', suppliers: suppliers?.items || [] })
  }

  const items = purchases?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pembelian Stok</h1>
          <p className="text-gray-500 mt-1">Catat belanja Cash vs Kredit/Tempo + Hutang Suplier</p>
        </div>
        {activeTab === 'list' && (
          <button onClick={handleNew} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Catat Pembelian
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="flex gap-4 px-4 overflow-x-auto" aria-label="Tab navigasi">
            <button
              onClick={() => setActiveTab('list')}
              className={`py-3 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                activeTab === 'list'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Package className="h-4 w-4 inline mr-1" />
              Daftar Pembelian
            </button>
            <button
              onClick={() => setActiveTab('restock')}
              className={`py-3 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                activeTab === 'restock'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Truck className="h-4 w-4 inline mr-1" />
              Rekomendasi Restock
            </button>
            <button
              onClick={() => setActiveTab('payables')}
              className={`py-3 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                activeTab === 'payables'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <CreditCard className="h-4 w-4 inline mr-1" />
              Hutang Suplier ({(payables?.length || 0)})
            </button>
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'list' && <PurchaseList items={items} onPay={payMutation.mutate} />}
          {activeTab === 'restock' && <RestockSheetView data={restockSheet} />}
          {activeTab === 'payables' && <AccountsPayableAlert alerts={payables || []} />}
        </div>
      </div>

      {activeDrawer === 'purchase' && <PurchaseEntryDrawer onClose={closeDrawer} />}
    </div>
  )
}

function PurchaseList({ items, onPay }: { items: any[]; onPay: (id: number) => void }) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Belum ada catatan pembelian.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full" role="table">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Suplier</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Jumlah</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Biaya</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metode</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jatuh Tempo</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{formatDate(item.purchase_date)}</td>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.ingredient_name}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{item.supplier_name}</td>
                <td className="px-4 py-3 text-right text-sm text-gray-600">{formatNumber(item.quantity)}</td>
                <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">{formatRupiah(item.total_cost)}</td>
                <td className="px-4 py-3">
                  <span className={`badge ${item.payment_method === 'CASH' ? 'badge-success' : 'badge-info'}`}>
                    {item.payment_method}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`badge ${item.payment_status === 'PAID' ? 'badge-success' : 'badge-warning'}`}>
                    {item.payment_status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {item.due_date ? formatDate(item.due_date) : '-'}
                </td>
                <td className="px-4 py-3 text-right">
                  {item.payment_method === 'CREDIT' && item.payment_status === 'UNPAID' && (
                    <button
                      onClick={() => onPay(item.id)}
                      className="btn-secondary text-sm flex items-center gap-1"
                    >
                      <DollarSign className="h-3.5 w-3.5" />
                      Bayar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}