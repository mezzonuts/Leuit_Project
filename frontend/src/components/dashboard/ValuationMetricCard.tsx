import { forwardRef } from 'react'
import { formatRupiah } from '@/utils/formatters'

interface ValuationMetricCardProps {
  title: string
  value: number
  icon: React.ReactNode
  iconColor: string
  bgColor: string
  subtitle?: string
}

const ValuationMetricCard = forwardRef<HTMLDivElement, ValuationMetricCardProps>(
  ({ title, value, icon, iconColor, bgColor, subtitle }, ref) => {
    return (
      <div
        ref={ref}
        className={`card p-5 ${bgColor} border-l-4 border-l-primary-500`}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {formatRupiah(value)}
            </p>
            {subtitle && <p className="mt-1 text-xs text-gray-500">{subtitle}</p>}
          </div>
          <div className={`p-3 rounded-xl ${bgColor} ${iconColor}`}>
            {icon}
          </div>
        </div>
      </div>
    )
  }
)

ValuationMetricCard.displayName = 'ValuationMetricCard'

export default ValuationMetricCard