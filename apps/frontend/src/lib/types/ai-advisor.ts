// AI Advisor Types for FinanceHub

// ================= STRATEGY EXPLANATION =================

export interface StrategyExplanationRequest {
  strategy: string;
  underlying?: string;
  params?: Record<string, number>;
}

export interface StrategyExplanationResponse {
  strategy: string;
  explanation: string;
  risk_level: 'low' | 'medium' | 'high';
  max_profit?: string;
  max_loss?: string;
  breakeven_points?: string[];
  best_for?: string;
  example?: {
    setup: string;
    payoff_at_expiry: Record<string, number>;
  };
  generated_at: string;
}

// ================= STRATEGY SUGGESTION =================

export interface StrategySuggestionRequest {
  market_outlook: 'bullish' | 'bearish' | 'neutral' | 'volatile';
  risk_tolerance: 'low' | 'medium' | 'high';
  capital: number;
  time_horizon?: 'short' | 'medium' | 'long';
  underlying?: string;
}

export interface SuggestedStrategy {
  name: string;
  type: string;
  rationale: string;
  risk_level: 'low' | 'medium' | 'high';
  expected_return: string;
  capital_required: number;
  setup_steps: string[];
  key_metrics: {
    max_profit: string;
    max_loss: string;
    breakeven: string;
    delta?: number;
    theta?: number;
  };
}

export interface StrategySuggestionResponse {
  strategies: SuggestedStrategy[];
  market_context: string;
  generated_at: string;
}

// ================= FORECAST NARRATIVE =================

export interface ForecastNarrativeRequest {
  symbols: string[];
  horizon: '1d' | '1w' | '1m' | '3m';
  scenario?: 'base' | 'bull' | 'bear';
  include_sentiment?: boolean;
}

export interface ForecastDataPoint {
  date: string;
  predicted_price: number;
  confidence_lower: number;
  confidence_upper: number;
}

export interface ForecastNarrativeResponse {
  symbol: string;
  current_price: number;
  forecast: ForecastDataPoint[];
  narrative: string;
  key_factors: string[];
  sentiment_score: number;
  sentiment_label: 'bullish' | 'bearish' | 'neutral';
  generated_at: string;
}

// ================= RISK EXPLANATION =================

export interface RiskExplanationRequest {
  metric: string;
  value: number;
  context?: string;
  asset?: string;
}

export interface RiskExplanationResponse {
  metric: string;
  value: number;
  unit: string;
  explanation: string;
  interpretation: string;
  practical_example: string;
  related_metrics: string[];
  historical_context?: {
    percentile: number;
    comparison: string;
  };
  generated_at: string;
}

// ================= USAGE STATS =================

export interface UsageStatsResponse {
  requests_this_month: number;
  requests_limit: number;
  reset_date: string;
  usage_percentage: number;
  plan_type: string;
}

export interface AccessStatusResponse {
  has_access: boolean;
  feature: string;
  reason?: string;
  upgrade_required?: string;
}

// ================= AI CHAT =================

export interface AIChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachments?: ChatAttachment[];
}

export interface ChatAttachment {
  type: 'chart' | 'table' | 'strategy' | 'forecast';
  data: Record<string, unknown>;
  title?: string;
}

export interface AIChatRequest {
  message: string;
  context?: {
    portfolio_id?: string;
    symbols?: string[];
    timeframe?: string;
  };
  stream?: boolean;
}

export interface AIChatResponse {
  message: AIChatMessage;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

// ================= PORTFOLIO ANALYSIS =================

export interface PortfolioAnalysisRequest {
  portfolio_id?: string;
  holdings?: AdvisorHoldingInput[];
  include_recommendations?: boolean;
}

export interface AdvisorHoldingInput {
  symbol: string;
  quantity: number;
  avg_cost: number;
}

export interface PortfolioAnalysisResponse {
  overall_score: number;
  diversification_score: number;
  risk_score: number;
  opportunities: string[];
  risks: string[];
  recommendations: Recommendation[];
  generated_at: string;
}

export interface Recommendation {
  type: 'buy' | 'sell' | 'hold' | 'hedge';
  symbol: string;
  rationale: string;
  confidence: number;
  suggested_action?: string;
}

// ================= MARKET ANALYSIS =================

export interface MarketAnalysisRequest {
  symbols?: string[];
  indices?: string[];
  include_sentiment?: boolean;
  include_technical?: boolean;
}

export interface MarketAnalysisResponse {
  overview: {
    sentiment: 'bullish' | 'bearish' | 'neutral';
    sentiment_score: number;
    major_movements: MarketMovement[];
  };
  sectors: SectorAnalysis[];
  top_movers: AssetMovement[];
  risk_factors: string[];
  opportunities: string[];
  generated_at: string;
}

export interface MarketMovement {
  symbol: string;
  change: number;
  reason: string;
}

export interface SectorAnalysis {
  sector: string;
  performance: number;
  sentiment: string;
  top_assets: string[];
}

export interface AssetMovement {
  symbol: string;
  price: number;
  change: number;
  volume: number;
}

// ================= BATCH ANALYSIS =================

export interface BatchAnalysisRequest {
  requests: Array<{
    type: 'forecast' | 'strategy' | 'risk' | 'portfolio';
    payload: Record<string, unknown>;
  }>;
}

export interface BatchAnalysisResponse {
  results: Array<{
    type: string;
    success: boolean;
    data?: Record<string, unknown>;
    error?: string;
  }>;
  total_tokens: number;
  generated_at: string;
}

// ================= ENHANCED AI ANALYSIS (I4) =================

export interface FullMarketAnalysisRequest {
  symbol: string;
}

export interface FullMarketAnalysisResponse {
  symbol: string;
  title: string;
  content: string;
  summary: string;
  last_updated: string;
  version: number;
  next_refresh: string;
  is_premium_content: boolean;
}

export interface SectorAnalysisRequest {
  sector_name: string;
}

export interface SectorAnalysisResponse {
  sector: string;
  title: string;
  content: string;
  summary: string;
  last_updated: string;
}

export interface RiskCommentaryResponse {
  title: string;
  content: string;
  summary: string;
  last_updated: string;
}

export interface VolatilityOutlookRequest {
  symbol?: string;
}

export interface VolatilityOutlookResponse {
  symbol: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown>;
  last_updated: string;
}

export interface BondMarketAnalysisResponse {
  title: string;
  content: string;
  summary: string;
  last_updated: string;
  yield_data?: {
    treasury_10y: number;
    treasury_2y: number;
    corporate_ig: number;
    corporate_hy: number;
  };
}

// ================= ERROR TYPES =================

export interface AIAdvisorError {
  error: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface AnalysisTemplate {
  id: string;
  name: string;
  description: string;
  category: 'market' | 'portfolio' | 'strategy' | 'risk';
  fields: TemplateField[];
}

export interface TemplateField {
  key: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'date';
  required: boolean;
  options?: string[];
}

export interface AITemplateListResponse {
  templates: AnalysisTemplate[];
  total: number;
  page: number;
  page_size: number;
}

export function isAIAdvisorError(obj: unknown): obj is AIAdvisorError {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'error' in obj &&
    'code' in obj
  );
}

// ================= HELPER FUNCTIONS =================

export function formatSentimentScore(score: number): string {
  if (score >= 0.7) return 'Strongly Bullish';
  if (score >= 0.5) return 'Bullish';
  if (score >= 0.3) return 'Slightly Bullish';
  if (score >= -0.3) return 'Neutral';
  if (score >= -0.5) return 'Slightly Bearish';
  if (score >= -0.7) return 'Bearish';
  return 'Strongly Bearish';
}

export function getRiskColor(risk: 'low' | 'medium' | 'high'): string {
  switch (risk) {
    case 'low':
      return 'text-green-500';
    case 'medium':
      return 'text-yellow-500';
    case 'high':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
}

export function getRiskBgColor(risk: 'low' | 'medium' | 'high'): string {
  switch (risk) {
    case 'low':
      return 'bg-green-500/10 border-green-500';
    case 'medium':
      return 'bg-yellow-500/10 border-yellow-500';
    case 'high':
      return 'bg-red-500/10 border-red-500';
    default:
      return 'bg-gray-500/10 border-gray-500';
  }
}

