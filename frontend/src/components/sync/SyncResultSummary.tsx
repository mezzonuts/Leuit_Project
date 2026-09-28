import { X, CheckCircle, AlertCircle, RefreshCw, Package, Clock } from 'lucide-react'
import { formatDate, formatNumber } from '@/utils/formatters'
import { cn } from '@/utils/formatters'

interface SyncResultSummaryProps {
  result: any
  onClose: () => void
}

export default function SyncResultSummary({ result, onClose }: SyncResultSummaryProps) {
  const isSuccess = result.new_inserted > 0

  return (
    <div className={cn('p-4 rounded-lg border flex items-start gap-3', isSuccess ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200')}>
      <div className={cn('p-3 rounded-full flex-shrink-0', isSuccess ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600')}>
        {isSuccess ? <CheckCircle className="h-6 w-6" /> : <AlertCircle className="h-6 w-6" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="font-semibold text-gray-900">{isSuccess ? 'Sinkronisasi Berhasil' : 'Tidak Ada Data Baru'}</p>
          <button onClick={onClose} className="p-1 rounded hover:bg-gray-200 text-gray-500" aria-label="Tutup">
            <X className="h-5 w-5" />
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {result.new_inserted} transaksi baru ditambahkan, {result.duplicates_skipped} duplikat dilewati
        </p>

        <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t border-gray-200">
          <div className="text-center p-2 bg-white rounded-lg">
            <p className="text-2xl font-bold text-green-600">{result.new_inserted}</p>
            <p className="text-xs text-gray-500">Transaksi Baru</p>
          </div>
          <div className="text-center p-2 bg-white rounded-lg">
            <p className="text-2xl font-bold text-gray-500">{result.duplicates_skipped}</p>
            <p className="text-xs text-gray-500">Duplikat Dilewati</p>
          </div>
          <div className="text-center p-2 bg-white rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{result.reconciled_stock_items}</p>
            <p className="text-xs text-gray-500">Bahan Disinkronkan</p>
          </div>
        </div>

        {result.date_range_start && result.date_range_end && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm text-gray-600 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Periode: {formatDate(result.date_range_start)} - {formatDate(result.date_range_end)}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}