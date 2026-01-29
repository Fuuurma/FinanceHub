/**
 * SEC Filings Types
 * Types for SEC Edgar API responses - company filings, insider trading, annual/quarterly reports
 */

export interface SECFiling {
  id: string
  symbol: string
  form_type: '10-K' | '10-Q' | '8-K' | '4' | 'DEF 14A' | 'S-1' | 'S-3' | '20-F' | '40-F'
  filed_at: string
  report_date: string
  document_url: string
  accession_number?: string
  file_number?: string
}

export interface SECFilingList {
  symbol: string
  filings: SECFiling[]
  total_filings: number
  last_updated: string
}

export interface AnnualReport {
  symbol: string
  form_type: '10-K' | '20-F' | '40-F'
  filed_at: string
  report_date: string
  fiscal_year: number
  document_url: string
  accession_number: string
}

export interface QuarterlyReport {
  symbol: string
  form_type: '10-Q'
  filed_at: string
  report_date: string
  fiscal_year: number
  fiscal_period: number
  document_url: string
  accession_number: string
}

export interface CurrentReport {
  symbol: string
  form_type: '8-K'
  filed_at: string
  report_date: string
  document_url: string
  accession_number: string
}

export interface InsiderTrade {
  name: string
  action: 'buy' | 'sell' | 'sell_exercise' | 'gift' | 'acquire' | 'dispose'
  shares: number
  price: number
  total_shares?: number
  date: string
  transaction_id?: string
  ownership_type?: string
}

export interface FilingsSummary {
  symbol: string
  total_filings: number
  filing_counts: {
    '10-K': number
    '10-Q': number
    '8-K': number
    '4': number
    other: number
  }
  last_updated: string
}

export interface CompanyInfoSEC {
  symbol: string
  cik: string
  name: string
  sic: string
  sic_description: string
  state_of_incorporation: string
  state_location: string
  fiscal_year_end: string
  business_address?: string
  mailing_address?: string
}
