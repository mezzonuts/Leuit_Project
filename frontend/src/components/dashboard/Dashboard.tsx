import { useQuery } from '@tanstack/react-query'
import { TrendingUp, AlertTriangle, Package, DollarSign, Download } from 'lucide-react'
import { api } from '@/services/api'
import { downloadValuationCSV } from '@/utils/exportCsv'
import ValuationMetricCard from './ValuationMetricCard'
import UsageTrendBarChart from './UsageTrendBarChart'
import CriticalAlertsSection from './CriticalAlertsSection'
import StockHealthTable from './StockHealthTable'

export default function Dashboard() {
  const { data: valuation } = useQuery({
    queryKey: ['valuation'],
    queryFn: () => api.get('/valuation').then(res => res.data),
  })

  const { data: stockHealth } = useQuery({
    queryKey: ['stock-health'],
    queryFn: () => api.get('/inventory', { params: { active_only: true } }).then(res => res.data),
  })

  const { data: alerts } = useQuery({
    queryKey: ['critical-alerts'],
    queryFn: () => api.get('/inventory/alerts').then(res => res.data),
  })

  const handleExportValuation = () => {
    if (stockHealth?.items) {
      downloadValuationCSV(stockHealth.items)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Pusat pantau stok, valuasi aset & peringatan kritis</p>
        </div>
        <button
          onClick={handleExportValuation}
          disabled={!valuation}
          className="btn-secondary flex items-center gap-2"
        >
          <Download className="h-4 w-4" />
          Ekspor Valuasi CSV
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <ValuationMetricCard
          title="Total Valuasi Aset"
          value={valuation?.total_valuation || 0}
          icon={<DollarSign />}
          iconColor="text-green-600"
          bgColor="bg-green-50"
          subtitle={`${valuation?.total_ingredients || 0} bahan aktif`}
        />
        <ValuationMetricCard
          title="Stok Rendah"
          value={valuation?.low_stock_count || 0}
          icon={<Package />}
          iconColor="text-warning-600"
          bgColor="bg-warning-50"
          subtitle="Di bawah threshold minimum"
        />
        <ValuationMetricCard
          title="Segera Kadaluwarsa"
          value={valuation?.expired_soon_count || 0}
          icon={<AlertTriangle />}
          iconColor="text-danger-600"
          bgColor="bg-danger-50"
          subtitle="< 3 hari sisa masa simpan"
        />
        <ValuationMetricCard
          title="Trend 30 Hari"
          value={stockHealth?.items?.length || 0}
          icon={<TrendingUp />}
          iconColor="text-blue-600"
          bgColor="bg-blue-50"
          subtitle="Bahan dengan data historis"
        />
      </div>

      {/* Charts & Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <UsageTrendBarChart />
          <CriticalAlertsSection alerts={alerts || []} />
        </div>
        <div className="space-y-6">
          <StockHealthTable items={stockHealth?.items || []} />
        </div>
      </div>
    </div>
  )
}