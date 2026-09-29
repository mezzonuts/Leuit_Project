import { Eye, Download, FileText, Clock } from 'lucide-react'
import { formatDate, formatDateTime, formatNumber } from '@/utils/formatters'

interface SyncHistoryTableProps {
  history: any[]
}

export default function SyncHistoryTable({ history }: SyncHistoryTableProps) {
  if (history.length === 0) {
    return (
      <div className="p-8 text-center">
        <Clock className="h-12 w-12 mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500">Belum ada riwayat sinkronisasi</p>
        <p className="text-sm text-gray-400 mt-1">Upload CSV pertama untuk memulai</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full" role="table">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal Upload</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Baris</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Baru</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Duplikat</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan Sync</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Periode Data</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {history.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm text-gray-900">{formatDateTime(item.uploaded_at)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <span className="text-sm font-medium text-gray-900 truncate max-w-xs">{item.file_name}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-right text-sm text-gray-600">{formatNumber(item.total_rows_read)}</td>
              <td className="px-4 py-3 text-right text-sm font-medium text-green-600">{formatNumber(item.new_rows_inserted)}</td>
              <td className="px-4 py-3 text-right text-sm text-gray-500">{formatNumber(item.duplicate_rows_skipped)}</td>
              <td className="px-4 py-3 text-right text-sm font-medium text-blue-600">{formatNumber(item.reconciled_stock_items)}</td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {formatDate(item.date_range_start)} - {formatDate(item.date_range_end)}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex items-center justify-end gap-1">
                  <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700" title="Detail">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700" title="Ekspor Detail">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}