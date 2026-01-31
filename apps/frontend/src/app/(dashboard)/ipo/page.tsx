'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar, TrendingUp, Clock, Star, Bell, RefreshCw } from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface IPOData {
  id: number
  company_name: string
  ticker: string
  exchange: string
  expected_price_min: number | null
  expected_price_max: number | null
  actual_price: number | null
  deal_size: number | null
  expected_date: string | null
  status: string
  sector: string
  industry: string
  lead_underwriter: string
}

interface CalendarSummary {
  summary: Record<string, { count: number; total_deal_size: number; ipos: any[] }>
  total_upcoming: number
  period_months: number
}

const STATUS_COLORS: Record<string, string> = {
  upcoming: 'bg-blue-100 text-blue-700',
  filed: 'bg-yellow-100 text-yellow-700',
  updated: 'bg-orange-100 text-orange-700',
  priced: 'bg-purple-100 text-purple-700',
  listed: 'bg-green-100 text-green-700',
  withdrawn: 'bg-red-100 text-red-700',
  postponed: 'bg-gray-100 text-gray-700',
}

export function IPOCalendarPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [upcomingIPOs, setUpcomingIPOs] = useState<IPOData[]>([])
  const [recentIPOs, setRecentIPOs] = useState<IPOData[]>([])
  const [calendarSummary, setCalendarSummary] = useState<CalendarSummary | null>(null)
  const [stats, setStats] = useState<any>(null)
  const [timeframe, setTimeframe] = useState('90')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const days = parseInt(timeframe)
      
      const [upcomingRes, recentRes, statsRes, calendarRes] = await Promise.all([
        fetch(`/api/ipo/upcoming?days_ahead=${days}&limit=50`),
        fetch('/api/ipo/recent?days_back=90&limit=20'),
        fetch('/api/ipo/stats/summary'),
        fetch(`/api/ipo/calendar/summary?months=3`),
      ])

      if (!upcomingRes.ok) throw new Error('Failed to load IPOs')
      
      const upcomingData = await upcomingRes.json()
      setUpcomingIPOs(upcomingData.ipos || [])
      
      const recentData = await recentRes.json()
      setRecentIPOs(recentData.ipos || [])
      
      const statsData = await statsRes.json()
      setStats(statsData)
      
      const calendarData = await calendarRes.json()
      setCalendarSummary(calendarData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load IPO data')
    } finally {
      setLoading(false)
    }
  }, [timeframe])

  useEffect(() => {
    loadData()
  }, [loadData])

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'TBD'
    try {
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    } catch {
      return dateStr
    }
  }

  const getPriceRange = (ipo: IPOData) => {
    if (ipo.actual_price) {
      return formatCurrency(ipo.actual_price)
    }
    if (ipo.expected_price_min && ipo.expected_price_max) {
      return `${formatCurrency(ipo.expected_price_min)} - ${formatCurrency(ipo.expected_price_max)}`
    }
    return 'TBD'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">IPO Calendar</h1>
          <p className="text-muted-foreground">Track upcoming and recent initial public offerings</p>
        </div>
        <div className="flex gap-2">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30">Next 30 days</SelectItem>
              <SelectItem value="60">Next 60 days</SelectItem>
              <SelectItem value="90">Next 90 days</SelectItem>
              <SelectItem value="180">Next 6 months</SelectItem>
              <SelectItem value="365">Next year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadData} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4 mr-2', loading && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Upcoming IPOs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.upcoming_count}</div>
              <p className="text-sm text-muted-foreground">In next {timeframe} days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="w-4 h-4" />
                This Week
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.this_week_count}</div>
              <p className="text-sm text-muted-foreground">Expected this week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                This Month
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.this_month_count}</div>
              <p className="text-sm text-muted-foreground">Expected this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Recently Listed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.last_30_days_listed}</div>
              <p className="text-sm text-muted-foreground">Last 30 days</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="upcoming">
        <TabsList>
          <TabsTrigger value="upcoming">Upcoming ({upcomingIPOs.length})</TabsTrigger>
          <TabsTrigger value="recent">Recently Listed ({recentIPOs.length})</TabsTrigger>
          <TabsTrigger value="calendar">Calendar View</TabsTrigger>
        </TabsList>

        <TabsContent value="upcoming" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming IPOs</CardTitle>
              <CardDescription>Companies planning to go public</CardDescription>
            </CardHeader>
            <CardContent>
              {upcomingIPOs.length > 0 ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Company</TableHead>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Exchange</TableHead>
                        <TableHead>Expected Date</TableHead>
                        <TableHead>Price Range</TableHead>
                        <TableHead>Deal Size</TableHead>
                        <TableHead>Sector</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {upcomingIPOs.map((ipo) => (
                        <TableRow key={ipo.id}>
                          <TableCell className="font-medium">{ipo.company_name}</TableCell>
                          <TableCell>{ipo.ticker || 'TBD'}</TableCell>
                          <TableCell>{ipo.exchange || 'TBD'}</TableCell>
                          <TableCell>{formatDate(ipo.expected_date)}</TableCell>
                          <TableCell>{getPriceRange(ipo)}</TableCell>
                          <TableCell>{ipo.deal_size ? formatCurrency(ipo.deal_size) : '-'}</TableCell>
                          <TableCell>{ipo.sector || '-'}</TableCell>
                          <TableCell>
                            <Badge className={STATUS_COLORS[ipo.status] || 'bg-gray-100'}>
                              {ipo.status}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No upcoming IPOs found in the selected timeframe
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recent" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Recently Listed</CardTitle>
              <CardDescription>IPOs that have gone public in the last 90 days</CardDescription>
            </CardHeader>
            <CardContent>
              {recentIPOs.length > 0 ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Company</TableHead>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Listed Date</TableHead>
                        <TableHead>Offer Price</TableHead>
                        <TableHead>Day 1 Change</TableHead>
                        <TableHead>Deal Size</TableHead>
                        <TableHead>Sector</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentIPOs.map((ipo) => (
                        <TableRow key={ipo.id}>
                          <TableCell className="font-medium">{ipo.company_name}</TableCell>
                          <TableCell>{ipo.ticker}</TableCell>
                          <TableCell>{formatDate(ipo.listed_date)}</TableCell>
                          <TableCell>{formatCurrency(ipo.actual_price) || '-'}</TableCell>
                          <TableCell className={cn(ipo.ipo_day_change_pct && ipo.ipo_day_change_pct > 0 ? 'text-green-500' : ipo.ipo_day_change_pct && ipo.ipo_day_change_pct < 0 ? 'text-red-500' : '')}>
                            {ipo.ipo_day_change_pct ? formatPercent(ipo.ipo_day_change_pct / 100) : '-'}
                          </TableCell>
                          <TableCell>{ipo.deal_size ? formatCurrency(ipo.deal_size) : '-'}</TableCell>
                          <TableCell>{ipo.sector || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No recently listed IPOs found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="calendar" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Breakdown</CardTitle>
              <CardDescription>IPO activity by month</CardDescription>
            </CardHeader>
            <CardContent>
              {calendarSummary?.summary && Object.keys(calendarSummary.summary).length > 0 ? (
                <div className="grid gap-4 md:grid-cols-3">
                  {Object.entries(calendarSummary.summary).map(([month, data]) => (
                    <div key={month} className="border rounded-lg p-4">
                      <h4 className="font-semibold mb-3">{month}</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">IPOs</span>
                          <span className="font-medium">{data.count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Total Deal Size</span>
                          <span className="font-medium">{formatCurrency(data.total_deal_size)}</span>
                        </div>
                      </div>
                      <div className="mt-3 pt-3 border-t">
                        <p className="text-xs text-muted-foreground">
                          {data.ipos.slice(0, 3).map((i: any) => i.company_name).join(', ')}
                          {data.ipos.length > 3 && ` +${data.ipos.length - 3} more`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No IPO data available for the selected period
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default IPOCalendarPage
