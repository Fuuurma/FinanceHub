export interface Dividend {
  id: string
  symbol: string
  ex_date: string
  pay_date: string
  record_date: string
  declared_date?: string
  amount: number
  frequency: 'quarterly' | 'monthly' | 'annual' | 'semi_annual' | 'special'
  type: 'regular' | 'special' | 'supplemental'
  currency: string
  note?: string
}

export interface DividendSummary {
  symbol: string
  total_paid: number
  payment_count: number
  avg_amount: number
  annual_yield_estimate: number
  next_ex_date?: string
  next_pay_date?: string
  next_amount?: number
}

export interface DividendHistoryResponse {
  dividends: Dividend[]
  summary: DividendSummary
  count: number
}
