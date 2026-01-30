'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { IndicatorChart } from '@/components/technical/IndicatorChart'
import { indicatorsApi } from '@/lib/api/indicators'
import { Search, RefreshCw, TrendingUp, BarChart2, Activity, LineChart as LineChartIcon } from 'lucide-react'

const INDICATOR_CONFIGS = [
  { id: 'sma', name: 'SMA', color: '#3b82f6', params: { period: 20 } },
  { id: 'ema', name: 'EMA', color: '#8b5cf6', params: { period: 12 } },
  { id: 'rsi', name: 'RSI', color: '#ef4444', params: { period: 14 }, referenceLines: [
    { value: 70, label: 'Overbought', color: '#ef4444' },
    { value: 30, label: 'Oversold', color: '#22c55e' },
  ]},
  { id: 'macd', name: 'MACD', color: '#10b981', params: {} },
  { id: 'bollinger', name: 'Bollinger Bands', color: '#f59e0b', params: { period: 20, std_dev: 2 } },
  { id: 'stochastic', name: 'Stochastic', color: '#f97316', params: { k_period: 14, d_period: 3 }, referenceLines: [
    { value: 80, label: 'Overbought', color: '#ef4444' },
    { value: 20, label: 'Oversold', color: '#22c55e' },
  ]},
  { id: 'wma', name: 'WMA', color: '#06b6d4', params: { period: 20 } },
  { id: 'mfi', name: 'MFI', color: '#ec4899', params: { period: 14 }, referenceLines: [
    { value: 80, label: 'Overbought', color: '#ef4444' },
    { value: 20, label: 'Oversold', color: '#22c55e' },
  ]},
  { id: 'vwap', name: 'VWAP', color: '#84cc16', params: {} },
  { id: 'ichimoku', name: 'Ichimoku', color: '#6366f1', params: {} },
  { id: 'parabolic-sar', name: 'Parabolic SAR', color: '#f43f5e', params: {} },
  { id: 'atr', name: 'ATR', color: '#a855f7', params: { period: 14 } },
  { id: 'cci', name: 'CCI', color: '#14b8a6', params: { period: 20 }, referenceLines: [
    { value: 100, label: 'Overbought', color: '#ef4444' },
    { value: -100, label: 'Oversold', color: '#22c55e' },
  ]},
  { id: 'williams_r', name: 'Williams %R', color: '#eab308', params: { period: 14 }, referenceLines: [
    { value: -20, label: 'Overbought', color: '#ef4444' },
    { value: -80, label: 'Oversold', color: '#22c55e' },
  ]},
  { id: 'obv', name: 'OBV', color: '#22c55e', params: {} },
]

export default function TechnicalAnalysisPage() {
  const params = useParams()
  const [symbol, setSymbol] = useState((params.symbol as string) || 'AAPL')
  const [searchInput, setSearchInput] = useState(symbol)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [priceData, setPriceData] = useState<Array<{ timestamp: string; close: number }>>([])
  
  const [indicators, setIndicators] = useState<Record<string, any>>({})
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>(['sma', 'rsi', 'macd'])
  const [days, setDays] = useState(90)

  const fetchIndicatorData = async (indicatorId: string, config: typeof INDICATOR_CONFIGS[0]) => {
    try {
      let data: any = null
      
      switch (indicatorId) {
        case 'sma':
          data = await indicatorsApi.getSMA(symbol, config.params.period, days)
          break
        case 'ema':
          data = await indicatorsApi.getEMA(symbol, config.params.period, days)
          break
        case 'rsi':
          data = await indicatorsApi.getRSI(symbol, config.params.period, days)
          break
        case 'macd':
          data = await indicatorsApi.getMACD(symbol)
          break
        case 'bollinger':
          data = await indicatorsApi.getBollinger(symbol, config.params.period, config.params.std_dev, days)
          break
        case 'stochastic':
          data = await indicatorsApi.getStochastic(symbol, config.params.k_period, config.params.d_period, 3, days)
          break
        case 'wma':
          data = await indicatorsApi.getWMA(symbol, config.params.period, days)
          break
        case 'mfi':
          data = await indicatorsApi.getMFI(symbol, config.params.period, days)
          break
        case 'vwap':
          data = await indicatorsApi.getVWAP(symbol, days)
          break
        case 'ichimoku':
          data = await indicatorsApi.getIchimoku(symbol)
          break
        case 'parabolic-sar':
          data = await indicatorsApi.getParabolicSAR(symbol)
          break
        case 'atr':
          data = await indicatorsApi.getATR(symbol, config.params.period, days)
          break
        case 'cci':
          data = await indicatorsApi.getCCI(symbol, config.params.period, days)
          break
        case 'williams_r':
          data = await indicatorsApi.getWilliamsR(symbol, config.params.period, days)
          break
        case 'obv':
          data = await indicatorsApi.getOBV(symbol, days)
          break
      }
      
      return data
    } catch (err) {
      console.error(`Failed to fetch ${indicatorId}:`, err)
      return null
    }
  }

  const fetchAllData = async () => {
    setLoading(true)
    setError('')

    try {
      // Fetch price data first
      const chartData = await indicatorsApi.getChart(symbol, '1y')
      if (chartData && Array.isArray(chartData)) {
        const formattedPriceData = chartData.map((d: any) => ({
          timestamp: d.timestamp || d.date,
          close: d.close || d.latestPrice,
        }))
        setPriceData(formattedPriceData)
      }

      // Fetch selected indicators
      const newIndicators: Record<string, any> = {}
      
      for (const indicatorId of selectedIndicators) {
        const config = INDICATOR_CONFIGS.find(c => c.id === indicatorId)
        if (config) {
          const data = await fetchIndicatorData(indicatorId, config)
          if (data) {
            newIndicators[indicatorId] = data
          }
        }
      }
      
      setIndicators(newIndicators)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (symbol) {
      fetchAllData()
    }
  }, [symbol, selectedIndicators, days])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      setSymbol(searchInput.toUpperCase())
    }
  }

  const handleRefresh = () => {
    if (symbol) {
      fetchAllData()
    }
  }

  const toggleIndicator = (indicatorId: string) => {
    setSelectedIndicators(prev => {
      if (prev.includes(indicatorId)) {
        return prev.filter(id => id !== indicatorId)
      } else {
        return [...prev, indicatorId]
      }
    })
  }

  const getIndicatorData = (indicatorId: string) => {
    const data = indicators[indicatorId]
    if (!data) return []

    if (Array.isArray(data)) {
      return data
    }
    
    if (data.data) {
      if (Array.isArray(data.data)) {
        return data.data
      }
      if (indicatorId === 'ichimoku' && data.data.tenkan) {
        return data.data.tenkan.map((d: any, i: number) => ({
          timestamp: d.timestamp,
          value: d.tenkan || d.value || d.kijun,
          ...(data.data.senkou_a?.[i] && { senkou_a: data.data.senkou_a[i].senkou_a }),
          ...(data.data.senkou_b?.[i] && { senkou_b: data.data.senkou_b[i].senkou_b }),
          ...(data.data.chikou?.[i] && { chikou: data.data.chikou[i].chikou }),
        }))
      }
      if (data.data.macd) {
        return data.data.macd.map((d: any, i: number) => ({
          timestamp: d.timestamp,
          value: d.macd || d.value,
          signal: d.signal,
          histogram: d.histogram,
        }))
      }
      if (data.data.psar) {
        return data.data.psar.map((d: any) => ({
          timestamp: d.timestamp,
          value: d.psar,
          trend: d.trend,
          signal: d.signal,
        }))
      }
      return Object.values(data.data).flat() as any[]
    }
    
    return []
  }

  const getConfig = (indicatorId: string) => INDICATOR_CONFIGS.find(c => c.id === indicatorId)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Technical Analysis</h1>
          <p className="text-muted-foreground">
            Comprehensive technical indicators and chart analysis
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={loading} variant="outline">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Enter stock/crypto symbol..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
            className="pl-9"
          />
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-2 border rounded-md"
        >
          <option value={30}>30 days</option>
          <option value={60}>60 days</option>
          <option value={90}>90 days</option>
          <option value={180}>180 days</option>
          <option value={365}>1 year</option>
        </select>
        <Button type="submit" disabled={loading}>
          Analyze
        </Button>
      </form>

      {error && (
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-sm text-red-500">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Indicator Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart2 className="h-5 w-5" />
            Select Indicators
          </CardTitle>
          <CardDescription>Toggle indicators to display on chart</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {INDICATOR_CONFIGS.map((config) => (
              <Button
                key={config.id}
                variant={selectedIndicators.includes(config.id) ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator(config.id)}
                className="gap-2"
              >
                {selectedIndicators.includes(config.id) && (
                  <Activity className="h-3 w-3" />
                )}
                {config.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Price Chart with Indicators */}
      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-96 w-full" />
          {selectedIndicators.slice(0, 3).map((i) => (
            <Skeleton key={i} className="h-64 w-full" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Main Price Chart */}
          <IndicatorChart
            data={priceData.map(d => ({ timestamp: d.timestamp, value: d.close }))}
            title={`${symbol} Price`}
            color="#3b82f6"
            showPrice={false}
            height={350}
          />

          {/* Selected Indicators */}
          {selectedIndicators.map((indicatorId) => {
            const config = getConfig(indicatorId)
            const data = getIndicatorData(indicatorId)
            
            if (!config || data.length === 0) return null

            return (
              <IndicatorChart
                key={indicatorId}
                data={data}
                title={config.name}
                color={config.color}
                showPrice={indicatorId === 'vwap'}
                priceData={priceData}
                referenceLines={config.referenceLines}
                height={250}
              />
            )
          })}
        </div>
      )}

      {/* Indicator Summary */}
      {Object.keys(indicators).length > 0 && !loading && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LineChartIcon className="h-5 w-5" />
              Technical Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {selectedIndicators.slice(0, 9).map((indicatorId) => {
                const config = getConfig(indicatorId)
                const data = getIndicatorData(indicatorId)
                const latest = data[data.length - 1]
                
                if (!config || !latest) return null

                return (
                  <div key={indicatorId} className="p-3 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{config.name}</span>
                      <Badge variant="outline" style={{ borderColor: config.color, color: config.color }}>
                        {latest.value?.toFixed(4) || 'N/A'}
                      </Badge>
                    </div>
                    {latest.signal && (
                      <p className="text-xs text-muted-foreground">
                        Signal: {latest.signal}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
