import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Save, Loader2, Package } from 'lucide-react'
import { useUIStore } from '@/stores'
import { api } from '@/services/api'
import { cn, formatNumber } from '@/utils/formatters'

const opnameSchema = z.object({
  quantity: z.number().min(0, 'Jumlah tidak boleh negatif'),
})

type OpnameFormSchema = z.infer<typeof opnameSchema>

interface StockOpnameModalProps {
  onClose: () => void
}

export default function StockOpnameModal({ onClose }: StockOpnameModalProps) {
  const { drawerData } = useUIStore()
  const ingredient = drawerData?.ingredient

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<OpnameFormSchema>({
    resolver: zodResolver(opnameSchema),
    defaultValues: { quantity: 0 },
  })

  const onSubmit = async (data: OpnameFormSchema) => {
    if (!ingredient) return
    await api.post(`/inventory/${ingredient.id}/stock-opname`, { quantity: data.quantity })
    onClose()
  }

  if (!ingredient) return null

  const difference = (ingredient.current_stock || 0) - (0) // Will be calculated after user input

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" role="dialog" aria-modal="true">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Package className="h-5 w-5 text-primary-600" />
            Stock Opname
          </h2>
          <button onClick={onClose} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100" aria-label="Tutup">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-4 space-y-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm font-medium text-gray-900">{ingredient.name}</p>
            <p className="text-sm text-gray-500">{ingredient.unit} • Stok sistem: <span className="font-medium">{formatNumber(ingredient.current_stock)}</span> {ingredient.unit}</p>
          </div>

          <div>
            <label className="label">Jumlah Stok Fisik (Hasil Hitung) *</label>
            <input
              type="number"
              {...register('quantity', { valueAsNumber: true })}
              placeholder="Masukkan jumlah stok fisik"
              className={cn('input', errors.quantity && 'border-danger-500')}
              autoFocus
            />
            {errors.quantity && <p className="mt-1 text-xs text-danger-600">{errors.quantity.message}</p>}
          </div>

          <div className="bg-gray-50 rounded-lg p-3 text-sm">
            <p className="text-gray-600">Stok sistem: <span className="font-medium">{formatNumber(ingredient.current_stock)}</span> {ingredient.unit}</p>
            <p className="text-gray-600">Stok fisik: <span className="font-medium">{watch('quantity') || 0}</span> {ingredient.unit}</p>
            <p className="font-medium text-gray-900">Selisih: <span className={difference > 0 ? 'text-danger-600' : difference < 0 ? 'text-green-600' : 'text-gray-600'}>{difference > 0 ? '+' : ''}{difference} {ingredient.unit}</span></p>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button type="button" onClick={onClose} className="btn-secondary">Batal</button>
            <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
              {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Simpan Penyesuaian
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}