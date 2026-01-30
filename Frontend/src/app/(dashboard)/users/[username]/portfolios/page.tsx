'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import { PageTabs, TabContent } from '@/components/ui/page-tabs'
import { Plus, Settings, Trash2, Eye, Search, RefreshCw, Briefcase, Users, Calendar } from 'lucide-react'
import Link from 'next/link'

interface Portfolio {
  id: string
  name: string
  holdings_count: number
  total_value: number
  total_pnl: number
  total_pnl_percent: number
  last_updated: string
  is_public: boolean
  owner: string
}

export default function PortfoliosPage({ params }: { params: { username: string } }) {
  const username = params.username
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    const timer = setTimeout(() => {
      setPortfolios([
        { id: '1', name: 'Growth Portfolio', holdings_count: 12, total_value: 145000, total_pnl: 25000, total_pnl_percent: 20.8, last_updated: '2024-01-15', is_public: true, owner: username },
        { id: '2', name: 'Dividend Income', holdings_count: 8, total_value: 89000, total_pnl: 8500, total_pnl_percent: 10.5, last_updated: '2024-01-14', is_public: true, owner: username },
        { id: '3', name: 'Tech Focus', holdings_count: 15, total_value: 234000, total_pnl: 52000, total_pnl_percent: 28.5, last_updated: '2024-01-15', is_public: false, owner: username },
      ])
      setLoading(false)
    }, 800)
    return () => clearTimeout(timer)
  }, [username])

  const handleRefresh = () => {
    setLoading(true)
    setError('')
    setTimeout(() => setLoading(false), 800)
  }

  const filteredPortfolios = portfolios.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const stats = [
    { title: 'Total Portfolios', value: portfolios.length, icon: Briefcase },
    { title: 'Total Value', value: `$${(portfolios.reduce((acc, p) => acc + p.total_value, 0) / 1000).toFixed(0)}K`, icon: RefreshCw },
    { title: 'Total P&L', value: `$${(portfolios.reduce((acc, p) => acc + p.total_pnl, 0) / 1000).toFixed(0)}K`, change: portfolios.reduce((acc, p) => acc + p.total_pnl_percent, 0) / portfolios.length || 0 },
    { title: 'Public', value: portfolios.filter(p => p.is_public).length, icon: Users },
  ]

  const tabs = [
    { value: 'all', label: 'All Portfolios', icon: Briefcase },
    { value: 'public', label: 'Public', icon: Users },
    { value: 'private', label: 'Private', icon: Settings },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${username}'s Portfolios`}
        description={`Manage and view ${username}'s investment portfolios`}
        loading={loading}
        onRefresh={handleRefresh}
        actions={
          <div className="flex gap-2">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search portfolios..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        }
      />

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      <PageTabs tabs={tabs} defaultValue="all" tabsClassName="grid w-full grid-cols-3">
        <TabContent value="all" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-48" />
              ))}
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {filteredPortfolios.length} of {portfolios.length} portfolios
                </div>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Portfolio
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredPortfolios.map((portfolio) => (
                  <Card key={portfolio.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                          {portfolio.is_public ? (
                            <Badge variant="outline" className="text-xs">
                              <Eye className="h-3 w-3 mr-1" />
                              Public
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-xs">
                              <Settings className="h-3 w-3 mr-1" />
                              Private
                            </Badge>
                          )}
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
                          <div className="flex items-center gap-1 mt-1">
                            <span className={`text-sm font-medium ${portfolio.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl.toLocaleString()}
                            </span>
                            <span className={`text-xs ${portfolio.total_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              ({portfolio.total_pnl_percent >= 0 ? '+' : ''}{portfolio.total_pnl_percent.toFixed(2)}%)
                            </span>
                          </div>
                        </div>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {filteredPortfolios.length === 0 && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center text-muted-foreground">
                      <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No portfolios found matching "{searchQuery}"</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabContent>

        <TabContent value="public" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2].map((i) => (
                <Skeleton key={i} className="h-48" />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredPortfolios.filter(p => p.is_public).map((portfolio) => (
                <Card key={portfolio.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                      <Badge variant="outline" className="text-xs">
                        <Eye className="h-3 w-3 mr-1" />
                        Public
                      </Badge>
                    </div>
                    <CardDescription>
                      {portfolio.holdings_count} holdings
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-2xl font-bold">${portfolio.total_value.toLocaleString()}</div>
                        <div className={`text-sm font-medium ${portfolio.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {portfolio.total_pnl >= 0 ? '+' : ''}{portfolio.total_pnl_percent.toFixed(2)}%
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabContent>

        <TabContent value="private" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1].map((i) => (
                <Skeleton key={i} className="h-48" />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredPortfolios.filter(p => !p.is_public).map((portfolio) => (
                <Card key={portfolio.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                      <Badge variant="secondary" className="text-xs">
                        <Settings className="h-3 w-3 mr-1" />
                        Private
                      </Badge>
                    </div>
                    <CardDescription>
                      {portfolio.holdings_count} holdings
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-2xl font-bold">${portfolio.total_value.toLocaleString()}</div>
                        <div className={`text-sm font-medium ${portfolio.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {portfolio.total_pnl >= 0 ? '+' : ''}{portfolio.total_pnl_percent.toFixed(2)}%
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Manage
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabContent>
      </PageTabs>

      <Card>
        <CardHeader>
          <CardTitle>Create New Portfolio</CardTitle>
          <CardDescription>Set up a new portfolio to track your investments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
              <div className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                <h4 className="font-semibold">Empty Portfolio</h4>
              </div>
              <p className="text-sm text-muted-foreground mt-1">Start fresh with no holdings</p>
            </div>
            <div className="p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                <h4 className="font-semibold">Copy Existing</h4>
              </div>
              <p className="text-sm text-muted-foreground mt-1">Duplicate an existing portfolio</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
