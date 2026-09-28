import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useEffect } from 'react'
import { X, Save, Loader2, Camera } from 'lucide-react'
import { useUIStore } from '@/stores'
import { api } from '@/services/api'
import { cn } from '@/utils/formatters'
import type { IngredientFormData } from '@/types'

const ingredientSchema = z.object({
  barcode_sku: z.string().optional(),
  name: z.string().min(1, 'Nama bahan wajib diisi'),
  unit: z.enum(['ml', 'gram', 'pcs']),
  cost_per_unit: z.number().min(0, 'HPP harus >= 0'),
  shelf_life_days: z.number().min(1, 'Masa simpan minimal 1 hari'),
  current_stock: z.number().min(0, 'Stok tidak boleh negatif'),
  min_stock_threshold: z.number().min(0, 'Threshold tidak boleh negatif'),
  lead_time_days: z.number().min(0, 'Lead time tidak boleh negatif').default(1),
})

type IngredientFormSchema = z.infer<typeof ingredientSchema>

interface IngredientDrawerProps {
  onClose: () => void
}

export default function IngredientDrawer({ onClose }: IngredientDrawerProps) {
  const { drawerData } = useUIStore()
  const isEdit = drawerData?.mode === 'edit'
  const isOpname = drawerData?.mode === 'opname'
  const ingredient = drawerData?.ingredient

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<IngredientFormSchema>({
    resolver: zodResolver(ingredientSchema),
    defaultValues: {
      barcode_sku: '',
      name: '',
      unit: 'gram',
      cost_per_unit: 0,
      shelf_life_days: 7,
      current_stock: 0,
      min_stock_threshold: 0,
      lead_time_days: 1,
    },
  })

  useEffect(() => {
    if (ingredient) {
      reset({
        barcode_sku: ingredient.barcode_sku || '',
        name: ingredient.name,
        unit: ingredient.unit,
        cost_per_unit: ingredient.cost_per_unit,
        shelf_life_days: ingredient.shelf_life_days,
        current_stock: isOpname ? 0 : ingredient.current_stock,
        min_stock_threshold: ingredient.min_stock_threshold,
        lead_time_days: ingredient.lead_time_days || 1,
      })
    } else {
      reset()
    }
  }, [ingredient, isOpname, reset])

  const onSubmit = async (data: IngredientFormSchema) => {
    if (isOpname) {
      await api.post(`/inventory/${ingredient.id}/stock-opname`, { quantity: data.current_stock })
    } else if (isEdit) {
      await api.put(`/inventory/${ingredient.id}`, data)
    } else {
      await api.post('/inventory', data)
    }
    onClose()
  }

  return (
    <div className="flex flex-col h-full bg-white" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
        <h2 id="drawer-title" className="text-lg font-semibold text-gray-900">
          {isOpname ? 'Stock Opname' : isEdit ? 'Edit Bahan' : 'Tambah Bahan Baru'}
        </h2>
        <button
          onClick={onClose}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100"
          aria-label="Tutup"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Nama Bahan *</label>
            <input
              {...register('name')}
              placeholder="Contoh: Susu Segar Lembang 1L"
              className={cn('input', errors.name && 'border-danger-500')}
            />
            {errors.name && <p className="mt-1 text-xs text-danger-600">{errors.name.message}</p>}
          </div>

          <div>
            <label className="label">Barcode / SKU</label>
            <div className="flex gap-2">
              <input
                {...register('barcode_sku')}
                placeholder="Scan atau ketik manual"
                className="input flex-1"
              />
              <button
                type="button"
                onClick={() => {}}
                className="btn-secondary flex items-center gap-1"
              >
                <Camera className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div>
            <label className="label">Satuan *</label>
            <select {...register('unit')} className="input">
              <option value="ml">ml</option>
              <option value="gram">gram</option>
              <option value="pcs">pcs</option>
            </select>
          </div>

          <div>
            <label className="label">HPP per Satuan (Rp) *</label>
            <input
              type="number"
              {...register('cost_per_unit', { valueAsNumber: true })}
              placeholder="Contoh: 12000"
              className={cn('input', errors.cost_per_unit && 'border-danger-500')}
            />
            {errors.cost_per_unit && <p className="mt-1 text-xs text-danger-600">{errors.cost_per_unit.message}</p>}
          </div>

          <div>
            <label className="label">Masa Simpan (Hari) *</label>
            <input
              type="number"
              {...register('shelf_life_days', { valueAsNumber: true })}
              placeholder="Contoh: 7"
              className={cn('input', errors.shelf_life_days && 'border-danger-500')}
            />
            {errors.shelf_life_days && <p className="mt-1 text-xs text-danger-600">{errors.shelf_life_days.message}</p>}
          </div>

          <div>
            <label className="label">Lead Time (Hari)</label>
            <input
              type="number"
              {...register('lead_time_days', { valueAsNumber: true })}
              placeholder="Contoh: 1"
              className="input"
            />
          </div>

          {!isOpname && (
            <>
              <div>
                <label className="label">Stok Saat Ini *</label>
                <input
                  type="number"
                  {...register('current_stock', { valueAsNumber: true })}
                  placeholder="Contoh: 50"
                  className={cn('input', errors.current_stock && 'border-danger-500')}
                />
                {errors.current_stock && <p className="mt-1 text-xs text-danger-600">{errors.current_stock.message}</p>}
              </div>

              <div>
                <label className="label">Threshold Minimum *</label>
                <input
                  type="number"
                  {...register('min_stock_threshold', { valueAsNumber: true })}
                  placeholder="Contoh: 10"
                  className={cn('input', errors.min_stock_threshold && 'border-danger-500')}
                />
                {errors.min_stock_threshold && <p className="mt-1 text-xs text-danger-600">{errors.min_stock_threshold.message}</p>}
              </div>
            </>
          )}

          {isOpname && (
            <div className="sm:col-span-2">
              <label className="label">Penyesuaian Stok (Jumlah Fisik Baru) *</label>
              <input
                type="number"
                {...register('current_stock', { valueAsNumber: true })}
                placeholder="Masukkan jumlah stok fisik yang dihitung"
                className={cn('input', errors.current_stock && 'border-danger-500')}
              />
              {errors.current_stock && <p className="mt-1 text-xs text-danger-600">{errors.current_stock.message}</p>}
              <p className="mt-1 text-xs text-gray-500">Sistem akan menghitung selisih otomatis dari stok sistem.</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 mt-6">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary"
          >
            Batal
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary flex items-center gap-2"
          >
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            {isOpname ? 'Simpan Penyesuaian' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  )
}