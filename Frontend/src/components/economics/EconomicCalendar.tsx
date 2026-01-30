'use client'

import { useState, useMemo, useCallback } from 'react'
import {
  Calendar,
  Filter,
  Download,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Clock,
  Globe,
  BarChart3,
  PieChart,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Search,
  Info,
  CheckCircle,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Calendar as CalendarComponent } from '@/components/ui/calendar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn, formatDate, formatNumber } from '@/lib/utils'

export type ImportanceLevel = 'high' | 'medium' | 'low'
export type EventCategory = 'gdp' | 'inflation' | 'employment' | 'interest_rate' | 'consumer' | 'housing' | 'manufacturing' | 'trade' | 'other'
export type Country = 'US' | 'EU' | 'UK' | 'JP' | 'CN' | 'CA' | 'AU' | 'global'

export interface EconomicEvent {
  id: string
  title: string
  country: Country
  category: EventCategory
  importance: ImportanceLevel
  date: string
  time: string
  actual?: number
  forecast?: number
  previous?: number
  unit?: string
  impact: 'positive' | 'negative' | 'neutral'
  description?: string
  series_id?: string
}

export interface EconomicCalendarProps {
  events?: EconomicEvent[]
  loading?: boolean
  onRefresh?: () => void
  className?: string
}

export interface DateRange {
  from: Date | undefined
  to: Date | undefined
}

const DATE_PRESETS = [
  { label: 'Today', days: 0 },
  { label: 'This Week', days: 7 },
  { label: 'This Month', days: 30 },
  { label: 'Next 7 Days', days: 7, future: true },
  { label: 'Next 30 Days', days: 30, future: true },
  { label: 'Next 3 Months', days: 90, future: true },
]

const CATEGORIES: { value: EventCategory; label: string; icon: React.ElementType }[] = [
  { value: 'gdp', label: 'GDP', icon: TrendingUp },
  { value: 'inflation', label: 'Inflation', icon: BarChart3 },
  { value: 'employment', label: 'Employment', icon: Clock },
  { value: 'interest_rate', label: 'Interest Rates', icon: TrendingDown },
  { value: 'consumer', label: 'Consumer', icon: Globe },
  { value: 'housing', label: 'Housing', icon: HomeIcon },
  { value: 'manufacturing', label: 'Manufacturing', icon: FactoryIcon },
  { value: 'trade', label: 'Trade', icon: Globe },
  { value: 'other', label: 'Other', icon: Info },
]

const COUNTRIES: { value: Country; label: string; flag: string }[] = [
  { value: 'US', label: 'United States', flag: '🇺🇸' },
  { value: 'EU', label: 'European Union', flag: '🇪🇺' },
  { value: 'UK', label: 'United Kingdom', flag: '🇬🇧' },
  { value: 'JP', label: 'Japan', flag: '🇯🇵' },
  { value: 'CN', label: 'China', flag: '🇨🇳' },
  { value: 'CA', label: 'Canada', flag: '🇨🇦' },
  { value: 'AU', label: 'Australia', flag: '🇦🇺' },
]

const IMPORTANCE_LEVELS: { value: ImportanceLevel; label: string; color: string }[] = [
  { value: 'high', label: 'High Impact', color: 'bg-red-500' },
  { value: 'medium', label: 'Medium Impact', color: 'bg-yellow-500' },
  { value: 'low', label: 'Low Impact', color: 'bg-green-500' },
]

function HomeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  )
}

function FactoryIcon({ className }: { className?: string }) {
  return (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z" />
      <path d="M17 18h1" />
      <path d="M12 18h1" />
      <path d="M7 18h1" />
    </svg>
  )
}

function getImportanceColor(level: ImportanceLevel): string {
  switch (level) {
    case 'high': return 'bg-red-100 text-red-800 border-red-300'
    case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    case 'low': return 'bg-green-100 text-green-800 border-green-300'
  }
}

function getImpactBadge(impact: 'positive' | 'negative' | 'neutral'): { label: string; color: string } {
  switch (impact) {
    case 'positive': return { label: 'Positive', color: 'bg-green-500' }
    case 'negative': return { label: 'Negative', color: 'bg-red-500' }
    case 'neutral': return { label: 'Neutral', color: 'bg-gray-500' }
  }
}

function getCountryFlag(country: Country): string {
  const found = COUNTRIES.find(c => c.value === country)
  return found?.flag || '🌍'
}

function generateMockEvents(startDate: Date, days: number): EconomicEvent[] {
  const eventTypes: Array<{
    title: string
    category: EventCategory
    importance: ImportanceLevel
    unit: string
  }> = [
    { title: 'GDP Growth Rate', category: 'gdp', importance: 'high', unit: '%' },
    { title: 'CPI YoY', category: 'inflation', importance: 'high', unit: '%' },
    { title: 'Nonfarm Payrolls', category: 'employment', importance: 'high', unit: 'K' },
    { title: 'Unemployment Rate', category: 'employment', importance: 'medium', unit: '%' },
    { title: 'Fed Funds Rate', category: 'interest_rate', importance: 'high', unit: '%' },
    { title: 'Core PCE Price Index', category: 'inflation', importance: 'medium', unit: '%' },
    { title: 'Retail Sales MoM', category: 'consumer', importance: 'medium', unit: '%' },
    { title: 'Housing Starts', category: 'housing', importance: 'low', unit: 'K' },
    { title: 'Consumer Confidence Index', category: 'consumer', importance: 'medium', unit: 'pts' },
    { title: 'Industrial Production MoM', category: 'manufacturing', importance: 'low', unit: '%' },
    { title: 'Trade Balance', category: 'trade', importance: 'low', unit: 'B' },
    { title: 'Initial Jobless Claims', category: 'employment', importance: 'medium', unit: 'K' },
  ]

  const events: EconomicEvent[] = []
  const usedDates = new Set<string>()

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const numEvents = Math.floor(Math.random() * 3) + 1

    for (let j = 0; j < numEvents; j++) {
      const eventType = eventTypes[Math.floor(Math.random() * eventType.length)]
      const dateStr = date.toISOString().split('T')[0]
      const timeKey = `${dateStr}-${eventType.title}`

      if (usedDates.has(timeKey)) continue
      usedDates.add(timeKey)

      const hour = 8 + Math.floor(Math.random() * 10)
      const minute = Math.floor(Math.random() * 60)

      const actual = eventType.unit === '%' ? (Math.random() * 5 - 1).toFixed(1) :
                     eventType.unit === 'K' ? (Math.random() * 300 + 50).toFixed(0) :
                     (Math.random() * 100 + 50).toFixed(0)
      const forecast = (parseFloat(actual) + (Math.random() - 0.5) * 2).toFixed(1)
      const previous = (parseFloat(actual) + (Math.random() - 0.5) * 3).toFixed(1)

      const impact = parseFloat(actual) > parseFloat(forecast) ? 'positive' :
                     parseFloat(actual) < parseFloat(forecast) ? 'negative' : 'neutral'

      events.push({
        id: `evt-${dateStr}-${j}`,
        title: eventType.title,
        country: 'US',
        category: eventType.category,
        importance: eventType.importance,
        date: dateStr,
        time: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
        actual: parseFloat(actual),
        forecast: parseFloat(forecast),
        previous: parseFloat(previous),
        unit: eventType.unit,
        impact,
        description: `${eventType.title} for ${date.toLocaleDateString()}`,
      })
    }
  }

  return events.sort((a, b) => new Date(a.date + 'T' + a.time).getTime() - new Date(b.date + 'T' + b.time).getTime())
}

function EventCard({ event }: { event: EconomicEvent }) {
  const impact = getImpactBadge(event.impact)
  const importance = IMPORTANCE_LEVELS.find(i => i.value === event.importance)

  return (
    <div className={cn(
      'p-4 border-2 border-foreground/20 hover:border-foreground transition-all',
      'hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_var(--foreground)]'
    )}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getCountryFlag(event.country)}</span>
            <Badge variant="outline" className={cn('text-xs', getImportanceColor(event.importance))}>
              {importance?.label}
            </Badge>
            <Badge className={cn('text-xs text-white', impact.color)}>
              {impact.label}
            </Badge>
          </div>
          <h3 className="font-bold uppercase text-sm truncate">{event.title}</h3>
          <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>{formatDate(event.date)}</span>
            <Clock className="h-3 w-3 ml-2" />
            <span>{event.time}</span>
          </div>
        </div>
        <div className="text-right shrink-0">
          {event.actual !== undefined && (
            <div className="text-xl font-black">{event.actual}{event.unit}</div>
          )}
          <div className="text-xs text-muted-foreground mt-1">
            Forecast: {event.forecast}{event.unit}
          </div>
          <div className="text-xs text-muted-foreground">
            Previous: {event.previous}{event.unit}
          </div>
        </div>
      </div>
    </div>
  )
}

function SummaryCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'text-foreground',
}: {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ElementType
  color?: string
}) {
  return (
    <Card className="border-2 border-foreground">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground uppercase font-bold">{title}</p>
            <p className={cn('text-3xl font-black mt-1', color)}>{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
          </div>
          <Icon className={cn('h-8 w-8 opacity-20', color)} />
        </div>
      </CardContent>
    </Card>
  )
}

export function EconomicCalendar({
  events: initialEvents,
  loading = false,
  onRefresh,
  className,
}: EconomicCalendarProps) {
  const [events, setEvents] = useState<EconomicEvent[]>([])
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(),
    to: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  })
  const [selectedCountries, setSelectedCountries] = useState<Set<Country>>(new Set(['US', 'EU', 'UK', 'JP']))
  const [selectedCategories, setSelectedCategories] = useState<Set<EventCategory>>(new Set(CATEGORIES.map(c => c.value)))
  const [selectedImportance, setSelectedImportance] = useState<Set<ImportanceLevel>>(new Set(['high', 'medium', 'low']))
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'importance'>('date')
  const [activeTab, setActiveTab] = useState('calendar')

  useState(() => {
    if (initialEvents) {
      setEvents(initialEvents)
    } else {
      const mockEvents = generateMockEvents(new Date(), 45)
      setEvents(mockEvents)
    }
  })

  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      if (dateRange.from && new Date(event.date) < dateRange.from) return false
      if (dateRange.to && new Date(event.date) > dateRange.to) return false
      if (!selectedCountries.has(event.country)) return false
      if (!selectedCategories.has(event.category)) return false
      if (!selectedImportance.has(event.importance)) return false
      if (searchQuery && !event.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
      return true
    }).sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(a.date + 'T' + a.time).getTime() - new Date(b.date + 'T' + b.time).getTime()
      } else {
        const importanceOrder = { high: 0, medium: 1, low: 2 }
        return importanceOrder[a.importance] - importanceOrder[b.importance]
      }
    })
  }, [events, dateRange, selectedCountries, selectedCategories, selectedImportance, searchQuery, sortBy])

  const summaries = useMemo(() => {
    const total = filteredEvents.length
    const highImpact = filteredEvents.filter(e => e.importance === 'high').length
    const mediumImpact = filteredEvents.filter(e => e.importance === 'medium').length
    const lowImpact = filteredEvents.filter(e => e.importance === 'low').length
    const positive = filteredEvents.filter(e => e.impact === 'positive').length
    const negative = filteredEvents.filter(e => e.impact === 'negative').length
    const neutral = filteredEvents.filter(e => e.impact === 'neutral').length

    const eventsByCategory = CATEGORIES.reduce((acc, cat) => {
      acc[cat.label] = filteredEvents.filter(e => e.category === cat.value).length
      return acc
    }, {} as Record<string, number>)

    const eventsByCountry = COUNTRIES.reduce((acc, country) => {
      acc[country.flag] = filteredEvents.filter(e => e.country === country.value).length
      return acc
    }, {} as Record<string, number>)

    return {
      total,
      highImpact,
      mediumImpact,
      lowImpact,
      positive,
      negative,
      neutral,
      eventsByCategory,
      eventsByCountry,
    }
  }, [filteredEvents])

  const handleExportCSV = useCallback(() => {
    const headers = ['Date', 'Time', 'Country', 'Category', 'Importance', 'Title', 'Actual', 'Forecast', 'Previous', 'Impact']
    const rows = filteredEvents.map(e => [
      e.date,
      e.time,
      e.country,
      e.category,
      e.importance,
      e.title,
      e.actual?.toString() || '',
      e.forecast?.toString() || '',
      e.previous?.toString() || '',
      e.impact,
    ])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `economic-calendar-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }, [filteredEvents])

  const handleExportJSON = useCallback(() => {
    const data = JSON.stringify(filteredEvents, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `economic-calendar-${new Date().toISOString().split('T')[0]}.json`
    a.click()
  }, [filteredEvents])

  const toggleCountry = (country: Country) => {
    setSelectedCountries(prev => {
      const next = new Set(prev)
      if (next.has(country)) next.delete(country)
      else next.add(country)
      return next
    })
  }

  const toggleCategory = (category: EventCategory) => {
    setSelectedCategories(prev => {
      const next = new Set(prev)
      if (next.has(category)) next.delete(category)
      else next.add(category)
      return next
    })
  }

  const toggleImportance = (importance: ImportanceLevel) => {
    setSelectedImportance(prev => {
      const next = new Set(prev)
      if (next.has(importance)) next.delete(importance)
      else next.add(importance)
      return next
    })
  }

  const applyDatePreset = (preset: typeof DATE_PRESETS[0]) => {
    const today = new Date()
    const from = preset.future ? today : new Date(today)
    const to = new Date(today)

    if (preset.future) {
      to.setDate(to.getDate() + preset.days)
    } else {
      from.setDate(from.getDate() - preset.days)
    }

    setDateRange({ from, to })
  }

  if (loading) {
    return (
      <Card className={cn('border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground bg-muted/30">
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      <Card className="border-2 border-foreground">
        <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Economic_Calendar
              </CardTitle>
              <CardDescription className="text-xs font-mono">
                {filteredEvents.length} events from {dateRange.from?.toLocaleDateString()} to {dateRange.to?.toLocaleDateString()}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="h-8">
                    <Filter className="h-4 w-4 mr-1" />
                    Filters
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64">
                  <DropdownMenuLabel>Date Range</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <div className="p-2 grid grid-cols-2 gap-1">
                    {DATE_PRESETS.map(preset => (
                      <Button
                        key={preset.label}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => applyDatePreset(preset)}
                      >
                        {preset.label}
                      </Button>
                    ))}
                  </div>
                  <DropdownMenuSeparator />
                  <div className="p-2">
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" size="sm" className="w-full text-xs">
                          {dateRange.from && dateRange.to
                            ? `${dateRange.from.toLocaleDateString()} - ${dateRange.to.toLocaleDateString()}`
                            : 'Select custom range'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <CalendarComponent
                          mode="range"
                          selected={{ from: dateRange.from, to: dateRange.to }}
                          onSelect={(range) => setDateRange({ from: range?.from, to: range?.to })}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  <DropdownMenuSeparator />
                  <DropdownMenuLabel>Countries</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <div className="p-2 flex flex-wrap gap-1">
                    {COUNTRIES.map(country => (
                      <Button
                        key={country.value}
                        variant={selectedCountries.has(country.value) ? 'default' : 'outline'}
                        size="sm"
                        className="text-xs px-2"
                        onClick={() => toggleCountry(country.value)}
                      >
                        {country.flag}
                      </Button>
                    ))}
                  </div>

                  <DropdownMenuSeparator />
                  <DropdownMenuLabel>Importance</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {IMPORTANCE_LEVELS.map(level => (
                    <DropdownMenuCheckboxItem
                      key={level.value}
                      checked={selectedImportance.has(level.value)}
                      onCheckedChange={() => toggleImportance(level.value)}
                    >
                      <div className="flex items-center gap-2">
                        <div className={cn('w-3 h-3 rounded-full', level.color)} />
                        <span className="text-xs">{level.label}</span>
                      </div>
                    </DropdownMenuCheckboxItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              <Select value={sortBy} onValueChange={(v) => setSortBy(v as 'date' | 'importance')}>
                <SelectTrigger className="h-8 w-36">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Sort by Date</SelectItem>
                  <SelectItem value="importance">Sort by Impact</SelectItem>
                </SelectContent>
              </Select>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="h-8">
                    <Download className="h-4 w-4 mr-1" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuCheckboxItem onClick={handleExportCSV}>
                    Export as CSV
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem onClick={handleExportJSON}>
                    Export as JSON
                  </DropdownMenuCheckboxItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button variant="default" size="sm" onClick={onRefresh} className="h-8">
                <RefreshCw className="h-4 w-4 mr-1" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="border-2 border-foreground bg-background">
              <TabsTrigger value="calendar" className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs">
                Calendar
              </TabsTrigger>
              <TabsTrigger value="summary" className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs">
                Summary
              </TabsTrigger>
              <TabsTrigger value="list" className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs">
                List
              </TabsTrigger>
            </TabsList>

            <TabsContent value="calendar" className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search events..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>

              <div className="grid gap-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <SummaryCard
                    title="Total Events"
                    value={summaries.total}
                    icon={Calendar}
                  />
                  <SummaryCard
                    title="High Impact"
                    value={summaries.highImpact}
                    icon={AlertTriangle}
                    color="text-red-600"
                  />
                  <SummaryCard
                    title="Positive"
                    value={summaries.positive}
                    icon={TrendingUp}
                    color="text-green-600"
                  />
                  <SummaryCard
                    title="Negative"
                    value={summaries.negative}
                    icon={TrendingDown}
                    color="text-red-600"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="border-2 border-foreground">
                    <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
                      <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
                        <PieChart className="h-4 w-4" />
                        By Category
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-2">
                      {Object.entries(summaries.eventsByCategory).map(([category, count]) => (
                        <div key={category} className="flex items-center justify-between">
                          <span className="text-xs font-medium">{category}</span>
                          <div className="flex items-center gap-2">
                            <Progress value={(count / summaries.total) * 100} className="w-20 h-2" />
                            <span className="text-xs font-mono w-6">{count}</span>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  <Card className="border-2 border-foreground">
                    <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
                      <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        By Country
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-2">
                      {Object.entries(summaries.eventsByCountry).map(([flag, count]) => (
                        <div key={flag} className="flex items-center justify-between">
                          <span className="text-xs font-medium">{flag}</span>
                          <div className="flex items-center gap-2">
                            <Progress value={(count / summaries.total) * 100} className="w-20 h-2" />
                            <span className="text-xs font-mono w-6">{count}</span>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>

                <Card className="border-2 border-foreground">
                  <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
                    <CardTitle className="text-sm font-black uppercase">Upcoming High Impact Events</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="grid gap-3">
                      {filteredEvents.filter(e => e.importance === 'high').slice(0, 5).map(event => (
                        <EventCard key={event.id} event={event} />
                      ))}
                      {filteredEvents.filter(e => e.importance === 'high').length === 0 && (
                        <div className="text-center py-8 text-muted-foreground">
                          <CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                          <p className="font-black uppercase">No High Impact Events</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="summary" className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <SummaryCard title="Total Events" value={summaries.total} icon={Calendar} />
                <SummaryCard title="High Impact" value={summaries.highImpact} icon={AlertTriangle} color="text-red-600" />
                <SummaryCard title="Medium Impact" value={summaries.mediumImpact} icon={Clock} color="text-yellow-600" />
                <SummaryCard title="Low Impact" value={summaries.lowImpact} icon={CheckCircle} color="text-green-600" />
                <SummaryCard title="Positive" value={summaries.positive} icon={TrendingUp} color="text-green-600" />
                <SummaryCard title="Negative" value={summaries.negative} icon={TrendingDown} color="text-red-600" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="border-2 border-foreground">
                  <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
                    <CardTitle className="text-sm font-black uppercase">Impact Distribution</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="space-y-4">
                      {IMPORTANCE_LEVELS.map(level => (
                        <div key={level.value} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold uppercase">{level.label}</span>
                            <span className="text-xs font-mono">
                              {summaries.total > 0 ? ((level.value === 'high' ? summaries.highImpact : level.value === 'medium' ? summaries.mediumImpact : summaries.lowImpact) / summaries.total * 100).toFixed(0) : 0}%
                            </span>
                          </div>
                          <Progress
                            value={summaries.total > 0 ? ((level.value === 'high' ? summaries.highImpact : level.value === 'medium' ? summaries.mediumImpact : summaries.lowImpact) / summaries.total * 100) : 0}
                            className={cn(
                              'h-3',
                              level.value === 'high' && '[&>div]:bg-red-500',
                              level.value === 'medium' && '[&>div]:bg-yellow-500',
                              level.value === 'low' && '[&>div]:bg-green-500'
                            )}
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2 border-foreground">
                  <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
                    <CardTitle className="text-sm font-black uppercase">Market Impact Summary</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold uppercase">Bullish (Positive)</span>
                          <span className="text-xs font-mono">{summaries.positive}</span>
                        </div>
                        <Progress
                          value={summaries.total > 0 ? (summaries.positive / summaries.total * 100) : 0}
                          className="h-3 [&>div]:bg-green-500"
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold uppercase">Bearish (Negative)</span>
                          <span className="text-xs font-mono">{summaries.negative}</span>
                        </div>
                        <Progress
                          value={summaries.total > 0 ? (summaries.negative / summaries.total * 100) : 0}
                          className="h-3 [&>div]:bg-red-500"
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold uppercase">Neutral</span>
                          <span className="text-xs font-mono">{summaries.neutral}</span>
                        </div>
                        <Progress
                          value={summaries.total > 0 ? (summaries.neutral / summaries.total * 100) : 0}
                          className="h-3 [&>div]:bg-gray-400"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="list" className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search events..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>

              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {filteredEvents.length > 0 ? (
                  filteredEvents.map(event => (
                    <EventCard key={event.id} event={event} />
                  ))
                ) : (
                  <div className="text-center py-12 border-2 border-dashed border-foreground/20">
                    <Calendar className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
                    <p className="font-black uppercase text-muted-foreground">No Events Found</p>
                    <p className="text-xs text-muted-foreground mt-1">Try adjusting your filters</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

export function EconomicCalendarSkeleton() {
  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30">
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default EconomicCalendar
