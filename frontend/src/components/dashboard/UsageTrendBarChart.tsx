import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { api } from '@/services/api'
import { formatDate } from '@/utils/formatters'

interface UsageDataPoint {
  date: string
  ingredient_id: number
  ingredient_name: string
  total_quantity_used: number
}

export default function UsageTrendBarChart() {
  const [selectedIngredientId, setSelectedIngredientId] = useState<number | null>(null)

  const { data: ingredients } = useQuery({
    queryKey: ['ingredients-for-chart'],
    queryFn: () => api.get('/inventory', { params: { active_only: true } }).then(res => res.data),
  })

  const { data: usageData, isLoading } = useQuery({
    queryKey: ['usage-trend', selectedIngredientId],
    queryFn: () =>
      api.get('/dashboard/usage-trend', {
        params: { ingredient_id: selectedIngredientId, days: 30 },
      }).then(res => res.data),
    enabled: !!ingredients?.items?.length,
  })

  const ingredientOptions = ingredients?.items || []

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </div>
    )
  }

  const chartData = usageData?.map((item: UsageDataPoint) => ({
    date: formatDate(item.date),
    quantity: item.total_quantity_used,
    name: item.ingredient_name,
  })) || []

  return (
    <div className="card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Tren Konsumsi 30 Hari</h2>
        <select
          value={selectedIngredientId || ''}
          onChange={e => setSelectedIngredientId(e.target.value ? Number(e.target.value) : null)}
          className="input w-auto max-w-xs"
        >
          <option value="">Semua Bahan</option>
          {ingredientOptions.map((ing: any) => (
            <option key={ing.id} value={ing.id}>
              {ing.name}
            </option>
          ))}
        </select>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis type="number" name="Kuantitas" tickFormatter={val => `${val}`} />
            <YAxis type="category" dataKey="date" width={80} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number) => [value.toLocaleString('id-ID'), 'Terpakai']}
              labelFormatter={(label) => `Tanggal: ${label}`}
            />
            <Legend />
            <Bar dataKey="quantity" name="Kuantitas" fill="#16a34a" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {chartData.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>Tidak ada data konsumsi untuk periode ini</p>
        </div>
      )}
    </div>
  )
}