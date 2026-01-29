/**
 * SEC Filings API Client
 * Client for SEC Edgar API endpoints - company filings, insider trading, annual/quarterly reports
 */

import { apiClient } from './client'
import type {
  SECFiling,
  SECFilingList,
  AnnualReport,
  QuarterlyReport,
  CurrentReport,
  InsiderTrade,
  FilingsSummary,
  CompanyInfoSEC,
} from '@/lib/types/sec-filings'

export const secFilingsApi = {
  // Company Info
  getCompanyInfo: (symbol: string) =>
    apiClient.get<CompanyInfoSEC>(`/api/v1/sec-filings/company/${symbol}`),

  // All Filings
  getCompanyFilings: (symbol: string, count = 10) =>
    apiClient.get<SECFilingList>(`/api/v1/sec-filings/filings/${symbol}`, {
      params: { count }
    }),

  // Annual Reports (10-K)
  getAnnualReports: (symbol: string, count = 5) =>
    apiClient.get<AnnualReport[]>(`/api/v1/sec-filings/10k/${symbol}`, {
      params: { count }
    }),

  // Quarterly Reports (10-Q)
  getQuarterlyReports: (symbol: string, count = 5) =>
    apiClient.get<QuarterlyReport[]>(`/api/v1/sec-filings/10q/${symbol}`, {
      params: { count }
    }),

  // Current Reports (8-K)
  getCurrentReports: (symbol: string, count = 10) =>
    apiClient.get<CurrentReport[]>(`/api/v1/sec-filings/8k/${symbol}`, {
      params: { count }
    }),

  // Insider Transactions
  getInsiderTransactions: (symbol: string, count = 50) =>
    apiClient.get<InsiderTrade[]>(`/api/v1/sec-filings/insider/${symbol}`, {
      params: { count }
    }),

  // Filings Summary
  getFilingsSummary: (symbol: string) =>
    apiClient.get<FilingsSummary>(`/api/v1/sec-filings/summary/${symbol}`),

  // Proxy Statements (DEF 14A)
  getProxyStatements: (symbol: string, count = 5) =>
    apiClient.get<SECFiling[]>(`/api/v1/sec-filings/proxy/${symbol}`, {
      params: { count }
    }),

  // Registration Statements (S-1, S-3)
  getRegistrationStatements: (symbol: string, count = 5) =>
    apiClient.get<SECFiling[]>(`/api/v1/sec-filings/registration/${symbol}`, {
      params: { count }
    }),
}
