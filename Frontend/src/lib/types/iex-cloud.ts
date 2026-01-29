/**
 * IEX Cloud Types
 * Types for IEX Cloud API responses - comprehensive stock fundamentals, earnings, ownership data
 */

// Company & Profile
export interface CompanyInfo {
  symbol: string
  companyName: string
  description: string
  industry: string
  sector: string
  CEO: string
  employees: number
  website: string
  country: string
  logo: string
  issueType?: string
  sectorKey?: string
}

// Key Statistics
export interface KeyStats {
  marketCap: number
  peRatio: number
  eps?: number
  divYield?: number
  beta: number
  week52High: number
  week52Low: number
  profitMargin?: number
  revenuePerShare?: number
  priceToBook: number
  priceToSales: number
  sharesOutstanding?: number
  avgVolume?: number
  ttmEPS?: number
  ttmDividendRate?: number
  dividendYieldPercentage?: number
}

// Advanced Statistics
export interface AdvancedStats {
  enterpriseValue: number
  forwardPE?: number
  pegRatio?: number
  sharesOutstanding: number
  revenueGrowth?: number
  netIncome?: number
  totalDebt?: number
  totalCash?: number
  currentDebt?: number
  currentAssets?: number
  currentLiabilities?: number
  bookValuePerShare?: number
  returnOnAssets?: number
  returnOnEquity?: number
  freeCashFlow?: number
  operatingMargin?: number
}

// Earnings
export interface EarningsReport {
  actualEPS: number
  estimatedEPS: number
  EPSSurprisePercent: number
  EPSSurpriseDollar?: number
  reportDate: string
  fiscalDate: string
  fiscalYear: number
  fiscalPeriod: number | null
  period: 'quarterly' | 'annual'
  announcementTime?: string
  currency?: string
}

// Analyst Estimates
export interface AnalystEstimates {
  estimatedEPS: number
  estimatedRevenue?: number
  estimatedChangePercent?: number
  fiscalYear: number
  fiscalPeriod: number
  currency?: string
  estimateCount?: number
}

// Ownership
export interface InstitutionalHolder {
  holder: string
  shares: number
  dateReported: string
  value: number
  pctHeld?: number
}

export interface InsiderTransaction {
  name: string
  action: 'buy' | 'sell' | 'sell_exercise'
  shares: number
  sharePrice: number
  date: string
  transactionId?: string
  totalInsiderShares?: number
}

// Peers
export interface PeerCompany {
  symbol: string
  name: string
  sector: string
  industry?: string
}

// Market Movers
export interface MarketMover {
  symbol: string
  latestPrice: number
  changePercent: number
  volume: number
  name?: string
}

// Sector Performance
export interface SectorPerformance {
  name: string
  performance: number
  sectorKey?: string
}

// Chart Data
export interface ChartDataPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  unadjustedVolume?: number
  change?: number
  changePercent?: number
  vwap?: number
}

// Quote Data
export interface Quote {
  symbol: string
  companyName?: string
  latestPrice: number
  change: number
  changePercent: number
  high: number
  low: number
  prevClose: number
  volume: number
  marketCap?: number
  peRatio?: number
  week52High?: number
  week52Low?: number
  avgTotalVolume?: number
  timestamp?: number
}

// Dividends
export interface Dividend {
  exDate: string
  paymentDate: string
  amount: number
  frequency: string
  currency?: string
}

// Splits
export interface StockSplit {
  exDate: string
  date: string
  ratio: number
  toFactor: number
  forFactor: number
}

// News
export interface NewsArticle {
  datetime: number
  headline: string
  source: string
  url: string
  summary?: string
  related?: string[]
  image?: string
}
