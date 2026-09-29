import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Calculator, Package, AlertCircle, CheckCircle, Loader2, ArrowDown } from 'lucide-react'
import { api } from '@/services/api'
import { formatNumber, cn } from '@/utils/formatters'
import type { Ingredient } from '@/types'

const scalerSchema = z.object({
  menu_item_id: z.number().min(1, 'Pilih menu'),
  target_portions: z.number().min(1, 'Target porsi minimal 1'),
})

type ScalerFormSchema = z.infer<typeof scalerSchema>

interface RecipeScalerToolProps {
  ingredients: Ingredient[]
}

export default function RecipeScalerTool({ ingredients: _ingredients }: RecipeScalerToolProps) {
  const { register, watch, formState: { errors } } = useForm<ScalerFormSchema>({
    resolver: zodResolver(scalerSchema),
    defaultValues: {
      menu_item_id: 0,
      target_portions: 100,
    },
  })

  const { data: menus } = useQuery({
    queryKey: ['menus-for-scaler'],
    queryFn: () => api.get('/bom/menus').then(res => res.data),
  })

  const [result, setResult] = useState<any>(null)

  const scalerMutation = useMutation({
    mutationFn: (data: ScalerFormSchema) => api.post('/bom/scaler', data),
    onSuccess: (data) => {
      setResult(data)
    },
  })

  const selectedMenuId = watch('menu_item_id')
  const targetPortions = watch('target_portions')

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault()
    scalerMutation.mutate({ menu_item_id: selectedMenuId, target_portions: targetPortions })
  }

  const menuOptions = menus?.items || []

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calculator className="h-5 w-5 text-primary-600" />
          Simulasi Kebutuhan Bahan (Recipe Scaler)
        </h2>

        <form onSubmit={handleCalculate} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Menu *</label>
              <select
                {...register('menu_item_id')}
                className={cn('input', errors.menu_item_id && 'border-danger-500')}
              >
                <option value={0}>Pilih menu</option>
                {menuOptions.map((menu: any) => (
                  <option key={menu.id} value={menu.id}>{menu.name} (Rp {menu.sale_price?.toLocaleString('id-ID')})</option>
                ))}
              </select>
              {errors.menu_item_id && <p className="mt-1 text-xs text-danger-600">{errors.menu_item_id.message}</p>}
            </div>

            <div>
              <label className="label">Target Produksi (Porsi) *</label>
              <input
                type="number"
                {...register('target_portions', { valueAsNumber: true })}
                placeholder="Contoh: 100"
                className={cn('input', errors.target_portions && 'border-danger-500')}
              />
              {errors.target_portions && <p className="mt-1 text-xs text-danger-600">{errors.target_portions.message}</p>}
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-200">
            <button
              type="submit"
              disabled={scalerMutation.isPending || !selectedMenuId}
              className="btn-primary flex items-center gap-2"
            >
              {scalerMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calculator className="h-4 w-4" />}
              Hitung Kebutuhan
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <h3 className="text-lg font-semibold text-gray-900">
                Hasil Simulasi: {result.menu_name} × {result.target_portions} porsi
              </h3>
              <span className={`badge ${result.all_sufficient ? 'badge-success' : 'badge-danger'} flex items-center gap-1`}>
                {result.all_sufficient ? <CheckCircle className="h-3.5 w-3.5" /> : <AlertCircle className="h-3.5 w-3.5" />}
                {result.all_sufficient ? 'Semua Bahan Cukup' : 'Ada Bahan Kurang'}
              </span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full" role="table">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bahan Baku</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Resep / Porsi</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Kebutuhan</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Stok Saat Ini</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kekurangan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {result.items.map((item: any) => (
                  <tr key={item.ingredient_name} className={!item.is_sufficient ? 'bg-danger-50/50' : ''}>
                    <td className="px-4 py-3 font-medium text-gray-900">{item.ingredient_name}</td>
                    <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.per_portion)} {item.unit}</td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900">{formatNumber(item.total_needed)} {item.unit}</td>
                    <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.current_stock)} {item.unit}</td>
                    <td className="px-4 py-3">
                      <span className={`badge ${item.is_sufficient ? 'badge-success' : 'badge-danger'} flex items-center gap-1`}>
                        {item.is_sufficient ? <CheckCircle className="h-3.5 w-3.5" /> : <Package className="h-3.5 w-3.5" />}
                        {item.is_sufficient ? 'CUKUP' : 'KURANG'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {!item.is_sufficient && (
                        <div className="flex items-center gap-1 text-danger-600 font-medium">
                          <ArrowDown className="h-4 w-4" />
                          {formatNumber(item.deficit)} {item.unit}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {!result.all_sufficient && (
            <div className="p-4 bg-danger-50 border-t border-danger-200">
              <h4 className="font-medium text-danger-800 mb-2 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Bahan yang harus dibeli tambahan:
              </h4>
              <ul className="space-y-1 text-sm text-danger-700">
                {result.items.filter((i: any) => !i.is_sufficient).map((item: any) => (
                  <li key={item.ingredient_name} className="flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    <span>{item.ingredient_name}: beli tambahan {formatNumber(item.deficit)} {item.unit}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {scalerMutation.isError && (
        <div className="card p-4 bg-danger-50 border-danger-200">
          <p className="text-danger-700">Gagal menghitung: {(scalerMutation.error as any)?.response?.data?.detail || 'Error tidak diketahui'}</p>
        </div>
      )}
    </div>
  )
}