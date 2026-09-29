import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useRef, useCallback } from 'react'
import { Upload, FileText, RefreshCw, Clock, CheckCircle } from 'lucide-react'
import { api } from '@/services/api'
import { cn } from '@/utils/formatters'
import { useUIStore } from '@/stores'
import PosSyncDrawer from './PosSyncDrawer'
import SyncResultSummary from './SyncResultSummary'
import SyncHistoryTable from './SyncHistoryTable'

export default function Sync() {
  const queryClient = useQueryClient()
  const { openDrawer, closeDrawer, activeDrawer } = useUIStore()
  const [dragActive, setDragActive] = useState(false)
  const [lastSyncResult, setLastSyncResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: history } = useQuery({
    queryKey: ['sync-history'],
    queryFn: () => api.get('/sync/history').then(res => res.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/sync/pos-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    onSuccess: (res) => {
      setLastSyncResult(res.data)
      queryClient.invalidateQueries({ queryKey: ['sync-history'] })
      queryClient.invalidateQueries({ queryKey: ['ingredients'] })
      queryClient.invalidateQueries({ queryKey: ['valuation'] })
      queryClient.invalidateQueries({ queryKey: ['stock-health'] })
      queryClient.invalidateQueries({ queryKey: ['critical-alerts'] })
      queryClient.invalidateQueries({ queryKey: ['usage-trend'] })
    },
  })

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    if (!file.name.endsWith('.csv')) {
      alert('Hanya file CSV yang diperbolehkan')
      return
    }
    uploadMutation.mutate(file)
  }

  const handleOpenDrawer = () => {
    openDrawer('sync')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sinkronisasi POS</h1>
          <p className="text-gray-500 mt-1">Upload CSV kasir berkala dengan deduplikasi otomatis & rekonsiliasi stok</p>
        </div>
        <button onClick={handleOpenDrawer} className="btn-primary flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Upload CSV Baru
        </button>
      </div>

      {/* Upload Zone */}
      <div
        className={cn(
          'card p-8 text-center border-2 border-dashed transition-colors',
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
        aria-label="Area upload CSV kasir"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
          aria-hidden="true"
        />

        {uploadMutation.isPending ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3">
              <RefreshCw className="h-10 w-10 animate-spin text-primary-600" />
              <div className="text-left">
                <p className="text-lg font-semibold text-gray-900">Memproses CSV...</p>
                <p className="text-gray-600">Sedang memindai hash duplikasi & menghitung pengurangan stok</p>
              </div>
            </div>
            <div className="w-full max-w-md mx-auto">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary-600 animate-pulse" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        ) : lastSyncResult ? (
          <SyncResultSummary result={lastSyncResult} onClose={() => setLastSyncResult(null)} />
        ) : (
          <div className="space-y-4">
            <FileText className="h-16 w-16 mx-auto text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900">Seret & Lepas File CSV Kasir</h3>
            <p className="text-gray-500">Atau klik untuk memilih file</p>
            <p className="text-sm text-gray-400">Format didukung: Moka POS, Majoo, Olsera (CSV ekspor standar)</p>
            <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-400">
              <span className="px-2 py-1 bg-gray-100 rounded">Order_ID</span>
              <span className="px-2 py-1 bg-gray-100 rounded">Timestamp</span>
              <span className="px-2 py-1 bg-gray-100 rounded">Item_Name</span>
              <span className="px-2 py-1 bg-gray-100 rounded">Qty</span>
              <span className="px-2 py-1 bg-gray-100 rounded">Menu_ID</span>
            </div>
          </div>
        )}
      </div>

      {/* Last Result Summary */}
      {lastSyncResult && !uploadMutation.isPending && (
        <div className="card p-4 bg-green-50 border-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <div>
                <p className="font-medium text-green-800">Sinkronisasi Berhasil</p>
                <p className="text-sm text-green-700">
                  {lastSyncResult.new_inserted} transaksi baru, {lastSyncResult.duplicates_skipped} duplikat dilewati
                </p>
              </div>
            </div>
            <button onClick={() => setLastSyncResult(null)} className="btn-ghost text-sm">
              Tutup
            </button>
          </div>
        </div>
      )}

      {/* History */}
      <div className="card">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Clock className="h-5 w-5 text-gray-600" />
            Riwayat Sinkronisasi
          </h2>
        </div>
        <SyncHistoryTable history={history?.items || []} />
      </div>

      {activeDrawer === 'sync' && <PosSyncDrawer onClose={closeDrawer} />}
    </div>
  )
}