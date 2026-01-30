'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell,
  ReferenceLine,
} from 'recharts'
import type { SectorAttribution } from '@/lib/types/attribution'
import { SECTOR_COLORS } from '@/lib/types/attribution'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface SectorAttributionChartProps {
  data: SectorAttribution[]
  type?: 'bar' | 'pie'
  loading?: boolean
  showBenchmark?: boolean
  benchmarkReturn?: number
}

export function SectorAttributionChart({
  data,
  type = 'bar',
  loading = false,
  showBenchmark = false,
  benchmarkReturn,
}: SectorAttributionChartProps) {
  if (loading) {
    return (
      <div className="h-[400px] w-full bg-muted animate-pulse rounded-lg" />
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[400px] w-full flex items-center justify-center bg-muted/50 rounded-lg">
        <p className="text-muted-foreground">No attribution data available</p>
      </div>
    )
  }

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload
      const outperformance = benchmarkReturn !== undefined
        ? item.return - benchmarkReturn
        : undefined

      return (
        <div className="bg-background border rounded-lg shadow-lg p-3">
          <p className="font-medium capitalize mb-2">
            {item.sector || item.name}
          </p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-8">
              <span className="text-muted-foreground">Weight:</span>
              <span className="font-medium">{item.weight.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between gap-8">
              <span className="text-muted-foreground">Return:</span>
              <span className={cn(
                'font-medium',
                item.return >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {formatPercent(item.return)}
              </span>
            </div>
            <div className="flex justify-between gap-8">
              <span className="text-muted-foreground">Contribution:</span>
              <span className={cn(
                'font-medium',
                item.contribution >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {formatPercent(item.contribution)}
              </span>
            </div>
            {outperformance !== undefined && (
              <div className="flex justify-between gap-8">
                <span className="text-muted-foreground">vs Benchmark:</span>
                <span className={cn(
                  'font-medium',
                  outperformance >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatPercent(outperformance)}
                </span>
              </div>
            )}
            <div className="flex justify-between gap-8">
              <span className="text-muted-foreground">Holdings:</span>
              <span className="font-medium">{item.holdings_count}</span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  const renderLegend = (props: any) => {
    const { payload } = props
    return (
      <ul className="flex flex-wrap justify-center gap-3 mt-4">
        {payload.map((entry: any, index: number) => (
          <li key={`legend-${index}`} className="flex items-center gap-1.5 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="capitalize">{entry.value}</span>
          </li>
        ))}
      </ul>
    )
  }

  if (type === 'pie') {
    return (
      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="45%"
              outerRadius={140}
              fill="#8884d8"
              dataKey="contribution"
              nameKey="sector"
              label={({ sector, percent }) =>
                `${sector} (${(percent * 100).toFixed(0)}%)`
              }
              labelLine={false}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={SECTOR_COLORS[entry.sector] || SECTOR_COLORS['Other']}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            type="number"
            tickFormatter={(value) => `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`}
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            type="category"
            dataKey="sector"
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
            width={90}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {showBenchmark && benchmarkReturn !== undefined && (
            <ReferenceLine
              x={benchmarkReturn}
              stroke="#F59E0B"
              strokeDasharray="5 5"
              label={{
                value: `Benchmark: ${formatPercent(benchmarkReturn)}`,
                position: 'top',
                fill: '#F59E0B',
                fontSize: 11,
              }}
            />
          )}
          <Bar
            dataKey="allocation_effect"
            name="Allocation Effect"
            stackId="a"
            fill="#3B82F6"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="selection_effect"
            name="Selection Effect"
            stackId="a"
            fill="#10B981"
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
