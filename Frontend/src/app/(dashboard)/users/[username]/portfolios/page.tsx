'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { Plus, Settings, Trash2, Eye } from 'lucide-react'

interface Portfolio {
  id: string
  name: string
  holdings_count: number
  total_value: number
  last_updated: string
}

export default function PortfoliosPage({ params }: { params: { username: string } }) {
  const [portfolios] = useState<Portfolio[]>([
    { id: '1', name: 'Growth Portfolio', holdings_count: 12, total_value: 145000, last_updated: '2024-01-15' },
    { id: '2', name: 'Dividend Income', holdings_count: 8, total_value: 89000, last_updated: '2024-01-14' },
    { id: '3', name: 'Tech Focus', holdings_count: 15, total_value: 234000, last_updated: '2024-01-15' },
  ])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolios</h1>
          <p className="text-muted-foreground">Manage {params.username}'s portfolios</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Portfolio
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {portfolios.map((portfolio) => (
          <Card key={portfolio.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{portfolio.name}</CardTitle>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <CardDescription>
                {portfolio.holdings_count} holdings • Updated {portfolio.last_updated}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">${portfolio.total_value.toLocaleString()}</div>
                  <div className="text-sm text-muted-foreground">Total Value</div>
                </div>
                <Badge variant="secondary">Active</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Create New Portfolio</CardTitle>
          <CardDescription>Set up a new portfolio to track your investments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 border rounded-lg hover:bg-muted/50 cursor-pointer">
              <h4 className="font-semibold">Empty Portfolio</h4>
              <p className="text-sm text-muted-foreground">Start fresh with no holdings</p>
            </div>
            <div className="p-4 border rounded-lg hover:bg-muted/50 cursor-pointer">
              <h4 className="font-semibold">Copy Existing</h4>
              <p className="text-sm text-muted-foreground">Duplicate an existing portfolio</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
