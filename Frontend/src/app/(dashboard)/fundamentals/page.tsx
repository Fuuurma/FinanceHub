'use client'

import { useState } from 'react'
import { fundamentalsApi } from '@/lib/api/fundamentals'
import type { EquityValuation, ScreenerResult } from '@/lib/types'

export default function FundamentalsPage() {
  const [symbol, setSymbol] = useState('')
  const [valuation, setValuation] = useState<EquityValuation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!symbol.trim()) return

    setLoading(true)
    setError('')
    setValuation(null)

    try {
      const response = await fundamentalsApi.getEquityFundamentals(symbol.toUpperCase())
      if (response.data.valuation) {
        setValuation(response.data.valuation)
      } else {
        setError('No fundamentals data found for this symbol')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch fundamentals')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Fundamental Data</h1>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="Enter stock symbol (e.g., AAPL)"
            className="flex-1 p-3 border border-gray-300 rounded-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 mb-6 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {valuation && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">
            {valuation.symbol} Valuation Metrics
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Market Cap</h3>
              <p className="text-2xl font-bold">
                {valuation.market_cap
                  ? `$${(valuation.market_cap / 1e9).toFixed(2)}B`
                  : 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">P/E Ratio</h3>
              <p className="text-2xl font-bold">
                {valuation.pe_ratio?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Forward P/E</h3>
              <p className="text-2xl font-bold">
                {valuation.pe_forward?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">P/B Ratio</h3>
              <p className="text-2xl font-bold">
                {valuation.pb_ratio?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">P/S Ratio</h3>
              <p className="text-2xl font-bold">
                {valuation.ps_ratio?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Dividend Yield</h3>
              <p className="text-2xl font-bold">
                {valuation.dividend_yield
                  ? `${(valuation.dividend_yield * 100).toFixed(2)}%`
                  : 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Beta</h3>
              <p className="text-2xl font-bold">
                {valuation.beta?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">ROE</h3>
              <p className="text-2xl font-bold">
                {valuation.roe ? `${(valuation.roe * 100).toFixed(2)}%` : 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Debt/Equity</h3>
              <p className="text-2xl font-bold">
                {valuation.debt_to_equity?.toFixed(2) || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Stock Screener</h2>
          <p className="text-gray-600 mb-4">
            Filter stocks by valuation metrics, market cap, and more.
          </p>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            Open Screener
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Crypto Protocols</h2>
          <p className="text-gray-600 mb-4">
            View TVL and metrics for DeFi protocols.
          </p>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            View Protocols
          </button>
        </div>
      </div>
    </div>
  )
}
