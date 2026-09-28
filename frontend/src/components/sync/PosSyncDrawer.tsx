import { X, Upload, FileText, RefreshCw, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { useUIStore } from '@/stores'
import { api } from '@/services/api'
import { formatDate, formatNumber } from '@/utils/formatters'
import { cn } from '@/utils/formatters'

interface PosSyncDrawerProps {
  onClose: () => void
}

export default function PosSyncDrawer({ onClose }: PosSyncDrawerProps) {
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const files = e.dataTransfer.files
    if (files.length > 0) handleFile(files[0])
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Hanya file CSV yang diperbolehkan')
      return
    }
    setError(null)
    setUploading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/sync/pos-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Gagal mengupload file')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
        <h2 id="drawer-title" className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Upload className="h-5 w-5 text-primary-600" />
          Upload CSV Kasir
        </h2>
        <button onClick={onClose} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100" aria-label="Tutup">
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {!result && !uploading ? (
          <div
            className={cn(
              'border-2 border-dashed rounded-xl p-8 text-center transition-colors',
              dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />

            <FileText className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900">Seret & Lepas File CSV</h3>
            <p className="text-gray-500 mt-1">Atau klik untuk memilih file</p>
            <p className="text-sm text-gray-400 mt-2">Format: Moka POS, Majoo, Olsera</p>

            {error && (
              <div className="mt-4 p-3 bg-danger-50 border border-danger-200 rounded-lg text-danger-700 text-sm flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}
          </div>
        ) : null}

        {uploading && (
          <div className="space-y-4 text-center">
            <RefreshCw className="h-16 w-16 animate-spin mx-auto text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Memproses CSV...</h3>
            <p className="text-gray-600">Memindai hash duplikasi & menghitung pengurangan stok bahan baku</p>
            <div className="w-full max-w-md mx-auto">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-600 animate-pulse" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className={cn('p-4 rounded-lg border flex items-center gap-3', result.new_inserted > 0 ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200')}>
              <div className={cn('p-3 rounded-full', result.new_inserted > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600')}>
                {result.new_inserted > 0 ? <CheckCircle className="h-6 w-6" /> : <FileText className="h-6 w-6" />}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">{result.new_inserted > 0 ? 'Sinkronisasi Berhasil' : 'Tidak Ada Data Baru'}</p>
                <p className="text-sm text-gray-600">
                  {result.new_inserted} transaksi baru ditambahkan, {result.duplicates_skipped} duplikat dilewati
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="card p-3 text-center">
                <p className="text-2xl font-bold text-green-600">{result.new_inserted}</p>
                <p className="text-xs text-gray-500">Transaksi Baru</p>
              </div>
              <div className="card p-3 text-center">
                <p className="text-2xl font-bold text-gray-500">{result.duplicates_skipped}</p>
                <p className="text-xs text-gray-500">Duplikat Dilewati</p>
              </div>
              <div className="card p-3 text-center">
                <p className="text-2xl font-bold text-blue-600">{result.reconciled_stock_items}</p>
                <p className="text-xs text-gray-500">Bahan Disinkronkan</p>
              </div>
            </div>

            {result.date_range_start && result.date_range_end && (
              <div className="card p-3 bg-gray-50">
                <p className="text-sm text-gray-600">
                  Periode data: <span className="font-medium">{formatDate(result.date_range_start)}</span> - <span className="font-medium">{formatDate(result.date_range_end)}</span>
                </p>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
              <button onClick={() => { setResult(null); setError(null) }} className="btn-secondary">Upload Lagi</button>
              <button onClick={onClose} className="btn-primary">Selesai</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}