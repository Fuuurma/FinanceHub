/**
 * Economic Indicator Types
 * FRED Economic Data types
 */

export interface EconomicIndicator {
  id: string
  series_id: string
  title: string
  description: string
  units: string
  frequency: 'd' | 'w' | 'bw' | 'm' | 'q' | 'sa' | 'a'
  seasonal_adjustment: string
  last_updated: string
  observation_start: string
  observation_end: string
  popularity_score: number
  tags: string[]
}

export interface EconomicDataPoint {
  id: string
  indicator: string
  date: string
  value: number
  realtime_start: string
  realtime_end: string
}

export type Frequency = 'd' | 'w' | 'm' | 'q' | 'a'

export interface MacroDashboardData {
  gdp?: {
    observations: Array<{ date: string; value: string }>
    seriess?: Array<{
      title: string
      units: string
      frequency: string
    }>
  }
  cpi?: {
    observations: Array<{ date: string; value: string }>
  }
  unemployment?: {
    observations: Array<{ date: string; value: string }>
  }
  fed_funds_rate?: {
    observations: Array<{ date: string; value: string }>
  }
  treasury_yields?: Record<string, {
    name: string
    rate: number | null
    date: string | null
    series_id: string
  }>
  mortgage_rates?: Record<string, {
    rate: number | null
    date: string | null
  }>
  housing?: {
    housing_starts?: {
      value: number | null
      date: string | null
      units: string
    }
    building_permits?: {
      value: number | null
      date: string | null
      units: string
    }
  }
  consumer_sentiment?: {
    observations: Array<{ date: string; value: string }>
  }
  retail_sales?: {
    observations: Array<{ date: string; value: string }>
  }
  industrial_production?: {
    observations: Array<{ date: string; value: string }>
  }
  capacity_utilization?: {
    observations: Array<{ date: string; value: string }>
  }
  personal_saving_rate?: {
    observations: Array<{ date: string; value: string }>
  }
}

export interface YieldCurveData {
  [maturity: string]: {
    name: string
    rate: number | null
    date: string | null
    series_id: string
  }
}

export interface CreditSpreadsData {
  baa_aa_spread?: number | null
  aaa_aa_spread?: number | null
}

export interface InflationData {
  cpi?: number | null
  pce?: number | null
  core_cpi?: number | null
  core_pce?: number | null
  inflation_expectation_5y?: number | null
}

export interface EconomicIndicatorCard {
  id: string
  title: string
  value: number | string
  change?: number
  changeType?: 'positive' | 'negative' | 'neutral'
  unit: string
  date: string
  category: 'gdp' | 'inflation' | 'employment' | 'interest_rates' | 'housing' | 'consumer' | 'industrial'
  icon?: string
  description?: string
}

export interface YieldCurvePoint {
  maturity: string
  name: string
  rate: number
  date: string
}

export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

export interface DashboardConfig {
  visibleCategories: string[]
  defaultTimeframe: Frequency
  chartType: 'line' | 'bar' | 'area'
  showGridlines: boolean
  showAnnotations: boolean
  compactMode: boolean
}

export const DEFAULT_DASHBOARD_CONFIG: DashboardConfig = {
  visibleCategories: ['gdp', 'inflation', 'employment', 'interest_rates', 'housing'],
  defaultTimeframe: 'm',
  chartType: 'line',
  showGridlines: true,
  showAnnotations: false,
  compactMode: false,
}
