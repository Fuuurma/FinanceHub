'use client'

import { useState } from 'react'
import { fundamentalsApi } from '@/lib/api/fundamentals'
import type {
  EquityValuation,
  CryptoProtocolMetrics,
  BondMetrics,
  YieldCurvePoint,
  ScreenerFilter,
  ScreenerResult,
  PeriodType,
} from '@/lib/types'
import { TrendingUp, TrendingDown, DollarSign, Percent, BarChart2, Search, RefreshCw } from 'lucide-react'

export default function FundamentalsPage() {
  const [activeTab, setActiveTab] = useState<'equities' | 'crypto' | 'bonds'>('equities')
  const [symbol, setSymbol] = useState('')
  const [valuation, setValuation] = useState<EquityValuation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [cryptoProtocols, setCryptoProtocols] = useState<CryptoProtocolMetrics[]>([])
  const [cryptoLoading, setCryptoLoading] = useState(false)

  const [bondMetrics, setBondMetrics] = useState<BondMetrics[]>([])
  const [yieldCurve, setYieldCurve] = useState<YieldCurvePoint[]>([])
  const [bondsLoading, setBondsLoading] = useState(false)

  const [screenerResults, setScreenerResults] = useState<ScreenerResult[]>([])
  const [screenerLoading, setScreenerLoading] = useState(false)
  const [screenerFilters, setScreenerFilters] = useState<ScreenerFilter>({
    pe_ratio_min: 0,
    pe_ratio_max: 50,
    market_cap_min: 1e9,
    dividend_yield_min: 0,
  })

  const handleEquitySearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!symbol.trim()) return

    setLoading(true)
    setError('')
    setValuation(null)

    try {
      const response = await fundamentalsApi.getEquityFundamentals(symbol.toUpperCase())
      if (response.valuation) {
        setValuation(response.valuation)
      } else {
        setError('No fundamentals data found for this symbol')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch fundamentals')
    } finally {
      setLoading(false)
    }
  }

  const loadCryptoProtocols = async () => {
    setCryptoLoading(true)
    try {
      const response = await fundamentalsApi.getAllCryptoProtocols()
      setCryptoProtocols(response)
    } catch (err) {
      console.error('Failed to load crypto protocols:', err)
    } finally {
      setCryptoLoading(false)
    }
  }

  const loadBondData = async () => {
    setBondsLoading(true)
    try {
      const [bondsResponse, yieldResponse] = await Promise.all([
        fundamentalsApi.getBondMetrics(),
        fundamentalsApi.getYieldCurve(),
      ])
      setBondMetrics(bondsResponse)
      setYieldCurve(yieldResponse)
    } catch (err) {
      console.error('Failed to load bond data:', err)
    } finally {
      setBondsLoading(false)
    }
  }

  const runScreener = async () => {
    setScreenerLoading(true)
    try {
      const response = await fundamentalsApi.screenStocks(screenerFilters)
      setScreenerResults(response)
    } catch (err) {
      console.error('Failed to run screener:', err)
    } finally {
      setScreenerLoading(false)
    }
  }

  const MetricCard = ({
    title,
    value,
    subtitle,
    positive,
  }: {
    title: string
    value: string
    subtitle?: string
    positive?: boolean
  }) => (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <p className={`text-2xl font-bold ${positive ? 'text-green-600' : positive === false ? 'text-red-600' : ''}`}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Fundamental Data</h1>

      <div className="flex gap-2 mb-6">
        {(['equities', 'crypto', 'bonds'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'equities' && (
        <div className="space-y-6">
          <form onSubmit={handleEquitySearch} className="mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="Enter stock symbol (e.g., AAPL, MSFT)"
                className="flex-1 p-3 border border-gray-300 rounded-lg"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Search
              </button>
            </div>
          </form>

          {error && (
            <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {valuation && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <BarChart2 className="h-6 w-6" />
                {valuation.symbol} Valuation Metrics
              </h2>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard
                  title="Market Cap"
                  value={valuation.market_cap ? `$${(valuation.market_cap / 1e9).toFixed(2)}B` : 'N/A'}
                  subtitle="Total market value"
                />
                <MetricCard
                  title="P/E Ratio"
                  value={valuation.pe_ratio?.toFixed(2) || 'N/A'}
                  subtitle="Price to Earnings"
                  positive={!!(valuation.pe_ratio && valuation.pe_ratio < 20)}
                />
                <MetricCard
                  title="Forward P/E"
                  value={valuation.pe_forward?.toFixed(2) || 'N/A'}
                  subtitle="Forward earnings"
                />
                <MetricCard
                  title="P/B Ratio"
                  value={valuation.pb_ratio?.toFixed(2) || 'N/A'}
                  subtitle="Price to Book"
                />
                <MetricCard
                  title="P/S Ratio"
                  value={valuation.ps_ratio?.toFixed(2) || 'N/A'}
                  subtitle="Price to Sales"
                />
                <MetricCard
                  title="Dividend Yield"
                  value={valuation.dividend_yield ? `${(valuation.dividend_yield * 100).toFixed(2)}%` : 'N/A'}
                  subtitle="Annual dividend"
                />
                <MetricCard
                  title="Beta"
                  value={valuation.beta?.toFixed(2) || 'N/A'}
                  subtitle="Volatility vs market"
                />
                <MetricCard
                  title="ROE"
                  value={valuation.roe ? `${(valuation.roe * 100).toFixed(2)}%` : 'N/A'}
                  subtitle="Return on Equity"
                  positive={!!(valuation.roe && valuation.roe > 0.15)}
                />
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Stock Screener</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min P/E</label>
                <input
                  type="number"
                  value={screenerFilters.pe_ratio_min}
                  onChange={(e) => setScreenerFilters({ ...screenerFilters, pe_ratio_min: parseFloat(e.target.value) })}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max P/E</label>
                <input
                  type="number"
                  value={screenerFilters.pe_ratio_max}
                  onChange={(e) => setScreenerFilters({ ...screenerFilters, pe_ratio_max: parseFloat(e.target.value) })}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Market Cap ($)</label>
                <input
                  type="number"
                  value={screenerFilters.market_cap_min}
                  onChange={(e) => setScreenerFilters({ ...screenerFilters, market_cap_min: parseFloat(e.target.value) })}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Dividend Yield (%)</label>
                <input
                  type="number"
                  value={screenerFilters.dividend_yield_min}
                  onChange={(e) => setScreenerFilters({ ...screenerFilters, dividend_yield_min: parseFloat(e.target.value) })}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
            </div>
            <button
              onClick={runScreener}
              disabled={screenerLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {screenerLoading ? 'Searching...' : 'Find Stocks'}
            </button>

            {screenerResults.length > 0 && (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="p-3 text-left">Symbol</th>
                      <th className="p-3 text-left">Name</th>
                      <th className="p-3 text-right">Market Cap</th>
                      <th className="p-3 text-right">P/E</th>
                      <th className="p-3 text-right">Dividend</th>
                      <th className="p-3 text-right">Price</th>
                      <th className="p-3 text-right">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {screenerResults.map((result) => (
                      <tr key={result.symbol} className="border-b hover:bg-gray-50">
                        <td className="p-3 font-medium">{result.symbol}</td>
                        <td className="p-3">{result.name}</td>
                        <td className="p-3 text-right">${(result.market_cap / 1e9).toFixed(2)}B</td>
                        <td className="p-3 text-right">{result.pe_ratio?.toFixed(2) || 'N/A'}</td>
                        <td className="p-3 text-right">{result.dividend_yield ? `${(result.dividend_yield * 100).toFixed(2)}%` : 'N/A'}</td>
                        <td className="p-3 text-right">${result.price.toFixed(2)}</td>
                        <td className={`p-3 text-right ${result.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {result.change_percent >= 0 ? '+' : ''}{result.change_percent.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'crypto' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">DeFi Protocols</h2>
            <button
              onClick={loadCryptoProtocols}
              disabled={cryptoLoading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              {cryptoLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : null}
              Load Protocols
            </button>
          </div>

          {cryptoProtocols.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cryptoProtocols.map((protocol) => (
                <div key={protocol.protocol} className="bg-white rounded-lg shadow p-4">
                  <h3 className="font-bold text-lg mb-2">{protocol.protocol}</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-500">TVL</span>
                      <span className="font-medium">${(protocol.tvl || 0).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">24h Change</span>
                      <span className={`font-medium ${(protocol.tvl_change_24h || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {(protocol.tvl_change_24h || 0) >= 0 ? '+' : ''}{(protocol.tvl_change_24h || 0).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">7d Change</span>
                      <span className={`font-medium ${(protocol.tvl_change_7d || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {(protocol.tvl_change_7d || 0) >= 0 ? '+' : ''}{(protocol.tvl_change_7d || 0).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Staking Yield</span>
                      <span className="font-medium">{(protocol.staking_yield || 0).toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {cryptoProtocols.length === 0 && !cryptoLoading && (
            <div className="bg-gray-100 rounded-lg p-8 text-center text-gray-500">
              Click "Load Protocols" to view DeFi protocol data
            </div>
          )}
        </div>
      )}

      {activeTab === 'bonds' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Bond & Treasury Data</h2>
            <button
              onClick={loadBondData}
              disabled={bondsLoading}
              className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 flex items-center gap-2"
            >
              {bondsLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : null}
              Load Data
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-bold text-lg mb-4">Yield Curve</h3>
              {yieldCurve.length > 0 ? (
                <div className="space-y-2">
                  {yieldCurve.map((point) => (
                    <div key={point.maturity} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="font-medium">{point.maturity}</span>
                      <span className="text-lg font-bold text-amber-600">{(point.rate * 100).toFixed(3)}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No yield curve data available</p>
              )}
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-bold text-lg mb-4">Bond Metrics</h3>
              {bondMetrics.length > 0 ? (
                <div className="space-y-3">
                  {bondMetrics.slice(0, 10).map((bond) => (
                    <div key={bond.symbol} className="p-3 bg-gray-50 rounded">
                      <div className="flex justify-between mb-1">
                        <span className="font-medium">{bond.symbol}</span>
                        <span className="text-amber-600 font-bold">{(bond.yield_rate || 0).toFixed(3)}%</span>
                      </div>
                      <div className="flex justify-between text-sm text-gray-500">
                        <span>Price: ${(bond.price || 0).toFixed(2)}</span>
                        <span>Coupon: {(bond.coupon_rate || 0).toFixed(2)}%</span>
                        {bond.credit_rating && <span>Rating: {bond.credit_rating}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No bond metrics available</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
