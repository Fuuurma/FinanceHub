'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'

const assetCategories = [
  { type: 'stock', name: 'Stocks', description: 'Publicly traded company shares', count: '8,234', color: 'bg-blue-500' },
  { type: 'crypto', name: 'Cryptocurrencies', description: 'Digital currencies and tokens', count: '2,847', color: 'bg-orange-500' },
  { type: 'forex', name: 'Forex', description: 'Foreign exchange currency pairs', count: '175', color: 'bg-green-500' },
  { type: 'commodity', name: 'Commodities', description: 'Physical goods and resources', count: '52', color: 'bg-yellow-500' },
  { type: 'bond', name: 'Bonds', description: 'Fixed income securities', count: '1,234', color: 'bg-purple-500' },
  { type: 'etf', name: 'ETFs', description: 'Exchange traded funds', count: '2,891', color: 'bg-pink-500' },
  { type: 'index', name: 'Indices', description: 'Market index tracking funds', count: '156', color: 'bg-cyan-500' },
]

export default function AssetsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Assets</h1>
        <p className="text-muted-foreground">Browse all available asset types</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {assetCategories.map((category) => (
          <Link key={category.type} href={`/assets/${category.type}`}>
            <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{category.name}</CardTitle>
                  <div className={`w-3 h-3 rounded-full ${category.color}`} />
                </div>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="secondary">{category.count} assets</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Stats</CardTitle>
          <CardDescription>Overview of all asset categories</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold">15,589</div>
              <div className="text-sm text-muted-foreground">Total Assets</div>
            </div>
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold">$98.4T</div>
              <div className="text-sm text-muted-foreground">Total Market Cap</div>
            </div>
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold">24/7</div>
              <div className="text-sm text-muted-foreground">Trading Available</div>
            </div>
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold">50+</div>
              <div className="text-sm text-muted-foreground">Global Exchanges</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
