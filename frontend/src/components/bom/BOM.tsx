import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, ChefHat, Calculator } from 'lucide-react'
import { api } from '@/services/api'
import { useUIStore } from '@/stores'
import RecipeDrawer from './RecipeDrawer'
import RecipeScalerTool from './RecipeScalerTool'

export default function BOM() {
  const { openDrawer, closeDrawer, activeDrawer } = useUIStore()
  const [activeTab, setActiveTab] = useState<'menus' | 'scaler'>('menus')

  const { data: menus } = useQuery({
    queryKey: ['menus'],
    queryFn: () => api.get('/bom/menus').then(res => res.data),
  })

  const { data: ingredients } = useQuery({
    queryKey: ['ingredients-for-bom'],
    queryFn: () => api.get('/inventory', { params: { active_only: true } }).then(res => res.data),
  })

  const handleNewMenu = () => {
    openDrawer('recipe', { mode: 'create', ingredients: ingredients?.items || [] })
  }

  const handleEditMenu = (menu: any) => {
    openDrawer('recipe', { mode: 'edit', menu, ingredients: ingredients?.items || [] })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resep & Menu</h1>
          <p className="text-gray-500 mt-1">Bill of Materials & Recipe Scaler untuk simulasi porsi</p>
        </div>
        {activeTab === 'menus' && (
          <button onClick={handleNewMenu} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Tambah Menu
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="flex gap-4 px-4" aria-label="Tab navigasi">
            <button
              onClick={() => setActiveTab('menus')}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'menus'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <ChefHat className="h-4 w-4 inline mr-1" />
              Daftar Menu & Resep
            </button>
            <button
              onClick={() => setActiveTab('scaler')}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'scaler'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Calculator className="h-4 w-4 inline mr-1" />
              Recipe Scaler
            </button>
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'menus' ? (
            <MenuList menus={menus?.items || []} onEdit={handleEditMenu} onNew={handleNewMenu} />
          ) : (
            <RecipeScalerTool ingredients={ingredients?.items || []} />
          )}
        </div>
      </div>

      {activeDrawer === 'recipe' && <RecipeDrawer onClose={closeDrawer} />}
    </div>
  )
}

function MenuList({ menus, onEdit, onNew }: { menus: any[]; onEdit: (menu: any) => void; onNew: () => void }) {
  if (menus.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Belum ada menu. Buat menu pertama untuk memulai.</p>
        <button onClick={onNew} className="btn-primary flex items-center gap-2 mx-auto">
          <Plus className="h-4 w-4" />
          Tambah Menu
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {menus.map((menu) => (
        <div key={menu.id} className="card-hover p-4 border border-gray-200 rounded-lg">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <ChefHat className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{menu.name}</h3>
                <p className="text-sm text-gray-500">Harga jual: Rp {menu.sale_price?.toLocaleString('id-ID') || '-'}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onEdit(menu)}
                className="btn-secondary text-sm"
              >
                Edit Resep
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}