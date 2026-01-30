// AI Advisor API Client
// Uses the smart proxy at localhost:8888/v4 for GLM-4.7

import {
  StrategyExplanationRequest,
  StrategyExplanationResponse,
  StrategySuggestionRequest,
  StrategySuggestionResponse,
  ForecastNarrativeRequest,
  ForecastNarrativeResponse,
  RiskExplanationRequest,
  RiskExplanationResponse,
  AccessStatusResponse,
  AIChatRequest,
  AIChatResponse,
  PortfolioAnalysisRequest,
  PortfolioAnalysisResponse,
  MarketAnalysisRequest,
  MarketAnalysisResponse,
  AIAdvisorError,
  FullMarketAnalysisResponse,
  SectorAnalysisResponse,
  RiskCommentaryResponse,
  VolatilityOutlookResponse,
  BondMarketResponse,
  AITemplateListResponse,
} from '@/lib/types/ai-advisor'
import { apiClient, ApiError } from './client'

const AI_API_BASE = '/ai'

async function handleAIResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({})) as AIAdvisorError
    throw new ApiError(
      error.error || 'AI request failed',
      response.status,
      error.code || 'AI_ERROR'
    )
  }
  return response.json()
}

export interface UsageStatsResponse {
  total_requests: number
  used_tokens: number
  remaining_tokens: number
  limit_type: string
  last_reset: string
  requests_this_month: number
  requests_limit: number
  plan_type: string
  reset_date: string
}

// ================= STRATEGY EXPLANATION =================

export async function explainStrategy(
  request: StrategyExplanationRequest
): Promise<StrategyExplanationResponse> {
  return apiClient.post<StrategyExplanationResponse>(`${AI_API_BASE}/explain-strategy`, request)
}

// ================= STRATEGY SUGGESTION =================

export async function suggestStrategy(
  request: StrategySuggestionRequest
): Promise<StrategySuggestionResponse> {
  return apiClient.post<StrategySuggestionResponse>(`${AI_API_BASE}/suggest-strategy`, request)
}

// ================= FORECAST NARRATIVE =================

export async function getForecastNarrative(
  request: ForecastNarrativeRequest
): Promise<ForecastNarrativeResponse[]> {
  const params: Record<string, string | number> = {
    symbols: request.symbols.join(','),
    horizon: request.horizon,
  }
  if (request.scenario) params.scenario = request.scenario
  if (request.include_sentiment !== undefined) params.include_sentiment = Number(request.include_sentiment)

  return apiClient.get<ForecastNarrativeResponse[]>(`${AI_API_BASE}/forecast-narrative`, { params })
}

// ================= RISK EXPLANATION =================

export async function explainRisk(
  request: RiskExplanationRequest
): Promise<RiskExplanationResponse> {
  const params: Record<string, string | number> = {
    metric: request.metric,
    value: request.value,
  }
  if (request.context) params.context = request.context
  if (request.asset) params.asset = request.asset

  return apiClient.get<RiskExplanationResponse>(`${AI_API_BASE}/explain-risk`, { params })
}

// ================= USAGE STATS =================

export async function getUsageStats(): Promise<UsageStatsResponse> {
  return apiClient.get<UsageStatsResponse>(`${AI_API_BASE}/usage`)
}

export async function checkAccessStatus(feature?: string): Promise<AccessStatusResponse> {
  const params = feature ? { feature } : undefined
  return apiClient.get<AccessStatusResponse>(`${AI_API_BASE}/access`, params ? { params } : undefined)
}

// ================= AI CHAT =================

export async function sendChatMessage(
  request: AIChatRequest
): Promise<AIChatResponse> {
  return apiClient.post<AIChatResponse>(`${AI_API_BASE}/chat`, request)
}

export async function* streamChatMessage(
  request: AIChatRequest
): AsyncGenerator<string, void, unknown> {
  const response = await fetch(`${apiClient.baseUrl}${AI_API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text-event-stream',
      ...apiClient.defaultHeaders,
    },
    body: JSON.stringify({ ...request, stream: true }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({})) as AIAdvisorError
    throw new ApiError(
      error.error || 'AI chat failed',
      response.status,
      error.code || 'AI_CHAT_ERROR'
    )
  }

  const reader = response.body?.getReader()
  if (!reader) throw new Error('No stream available')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') return
        try {
          const parsed = JSON.parse(data)
          if (parsed.token) yield parsed.token
        } catch {
          yield data
        }
      }
    }
  }
}

// ================= PORTFOLIO ANALYSIS =================

export async function analyzePortfolio(
  request: PortfolioAnalysisRequest
): Promise<PortfolioAnalysisResponse> {
  return apiClient.post<PortfolioAnalysisResponse>(`${AI_API_BASE}/portfolio-analysis`, request)
}

// ================= MARKET ANALYSIS =================

export async function analyzeMarket(
  request: MarketAnalysisRequest
): Promise<MarketAnalysisResponse> {
  const params: Record<string, string | number> = {}
  if (request.symbols) params.symbols = request.symbols.join(',')
  if (request.indices) params.indices = request.indices.join(',')
  if (request.include_sentiment !== undefined) params.include_sentiment = Number(request.include_sentiment)
  if (request.include_technical !== undefined) params.include_technical = Number(request.include_technical)

  return apiClient.get<MarketAnalysisResponse>(`${AI_API_BASE}/market-analysis`, { params })
}

// ================= ENHANCED AI ENDPOINTS (I4) =================

export async function getFullMarketAnalysis(
  symbol: string
): Promise<FullMarketAnalysisResponse> {
  return apiClient.get<FullMarketAnalysisResponse>(`${AI_API_BASE}/market/${symbol}/full`)
}

export async function getSectorAnalysis(
  sector: string
): Promise<SectorAnalysisResponse> {
  return apiClient.get<SectorAnalysisResponse>(`${AI_API_BASE}/sector/${encodeURIComponent(sector)}`)
}

export async function getRiskCommentary(): Promise<RiskCommentaryResponse> {
  return apiClient.get<RiskCommentaryResponse>(`${AI_API_BASE}/risk-commentary`)
}

export async function getVolatilityOutlook(
  symbol: string = 'SPY'
): Promise<VolatilityOutlookResponse> {
  return apiClient.get<VolatilityOutlookResponse>(`${AI_API_BASE}/volatility-outlook`, {
    params: { symbol }
  })
}

export async function getBondMarketAnalysis(): Promise<BondMarketResponse> {
  return apiClient.get<BondMarketResponse>(`${AI_API_BASE}/bond-market`)
}

export async function getAITemplates(
  templateType?: string,
  assetClass?: string
): Promise<AITemplateListResponse> {
  const params: Record<string, string> = {}
  if (templateType) params.template_type = templateType
  if (assetClass) params.asset_class = assetClass

  return apiClient.get<AITemplateListResponse>(`${AI_API_BASE}/templates`, { params })
}

// ================= AI ADVISOR API EXPORTS =================

export const aiAdvisorApi = {
  explainStrategy,
  suggestStrategy,
  getForecastNarrative,
  explainRisk,
  getUsageStats,
  checkAccessStatus,
  sendChatMessage,
  streamChatMessage,
  analyzePortfolio,
  analyzeMarket,
  // Enhanced AI endpoints (I4)
  getFullMarketAnalysis,
  getSectorAnalysis,
  getRiskCommentary,
  getVolatilityOutlook,
  getBondMarketAnalysis,
  getAITemplates,
}

export default aiAdvisorApi
