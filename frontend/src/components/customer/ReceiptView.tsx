import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { formatRupiah } from '@/utils/formatters'
import { Printer, Share2 } from 'lucide-react'

interface ReceiptViewProps {
  transactionId: number
}

export default function ReceiptView({ transactionId }: ReceiptViewProps) {
  const { data: receipt, isLoading } = useQuery({
    queryKey: ['receipt', transactionId],
    queryFn: async () => {
      const res = await api.get(`/sales/${transactionId}/receipt`)
      return res.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Memuat struk...</div>
  }

  if (!receipt) {
    return <div className="text-center py-8 text-gray-500">Struk tidak ditemukan</div>
  }

  return (
    <div className="max-w-sm mx-auto">
      <div className="card font-mono text-sm">
        <div className="text-center border-b pb-3 mb-3">
          <h2 className="text-lg font-bold">LEUIT</h2>
          <p className="text-gray-600">Lumbung Digital & Prediksi Stok Kafe</p>
        </div>
        
        <div className="space-y-1 mb-3">
          <div className="flex justify-between">
            <span>No.</span>
            <span>{receipt.transaction_id}</span>
          </div>
          <div className="flex justify-between">
            <span>Tanggal</span>
            <span>{new Date(receipt.date).toLocaleDateString('id-ID')}</span>
          </div>
        </div>
        
        <div className="border-t pt-3 space-y-1">
          <div className="flex justify-between font-bold">
            <span>Item</span>
            <span>Harga</span>
          </div>
          {receipt.items?.map((item: any) => (
            <div key={item.id} className="flex justify-between">
              <span>{item.name} x{item.quantity}</span>
              <span>{formatRupiah(item.subtotal)}</span>
            </div>
          ))}
        </div>
        
        <div className="border-t mt-3 pt-3">
          <div className="flex justify-between font-bold text-lg">
            <span>Total</span>
            <span>{formatRupiah(receipt.total)}</span>
          </div>
        </div>
        
        <div className="text-center mt-4 pt-3 border-t text-gray-500">
          <p>Terima kasih atas kunjungan Anda!</p>
        </div>
      </div>
      
      <div className="flex gap-2 mt-4">
        <button
          onClick={() => window.print()}
          className="btn-secondary flex-1 flex items-center justify-center gap-1"
        >
          <Printer className="h-4 w-4" />
          Cetak
        </button>
        <button
          onClick={() => {
            const text = `Struk LEUIT\nTotal: ${formatRupiah(receipt.total)}\nTerima kasih!`
            navigator.clipboard.writeText(text)
          }}
          className="btn-secondary flex-1 flex items-center justify-center gap-1"
        >
          <Share2 className="h-4 w-4" />
          Share
        </button>
      </div>
    </div>
  )
}
