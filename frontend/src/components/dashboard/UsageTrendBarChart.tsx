import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { api } from '@/services/api'
import { Layers } from 'lucide-react'
import CategoryManager from '@/components/inventory/CategoryManager'

interface CategoryUsage {
  category_name: string
  category_color: string
  total_used: number
  ingredient_count: number
}

export default function UsageTrendBarChart() {
  const [groupBy, setGroupBy] = useState<'category' | 'daily'>('category')
  const [showCategoryManager, setShowCategoryManager] = useState(false)

  const { data: usageData, isLoading } = useQuery({
    queryKey: ['usage-trend-chart', groupBy],
    queryFn: () =>
      api.get('/inventory/usage-trend', {
        params: { days: 30, group_by: groupBy },
      }).then(res => res.data),
  })

  const chartData = Array.isArray(usageData)
    ? groupBy === 'category'
      ? usageData.map((item: CategoryUsage) => ({
          name: item.category_name,
          value: item.total_used,
          fill: item.category_color,
          count: item.ingredient_count,
        }))
      : usageData.map((item: any) => ({
          name: item.date?.substring(5, 10) || item.date,
          value: item.total_quantity_used,
          fill: '#16a34a',
        }))
    : []

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Tren Konsumsi 30 Hari</h2>
        <div className="flex items-center gap-2">
          <select
            value={groupBy}
            onChange={e => setGroupBy(e.target.value as 'category' | 'daily')}
            className="form-input text-sm w-auto"
            aria-label="Group by"
          >
            <option value="category">Per Kategori</option>
            <option value="daily">Per Hari</option>
          </select>
          <button
            onClick={() => setShowCategoryManager(true)}
            className="btn-secondary flex items-center gap-1 text-sm"
          >
            <Layers className="h-4 w-4" />
            Kategori
          </button>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip
              formatter={(value: number) => [value.toLocaleString('id-ID'), groupBy === 'category' ? 'Total Dipakai' : 'Kuantitas']}
            />
            {groupBy === 'category' && <Legend />}
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {groupBy === 'category' && chartData.map((entry, index) => (
                <Bar key={index} dataKey="value" fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {chartData.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>Tidak ada data konsumsi untuk periode ini</p>
        </div>
      )}

      {showCategoryManager && (
        <CategoryManager onClose={() => setShowCategoryManager(false)} />
      )}
    </div>
  )
}
