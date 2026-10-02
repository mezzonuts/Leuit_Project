import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import DateRangePicker from '@/components/ui/DateRangePicker'
import { Loader2 } from 'lucide-react'

const METRICS = [
  { value: 'sales', label: 'Penjualan' },
  { value: 'usage', label: 'Penggunaan' },
]

const GRANULARITIES = [
  { value: 'daily', label: 'Harian' },
  { value: 'weekly', label: 'Mingguan' },
  { value: 'monthly', label: 'Bulanan' },
]

export default function DrillDownChart() {
  const [metric, setMetric] = useState('sales')
  const [granularity, setGranularity] = useState('daily')
  const [days, setDays] = useState(30)
  const [startDate, setStartDate] = useState(() => {
    const d = new Date()
    d.setDate(d.getDate() - 30)
    return d.toISOString().split('T')[0]
  })
  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  const { data, isLoading } = useQuery({
    queryKey: ['analytics', 'drill-down', metric, granularity, startDate, endDate],
    queryFn: async () => {
      const res = await api.get('/analytics/drill-down', {
        params: { metric, granularity, days, start_date: startDate, end_date: endDate },
      })
      return res.data
    },
  })

  const chartData = data?.data || []

  return (
    <div className="card">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Drill-Down Analytics</h2>
        <div className="flex items-center gap-2">
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="form-input text-sm"
            aria-label="Metrik"
          >
            {METRICS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <select
            value={granularity}
            onChange={(e) => setGranularity(e.target.value)}
            className="form-input text-sm"
            aria-label="Granularitas"
          >
            {GRANULARITIES.map((g) => (
              <option key={g.value} value={g.value}>{g.label}</option>
            ))}
          </select>
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onChange={(start, end) => {
              setStartDate(start)
              setEndDate(end)
              const diffDays = Math.floor((new Date(end).getTime() - new Date(start).getTime()) / (1000 * 60 * 60 * 24))
              setDays(diffDays)
            }}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey={metric === 'sales' ? 'transaction_count' : 'total_used'}
              fill="#6366f1"
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
