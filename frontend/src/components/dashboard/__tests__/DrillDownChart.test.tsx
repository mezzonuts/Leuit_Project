import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DrillDownChart from '../DrillDownChart'
import { vi, describe, it, expect } from 'vitest'

vi.mock('@/services/api', () => ({
  api: { get: vi.fn().mockResolvedValue({ data: { data: [], total_transactions: 0 } }) },
}))

vi.mock('@/components/ui/DateRangePicker', () => ({
  default: ({ startDate, endDate }: any) => (
    <div data-testid="date-range-picker">{startDate} to {endDate}</div>
  ),
}))

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="chart">{children}</div>,
  BarChart: ({ children }: any) => <div>{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
}))

const renderChart = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <DrillDownChart />
    </QueryClientProvider>
  )
}

describe('DrillDownChart', () => {
  it('renders title', () => {
    renderChart()
    expect(screen.getByText('Drill-Down Analytics')).toBeInTheDocument()
  })

  it('renders metric select', () => {
    renderChart()
    expect(screen.getByLabelText('Metrik')).toBeInTheDocument()
  })

  it('renders granularity select', () => {
    renderChart()
    expect(screen.getByLabelText('Granularitas')).toBeInTheDocument()
  })

  it('renders date range picker', () => {
    renderChart()
    expect(screen.getByTestId('date-range-picker')).toBeInTheDocument()
  })

  it('shows chart when data loaded', async () => {
    renderChart()
    await waitFor(() => {
      expect(screen.getByTestId('chart')).toBeInTheDocument()
    })
  })
})
