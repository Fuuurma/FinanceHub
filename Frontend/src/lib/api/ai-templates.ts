// AI Templates and Reports API Client

import { apiClient } from './client'
import type {
  Template,
  TemplateListResponse,
  TemplateDetailResponse,
  TemplateGenerateRequest,
  TemplateGenerateResponse,
  TierInfo,
  Report,
  ReportListResponse,
  RegenerateResponse,
  TemplateFilter,
  TemplateType,
} from '@/lib/types/ai-templates'

const AI_API_BASE = '/ai/v2'

// ================= TEMPLATES API =================

export async function listTemplates(params: TemplateFilter = {}): Promise<Template[]> {
  const query = new URLSearchParams()
  
  if (params.template_type) query.set('template_type', params.template_type)
  if (params.asset_class) query.set('asset_class', params.asset_class)
  if (params.symbol) query.set('symbol', params.symbol)
  if (params.sector) query.set('sector', params.sector)
  query.set('limit', '100')
  
  const response = await apiClient.get<TemplateListResponse>(
    `${AI_API_BASE}/templates?${query}`
  )
  return response.templates
}

export async function getTemplate(templateId: string): Promise<TemplateDetailResponse> {
  return apiClient.get<TemplateDetailResponse>(`${AI_API_BASE}/templates/${templateId}`)
}

export async function getTemplatesByType(
  templateType: TemplateType,
  symbol?: string
): Promise<Template[]> {
  const query = symbol ? `?symbol=${symbol}` : ''
  return apiClient.get<Template[]>(`${AI_API_BASE}/templates/type/${templateType}${query}`)
}

export async function getTemplateTypes(): Promise<TierInfo[]> {
  return apiClient.get<TierInfo[]>(`${AI_API_BASE}/templates/types`)
}

export async function getStaleTemplates(limit: number = 20): Promise<{
  count: number
  templates: Array<{
    id: string
    template_type: string
    symbol: string | null
    sector: string | null
    last_generated: string
    next_refresh: string
    age_hours: number
  }>
}> {
  return apiClient.get(`${AI_API_BASE}/templates/stale?limit=${limit}`)
}

export async function generateTemplate(
  request: TemplateGenerateRequest
): Promise<TemplateGenerateResponse> {
  return apiClient.post<TemplateGenerateResponse>(
    `${AI_API_BASE}/templates/generate`,
    request
  )
}

export async function refreshAllTemplates(): Promise<{
  status: string
  message: string
  estimated_time: string
}> {
  return apiClient.post(`${AI_API_BASE}/templates/refresh-all`)
}

// ================= REPORTS API =================

export async function listUserReports(
  limit: number = 20,
  offset: number = 0
): Promise<ReportListResponse> {
  return apiClient.get<ReportListResponse>(
    `${AI_API_BASE}/reports?limit=${limit}&offset=${offset}`
  )
}

export async function getReport(reportId: string): Promise<Report> {
  return apiClient.get<Report>(`${AI_API_BASE}/reports/${reportId}`)
}

export async function getPortfolioReport(
  portfolioId: string,
  reportType: string = 'portfolio_report'
): Promise<Report> {
  return apiClient.get<Report>(
    `${AI_API_BASE}/reports/portfolio/${portfolioId}?report_type=${reportType}`
  )
}

export async function regeneratePortfolioReport(
  portfolioId: string,
  reportType: string = 'portfolio_report'
): Promise<RegenerateResponse> {
  return apiClient.post<RegenerateResponse>(
    `${AI_API_BASE}/reports/portfolio/${portfolioId}/regenerate?report_type=${reportType}`
  )
}

export async function getLatestReports(limit: number = 5): Promise<{
  reports: Report[]
  count: number
}> {
  return apiClient.get(`${AI_API_BASE}/reports/latest?limit=${limit}`)
}

export async function deleteReport(reportId: string): Promise<{
  status: string
  report_id: string
}> {
  return apiClient.delete(`${AI_API_BASE}/reports/${reportId}`)
}

// ================= COMBINED EXPORTS =================

export const aiTemplatesApi = {
  // Templates
  listTemplates,
  getTemplate,
  getTemplatesByType,
  getTemplateTypes,
  getStaleTemplates,
  generateTemplate,
  refreshAllTemplates,
  
  // Reports
  listUserReports,
  getReport,
  getPortfolioReport,
  regeneratePortfolioReport,
  getLatestReports,
  deleteReport,
}

export default aiTemplatesApi
