'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Ownership } from '@/lib/types/iex-cloud'

interface OwnershipChartProps {
  ownership?: Ownership | null
  loading?: boolean
  error?: string
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export function OwnershipChart({ ownership, loading, error }: OwnershipChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || !ownership) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Ownership</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No ownership data available'}</p>
        </CardContent>
      </Card>
    )
  }

  // Prepare institutional ownership data
  const institutionalData = ownership.institutionalOwnership
    .slice(0, 10)
    .map((owner) => ({
      name: owner.ownerName,
      value: owner.shares,
      percentage: owner.positionPct,
    }))

  // Prepare fund ownership data
  const fundData = ownership.fundOwnership
    .slice(0, 10)
    .map((fund) => ({
      name: fund.fundName,
      value: fund.shares,
      percentage: fund.positionPct,
    }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm text-muted-foreground">
            Shares: {data.value.toLocaleString()}
          </p>
          <p className="text-sm text-muted-foreground">
            {data.percentage?.toFixed(2)}% of outstanding
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-4">
      {/* Institutional Ownership */}
      <Card>
        <CardHeader>
          <CardTitle>Institutional Ownership</CardTitle>
        </CardHeader>
        <CardContent>
          {institutionalData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={institutionalData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {institutionalData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">No institutional ownership data available</p>
          )}
        </CardContent>
      </Card>

      {/* Fund Ownership */}
      <Card>
        <CardHeader>
          <CardTitle>Fund Ownership</CardTitle>
        </CardHeader>
        <CardContent>
          {fundData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={fundData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {fundData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">No fund ownership data available</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
