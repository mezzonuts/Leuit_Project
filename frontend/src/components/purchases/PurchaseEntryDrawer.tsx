import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useEffect } from 'react'
import { X, Save, Loader2, Calendar } from 'lucide-react'
import { useUIStore } from '@/stores'
import { api } from '@/services/api'
import { cn, formatRupiah } from '@/utils/formatters'
import type { Supplier } from '@/types'

const purchaseSchema = z.object({
  purchase_date: z.string().min(1, 'Tanggal wajib diisi'),
  ingredient_id: z.number().min(1, 'Pilih bahan baku'),
  supplier_id: z.number().min(1, 'Pilih suplier'),
  quantity: z.number().min(0.001, 'Jumlah harus > 0'),
  total_cost: z.number().min(0, 'Total biaya tidak boleh negatif'),
  payment_method: z.enum(['CASH', 'CREDIT']),
  payment_status: z.enum(['PAID', 'UNPAID']).default('PAID'),
  due_date: z.string().optional(),
})

type PurchaseFormSchema = z.infer<typeof purchaseSchema>

interface PurchaseEntryDrawerProps {
  onClose: () => void
}

export default function PurchaseEntryDrawer({ onClose }: PurchaseEntryDrawerProps) {
  const { drawerData } = useUIStore()
  const suppliers = drawerData?.suppliers || []
  const ingredients = drawerData?.ingredients || []

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<PurchaseFormSchema>({
    resolver: zodResolver(purchaseSchema),
    defaultValues: {
      purchase_date: new Date().toISOString().split('T')[0],
      ingredient_id: 0,
      supplier_id: 0,
      quantity: 1,
      total_cost: 0,
      payment_method: 'CASH',
      payment_status: 'PAID',
      due_date: '',
    },
  })

  const paymentMethod = watch('payment_method')

  useEffect(() => {
    if (paymentMethod === 'CREDIT') {
      setValue('payment_status', 'UNPAID')
    } else {
      setValue('payment_status', 'PAID')
      setValue('due_date', '')
    }
  }, [paymentMethod, setValue])

  const onSubmit = async (data: PurchaseFormSchema) => {
    await api.post('/purchases', data)
    onClose()
  }

  return (
    <div className="flex flex-col h-full bg-white" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
        <h2 id="drawer-title" className="text-lg font-semibold text-gray-900">Catat Pembelian Baru</h2>
        <button onClick={onClose} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100" aria-label="Tutup">
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Tanggal Pembelian *</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="date"
                {...register('purchase_date')}
                className={cn('input pl-10', errors.purchase_date && 'border-danger-500')}
              />
            </div>
            {errors.purchase_date && <p className="mt-1 text-xs text-danger-600">{errors.purchase_date.message}</p>}
          </div>

          <div>
            <label className="label">Bahan Baku *</label>
            <select
              {...register('ingredient_id', { valueAsNumber: true })}
              className={cn('input', errors.ingredient_id && 'border-danger-500')}
            >
              <option value={0}>Pilih bahan baku</option>
              {ingredients.map((ing: any) => (
                <option key={ing.id} value={ing.id}>{ing.name} ({ing.unit}) - {formatRupiah(ing.cost_per_unit)}/{ing.unit}</option>
              ))}
            </select>
            {errors.ingredient_id && <p className="mt-1 text-xs text-danger-600">{errors.ingredient_id.message}</p>}
          </div>

          <div>
            <label className="label">Suplier *</label>
            <select
              {...register('supplier_id', { valueAsNumber: true })}
              className={cn('input', errors.supplier_id && 'border-danger-500')}
            >
              <option value={0}>Pilih suplier</option>
              {suppliers.map((s: Supplier) => (
                <option key={s.id} value={s.id}>{s.name} - {s.payment_terms_days > 0 ? `Tempo ${s.payment_terms_days} hari` : 'Cash'}</option>
              ))}
            </select>
            {errors.supplier_id && <p className="mt-1 text-xs text-danger-600">{errors.supplier_id.message}</p>}
          </div>

          <div>
            <label className="label">Jumlah *</label>
            <input
              type="number"
              step="0.001"
              {...register('quantity', { valueAsNumber: true })}
              placeholder="Contoh: 50"
              className={cn('input', errors.quantity && 'border-danger-500')}
            />
            {errors.quantity && <p className="mt-1 text-xs text-danger-600">{errors.quantity.message}</p>}
          </div>

          <div>
            <label className="label">Total Biaya (Rp) *</label>
            <input
              type="number"
              {...register('total_cost', { valueAsNumber: true })}
              placeholder="Contoh: 500000"
              className={cn('input', errors.total_cost && 'border-danger-500')}
            />
            {errors.total_cost && <p className="mt-1 text-xs text-danger-600">{errors.total_cost.message}</p>}
          </div>

          <div>
            <label className="label">Metode Pembayaran *</label>
            <select {...register('payment_method')} className={cn('input', errors.payment_method && 'border-danger-500')}>
              <option value="CASH">Cash (Tunai)</option>
              <option value="CREDIT">Kredit / Tempo</option>
            </select>
            {errors.payment_method && <p className="mt-1 text-xs text-danger-600">{errors.payment_method.message}</p>}
          </div>

          {paymentMethod === 'CREDIT' && (
            <>
              <div>
                <label className="label">Status Pembayaran</label>
                <select {...register('payment_status')} className="input">
                  <option value="UNPAID">Belum Bayar</option>
                  <option value="PAID">Lunas</option>
                </select>
              </div>

              <div>
                <label className="label">Jatuh Tempo *</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="date"
                    {...register('due_date')}
                    className={cn('input pl-10', errors.due_date && 'border-danger-500')}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
                {errors.due_date && <p className="mt-1 text-xs text-danger-600">{errors.due_date.message}</p>}
              </div>
            </>
          )}

          {paymentMethod === 'CASH' && (
            <div className="sm:col-span-2">
              <p className="text-sm text-green-700 bg-green-50 p-3 rounded-lg">
                <span className="font-medium">Pembayaran Cash:</span> Stok akan bertambah langsung, tidak ada hutang suplier.
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button type="button" onClick={onClose} className="btn-secondary">Batal</button>
          <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Simpan Pembelian
          </button>
        </div>
      </form>
    </div>
  )
}