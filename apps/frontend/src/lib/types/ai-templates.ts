// AI Templates and Reports Type Definitions

export type TemplateType =
  | 'market_summary'
  | 'asset_analysis'
  | 'sector_report'
  | 'risk_commentary'
  | 'sentiment_summary'
  | 'volatility_outlook'
  | 'options_strategy'
  | 'bond_market'
  | 'crypto_market'
  | 'earnings_preview'
  | 'macro_outlook'

export type ReportType =
  | 'portfolio_report'
  | 'holdings_analysis'
  | 'performance_attribution'
  | 'risk_assessment'
  | 'rebalancing_suggestion'
  | 'tax_efficiency'

export interface Template {
  id: string
  template_type: TemplateType
  symbol: string | null
  sector: string | null
  asset_class: string | null
  title: string
  summary: string
  content: string
  metadata: Record<string, unknown>
  version: number
  last_generated_at: string
  next_refresh_at: string
  is_active: boolean
  is_stale: boolean
  access_tier: 'free' | 'premium' | 'locked'
  tier_badge: string | null
}

export interface TemplateListResponse {
  templates: Template[]
  total: number
  limit: number
  offset: number
}

export interface TemplateDetailResponse {
  template: Template
  delta_update: DeltaUpdate | null
  related_templates: RelatedTemplate[]
}

export interface DeltaUpdate {
  type: 'price_change'
  symbol: string
  template_price: number
  current_price: number
  change_pct: number
  direction: 'up' | 'down'
  message: string
}

export interface RelatedTemplate {
  id: string
  type: TemplateType
  title: string
  summary: string
}

export interface TierInfo {
  template_type: TemplateType
  free_access: boolean
  premium_access: boolean
  description: string
}

export interface TemplateGenerateRequest {
  template_type: TemplateType
  symbol?: string
  sector?: string
  asset_class?: string
  force?: boolean
}

export interface TemplateGenerateResponse {
  id: string
  template_type: TemplateType
  symbol: string | null
  title: string
  status: 'generated' | 'queued'
  generated_at: string
}

export interface Report {
  id: string
  report_type: ReportType
  portfolio_id: string | null
  watchlist_id: string | null
  title: string
  summary: string
  content: string
  metadata: Record<string, unknown>
  version: number
  generated_at: string
  expires_at: string
  is_stale: boolean
  is_expired: boolean
  status: 'fresh' | 'stale' | 'generating' | 'expired'
}

export interface ReportListResponse {
  reports: Report[]
  total: number
  premium_reports: number
  free_reports: number
}

export interface RegenerateResponse {
  status: 'queued' | 'generating' | 'ready'
  report_id: string
  estimated_time: string
}

export interface TemplateFilter {
  template_type?: TemplateType
  asset_class?: string
  symbol?: string
  sector?: string
  tier?: 'all' | 'free' | 'premium'
}

export const TEMPLATE_TYPE_LABELS: Record<TemplateType, string> = {
  market_summary: 'Market Summary',
  asset_analysis: 'Asset Analysis',
  sector_report: 'Sector Report',
  risk_commentary: 'Risk Commentary',
  sentiment_summary: 'Sentiment Summary',
  volatility_outlook: 'Volatility Outlook',
  options_strategy: 'Options Strategy',
  bond_market: 'Bond Market',
  crypto_market: 'Crypto Market',
  earnings_preview: 'Earnings Preview',
  macro_outlook: 'Macro Outlook',
}

export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  portfolio_report: 'Portfolio Report',
  holdings_analysis: 'Holdings Analysis',
  performance_attribution: 'Performance Attribution',
  risk_assessment: 'Risk Assessment',
  rebalancing_suggestion: 'Rebalancing Suggestion',
  tax_efficiency: 'Tax Efficiency',
}

export const TIER_CONFIG = {
  free: {
    label: 'Free',
    badge: 'Free',
    color: 'bg-green-500',
  },
  premium: {
    label: 'Premium',
    badge: '⭐ Premium',
    color: 'bg-amber-500',
  },
  locked: {
    label: 'Locked',
    badge: '🔒 Premium',
    color: 'bg-gray-500',
  },
} as const

export const TEMPLATE_TIERS: Record<TemplateType, { free: boolean; premium: boolean }> = {
  market_summary: { free: true, premium: true },
  asset_analysis: { free: true, premium: true },
  sector_report: { free: false, premium: true },
  risk_commentary: { free: true, premium: true },
  sentiment_summary: { free: true, premium: true },
  volatility_outlook: { free: false, premium: true },
  options_strategy: { free: false, premium: true },
  bond_market: { free: false, premium: true },
  crypto_market: { free: true, premium: true },
  earnings_preview: { free: false, premium: true },
  macro_outlook: { free: false, premium: true },
}
