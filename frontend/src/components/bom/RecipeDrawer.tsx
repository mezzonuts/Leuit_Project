import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useEffect } from 'react'
import { X, Save, Loader2, Plus, Trash2, Minus } from 'lucide-react'
import { useUIStore } from '@/stores'
import { api } from '@/services/api'
import { cn, formatRupiah } from '@/utils/formatters'
import type { Ingredient, MenuItem } from '@/types'

const recipeItemSchema = z.object({
  ingredient_id: z.number().min(1, 'Pilih bahan baku'),
  quantity_required: z.number().min(0.001, 'Jumlah harus > 0'),
})

const menuSchema = z.object({
  name: z.string().min(1, 'Nama menu wajib diisi'),
  sale_price: z.number().min(0, 'Harga jual tidak boleh negatif'),
  pos_item_id: z.string().optional(),
  recipes: z.array(recipeItemSchema).min(1, 'Minimal 1 bahan dalam resep'),
})

type MenuFormSchema = z.infer<typeof menuSchema>

interface RecipeDrawerProps {
  onClose: () => void
}

export default function RecipeDrawer({ onClose }: RecipeDrawerProps) {
  const { drawerData } = useUIStore()
  const isEdit = drawerData?.mode === 'edit'
  const menu = drawerData?.menu
  const ingredients = drawerData?.ingredients || []

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<MenuFormSchema>({
    resolver: zodResolver(menuSchema),
    defaultValues: {
      name: '',
      sale_price: 0,
      pos_item_id: '',
      recipes: [{ ingredient_id: 0, quantity_required: 0 }],
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'recipes' })
  const recipes = watch('recipes')

  useEffect(() => {
    if (menu) {
      reset({
        name: menu.name,
        sale_price: menu.sale_price,
        pos_item_id: menu.pos_item_id || '',
        recipes: menu.recipes?.map((r: any) => ({
          ingredient_id: r.ingredient_id,
          quantity_required: r.quantity_required,
        })) || [{ ingredient_id: 0, quantity_required: 0 }],
      })
    } else {
      reset({
        name: '',
        sale_price: 0,
        pos_item_id: '',
        recipes: [{ ingredient_id: 0, quantity_required: 0 }],
      })
    }
  }, [menu, reset])

  const calculateTotalCost = () => {
    return recipes.reduce((total, recipe) => {
      const ingredient = ingredients.find((i: Ingredient) => i.id === recipe.ingredient_id)
      if (ingredient) {
        return total + ingredient.cost_per_unit * recipe.quantity_required
      }
      return total
    }, 0)
  }

  const totalCost = calculateTotalCost()

  const onSubmit = async (data: MenuFormSchema) => {
    const payload = {
      name: data.name,
      sale_price: data.sale_price,
      pos_item_id: data.pos_item_id,
      recipes: data.recipes,
    }

    if (isEdit) {
      await api.put(`/bom/menus/${menu.id}`, payload)
    } else {
      await api.post('/bom/menus', payload)
    }
    onClose()
  }

  return (
    <div className="flex flex-col h-full bg-white" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
        <h2 id="drawer-title" className="text-lg font-semibold text-gray-900">
          {isEdit ? 'Edit Menu & Resep' : 'Tambah Menu Baru'}
        </h2>
        <button onClick={onClose} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100" aria-label="Tutup">
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Menu Info */}
        <div className="card p-4 space-y-4">
          <h3 className="font-semibold text-gray-900">Informasi Menu</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Nama Menu *</label>
              <input
                {...register('name')}
                placeholder="Contoh: Es Kopi Susu Aren"
                className={cn('input', errors.name && 'border-danger-500')}
              />
              {errors.name && <p className="mt-1 text-xs text-danger-600">{errors.name.message}</p>}
            </div>
            <div>
              <label className="label">Harga Jual (Rp) *</label>
              <input
                type="number"
                {...register('sale_price', { valueAsNumber: true })}
                placeholder="Contoh: 25000"
                className={cn('input', errors.sale_price && 'border-danger-500')}
              />
              {errors.sale_price && <p className="mt-1 text-xs text-danger-600">{errors.sale_price.message}</p>}
            </div>
            <div>
              <label className="label">POS Item ID</label>
              <input
                {...register('pos_item_id')}
                placeholder="ID dari sistem kasir (opsional)"
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Recipe Items */}
        <div className="card p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Komposisi Resep (BOM)</h3>
            <button
              type="button"
              onClick={() => append({ ingredient_id: 0, quantity_required: 0 })}
              className="btn-secondary text-sm flex items-center gap-1"
            >
              <Plus className="h-4 w-4" />
              Tambah Bahan
            </button>
          </div>

          {errors.recipes && <p className="text-xs text-danger-600">{errors.recipes.message}</p>}

          <div className="space-y-3">
            {fields.map((field, index) => (
              <div key={field.id} className="flex flex-col sm:flex-row gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 sm:flex-[2]">
                  <label className="label">Bahan Baku *</label>
                  <select
                    {...register(`recipes.${index}.ingredient_id`, { valueAsNumber: true })}
                    className={cn('input', errors.recipes?.[index]?.ingredient_id && 'border-danger-500')}
                  >
                    <option value={0}>Pilih bahan baku</option>
                    {ingredients.map((ing: Ingredient) => (
                      <option key={ing.id} value={ing.id}>
                        {ing.name} ({ing.unit}) - {formatRupiah(ing.cost_per_unit)}/{ing.unit}
                      </option>
                    ))}
                  </select>
                  {errors.recipes?.[index]?.ingredient_id && (
                    <p className="mt-1 text-xs text-danger-600">{errors.recipes[index].ingredient_id.message}</p>
                  )}
                </div>

                <div className="flex-1 sm:flex-[1]">
                  <label className="label">Jumlah per Porsi *</label>
                  <input
                    type="number"
                    step="0.001"
                    {...register(`recipes.${index}.quantity_required`, { valueAsNumber: true })}
                    placeholder="Contoh: 120"
                    className={cn('input', errors.recipes?.[index]?.quantity_required && 'border-danger-500')}
                  />
                  {errors.recipes?.[index]?.quantity_required && (
                    <p className="mt-1 text-xs text-danger-600">{errors.recipes[index].quantity_required.message}</p>
                  )}
                </div>

                <div className="flex items-end sm:w-12">
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    disabled={fields.length === 1}
                    className="p-2 rounded-lg text-gray-500 hover:bg-gray-200 hover:text-danger-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Hapus bahan"
                  >
                    <Minus className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Cost Summary */}
          <div className="pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-700">Total HPP per Porsi:</span>
              <span className="text-xl font-bold text-primary-600">{formatRupiah(totalCost)}</span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Margin: {menu?.sale_price ? formatRupiah(menu.sale_price - totalCost) : '-'} ({(menu?.sale_price && totalCost > 0) ? (((menu.sale_price - totalCost) / menu.sale_price) * 100).toFixed(1) : 0}%)
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button type="button" onClick={onClose} className="btn-secondary">Batal</button>
          <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            {isEdit ? 'Update Menu' : 'Buat Menu'}
          </button>
        </div>
      </form>
    </div>
  )
}