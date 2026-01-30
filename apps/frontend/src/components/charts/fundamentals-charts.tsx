'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'

interface ValuationChartProps {
  data: Array<{
    date: string
    pe_ratio: number | null
    pb_ratio: number | null
    ps_ratio: number | null
    dividend_yield: number | null
  }>
  metrics: ('pe_ratio' | 'pb_ratio' | 'ps_ratio' | 'dividend_yield')[]
}

export function ValuationChart({ data, metrics }: ValuationChartProps) {
  const formatData = data.map((item) => ({
    ...item,
    date: new Date(item.date).toLocaleDateString(),
  }))

  const colors = {
    pe_ratio: '#3b82f6',
    pb_ratio: '#10b981',
    ps_ratio: '#f59e0b',
    dividend_yield: '#ef4444',
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formatData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          {metrics.map((metric) => (
            <Line
              key={metric}
              type="monotone"
              dataKey={metric}
              stroke={colors[metric]}
              strokeWidth={2}
              dot={false}
              name={metric.replace('_', ' ').toUpperCase()}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

interface FinancialMetricsChartProps {
  data: Array<{
    date: string
    period: string
    total_revenue: number | null
    net_income: number | null
    gross_profit: number | null
    operating_income: number | null
  }>
}

export function FinancialMetricsChart({ data }: FinancialMetricsChartProps) {
  const formatData = data.map((item) => ({
    ...item,
    date: `${item.period} ${item.date.split('-')[0]}`,
    total_revenue_millions: item.total_revenue ? item.total_revenue / 1e6 : null,
    net_income_millions: item.net_income ? item.net_income / 1e6 : null,
    gross_profit_millions: item.gross_profit ? item.gross_profit / 1e6 : null,
  }))

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={formatData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} tickFormatter={(value) => `$${value}M`} />
          <Tooltip
            formatter={(value: number) => [`$${value.toLocaleString()}M`, '']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="total_revenue_millions"
            stackId="1"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.3}
            name="Revenue"
          />
          <Area
            type="monotone"
            dataKey="gross_profit_millions"
            stackId="2"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.3}
            name="Gross Profit"
          />
          <Area
            type="monotone"
            dataKey="net_income_millions"
            stackId="3"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.3}
            name="Net Income"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

interface ProfitabilityChartProps {
  data: Array<{
    date: string
    period: string
    gross_margin: number | null
    operating_margin: number | null
    net_margin: number | null
  }>
}

export function ProfitabilityChart({ data }: ProfitabilityChartProps) {
  const formatData = data.map((item) => ({
    ...item,
    date: `${item.period} ${item.date.split('-')[0]}`,
    gross_margin_pct: item.gross_margin ? item.gross_margin * 100 : null,
    operating_margin_pct: item.operating_margin ? item.operating_margin * 100 : null,
    net_margin_pct: item.net_margin ? item.net_margin * 100 : null,
  }))

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formatData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} tickFormatter={(value) => `${value}%`} />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="gross_margin_pct"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Gross Margin"
          />
          <Line
            type="monotone"
            dataKey="operating_margin_pct"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Operating Margin"
          />
          <Line
            type="monotone"
            dataKey="net_margin_pct"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
            name="Net Margin"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

interface YieldCurveChartProps {
  data: Array<{
    maturity: string
    rate: number
    date: string
  }>
}

export function YieldCurveChart({ data }: YieldCurveChartProps) {
  const maturityOrder = ['1M', '3M', '6M', '1Y', '2Y', '5Y', '10Y', '20Y', '30Y']
  
  const sortedData = [...data].sort((a, b) => {
    return maturityOrder.indexOf(a.maturity) - maturityOrder.indexOf(b.maturity)
  })

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={sortedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="maturity" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} tickFormatter={(value) => `${(value * 100).toFixed(2)}%`} />
          <Tooltip
            formatter={(value: number) => [`${(value * 100).toFixed(3)}%`, 'Yield']}
            labelFormatter={(label) => `Maturity: ${label}`}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Area
            type="monotone"
            dataKey="rate"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.3}
            name="Yield Rate"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

interface CryptoTVLChartProps {
  data: Array<{
    date: string
    tvl: number
  }>
  protocolName: string
}

export function CryptoTVLChart({ data, protocolName }: CryptoTVLChartProps) {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} tickFormatter={(value) => `$${(value / 1e9).toFixed(1)}B`} />
          <Tooltip
            formatter={(value: number) => [`$${value.toLocaleString()}`, 'TVL']}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Area
            type="monotone"
            dataKey="tvl"
            stroke="#8b5cf6"
            fill="#8b5cf6"
            fillOpacity={0.3}
            name={`${protocolName} TVL`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
