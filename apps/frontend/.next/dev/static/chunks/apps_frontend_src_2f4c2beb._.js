(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/apps/frontend/src/lib/utils.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn,
    "formatCurrency",
    ()=>formatCurrency,
    "formatDate",
    ()=>formatDate,
    "formatDateTime",
    ()=>formatDateTime,
    "formatNumber",
    ()=>formatNumber,
    "formatPercent",
    ()=>formatPercent,
    "formatTime",
    ()=>formatTime
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-client] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
function formatCurrency(value, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}
function formatPercent(value, decimals = 2) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(decimals)}%`;
}
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
function formatDateTime(date) {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}
function formatNumber(value) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numValue);
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ApiError",
    ()=>ApiError,
    "apiClient",
    ()=>apiClient
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/apps/frontend/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
/**
 * API Client
 * Centralized HTTP client with interceptors and error handling
 */ const API_BASE_URL = __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
class ApiError extends Error {
    status;
    code;
    constructor(message, status, code){
        super(message), this.status = status, this.code = code;
        this.name = 'ApiError';
    }
}
class ApiClient {
    baseUrl;
    defaultHeaders;
    constructor(baseUrl){
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }
    getAuthHeaders() {
        if ("TURBOPACK compile-time truthy", 1) {
            const token = localStorage.getItem('access_token');
            if (token) {
                return {
                    Authorization: `Bearer ${token}`
                };
            }
        }
        return {};
    }
    buildUrl(endpoint, params) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        if (params) {
            Object.entries(params).forEach(([key, value])=>{
                url.searchParams.set(key, String(value));
            });
        }
        return url.toString();
    }
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        if (!response.ok) {
            let errorMessage = 'An error occurred';
            if (contentType?.includes('application/json')) {
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {}
            }
            throw new ApiError(errorMessage, response.status, response.headers.get('x-error-code') || undefined);
        }
        if (contentType?.includes('application/json')) {
            return response.json();
        }
        return response.text();
    }
    async request(method, endpoint, options = {}) {
        const { headers, params, body, ...rest } = options;
        const url = this.buildUrl(endpoint, params);
        const config = {
            method,
            headers: {
                ...this.defaultHeaders,
                ...this.getAuthHeaders(),
                ...headers
            },
            ...rest
        };
        if (body) {
            config.body = JSON.stringify(body);
        }
        try {
            const response = await fetch(url, config);
            return await this.handleResponse(response);
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            console.error('API request failed:', error);
            throw new ApiError('Network error occurred', 0, 'NETWORK_ERROR');
        }
    }
    async get(endpoint, options) {
        return this.request('GET', endpoint, options);
    }
    async post(endpoint, data, options) {
        return this.request('POST', endpoint, {
            ...options,
            body: data
        });
    }
    async put(endpoint, data, options) {
        return this.request('PUT', endpoint, {
            ...options,
            body: data
        });
    }
    async patch(endpoint, data, options) {
        return this.request('PATCH', endpoint, {
            ...options,
            body: data
        });
    }
    async delete(endpoint, options) {
        return this.request('DELETE', endpoint, options);
    }
    setAuthToken(token) {
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.setItem('access_token', token);
        }
    }
    clearAuthToken() {
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.removeItem('access_token');
        }
    }
    getAuthToken() {
        if ("TURBOPACK compile-time truthy", 1) {
            return localStorage.getItem('access_token');
        }
        //TURBOPACK unreachable
        ;
    }
    setRefreshToken(token) {
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.setItem('refresh_token', token);
        }
    }
    getRefreshToken() {
        if ("TURBOPACK compile-time truthy", 1) {
            return localStorage.getItem('refresh_token');
        }
        //TURBOPACK unreachable
        ;
    }
}
const apiClient = new ApiClient(API_BASE_URL);
;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/portfolio.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "portfoliosApi",
    ()=>portfoliosApi
]);
/**
 * Portfolios API
 * All portfolio-related API calls for portfolio management
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
;
const portfoliosApi = {
    /**
   * Get all user portfolios (alias for list)
   */ getPortfolios: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/portfolios/'),
    /**
   * Get all user portfolios
   */ list: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/portfolios/'),
    /**
   * Get single portfolio by ID
   */ getPortfolio: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/`),
    /**
   * Create new portfolio
   */ createPortfolio: (data)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post('/portfolios/', data),
    /**
   * Update portfolio
   */ updatePortfolio: (portfolioId, data)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].put(`/portfolios/${portfolioId}/`, data),
    /**
   * Delete portfolio
   */ deletePortfolio: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].delete(`/portfolios/${portfolioId}/`),
    /**
   * Get portfolio holdings
   */ getHoldings: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/holdings/`),
    /**
   * Get holdings summary
   */ getHoldingsSummary: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/holdings-summary/`),
    /**
   * Get portfolio transactions
   */ getTransactions: (portfolioId, filter)=>{
        const params = {};
        if (filter) {
            if (filter.type) params.type = filter.type;
            if (filter.symbol) params.symbol = filter.symbol;
            if (filter.asset_type) params.asset_type = filter.asset_type;
            if (filter.start_date) params.start_date = filter.start_date;
            if (filter.end_date) params.end_date = filter.end_date;
        }
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/transactions/`, {
            params
        });
    },
    /**
   * Get portfolio history (value over time)
   */ getHistory: (portfolioId, period = '1m')=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/history/`, {
            params: {
                period
            }
        }),
    /**
   * Get portfolio performance metrics
   */ getMetrics: (portfolioId, period = '1m')=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/metrics/`, {
            params: {
                period
            }
        }),
    /**
   * Add holding to portfolio
   */ addHolding: (portfolioId, data)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`/portfolios/${portfolioId}/holdings/`, data),
    /**
   * Update holding
   */ updateHolding: (portfolioId, holdingId, data)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].put(`/portfolios/${portfolioId}/holdings/${holdingId}/`, data),
    /**
   * Remove holding from portfolio
   */ removeHolding: (portfolioId, holdingId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].delete(`/portfolios/${portfolioId}/holdings/${holdingId}/`),
    /**
   * Add transaction to portfolio
   */ addTransaction: (portfolioId, data)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`/portfolios/${portfolioId}/transactions/`, data)
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/utils/attribution-calculations.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "BENCHMARK_CATEGORIES",
    ()=>BENCHMARK_CATEGORIES,
    "BENCHMARK_CONFIGS",
    ()=>BENCHMARK_CONFIGS,
    "DEFAULT_ATTRIBUTION_PERIODS",
    ()=>DEFAULT_ATTRIBUTION_PERIODS,
    "calculateAssetClassAttribution",
    ()=>calculateAssetClassAttribution,
    "calculateAttributionSummary",
    ()=>calculateAttributionSummary,
    "calculateBenchmarkComparison",
    ()=>calculateBenchmarkComparison,
    "calculateBrinsonFachlerAttribution",
    ()=>calculateBrinsonFachlerAttribution,
    "calculateHoldingAttribution",
    ()=>calculateHoldingAttribution,
    "calculateSectorAttribution",
    ()=>calculateSectorAttribution,
    "filterAttribution",
    ()=>filterAttribution,
    "formatAttributionValue",
    ()=>formatAttributionValue,
    "generateAttributionTrend",
    ()=>generateAttributionTrend,
    "getAttributionPeriodData",
    ()=>getAttributionPeriodData,
    "getBenchmarkReturn",
    ()=>getBenchmarkReturn,
    "sortAttribution",
    ()=>sortAttribution
]);
function createFastHoldingData(holdings) {
    return {
        ids: holdings.map((h)=>h.id),
        symbols: holdings.map((h)=>h.symbol),
        names: holdings.map((h)=>h.name),
        sectors: holdings.map((h)=>h.sector || 'Other'),
        assetClasses: holdings.map((h)=>h.asset_class),
        currentValues: Float64Array.from(holdings.map((h)=>h.current_value)),
        avgCosts: Float64Array.from(holdings.map((h)=>h.average_cost)),
        currentPrices: Float64Array.from(holdings.map((h)=>h.current_price)),
        unrealizedPnls: Float64Array.from(holdings.map((h)=>h.unrealized_pnl))
    };
}
function calculateTotalValueFast(data) {
    let total = 0;
    const values = data.currentValues;
    for(let i = 0; i < values.length; i++){
        total += values[i];
    }
    return total;
}
function calculateWeightsFast(data, totalValue) {
    const weights = new Float64Array(data.currentValues.length);
    if (totalValue > 0) {
        for(let i = 0; i < weights.length; i++){
            weights[i] = data.currentValues[i] / totalValue * 100;
        }
    }
    return weights;
}
function calculateReturnsFast(data) {
    const returns = new Float64Array(data.currentValues.length);
    for(let i = 0; i < returns.length; i++){
        if (data.avgCosts[i] > 0) {
            returns[i] = (data.currentPrices[i] - data.avgCosts[i]) / data.avgCosts[i] * 100;
        }
    }
    return returns;
}
function calculateContributionsFast(weights, returns) {
    const contributions = new Float64Array(weights.length);
    for(let i = 0; i < contributions.length; i++){
        contributions[i] = weights[i] / 100 * returns[i];
    }
    return contributions;
}
const DEFAULT_ATTRIBUTION_PERIODS = [
    {
        value: '1d',
        label: '1D'
    },
    {
        value: '1w',
        label: '1W'
    },
    {
        value: '1m',
        label: '1M'
    },
    {
        value: '3m',
        label: '3M'
    },
    {
        value: '6m',
        label: '6M'
    },
    {
        value: '1y',
        label: '1Y'
    },
    {
        value: '2y',
        label: '2Y'
    },
    {
        value: '3y',
        label: '3Y'
    },
    {
        value: '5y',
        label: '5Y'
    },
    {
        value: 'ytd',
        label: 'YTD'
    },
    {
        value: 'all',
        label: 'All'
    }
];
const BENCHMARK_CONFIGS = [
    {
        type: 'sp500',
        name: 'S&P 500',
        description: '500 largest US companies',
        category: 'us_indices',
        annualized_return: 0.10,
        volatility: 0.15
    },
    {
        type: 'nasdaq100',
        name: 'NASDAQ-100',
        description: '100 largest non-financial stocks',
        category: 'us_indices',
        annualized_return: 0.14,
        volatility: 0.20
    },
    {
        type: 'dow30',
        name: 'Dow Jones 30',
        description: '30 blue-chip companies',
        category: 'us_indices',
        annualized_return: 0.09,
        volatility: 0.13
    },
    {
        type: 'russell2000',
        name: 'Russell 2000',
        description: '2000 small-cap companies',
        category: 'us_indices',
        annualized_return: 0.08,
        volatility: 0.22
    },
    {
        type: 'vti',
        name: 'VTI',
        description: 'Vanguard Total Stock Market',
        category: 'etf',
        annualized_return: 0.10,
        volatility: 0.16
    },
    {
        type: 'qqq',
        name: 'QQQ',
        description: 'Invesco NASDAQ 100',
        category: 'etf',
        annualized_return: 0.14,
        volatility: 0.21
    },
    {
        type: 'spy',
        name: 'SPY',
        description: 'SPDR S&P 500 ETF',
        category: 'etf',
        annualized_return: 0.10,
        volatility: 0.15
    },
    {
        type: 'dia',
        name: 'DIA',
        description: 'SPDR Dow Jones ETF',
        category: 'etf',
        annualized_return: 0.09,
        volatility: 0.13
    },
    {
        type: 'iwm',
        name: 'IWM',
        description: 'iShares Russell 2000',
        category: 'etf',
        annualized_return: 0.08,
        volatility: 0.22
    },
    {
        type: 'vgt',
        name: 'VGT',
        description: 'Vanguard Information Tech',
        category: 'etf',
        annualized_return: 0.16,
        volatility: 0.24
    },
    {
        type: 'vht',
        name: 'VHT',
        description: 'Vanguard Health Care',
        category: 'etf',
        annualized_return: 0.11,
        volatility: 0.15
    },
    {
        type: 'vcr',
        name: 'VCR',
        description: 'Vanguard Consumer Disc.',
        category: 'etf',
        annualized_return: 0.10,
        volatility: 0.18
    },
    {
        type: 'vdc',
        name: 'VDC',
        description: 'Vanguard Consumer Staples',
        category: 'etf',
        annualized_return: 0.08,
        volatility: 0.12
    },
    {
        type: 'ven',
        name: 'VEN',
        description: 'Vanguard Energy',
        category: 'etf',
        annualized_return: 0.07,
        volatility: 0.28
    },
    {
        type: 'vfi',
        name: 'VFI',
        description: 'Vanguard Financials',
        category: 'etf',
        annualized_return: 0.09,
        volatility: 0.20
    },
    {
        type: 'viu',
        name: 'VIU',
        description: 'Vanguard Developed ex-US',
        category: 'international',
        annualized_return: 0.06,
        volatility: 0.18
    },
    {
        type: 'acwx',
        name: 'ACWX',
        description: 'iShares MSCI AC World ex-US',
        category: 'international',
        annualized_return: 0.05,
        volatility: 0.17
    },
    {
        type: 'bnd',
        name: 'BND',
        description: 'Vanguard Total Bond Market',
        category: 'bonds',
        annualized_return: 0.04,
        volatility: 0.06
    },
    {
        type: 'agg',
        name: 'AGG',
        description: 'iShares Core US Aggregate',
        category: 'bonds',
        annualized_return: 0.03,
        volatility: 0.05
    },
    {
        type: 'tlt',
        name: 'TLT',
        description: 'iShares 20+ Year Treasury',
        category: 'bonds',
        annualized_return: 0.02,
        volatility: 0.20
    },
    {
        type: 'gld',
        name: 'GLD',
        description: 'SPDR Gold Shares',
        category: 'custom',
        annualized_return: 0.06,
        volatility: 0.16
    },
    {
        type: 'bitcoin',
        name: 'Bitcoin',
        description: 'BTC/USD',
        category: 'crypto',
        annualized_return: 0.45,
        volatility: 0.70
    },
    {
        type: 'ethereum',
        name: 'Ethereum',
        description: 'ETH/USD',
        category: 'crypto',
        annualized_return: 0.35,
        volatility: 0.65
    }
];
const BENCHMARK_CATEGORIES = [
    {
        value: 'us_indices',
        label: 'US Indices'
    },
    {
        value: 'etf',
        label: 'ETFs'
    },
    {
        value: 'crypto',
        label: 'Cryptocurrency'
    },
    {
        value: 'bonds',
        label: 'Bonds'
    },
    {
        value: 'international',
        label: 'International'
    }
];
function calculateHoldingAttribution(holdings, periodReturn = 0) {
    if (holdings.length === 0) return [];
    const data = createFastHoldingData(holdings);
    const totalValue = calculateTotalValueFast(data);
    const weights = calculateWeightsFast(data, totalValue);
    const returns = calculateReturnsFast(data);
    const contributions = calculateContributionsFast(weights, returns);
    const result = new Array(holdings.length);
    for(let i = 0; i < holdings.length; i++){
        const contributionPercent = periodReturn !== 0 ? contributions[i] / periodReturn * 100 : 0;
        result[i] = {
            holding_id: data.ids[i],
            symbol: data.symbols[i],
            name: data.names[i],
            sector: data.sectors[i],
            asset_class: data.assetClasses[i],
            weight: weights[i],
            return: returns[i],
            contribution: contributions[i],
            contribution_percent: isNaN(contributionPercent) ? 0 : contributionPercent,
            value_start: data.currentValues[i] / (1 + returns[i] / 100),
            value_end: data.currentValues[i],
            value_change: data.unrealizedPnls[i],
            avg_weight: weights[i]
        };
    }
    result.sort((a, b)=>b.contribution - a.contribution);
    return result;
}
function calculateSectorAttribution(holdings, periodReturn = 0) {
    const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn);
    const totalValue = holdings.reduce((sum, h)=>sum + h.current_value, 0);
    const sectorMap = new Map();
    const sectorWeights = new Map();
    const sectorContributions = new Map();
    const sectorHoldingsCount = new Map();
    const sectorTopHoldings = new Map();
    for (const h of holdingAttribution){
        const key = h.sector;
        if (!sectorMap.has(key)) {
            sectorMap.set(key, []);
            sectorWeights.set(key, 0);
            sectorContributions.set(key, 0);
            sectorHoldingsCount.set(key, 0);
            sectorTopHoldings.set(key, {
                symbol: '',
                contribution: -Infinity,
                return: 0
            });
        }
        const contributions = sectorMap.get(key);
        contributions.push(h.contribution);
        sectorWeights.set(key, sectorWeights.get(key) + h.weight);
        sectorContributions.set(key, sectorContributions.get(key) + h.contribution);
        sectorHoldingsCount.set(key, sectorHoldingsCount.get(key) + 1);
        const topHolding = sectorTopHoldings.get(key);
        if (h.contribution > topHolding.contribution) {
            sectorTopHoldings.set(key, {
                symbol: h.symbol,
                contribution: h.contribution,
                return: h.return
            });
        }
    }
    const sectors = [];
    sectorMap.forEach((_, sector)=>{
        const weight = sectorWeights.get(sector);
        const contribution = sectorContributions.get(sector);
        const count = sectorHoldingsCount.get(sector);
        const topHolding = sectorTopHoldings.get(sector);
        const sectorReturn = weight > 0 ? contribution / (weight / 100) : 0;
        const allocationEffect = (weight - 10) * sectorReturn * 0.1;
        const selectionEffect = contribution - allocationEffect;
        sectors.push({
            sector,
            weight,
            return: sectorReturn,
            contribution,
            contribution_percent: totalValue > 0 ? contribution / periodReturn * 100 : 0,
            holdings_count: count,
            top_holding: topHolding.symbol,
            top_holding_return: topHolding.return,
            allocation_effect: allocationEffect,
            selection_effect: selectionEffect,
            total_effect: contribution
        });
    });
    return sectors.sort((a, b)=>b.contribution - a.contribution);
}
function calculateAssetClassAttribution(holdings, periodReturn = 0) {
    const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn);
    const totalValue = holdings.reduce((sum, h)=>sum + h.current_value, 0);
    const classMap = new Map();
    for (const h of holdingAttribution){
        const key = h.asset_class;
        if (!classMap.has(key)) {
            classMap.set(key, {
                weight: 0,
                contribution: 0,
                holdings: 0,
                sectors: new Set()
            });
        }
        const entry = classMap.get(key);
        entry.weight += h.weight;
        entry.contribution += h.contribution;
        entry.holdings++;
        entry.sectors.add(h.sector);
    }
    const classes = [];
    classMap.forEach((value, assetClass)=>{
        const classReturn = value.weight > 0 ? value.contribution / (value.weight / 100) : 0;
        classes.push({
            asset_class: assetClass,
            weight: value.weight,
            return: classReturn,
            contribution: value.contribution,
            contribution_percent: totalValue > 0 ? value.contribution / periodReturn * 100 : 0,
            holdings_count: value.holdings,
            sectors_count: value.sectors.size
        });
    });
    return classes.sort((a, b)=>b.contribution - a.contribution);
}
function calculateAttributionSummary(holdings, periodReturn = 0) {
    const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn);
    const sectorAttribution = calculateSectorAttribution(holdings, periodReturn);
    const totalContribution = holdingAttribution.reduce((sum, h)=>sum + h.contribution, 0);
    const allocationEffect = sectorAttribution.reduce((sum, s)=>sum + s.allocation_effect, 0);
    const selectionEffect = sectorAttribution.reduce((sum, s)=>sum + s.selection_effect, 0);
    const positiveHoldings = holdingAttribution.filter((h)=>h.contribution > 0).length;
    const negativeHoldings = holdingAttribution.filter((h)=>h.contribution < 0).length;
    const neutralHoldings = holdingAttribution.filter((h)=>h.contribution === 0).length;
    return {
        total_return: periodReturn,
        total_contribution: totalContribution,
        allocation_effect: allocationEffect,
        selection_effect: selectionEffect,
        total_effect: totalContribution,
        top_contributor: holdingAttribution[0] || null,
        bottom_contributor: holdingAttribution[holdingAttribution.length - 1] || null,
        best_sector: sectorAttribution[0] || null,
        worst_sector: sectorAttribution[sectorAttribution.length - 1] || null,
        positive_holdings: positiveHoldings,
        negative_holdings: negativeHoldings,
        neutral_holdings: neutralHoldings
    };
}
function calculateBenchmarkComparison(summary, holdings, benchmark, period) {
    const periodMultipliers = {
        '1d': 365,
        '1w': 52,
        '1m': 12,
        '3m': 4,
        '6m': 2,
        '1y': 1,
        '2y': 0.5,
        '3y': 0.333,
        '5y': 0.2,
        'ytd': 1.5,
        'all': 0.5
    };
    const multiplier = periodMultipliers[period] || 1;
    const benchmarkReturn = (benchmark.annualized_return || 0.10) * multiplier;
    const excessReturn = summary.total_return - benchmarkReturn;
    const excessReturnPercent = benchmarkReturn !== 0 ? excessReturn / Math.abs(benchmarkReturn) * 100 : 0;
    const trackingError = Math.abs(excessReturn) * 0.8;
    const informationRatio = trackingError !== 0 ? excessReturn / trackingError : 0;
    const beta = (benchmark.volatility || 0.15) > 0 ? 1 + (Math.random() * 0.2 - 0.1) : 1;
    const correlation = 0.85 + Math.random() * 0.1;
    const sectorAttribution = calculateSectorAttribution(holdings, summary.total_return);
    const sectorOutperformance = sectorAttribution.filter((s)=>s.return > benchmarkReturn);
    const sectorUnderperformance = sectorAttribution.filter((s)=>s.return < benchmarkReturn);
    const comparison = {
        benchmark_type: benchmark.type,
        benchmark_return: benchmarkReturn,
        portfolio_return: summary.total_return,
        excess_return: excessReturn,
        excess_return_percent: excessReturnPercent,
        tracking_error: trackingError,
        information_ratio: informationRatio,
        beta: beta,
        correlation: correlation,
        sector_outperformance: sectorOutperformance.slice(0, 3),
        sector_underperformance: sectorUnderperformance.slice(0, 3)
    };
    return {
        ...summary,
        benchmark_comparison: comparison
    };
}
function getBenchmarkReturn(benchmark, period) {
    const config = BENCHMARK_CONFIGS.find((b)=>b.type === benchmark);
    if (!config || !config.annualized_return) return 0.10;
    const periodMultipliers = {
        '1d': 1 / 365,
        '1w': 7 / 365,
        '1m': 30 / 365,
        '3m': 90 / 365,
        '6m': 180 / 365,
        '1y': 1,
        '2y': 2,
        '3y': 3,
        '5y': 5,
        'ytd': new Date().getMonth() / 12,
        'all': 3
    };
    const multiplier = periodMultipliers[period] || 1;
    return config.annualized_return * multiplier;
}
function generateAttributionTrend(dailyReturns) {
    let cumulativeContribution = 0;
    return dailyReturns.map((day)=>{
        cumulativeContribution += day.return;
        return {
            date: day.date,
            daily_return: day.return,
            cumulative_contribution: cumulativeContribution,
            allocation_effect: day.return * 0.4,
            selection_effect: day.return * 0.6
        };
    });
}
function filterAttribution(holdings, filters) {
    let filtered = [
        ...holdings
    ];
    if (filters.asset_class && filters.asset_class.length > 0) {
        filtered = filtered.filter((h)=>filters.asset_class.includes(h.asset_class));
    }
    if (filters.sector && filters.sector.length > 0) {
        filtered = filtered.filter((h)=>filters.sector.includes(h.sector || 'Other'));
    }
    return filtered;
}
function sortAttribution(holdings, sortBy = 'contribution', sortOrder = 'desc') {
    const attribution = calculateHoldingAttribution(holdings);
    return attribution.sort((a, b)=>{
        let comparison = 0;
        switch(sortBy){
            case 'contribution':
                comparison = a.contribution - b.contribution;
                break;
            case 'return':
                comparison = a.return - b.return;
                break;
            case 'weight':
                comparison = a.weight - b.weight;
                break;
            case 'name':
                comparison = a.name.localeCompare(b.name);
                break;
        }
        return sortOrder === 'desc' ? -comparison : comparison;
    });
}
function getAttributionPeriodData(periodAttributions, period) {
    return periodAttributions.find((p)=>p.period === period) || null;
}
function calculateBrinsonFachlerAttribution(portfolioWeight, benchmarkWeight, portfolioReturn, benchmarkReturn) {
    const weightDiff = portfolioWeight - benchmarkWeight;
    const returnDiff = portfolioReturn - benchmarkReturn;
    const allocation = weightDiff * benchmarkReturn;
    const selection = portfolioWeight * returnDiff;
    const interaction = weightDiff * returnDiff;
    const total = allocation + selection + interaction;
    return {
        allocation: Math.round(allocation * 100) / 100,
        selection: Math.round(selection * 100) / 100,
        interaction: Math.round(interaction * 100) / 100,
        total: Math.round(total * 100) / 100
    };
}
function formatAttributionValue(value) {
    const formatted = Math.abs(value).toFixed(2);
    return value >= 0 ? `+${formatted}%` : `-${formatted}%`;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/types/attribution.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "BENCHMARK_CATEGORIES",
    ()=>BENCHMARK_CATEGORIES,
    "BENCHMARK_CONFIGS",
    ()=>BENCHMARK_CONFIGS,
    "DEFAULT_ATTRIBUTION_PERIODS",
    ()=>DEFAULT_ATTRIBUTION_PERIODS,
    "SECTOR_COLORS",
    ()=>SECTOR_COLORS
]);
const SECTOR_COLORS = {
    'Technology': '#3B82F6',
    'Healthcare': '#10B981',
    'Financial': '#F59E0B',
    'Consumer': '#EC4899',
    'Energy': '#EF4444',
    'Industrial': '#8B5CF6',
    'Materials': '#06B6D4',
    'Real Estate': '#14B8A6',
    'Utilities': '#F97316',
    'Communication': '#6366F1',
    'Other': '#6B7280'
};
const DEFAULT_ATTRIBUTION_PERIODS = [
    {
        value: '1d',
        label: '1D'
    },
    {
        value: '1w',
        label: '1W'
    },
    {
        value: '1m',
        label: '1M'
    },
    {
        value: '3m',
        label: '3M'
    },
    {
        value: '6m',
        label: '6M'
    },
    {
        value: '1y',
        label: '1Y'
    },
    {
        value: '2y',
        label: '2Y'
    },
    {
        value: '3y',
        label: '3Y'
    },
    {
        value: '5y',
        label: '5Y'
    },
    {
        value: 'ytd',
        label: 'YTD'
    },
    {
        value: 'all',
        label: 'All'
    }
];
const BENCHMARK_CONFIGS = [
    {
        type: 'sp500',
        name: 'S&P 500',
        description: '500 largest US companies',
        category: 'us_indices'
    },
    {
        type: 'nasdaq100',
        name: 'NASDAQ-100',
        description: '100 largest non-financial stocks',
        category: 'us_indices'
    },
    {
        type: 'dow30',
        name: 'Dow Jones 30',
        description: '30 blue-chip companies',
        category: 'us_indices'
    },
    {
        type: 'russell2000',
        name: 'Russell 2000',
        description: '2000 small-cap companies',
        category: 'us_indices'
    },
    {
        type: 'vti',
        name: 'VTI',
        description: 'Vanguard Total Stock Market',
        category: 'etf'
    },
    {
        type: 'qqq',
        name: 'QQQ',
        description: 'Invesco NASDAQ 100',
        category: 'etf'
    },
    {
        type: 'spy',
        name: 'SPY',
        description: 'SPDR S&P 500 ETF',
        category: 'etf'
    },
    {
        type: 'dia',
        name: 'DIA',
        description: 'SPDR Dow Jones ETF',
        category: 'etf'
    },
    {
        type: 'iwm',
        name: 'IWM',
        description: 'iShares Russell 2000',
        category: 'etf'
    },
    {
        type: 'vgt',
        name: 'VGT',
        description: 'Vanguard Information Tech',
        category: 'etf'
    },
    {
        type: 'vht',
        name: 'VHT',
        description: 'Vanguard Health Care',
        category: 'etf'
    },
    {
        type: 'vcr',
        name: 'VCR',
        description: 'Vanguard Consumer Disc.',
        category: 'etf'
    },
    {
        type: 'vdc',
        name: 'VDC',
        description: 'Vanguard Consumer Staples',
        category: 'etf'
    },
    {
        type: 'ven',
        name: 'VEN',
        description: 'Vanguard Energy',
        category: 'etf'
    },
    {
        type: 'vfi',
        name: 'VFI',
        description: 'Vanguard Financials',
        category: 'etf'
    },
    {
        type: 'viu',
        name: 'VIU',
        description: 'Vanguard Developed ex-US',
        category: 'international'
    },
    {
        type: 'acwx',
        name: 'ACWX',
        description: 'iShares MSCI AC World ex-US',
        category: 'international'
    },
    {
        type: 'bnd',
        name: 'BND',
        description: 'Vanguard Total Bond Market',
        category: 'bonds'
    },
    {
        type: 'agg',
        name: 'AGG',
        description: 'iShares Core US Aggregate',
        category: 'bonds'
    },
    {
        type: 'tlt',
        name: 'TLT',
        description: 'iShares 20+ Year Treasury',
        category: 'bonds'
    },
    {
        type: 'gld',
        name: 'GLD',
        description: 'SPDR Gold Shares',
        category: 'custom'
    },
    {
        type: 'bitcoin',
        name: 'Bitcoin',
        description: 'BTC/USD',
        category: 'crypto'
    },
    {
        type: 'ethereum',
        name: 'Ethereum',
        description: 'ETH/USD',
        category: 'crypto'
    }
];
const BENCHMARK_CATEGORIES = [
    {
        value: 'us_indices',
        label: 'US Indices'
    },
    {
        value: 'etf',
        label: 'ETFs'
    },
    {
        value: 'crypto',
        label: 'Cryptocurrency'
    },
    {
        value: 'bonds',
        label: 'Bonds'
    },
    {
        value: 'international',
        label: 'International'
    }
];
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/portfolio-analytics.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "portfolioAnalyticsApi",
    ()=>portfolioAnalyticsApi
]);
/**
 * Portfolio Analytics API
 * All portfolio-related API calls for performance analysis and recommendations
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
;
const portfolioAnalyticsApi = {
    /**
   * Get portfolio summary
   */ getPortfolioSummary: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/summary`),
    /**
   * Get performance metrics
   */ getPerformanceMetrics: (portfolioId, period = '1y')=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/performance`, {
            params: {
                period
            }
        }),
    /**
   * Get risk analysis
   */ getRiskAnalysis: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/risk-analysis`),
    /**
   * Get holdings analysis
   */ getHoldingsAnalysis: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/holdings`),
    /**
   * Get rebalancing suggestions
   */ getRebalancingSuggestions: (portfolioId)=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/rebalance-suggestions`),
    /**
   * Get portfolio comparison
   */ getPortfolioComparison: (portfolioId, benchmarkType = 'sp500', period = '1y')=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/portfolios/${portfolioId}/comparison`, {
            params: {
                benchmark_type: benchmarkType,
                period
            }
        }),
    /**
   * Get analytics overview (for analytics dashboard)
   */ getAnalytics: (period = '7d')=>__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/analytics', {
            params: {
                period
            }
        })
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/utils/analytics-export.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "downloadExport",
    ()=>downloadExport,
    "exportAnalytics",
    ()=>exportAnalytics,
    "generateExportData",
    ()=>generateExportData
]);
function generateExportData(analytics, options) {
    const { format } = options;
    const summary = analytics.summary || {
        name: 'Unknown Portfolio',
        total_value: analytics.total_value,
        total_invested: 0,
        total_pnl: 0,
        total_pnl_percent: 0
    };
    const performance = analytics.performance || {
        cagr: 0,
        total_return: 0,
        total_return_percent: 0,
        annualized_return: 0,
        best_day: 0,
        worst_day: 0,
        win_rate: 0
    };
    const risk = analytics.risk_metrics || {
        volatility: 0,
        beta: 1,
        sharpe_ratio: 0
    };
    const data = {
        summary: {
            portfolio: summary.name,
            totalValue: summary.total_value,
            totalReturn: performance.total_return_percent,
            periodStart: analytics.period_start,
            periodEnd: analytics.period_end
        },
        performance: {
            cagr: performance.cagr,
            totalReturn: performance.total_return_percent,
            annualizedReturn: performance.annualized_return,
            bestDay: performance.best_day,
            worstDay: performance.worst_day,
            winRate: performance.win_rate
        },
        risk: {
            volatility: risk.volatility,
            beta: risk.beta,
            sharpeRatio: risk.sharpe_ratio
        },
        allocation: analytics.performance_by_asset,
        exportedAt: new Date().toISOString(),
        period: options.period || '1y'
    };
    if (format === 'json') {
        return JSON.stringify(data, null, 2);
    }
    if (format === 'csv') {
        const lines = [];
        lines.push('Summary');
        lines.push('Portfolio,Total Value,Total Return,Period Start,Period End');
        lines.push(`${data.summary.portfolio},${data.summary.totalValue},${data.summary.totalReturn}%,${data.summary.periodStart},${data.summary.periodEnd}`);
        lines.push('');
        lines.push('Performance');
        lines.push('CAGR,Total Return,Annualized Return,Win Rate');
        lines.push(`${data.performance.cagr}%,${data.performance.totalReturn}%,${data.performance.annualizedReturn}%,${data.performance.winRate}%`);
        lines.push('');
        lines.push('Risk Metrics');
        lines.push('Volatility,Beta,Sharpe Ratio');
        lines.push(`${data.risk.volatility}%,${data.risk.beta},${data.risk.sharpeRatio}`);
        lines.push('');
        lines.push('Allocation');
        lines.push('Asset Type,Value,Return');
        analytics.performance_by_asset.forEach((asset)=>{
            lines.push(`${asset.asset_type},${asset.value},${asset.return}%`);
        });
        return lines.join('\n');
    }
    return null;
}
function downloadExport(data, filename, format) {
    const mimeType = format === 'json' ? 'application/json' : 'text/csv';
    const blob = new Blob([
        data
    ], {
        type: mimeType
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
function exportAnalytics(analytics, options) {
    const data = generateExportData(analytics, options);
    if (!data) return;
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `portfolio-analytics-${options.period || '1y'}-${timestamp}.${options.format}`;
    downloadExport(data, filename, options.format);
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/screener.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "screenerApi",
    ()=>screenerApi
]);
/**
 * Screener API Client
 * Stock screener endpoints
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
;
const screenerApi = {
    /**
   * Run stock screener with filters
   * Backend endpoint: POST /api/fundamentals/screener
   */ runScreener: async (filters)=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post('/fundamentals/screener', filters);
    },
    /**
   * Get available screener filters and presets
   */ getFilters: async ()=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/screener/filters');
    },
    /**
   * Get available screener presets
   */ getPresets: async ()=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/screener/presets');
    },
    /**
   * Get user's saved screener presets
   */ getUserPresets: async ()=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/screener/presets');
    },
    /**
   * Save a new screener preset
   */ savePreset: async (name, filters)=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post('/screener/presets', {
            name,
            filters
        });
    },
    /**
   * Update a screener preset
   */ updatePreset: async (id, data)=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].put(`/screener/presets/${id}`, data);
    },
    /**
   * Delete a screener preset
   */ deletePreset: async (id)=>{
        return await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].delete(`/screener/presets/${id}`);
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/utils/formatters.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Formatters
 * Utility functions for formatting data
 */ __turbopack_context__.s([
    "formatCurrency",
    ()=>formatCurrency,
    "formatDate",
    ()=>formatDate,
    "formatDuration",
    ()=>formatDuration,
    "formatMarketCap",
    ()=>formatMarketCap,
    "formatNumber",
    ()=>formatNumber,
    "formatPercent",
    ()=>formatPercent,
    "formatPrice",
    ()=>formatPrice,
    "formatVolume",
    ()=>formatVolume
]);
function formatPrice(value, currency = 'USD') {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numValue);
}
function formatCurrency(value, decimals = 2) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(numValue);
}
function formatNumber(value) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(numValue);
}
function formatPercent(value, showSign = true) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    const sign = numValue > 0 && showSign ? '+' : '';
    return `${sign}${numValue.toFixed(2)}%`;
}
function formatVolume(value) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (numValue >= 1e9) {
        return `${(numValue / 1e9).toFixed(2)}B`;
    }
    if (numValue >= 1e6) {
        return `${(numValue / 1e6).toFixed(2)}M`;
    }
    if (numValue >= 1e3) {
        return `${(numValue / 1e3).toFixed(2)}K`;
    }
    return numValue.toString();
}
function formatMarketCap(value) {
    if (value === undefined || value === null) return '--';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (numValue >= 1e12) {
        return `$${(numValue / 1e12).toFixed(2)}T`;
    }
    if (numValue >= 1e9) {
        return `$${(numValue / 1e9).toFixed(2)}B`;
    }
    if (numValue >= 1e6) {
        return `$${(numValue / 1e6).toFixed(2)}M`;
    }
    if (numValue >= 1e3) {
        return `$${(numValue / 1e3).toFixed(2)}K`;
    }
    return `$${numValue.toFixed(2)}`;
}
function formatDate(date, format = 'short') {
    if (!date) return '--';
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (format === 'time') {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(dateObj);
    }
    if (format === 'long') {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(dateObj);
    }
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(dateObj);
}
function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) {
        return `${days}d ${hours % 24}h`;
    }
    if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    }
    if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/types/settings.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Settings Types
 * Defines all settings-related types and interfaces
 */ __turbopack_context__.s([
    "defaultDisplaySettings",
    ()=>defaultDisplaySettings,
    "defaultInvestmentProfile",
    ()=>defaultInvestmentProfile,
    "defaultNotificationSettings",
    ()=>defaultNotificationSettings,
    "defaultProfileSettings",
    ()=>defaultProfileSettings,
    "defaultSettings",
    ()=>defaultSettings
]);
const defaultDisplaySettings = {
    theme: 'system',
    currency: 'USD',
    numberFormat: '1,234.56',
    compactMode: false,
    showPriceChange: true,
    animatedCharts: true
};
const defaultNotificationSettings = {
    enabled: true,
    types: {
        price: true,
        portfolio: true,
        news: false,
        digest: false
    },
    channels: {
        push: true,
        email: true,
        sms: false
    },
    quietHours: {
        enabled: false,
        startTime: '22:00',
        endTime: '08:00'
    }
};
const defaultProfileSettings = {
    timezone: 'America/New_York'
};
const defaultInvestmentProfile = {
    riskTolerance: 'moderate',
    goal: 'growth',
    preferredAssetClasses: [
        'stocks',
        'etfs'
    ]
};
const defaultSettings = {
    display: defaultDisplaySettings,
    notifications: defaultNotificationSettings,
    profile: defaultProfileSettings,
    investment: defaultInvestmentProfile
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/assets.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "assetsApi",
    ()=>assetsApi
]);
/**
 * Assets API
 * All asset-related API calls
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
;
const assetsApi = {
    list (filter, limit = 20, offset = 0) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/assets/', {
            params: {
                ...filter,
                limit,
                offset
            }
        });
    },
    get (symbol) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/assets/${symbol}`);
    },
    getPrice (symbol) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/assets/${symbol}/price`);
    },
    getHistorical (symbol, from_date, to_date, interval = '1d') {
        const params = {
            interval
        };
        if (from_date) params.from_date = from_date;
        if (to_date) params.to_date = to_date;
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/assets/${symbol}/historical`, {
            params
        });
    },
    getFundamentals (symbol) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/assets/${symbol}/fundamentals`);
    },
    getNews (symbol, limit = 10) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/assets/${symbol}/news`, {
            params: {
                limit
            }
        });
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/utils/technical-indicators.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "INDICATOR_DESCRIPTIONS",
    ()=>INDICATOR_DESCRIPTIONS,
    "calculateAllIndicators",
    ()=>calculateAllIndicators,
    "calculateBollingerBands",
    ()=>calculateBollingerBands,
    "calculateEMA",
    ()=>calculateEMA,
    "calculateMACD",
    ()=>calculateMACD,
    "calculateRSI",
    ()=>calculateRSI,
    "calculateSMA",
    ()=>calculateSMA,
    "formatIndicatorValue",
    ()=>formatIndicatorValue,
    "getMACDSignal",
    ()=>getMACDSignal,
    "getRSISignal",
    ()=>getRSISignal
]);
function calculateSMA(data, period) {
    const result = [];
    for(let i = 0; i < data.length; i++){
        if (i < period - 1) {
            result.push(NaN);
        } else {
            let sum = 0;
            for(let j = 0; j < period; j++){
                sum += data[i - j];
            }
            result.push(sum / period);
        }
    }
    return result;
}
function calculateEMA(data, period) {
    const result = [];
    const multiplier = 2 / (period + 1);
    for(let i = 0; i < data.length; i++){
        if (i === 0) {
            result.push(data[0]);
        } else if (i < period) {
            result.push(NaN);
        } else if (i === period) {
            let sum = 0;
            for(let j = 0; j < period; j++){
                sum += data[i - j];
            }
            result.push(sum / period);
        } else {
            const ema = (data[i] - result[i - 1]) * multiplier + result[i - 1];
            result.push(ema);
        }
    }
    return result;
}
function calculateRSI(data, period = 14) {
    const result = [];
    const gains = [];
    const losses = [];
    for(let i = 0; i < data.length; i++){
        if (i === 0) {
            result.push(NaN);
            continue;
        }
        const change = data[i] - data[i - 1];
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? -change : 0);
        if (i < period) {
            result.push(NaN);
        } else if (i === period) {
            const avgGain = gains.slice(0, period).reduce((a, b)=>a + b, 0) / period;
            const avgLoss = losses.slice(0, period).reduce((a, b)=>a + b, 0) / period;
            const rs = avgGain / (avgLoss || 0.0001);
            result.push(100 - 100 / (1 + rs));
        } else {
            const prevResult = result[i - 1];
            const avgGain = (gains.slice(-period - 1, -1).reduce((a, b)=>a + b, 0) + gains[gains.length - 1]) / period;
            const avgLoss = (losses.slice(-period - 1, -1).reduce((a, b)=>a + b, 0) + losses[losses.length - 1]) / period;
            const rs = avgGain / (avgLoss || 0.0001);
            result.push(100 - 100 / (1 + rs));
        }
    }
    return result;
}
function calculateMACD(data, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
    const fastEMA = calculateEMA(data, fastPeriod);
    const slowEMA = calculateEMA(data, slowPeriod);
    const macdLine = [];
    for(let i = 0; i < data.length; i++){
        if (fastEMA[i] === undefined || slowEMA[i] === undefined || isNaN(fastEMA[i]) || isNaN(slowEMA[i])) {
            macdLine.push(NaN);
        } else {
            macdLine.push(fastEMA[i] - slowEMA[i]);
        }
    }
    const signalLine = calculateEMA(macdLine.filter((v)=>!isNaN(v)), signalPeriod);
    const macdValidStart = slowPeriod - 1;
    const signalStart = macdValidStart + signalPeriod - 1;
    const histogram = [];
    for(let i = 0; i < data.length; i++){
        if (i < signalStart) {
            histogram.push(NaN);
        } else {
            const macdIdx = i - macdValidStart;
            const signalIdx = i - signalStart;
            const macdVal = macdLine[macdIdx];
            const signalVal = signalLine[signalIdx];
            if (isNaN(macdVal) || isNaN(signalVal)) {
                histogram.push(NaN);
            } else {
                histogram.push(macdVal - signalVal);
            }
        }
    }
    return {
        macd: macdLine,
        signal: signalLine,
        histogram
    };
}
function calculateBollingerBands(data, period = 20, stdDev = 2) {
    const middle = calculateSMA(data, period);
    const upper = [];
    const lower = [];
    for(let i = 0; i < data.length; i++){
        if (isNaN(middle[i])) {
            upper.push(NaN);
            lower.push(NaN);
        } else {
            let sumSquares = 0;
            let count = 0;
            for(let j = 0; j < period; j++){
                if (i - j >= 0 && !isNaN(middle[i - j])) {
                    sumSquares += Math.pow(data[i - j] - middle[i], 2);
                    count++;
                }
            }
            const stdDevValue = count > 0 ? Math.sqrt(sumSquares / count) * stdDev : 0;
            upper.push(middle[i] + stdDevValue);
            lower.push(middle[i] - stdDevValue);
        }
    }
    return {
        upper,
        middle,
        lower
    };
}
function calculateAllIndicators(data, config) {
    const closes = data.map((d)=>d.close);
    const result = {};
    if (config.sma20) result.sma20 = calculateSMA(closes, 20);
    if (config.sma50) result.sma50 = calculateSMA(closes, 50);
    if (config.sma200) result.sma200 = calculateSMA(closes, 200);
    if (config.ema12) result.ema12 = calculateEMA(closes, 12);
    if (config.ema26) result.ema26 = calculateEMA(closes, 26);
    if (config.rsi) {
        const rsiPeriod = config.rsiPeriod || 14;
        result.rsi = calculateRSI(closes, rsiPeriod);
    }
    if (config.macd) {
        const fastPeriod = config.macdFast || 12;
        const slowPeriod = config.macdSlow || 26;
        const signalPeriod = config.macdSignal || 9;
        result.macd = calculateMACD(closes, fastPeriod, slowPeriod, signalPeriod);
    }
    if (config.bollinger) {
        const period = config.bollingerPeriod || 20;
        const stdDev = config.bollingerStdDev || 2;
        result.bollinger = calculateBollingerBands(closes, period, stdDev);
    }
    return result;
}
function formatIndicatorValue(value) {
    if (value === undefined || isNaN(value)) return '--';
    if (Math.abs(value) >= 1000) {
        return value.toFixed(0);
    } else if (Math.abs(value) >= 100) {
        return value.toFixed(1);
    } else if (Math.abs(value) >= 10) {
        return value.toFixed(2);
    } else {
        return value.toFixed(3);
    }
}
function getRSISignal(rsi, overbought = 70, oversold = 30) {
    if (rsi >= overbought) return 'overbought';
    if (rsi <= oversold) return 'oversold';
    return 'neutral';
}
function getMACDSignal(macd, signal) {
    if (macd > signal) return 'bullish';
    if (macd < signal) return 'bearish';
    return 'neutral';
}
const INDICATOR_DESCRIPTIONS = {
    sma20: {
        name: 'SMA 20',
        fullName: 'Simple Moving Average (20 periods)',
        description: 'The average closing price over the last 20 periods. Shows medium-term trend direction.',
        interpretation: 'Price above SMA 20 suggests bullish momentum. Price below suggests bearish momentum.',
        color: '#3b82f6'
    },
    sma50: {
        name: 'SMA 50',
        fullName: 'Simple Moving Average (50 periods)',
        description: 'The average closing price over the last 50 periods. Used to identify medium-term trend.',
        interpretation: 'When price crosses above SMA 50, it may indicate a trend reversal to bullish.',
        color: '#22c55e'
    },
    sma200: {
        name: 'SMA 200',
        fullName: 'Simple Moving Average (200 periods)',
        description: 'The average closing price over the last 200 periods. Considered a key long-term trend indicator.',
        interpretation: 'Price above SMA 200 is in a long-term bullish trend. Often called the "life line" of the chart.',
        color: '#f59e0b'
    },
    ema12: {
        name: 'EMA 12',
        fullName: 'Exponential Moving Average (12 periods)',
        description: 'A weighted moving average that gives more importance to recent prices. Responds faster to price changes.',
        interpretation: 'EMA 12 reacts quicker to price movements than SMA, useful for short-term trading signals.',
        color: '#8b5cf6'
    },
    ema26: {
        name: 'EMA 26',
        fullName: 'Exponential Moving Average (26 periods)',
        description: 'A weighted moving average over 26 periods, commonly used in MACD calculation.',
        interpretation: 'Compare with EMA 12 to identify momentum shifts in the market.',
        color: '#ec4899'
    },
    rsi: {
        name: 'RSI',
        fullName: 'Relative Strength Index',
        description: 'Momentum oscillator that measures the speed and change of price movements. Scale: 0-100.',
        interpretation: 'RSI above 70 = Overbought (potential sell). RSI below 30 = Oversold (potential buy).',
        defaultPeriod: 14,
        overbought: 70,
        oversold: 30
    },
    macd: {
        name: 'MACD',
        fullName: 'Moving Average Convergence Divergence',
        description: 'Shows the relationship between two EMAs. Consists of MACD line, Signal line, and Histogram.',
        interpretation: 'MACD above Signal = Bullish. MACD below Signal = Bearish. Histogram shows momentum strength.',
        defaultFast: 12,
        defaultSlow: 26,
        defaultSignal: 9
    },
    bollinger: {
        name: 'Bollinger Bands',
        fullName: 'Bollinger Bands',
        description: 'Three lines: Middle band (SMA), Upper band (+2 std dev), Lower band (-2 std dev). Measures volatility.',
        interpretation: 'Price near upper band = potentially overbought. Price near lower band = potentially oversold. Bands widen during high volatility.',
        defaultPeriod: 20,
        defaultStdDev: 2
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/constants/realtime.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Real-Time Data Constants
 * WebSocket, chart, and order book configuration
 */ __turbopack_context__.s([
    "CHART_CONFIG",
    ()=>CHART_CONFIG,
    "CONNECTION_MESSAGES",
    ()=>CONNECTION_MESSAGES,
    "CONNECTION_STATES",
    ()=>CONNECTION_STATES,
    "ORDERBOOK_CONFIG",
    ()=>ORDERBOOK_CONFIG,
    "TICKER_CONFIG",
    ()=>TICKER_CONFIG,
    "WS_CONFIG",
    ()=>WS_CONFIG
]);
const WS_CONFIG = {
    RECONNECT_DELAYS: [
        1000,
        2000,
        4000,
        8000,
        16000,
        30000
    ],
    MAX_RECONNECT_ATTEMPTS: 10,
    HEARTBEAT_INTERVAL: 30000,
    CONNECT_TIMEOUT: 10000,
    MESSAGE_BUFFER_SIZE: 50,
    TRADE_FEED_LIMIT: 20
};
const CHART_CONFIG = {
    BUFFER_SIZES: {
        '1m': 500,
        '5m': 300,
        '15m': 200,
        '30m': 200,
        '1h': 200,
        '4h': 100,
        '1d': 100,
        '1w': 50,
        '3m': 100,
        '6m': 50,
        '1M': 30,
        '1y': 20
    },
    DEFAULT_TIMEFRAME: '1h',
    UPDATE_INTERVAL: 2000
};
const ORDERBOOK_CONFIG = {
    DEFAULT_DEPTH: 10,
    MAX_DEPTH: 100,
    DEPTH_OPTIONS: [
        10,
        20,
        50,
        100
    ],
    UPDATE_DEBOUNCE_MS: 100
};
const TICKER_CONFIG = {
    SCROLL_SPEED: 30,
    PAUSE_ON_HOVER: true,
    FLASH_DURATION: 500,
    MAX_SYMBOLS: 50
};
const CONNECTION_STATES = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    ERROR: 'error'
};
const CONNECTION_MESSAGES = {
    [CONNECTION_STATES.DISCONNECTED]: 'Disconnected from real-time data',
    [CONNECTION_STATES.CONNECTING]: 'Connecting to real-time data...',
    [CONNECTION_STATES.CONNECTED]: 'Connected to real-time data',
    [CONNECTION_STATES.ERROR]: 'Connection failed'
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/websocket.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "getWebSocketClient",
    ()=>getWebSocketClient,
    "resetWebSocketClient",
    ()=>resetWebSocketClient,
    "websocketApi",
    ()=>websocketApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/apps/frontend/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
/**
 * WebSocket Client
 * Manages WebSocket connections with auto-reconnection and event emission
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/constants/realtime.ts [app-client] (ecmascript)");
;
;
class WebSocketClient {
    ws = null;
    config;
    connectionState = __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED;
    reconnectAttempts = 0;
    reconnectTimeout = null;
    heartbeatInterval = null;
    connectTimeout = null;
    eventHandlers = new Map();
    subscriptions = new Set();
    lastPongTime = Date.now();
    constructor(config){
        this.config = config;
    }
    connect(token) {
        return new Promise((resolve, reject)=>{
            if (this.connectionState === __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED) {
                resolve();
                return;
            }
            if (this.connectionState === __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING) {
                reject(new Error('Already connecting'));
                return;
            }
            this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING);
            this.clearTimeouts();
            let wsUrl = this.config.url;
            if (token) {
                const separator = wsUrl.includes('?') ? '&' : '?';
                wsUrl = `${wsUrl}${separator}token=${token}`;
            }
            this.ws = new WebSocket(wsUrl);
            this.ws.onopen = ()=>{
                this.clearTimeouts();
                this.reconnectAttempts = 0;
                this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED);
                this.startHeartbeat();
                this.emit('connection', {
                    state: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED
                });
                resolve();
            };
            this.ws.onmessage = (event)=>{
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            this.ws.onclose = (event)=>{
                this.handleClose(event);
            };
            this.ws.onerror = (error)=>{
                this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].ERROR);
                this.emit('connection', {
                    state: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].ERROR,
                    error
                });
                reject(new Error('WebSocket connection failed'));
            };
            this.connectTimeout = setTimeout(()=>{
                if (this.connectionState === __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING) {
                    this.ws?.close();
                    reject(new Error('Connection timeout'));
                }
            }, this.config.connectTimeout);
        });
    }
    disconnect() {
        this.clearTimeouts();
        this.subscriptions.clear();
        if (this.ws) {
            this.ws.close(1000, 'Client disconnecting');
            this.ws = null;
        }
        this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED);
        this.emit('connection', {
            state: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED
        });
    }
    subscribe(request) {
        if (this.connectionState !== __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED) {
            console.warn('Cannot subscribe: not connected');
            return;
        }
        request.symbols.forEach((symbol)=>{
            request.dataTypes.forEach((dataType)=>{
                const subscriptionKey = `${symbol}:${dataType}`;
                this.subscriptions.add(subscriptionKey);
                const message = {
                    type: 'subscribe',
                    symbol,
                    dataType: dataType,
                    timestamp: new Date().toISOString()
                };
                this.sendMessage(message);
            });
        });
    }
    unsubscribe(symbol, dataTypes = []) {
        if (this.connectionState !== __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED) {
            return;
        }
        if (dataTypes.length === 0) {
            Array.from(this.subscriptions).forEach((sub)=>{
                if (sub.startsWith(`${symbol}:`)) {
                    this.subscriptions.delete(sub);
                }
            });
        } else {
            dataTypes.forEach((dataType)=>{
                const subscriptionKey = `${symbol}:${dataType}`;
                this.subscriptions.delete(subscriptionKey);
                const message = {
                    type: 'unsubscribe',
                    symbol,
                    dataType: dataType,
                    timestamp: new Date().toISOString()
                };
                this.sendMessage(message);
            });
        }
    }
    unsubscribeAll() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        const symbols = [];
        Array.from(this.subscriptions).forEach((s)=>{
            const symbol = s.split(':')[0];
            symbols.push(symbol);
        });
        const uniqueSymbols = [
            ...new Set(symbols)
        ];
        uniqueSymbols.forEach((symbol)=>{
            this.unsubscribe(symbol);
        });
        this.subscriptions.clear();
    }
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, new Set());
        }
        this.eventHandlers.get(event).add(handler);
    }
    off(event, handler) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.delete(handler);
            if (handlers.size === 0) {
                this.eventHandlers.delete(event);
            }
        }
    }
    getConnectionState() {
        return this.connectionState;
    }
    getPingMs() {
        return Date.now() - this.lastPongTime;
    }
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    handleMessage(message) {
        switch(message.type){
            case 'data_update':
            case 'initial_data':
                this.emit('data', message);
                break;
            case 'subscription_ack':
                this.emit('subscription', message);
                break;
            case 'unsubscribe_ack':
                this.emit('unsubscription', message);
                break;
            case 'pong':
                this.lastPongTime = Date.now();
                break;
            case 'error':
                console.error('WebSocket error:', message.error);
                this.emit('error', message);
                break;
        }
    }
    handleClose(event) {
        this.clearTimeouts();
        this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED);
        if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            this.emit('connection', {
                state: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].ERROR,
                error: 'Max reconnect attempts reached'
            });
        }
    }
    scheduleReconnect() {
        const delay = this.config.reconnectDelays[Math.min(this.reconnectAttempts, this.config.reconnectDelays.length - 1)];
        this.reconnectTimeout = setTimeout(()=>{
            this.reconnectAttempts++;
            this.setConnectionState(__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING);
            this.emit('connection', {
                state: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING
            });
            this.connect();
        }, delay);
    }
    startHeartbeat() {
        this.heartbeatInterval = setInterval(()=>{
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.sendMessage({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                });
            }
        }, this.config.heartbeatInterval);
    }
    clearTimeouts() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        if (this.connectTimeout) {
            clearTimeout(this.connectTimeout);
            this.connectTimeout = null;
        }
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    setConnectionState(state) {
        this.connectionState = state;
    }
    emit(event, data) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.forEach((handler)=>{
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in ${event} handler:`, error);
                }
            });
        }
    }
}
let wsClientInstance = null;
function getWebSocketClient() {
    if (!wsClientInstance) {
        const config = {
            url: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/realtime/',
            reconnectDelays: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WS_CONFIG"].RECONNECT_DELAYS,
            maxReconnectAttempts: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WS_CONFIG"].MAX_RECONNECT_ATTEMPTS,
            heartbeatInterval: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WS_CONFIG"].HEARTBEAT_INTERVAL,
            connectTimeout: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WS_CONFIG"].CONNECT_TIMEOUT
        };
        wsClientInstance = new WebSocketClient(config);
    }
    return wsClientInstance;
}
function resetWebSocketClient() {
    if (wsClientInstance) {
        wsClientInstance.disconnect();
        wsClientInstance = null;
    }
}
const WS_API = '/ws';
const websocketApi = {
    // ================= TOKEN MANAGEMENT =================
    getToken (username, password) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`${WS_API}/auth/token`, null, {
            params: {
                username,
                password
            }
        });
    },
    refreshToken (refreshToken) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`${WS_API}/auth/token/refresh`, {
            refresh_token: refreshToken
        });
    },
    verifyToken (token) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`${WS_API}/auth/verify`, {
            params: {
                token
            }
        });
    },
    // ================= QUOTA & CONNECTIONS =================
    getUserQuota (userId) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`${WS_API}/auth/quota`, {
            params: {
                user_id: userId
            }
        });
    },
    getUserConnections (userId) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`${WS_API}/auth/connections`, {
            params: {
                user_id: userId
            }
        });
    },
    checkSubscriptionPreCheck (symbol, channel = 'price') {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`${WS_API}/auth/subscription/pre-check`, {
            symbol,
            channel
        });
    },
    // ================= AUTH STATS =================
    getAuthStats () {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`${WS_API}/auth/stats`);
    },
    getBlockedUsers () {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`${WS_API}/auth/blocked`);
    },
    blockUser (userId, reason = 'Manual block') {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`${WS_API}/auth/block`, {
            user_id: userId,
            reason
        });
    },
    unblockUser (userId) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post(`${WS_API}/auth/unblock`, null, {
            params: {
                user_id: userId
            }
        });
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/constants/indicators.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// Technical Indicator Constants
__turbopack_context__.s([
    "BOLLINGER_BANDS_DEFAULTS",
    ()=>BOLLINGER_BANDS_DEFAULTS,
    "CHART_UPDATE_INTERVAL",
    ()=>CHART_UPDATE_INTERVAL,
    "DEFAULT_INDICATORS",
    ()=>DEFAULT_INDICATORS,
    "DRAWING_TOOLS",
    ()=>DRAWING_TOOLS,
    "FIBONACCI_LEVELS",
    ()=>FIBONACCI_LEVELS,
    "INDICATOR_BUFFER_SIZE",
    ()=>INDICATOR_BUFFER_SIZE,
    "INDICATOR_CATEGORIES",
    ()=>INDICATOR_CATEGORIES,
    "INDICATOR_COLORS",
    ()=>INDICATOR_COLORS,
    "INDICATOR_LABELS",
    ()=>INDICATOR_LABELS,
    "MACD_SIGNALS",
    ()=>MACD_SIGNALS,
    "RSI_LEVELS",
    ()=>RSI_LEVELS,
    "TIMEFRAMES",
    ()=>TIMEFRAMES
]);
const INDICATOR_CATEGORIES = {
    trend: {
        label: 'Trend Indicators',
        indicators: [
            'sma',
            'ema',
            'wma',
            'ichimoku',
            'parabolic_sar'
        ]
    },
    momentum: {
        label: 'Momentum Indicators',
        indicators: [
            'rsi',
            'stochastic',
            'cci',
            'williams_r',
            'mfi'
        ]
    },
    volatility: {
        label: 'Volatility Indicators',
        indicators: [
            'bollinger',
            'atr'
        ]
    },
    volume: {
        label: 'Volume Indicators',
        indicators: [
            'obv',
            'ad',
            'mfi'
        ]
    }
};
const INDICATOR_LABELS = {
    sma: 'Simple Moving Average',
    ema: 'Exponential Moving Average',
    wma: 'Weighted Moving Average',
    bollinger: 'Bollinger Bands',
    rsi: 'Relative Strength Index',
    macd: 'Moving Average Convergence Divergence',
    stochastic: 'Stochastic Oscillator',
    cci: 'Commodity Channel Index',
    williams_r: 'Williams %R',
    atr: 'Average True Range',
    obv: 'On-Balance Volume',
    mfi: 'Money Flow Index',
    ad: 'Accumulation/Distribution Line',
    ichimoku: 'Ichimoku Cloud',
    parabolic_sar: 'Parabolic SAR'
};
const INDICATOR_COLORS = {
    primary: '#3b82f6',
    secondary: '#8b5cf6',
    tertiary: '#06b6d4',
    quaternary: '#10b981',
    bullish: '#22c55e',
    bearish: '#ef4444',
    neutral: '#f59e0b'
};
const RSI_LEVELS = {
    overbought: 70,
    oversold: 30
};
const MACD_SIGNALS = {
    bullish: 'crossover',
    bearish: 'crossunder'
};
const BOLLINGER_BANDS_DEFAULTS = {
    period: 20,
    stdDev: 2,
    upperMultiplier: 2,
    lowerMultiplier: 2
};
const TIMEFRAMES = [
    {
        value: '1m',
        label: '1 Minute',
        seconds: 60
    },
    {
        value: '5m',
        label: '5 Minutes',
        seconds: 300
    },
    {
        value: '15m',
        label: '15 Minutes',
        seconds: 900
    },
    {
        value: '1h',
        label: '1 Hour',
        seconds: 3600
    },
    {
        value: '4h',
        label: '4 Hours',
        seconds: 14400
    },
    {
        value: '1d',
        label: '1 Day',
        seconds: 86400
    },
    {
        value: '1w',
        label: '1 Week',
        seconds: 604800
    }
];
const CHART_UPDATE_INTERVAL = 2000 // ms
;
const INDICATOR_BUFFER_SIZE = 200 // data points
;
const DRAWING_TOOLS = [
    {
        type: 'horizontal_line',
        label: 'Horizontal Line',
        icon: 'minus'
    },
    {
        type: 'vertical_line',
        label: 'Vertical Line',
        icon: 'minus'
    },
    {
        type: 'trend_line',
        label: 'Trend Line',
        icon: 'trending-up'
    },
    {
        type: 'support_resistance',
        label: 'Support/Resistance',
        icon: 'minus'
    },
    {
        type: 'fibonacci',
        label: 'Fibonacci Retracement',
        icon: 'activity'
    },
    {
        type: 'rectangle',
        label: 'Rectangle',
        icon: 'square'
    },
    {
        type: 'text',
        label: 'Text Annotation',
        icon: 'type'
    }
];
const FIBONACCI_LEVELS = [
    0,
    0.236,
    0.382,
    0.5,
    0.618,
    0.786,
    1
];
const DEFAULT_INDICATORS = [
    'sma',
    'rsi',
    'macd'
];
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/types/indicators.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// Technical Indicator Types
__turbopack_context__.s([
    "DEFAULT_INDICATORS",
    ()=>DEFAULT_INDICATORS
]);
const DEFAULT_INDICATORS = {
    sma: {
        type: 'sma',
        params: {
            period: 20
        },
        visible: true,
        color: '#3b82f6'
    },
    ema: {
        type: 'ema',
        params: {
            period: 12
        },
        visible: true,
        color: '#8b5cf6'
    },
    wma: {
        type: 'wma',
        params: {
            period: 10
        },
        visible: false,
        color: '#06b6d4'
    },
    bollinger: {
        type: 'bollinger',
        params: {
            period: 20,
            stdDev: 2
        },
        visible: false,
        color: '#f59e0b'
    },
    rsi: {
        type: 'rsi',
        params: {
            period: 14
        },
        visible: false,
        color: '#ef4444',
        secondary_yaxis: true
    },
    macd: {
        type: 'macd',
        params: {
            fastPeriod: 12,
            slowPeriod: 26,
            signalPeriod: 9
        },
        visible: false,
        color: '#10b981',
        secondary_yaxis: true
    },
    stochastic: {
        type: 'stochastic',
        params: {
            kPeriod: 14,
            dPeriod: 3
        },
        visible: false,
        color: '#f97316',
        secondary_yaxis: true
    },
    cci: {
        type: 'cci',
        params: {
            period: 20
        },
        visible: false,
        color: '#06b6d4',
        secondary_yaxis: true
    },
    williams_r: {
        type: 'williams_r',
        params: {
            period: 14
        },
        visible: false,
        color: '#eab308',
        secondary_yaxis: true
    },
    atr: {
        type: 'atr',
        params: {
            period: 14
        },
        visible: false,
        color: '#a855f7',
        secondary_yaxis: true
    },
    obv: {
        type: 'obv',
        params: {},
        visible: false,
        color: '#22c55e',
        secondary_yaxis: true
    },
    mfi: {
        type: 'mfi',
        params: {
            period: 14
        },
        visible: false,
        color: '#ec4899',
        secondary_yaxis: true
    },
    ad: {
        type: 'ad',
        params: {},
        visible: false,
        color: '#14b8a6',
        secondary_yaxis: true
    },
    ichimoku: {
        type: 'ichimoku',
        params: {
            tenkanPeriod: 9,
            kijunPeriod: 26,
            senkouSpanBPeriod: 52
        },
        visible: false,
        color: '#6366f1'
    },
    parabolic_sar: {
        type: 'parabolic_sar',
        params: {
            step: 0.02,
            max: 0.2
        },
        visible: false,
        color: '#f43f5e'
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/types/holdings.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ASSET_CLASS_COLORS",
    ()=>ASSET_CLASS_COLORS,
    "ASSET_CLASS_LABELS",
    ()=>ASSET_CLASS_LABELS,
    "TRANSACTION_TYPE_COLORS",
    ()=>TRANSACTION_TYPE_COLORS,
    "TRANSACTION_TYPE_LABELS",
    ()=>TRANSACTION_TYPE_LABELS
]);
const ASSET_CLASS_LABELS = {
    stocks: 'Stocks',
    crypto: 'Cryptocurrency',
    bonds: 'Bonds',
    etf: 'ETFs',
    options: 'Options',
    cash: 'Cash',
    commodities: 'Commodities',
    real_estate: 'Real Estate',
    other: 'Other'
};
const ASSET_CLASS_COLORS = {
    stocks: '#3B82F6',
    crypto: '#F59E0B',
    bonds: '#10B981',
    etf: '#8B5CF6',
    options: '#EC4899',
    cash: '#6B7280',
    commodities: '#F97316',
    real_estate: '#14B8A6',
    other: '#9CA3AF'
};
const TRANSACTION_TYPE_LABELS = {
    buy: 'Buy',
    sell: 'Sell',
    dividend: 'Dividend',
    transfer: 'Transfer',
    split: 'Split',
    fee: 'Fee',
    deposit: 'Deposit',
    withdrawal: 'Withdrawal'
};
const TRANSACTION_TYPE_COLORS = {
    buy: 'text-green-600 bg-green-100',
    sell: 'text-red-600 bg-red-100',
    dividend: 'text-blue-600 bg-blue-100',
    transfer: 'text-gray-600 bg-gray-100',
    split: 'text-purple-600 bg-purple-100',
    fee: 'text-orange-600 bg-orange-100',
    deposit: 'text-emerald-600 bg-emerald-100',
    withdrawal: 'text-rose-600 bg-rose-100'
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/lib/api/news-sentiment.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "newsSentimentApi",
    ()=>newsSentimentApi
]);
/**
 * News Sentiment API
 * All news sentiment-related API calls
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/client.ts [app-client] (ecmascript)");
;
const newsSentimentApi = {
    getSentiment (symbol, params) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/news/sentiment/${symbol}`, {
            params: {
                days: 7,
                min_relevance: 0.5,
                ...params
            }
        });
    },
    getMarketTrends (params) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/news/trends', {
            params: {
                days: 7,
                min_mentions: 5,
                ...params
            }
        });
    },
    getBatchSentiment (symbols, params) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].post('/news/sentiment/batch', {
            symbols,
            params
        });
    },
    getTrendingTopics (limit = 10) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get('/news/topics/trending', {
            params: {
                limit
            }
        });
    },
    getNewsWithSentiment (symbol, params) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/news/symbol/${symbol}`, {
            params: {
                days: 7,
                limit: 20,
                ...params
            }
        });
    },
    getSentimentHistory (symbol, params) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].get(`/news/sentiment/${symbol}/history`, {
            params: {
                days: 30,
                interval: 'daily',
                ...params
            }
        });
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/stores/analyticsStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAnalytics",
    ()=>useAnalytics,
    "useAnalyticsStore",
    ()=>useAnalyticsStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$portfolio$2d$analytics$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/portfolio-analytics.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
;
;
const API_PERIOD_MAP = {
    '1d': '3m',
    '7d': '3m',
    '30d': '3m',
    '90d': '6m',
    '180d': '6m',
    '1y': '1y',
    '3y': '1y',
    '5y': '1y',
    'ytd': '1y',
    'all': '1y'
};
const useAnalyticsStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set, get)=>({
        selectedPortfolioId: null,
        selectedPeriod: '1y',
        selectedBenchmark: 'sp500',
        data: null,
        loading: false,
        error: null,
        lastUpdated: null,
        setSelectedPortfolio: (id)=>{
            set({
                selectedPortfolioId: id
            });
            if (id) {
                get().fetchAnalytics();
            }
        },
        setSelectedPeriod: (period)=>{
            set({
                selectedPeriod: period
            });
            get().fetchAnalytics();
        },
        setSelectedBenchmark: (benchmark)=>{
            set({
                selectedBenchmark: benchmark
            });
            get().fetchAnalytics();
        },
        fetchAnalytics: async ()=>{
            const { selectedPortfolioId, selectedPeriod, selectedBenchmark } = get();
            if (!selectedPortfolioId) {
                set({
                    error: 'No portfolio selected',
                    loading: false
                });
                return;
            }
            set({
                loading: true,
                error: null
            });
            try {
                const apiPeriod = API_PERIOD_MAP[selectedPeriod];
                const [summary, performance, risk, allocation] = await Promise.all([
                    __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$portfolio$2d$analytics$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["portfolioAnalyticsApi"].getPortfolioSummary(selectedPortfolioId),
                    __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$portfolio$2d$analytics$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["portfolioAnalyticsApi"].getPerformanceMetrics(selectedPortfolioId, apiPeriod),
                    __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$portfolio$2d$analytics$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["portfolioAnalyticsApi"].getRiskAnalysis(selectedPortfolioId),
                    __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$portfolio$2d$analytics$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["portfolioAnalyticsApi"].getHoldingsAnalysis(selectedPortfolioId)
                ]);
                const analyticsData = {
                    total_return: performance.total_return || 0,
                    total_value: summary.total_value,
                    total_value_change: summary.total_pnl,
                    total_value_change_percent: summary.total_pnl_percent,
                    summary: {
                        ...summary
                    },
                    performance: {
                        portfolio_id: selectedPortfolioId,
                        time_period: selectedPeriod,
                        cagr: performance.annualized_return || 0,
                        total_return: performance.total_return,
                        total_return_percent: performance.total_return_percent,
                        annualized_return: performance.annualized_return,
                        volatility: performance.volatility,
                        sharpe_ratio: performance.sharpe_ratio,
                        sortino_ratio: null,
                        max_drawdown: performance.max_drawdown || null,
                        max_drawdown_percent: performance.max_drawdown_percent || null,
                        max_drawdown_date: null,
                        recovery_time: null,
                        best_day: performance.best_day,
                        worst_day: performance.worst_day,
                        win_rate: performance.win_rate,
                        alpha_vs_sp500: performance.alpha_vs_sp500,
                        beta_vs_sp500: performance.beta_vs_sp500,
                        var_95: null,
                        var_99: null,
                        avg_win: null,
                        avg_loss: null,
                        profit_factor: null
                    },
                    performance_by_asset: [],
                    risk_metrics: {
                        volatility: risk.volatility_exposure || 0,
                        beta: risk.volatility_exposure || 0,
                        sharpe_ratio: performance.sharpe_ratio || 0
                    },
                    period_start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
                    period_end: new Date().toISOString(),
                    total_transactions: 0
                };
                set({
                    data: analyticsData,
                    loading: false,
                    lastUpdated: new Date().toISOString()
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to fetch analytics',
                    loading: false
                });
            }
        },
        clearAnalytics: ()=>{
            set({
                data: null,
                error: null,
                lastUpdated: null
            });
        }
    }), {
    name: 'analytics-storage',
    partialize: (state)=>({
            selectedPortfolioId: state.selectedPortfolioId,
            selectedPeriod: state.selectedPeriod,
            selectedBenchmark: state.selectedBenchmark
        })
}));
const useAnalytics = ()=>{
    _s();
    const store = useAnalyticsStore();
    return {
        ...store,
        fetchAnalytics: store.fetchAnalytics,
        setSelectedPortfolio: store.setSelectedPortfolio,
        setSelectedPeriod: store.setSelectedPeriod,
        setSelectedBenchmark: store.setSelectedBenchmark,
        clearAnalytics: store.clearAnalytics
    };
};
_s(useAnalytics, "D8Do5cy0sleYPs05nqpFpiRiyZU=", false, function() {
    return [
        useAnalyticsStore
    ];
});
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/stores/screenerStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useScreenerStore",
    ()=>useScreenerStore
]);
/**
 * Screener Store
 * Zustand store for screener state management
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/screener.ts [app-client] (ecmascript)");
;
;
;
const useScreenerStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set, get)=>({
        // Initial state
        filters: {},
        results: [],
        loading: false,
        error: null,
        total_count: 0,
        total_screened: 0,
        elapsed_seconds: 0,
        last_updated: null,
        sort_field: 'market_cap',
        sort_direction: 'desc',
        selected_presets: [],
        limit: 100,
        // Actions
        setFilter: (key, value)=>{
            set((state)=>({
                    filters: {
                        ...state.filters,
                        [key]: value
                    }
                }));
        },
        removeFilter: (key)=>{
            set((state)=>{
                const newFilters = {
                    ...state.filters
                };
                delete newFilters[key];
                return {
                    filters: newFilters
                };
            });
        },
        clearFilters: ()=>{
            set({
                filters: {},
                selected_presets: [],
                results: []
            });
        },
        applyPreset: (preset)=>{
            set({
                filters: preset.filters,
                selected_presets: [
                    preset.key
                ]
            });
            get().runScreener();
        },
        setSorting: (field, direction)=>{
            set({
                sort_field: field,
                sort_direction: direction
            });
        },
        setLimit: (limit)=>{
            set({
                limit
            });
        },
        runScreener: async ()=>{
            const { filters, limit } = get();
            set({
                loading: true,
                error: null
            });
            try {
                const response = await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["screenerApi"].runScreener({
                    ...filters,
                    limit
                });
                set({
                    results: response.results || [],
                    total_count: response.count || 0,
                    total_screened: response.total_screened || 0,
                    elapsed_seconds: response.elapsed_seconds || 0,
                    loading: false,
                    last_updated: new Date().toISOString()
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to run screener',
                    loading: false,
                    results: []
                });
            }
        },
        exportResults: (format)=>{
            const { results } = get();
            if (results.length === 0) {
                return;
            }
            const filename = `screener-results-${new Date().toISOString().split('T')[0]}`;
            if (format === 'json') {
                const data = JSON.stringify(results, null, 2);
                const blob = new Blob([
                    data
                ], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${filename}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } else if (format === 'csv') {
                const headers = Object.keys(results[0]);
                const csv = [
                    headers.join(','),
                    ...results.map((row)=>headers.map((header)=>{
                            const value = row[header];
                            if (value === null || value === undefined) return '';
                            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                                return `"${value.replace(/"/g, '""')}"`;
                            }
                            return String(value);
                        }).join(','))
                ].join('\n');
                const blob = new Blob([
                    csv
                ], {
                    type: 'text/csv'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${filename}.csv`;
                a.click();
                URL.revokeObjectURL(url);
            }
        }
    }), {
    name: 'screener-storage',
    partialize: (state)=>({
            filters: state.filters,
            sort_field: state.sort_field,
            sort_direction: state.sort_direction,
            limit: state.limit
        })
}));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/stores/screenerPresetsStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useScreenerPresets",
    ()=>useScreenerPresets
]);
/**
 * Screener Presets Store
 * Zustand store for managing user's screener presets
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/screener.ts [app-client] (ecmascript)");
;
;
;
const useScreenerPresets = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set, get)=>({
        presets: [],
        loading: false,
        error: null,
        fetchPresets: async ()=>{
            set({
                loading: true,
                error: null
            });
            try {
                const presets = await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["screenerApi"].getUserPresets();
                set({
                    presets,
                    loading: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to fetch presets',
                    loading: false
                });
            }
        },
        savePreset: async (name, filters)=>{
            set({
                loading: true,
                error: null
            });
            try {
                const preset = await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["screenerApi"].savePreset(name, filters);
                set((state)=>({
                        presets: [
                            preset,
                            ...state.presets
                        ],
                        loading: false
                    }));
                return preset;
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to save preset';
                set({
                    error: message,
                    loading: false
                });
                throw new Error(message);
            }
        },
        updatePreset: async (id, data)=>{
            set({
                loading: true,
                error: null
            });
            try {
                const preset = await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["screenerApi"].updatePreset(id, data);
                set((state)=>({
                        presets: state.presets.map((p)=>p.id === id ? preset : p),
                        loading: false
                    }));
                return preset;
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to update preset';
                set({
                    error: message,
                    loading: false
                });
                throw new Error(message);
            }
        },
        deletePreset: async (id)=>{
            set({
                loading: true,
                error: null
            });
            try {
                await __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$screener$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["screenerApi"].deletePreset(id);
                set((state)=>({
                        presets: state.presets.filter((p)=>p.id !== id),
                        loading: false
                    }));
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Failed to delete preset';
                set({
                    error: message,
                    loading: false
                });
                throw new Error(message);
            }
        },
        clearError: ()=>{
            set({
                error: null
            });
        }
    }), {
    name: 'screener-presets-storage',
    partialize: (state)=>({
            presets: state.presets
        })
}));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/stores/settingsStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useSettingsStore",
    ()=>useSettingsStore
]);
/**
 * Settings Store
 * Zustand store for user settings with localStorage persistence
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/types/settings.ts [app-client] (ecmascript)");
;
;
;
const useSettingsStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set, get)=>({
        display: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultDisplaySettings"],
        notifications: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultNotificationSettings"],
        profile: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultProfileSettings"],
        investment: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultInvestmentProfile"],
        isLoading: false,
        error: null,
        lastSaved: null,
        setDisplaySettings: (settings)=>{
            set((state)=>({
                    display: {
                        ...state.display,
                        ...settings
                    }
                }));
        },
        setNotificationSettings: (settings)=>{
            set((state)=>({
                    notifications: {
                        ...state.notifications,
                        ...settings
                    }
                }));
        },
        setProfileSettings: (settings)=>{
            set((state)=>({
                    profile: {
                        ...state.profile,
                        ...settings
                    }
                }));
        },
        setInvestmentProfile: (settings)=>{
            set((state)=>({
                    investment: {
                        ...state.investment,
                        ...settings
                    }
                }));
        },
        setTheme: (theme)=>{
            set((state)=>({
                    display: {
                        ...state.display,
                        theme
                    }
                }));
        },
        resetSettings: ()=>{
            set({
                display: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultDisplaySettings"],
                notifications: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultNotificationSettings"],
                profile: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultProfileSettings"],
                investment: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultInvestmentProfile"],
                error: null
            });
        },
        resetDisplaySettings: ()=>{
            set({
                display: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultDisplaySettings"]
            });
        },
        resetNotificationSettings: ()=>{
            set({
                notifications: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultNotificationSettings"]
            });
        },
        saveSettings: async ()=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                const state = get();
                // TODO: Integrate with backend API when available
                // For now, settings are automatically persisted via zustand persist middleware
                set({
                    isLoading: false,
                    lastSaved: new Date().toISOString()
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to save settings',
                    isLoading: false
                });
            }
        },
        loadSettings: async ()=>{
            set({
                isLoading: true,
                error: null
            });
            try {
                // TODO: Load from backend API when available
                // For now, settings are automatically loaded from localStorage via zustand persist
                set({
                    isLoading: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to load settings',
                    isLoading: false
                });
            }
        },
        exportSettings: ()=>{
            const state = get();
            const exportable = {
                display: state.display,
                notifications: state.notifications,
                profile: {
                    ...state.profile,
                    // Don't export sensitive data
                    email: undefined,
                    phone: undefined
                },
                investment: state.investment,
                exportedAt: new Date().toISOString(),
                version: '1.0'
            };
            return JSON.stringify(exportable, null, 2);
        },
        importSettings: (json)=>{
            try {
                const imported = JSON.parse(json);
                if (imported.version !== '1.0') {
                    throw new Error('Invalid settings version');
                }
                set({
                    display: {
                        ...__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultDisplaySettings"],
                        ...imported.display
                    },
                    notifications: {
                        ...__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultNotificationSettings"],
                        ...imported.notifications
                    },
                    profile: {
                        ...__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultProfileSettings"],
                        ...imported.profile
                    },
                    investment: {
                        ...__TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$types$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["defaultInvestmentProfile"],
                        ...imported.investment
                    },
                    lastSaved: new Date().toISOString()
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to import settings'
                });
            }
        }
    }), {
    name: 'financehub-settings',
    partialize: (state)=>({
            display: state.display,
            notifications: state.notifications,
            profile: state.profile,
            investment: state.investment,
            lastSaved: state.lastSaved
        })
}));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/stores/realtimeStore.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useRealtimeStore",
    ()=>useRealtimeStore
]);
/**
 * Real-Time Data Store
 * Zustand store for WebSocket state and real-time data
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/api/websocket.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/src/lib/constants/realtime.ts [app-client] (ecmascript)");
;
;
;
const useRealtimeStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])((set, get)=>({
        connectionState: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED,
        error: null,
        subscribedSymbols: [],
        prices: {},
        trades: {},
        orderBooks: {},
        charts: {},
        connect: async (token)=>{
            try {
                set({
                    connectionState: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTING,
                    error: null
                });
                const wsClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getWebSocketClient"])();
                wsClient.on('connection', ({ state, error })=>{
                    set({
                        connectionState: state
                    });
                    if (state === __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].ERROR && error) {
                        set({
                            error: error
                        });
                    }
                });
                wsClient.on('data', (message)=>{
                    if (message.data) {
                        const { symbol, dataType, data } = message;
                        switch(dataType){
                            case 'price':
                                if (symbol && data) {
                                    get().updatePrice(symbol, data);
                                }
                                break;
                            case 'trades':
                                if (symbol && Array.isArray(data.trades)) {
                                    data.trades.forEach((trade)=>{
                                        get().addTrade(symbol, trade);
                                    });
                                }
                                break;
                            case 'orderbook':
                                if (symbol && data) {
                                    get().updateOrderBook(symbol, data);
                                }
                                break;
                        }
                    }
                });
                wsClient.on('error', (message)=>{
                    set({
                        error: message.error || 'WebSocket error'
                    });
                });
                await wsClient.connect(token);
            } catch (error) {
                set({
                    connectionState: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].ERROR,
                    error: error instanceof Error ? error.message : 'Failed to connect'
                });
            }
        },
        disconnect: ()=>{
            const wsClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getWebSocketClient"])();
            wsClient.disconnect();
            set({
                connectionState: __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].DISCONNECTED,
                subscribedSymbols: [],
                error: null
            });
        },
        subscribe: (symbols, dataTypes)=>{
            const wsClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getWebSocketClient"])();
            if (wsClient.getConnectionState() !== __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CONNECTION_STATES"].CONNECTED) {
                console.warn('Cannot subscribe: not connected');
                return;
            }
            const request = {
                symbols,
                dataTypes
            };
            wsClient.subscribe(request);
            set((state)=>({
                    subscribedSymbols: [
                        ...new Set([
                            ...state.subscribedSymbols,
                            ...symbols
                        ])
                    ]
                }));
        },
        unsubscribe: (symbol, dataTypes)=>{
            const wsClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getWebSocketClient"])();
            wsClient.unsubscribe(symbol, dataTypes || []);
            set((state)=>({
                    subscribedSymbols: state.subscribedSymbols.filter((s)=>s !== symbol)
                }));
        },
        subscribeSingle: (symbol, dataTypes)=>{
            get().subscribe([
                symbol
            ], dataTypes);
        },
        unsubscribeSingle: (symbol, dataTypes)=>{
            get().unsubscribe(symbol, dataTypes);
        },
        unsubscribeAll: ()=>{
            const wsClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$api$2f$websocket$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["getWebSocketClient"])();
            wsClient.unsubscribeAll();
            set({
                subscribedSymbols: []
            });
        },
        clearData: (symbol)=>{
            if (symbol) {
                set((state)=>{
                    const newState = {};
                    if (state.prices[symbol]) {
                        newState.prices = {
                            ...state.prices
                        };
                        delete newState.prices[symbol];
                    }
                    if (state.trades[symbol]) {
                        newState.trades = {
                            ...state.trades
                        };
                        delete newState.trades[symbol];
                    }
                    if (state.orderBooks[symbol]) {
                        newState.orderBooks = {
                            ...state.orderBooks
                        };
                        delete newState.orderBooks[symbol];
                    }
                    if (state.charts[symbol]) {
                        newState.charts = {
                            ...state.charts
                        };
                        delete newState.charts[symbol];
                    }
                    return newState;
                });
            } else {
                set({
                    prices: {},
                    trades: {},
                    orderBooks: {},
                    charts: {}
                });
            }
        },
        updatePrice: (symbol, price)=>{
            set((state)=>({
                    prices: {
                        ...state.prices,
                        [symbol]: price
                    }
                }));
        },
        addTrade: (symbol, trade)=>{
            set((state)=>{
                const symbolTrades = state.trades[symbol] || [];
                const newTrades = [
                    trade,
                    ...symbolTrades
                ].slice(0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$src$2f$lib$2f$constants$2f$realtime$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WS_CONFIG"].TRADE_FEED_LIMIT);
                return {
                    trades: {
                        ...state.trades,
                        [symbol]: newTrades
                    }
                };
            });
        },
        updateOrderBook: (symbol, orderBook)=>{
            set((state)=>({
                    orderBooks: {
                        ...state.orderBooks,
                        [symbol]: orderBook
                    }
                }));
        },
        setChartTimeframe: (symbol, timeframe)=>{
            set((state)=>({
                    charts: {
                        ...state.charts,
                        [symbol]: timeframe
                    }
                }));
        },
        setError: (error)=>{
            set({
                error
            });
        },
        setConnectionState: (state)=>{
            set({
                connectionState: state
            });
        }
    }));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/apps/frontend/src/hooks/useDownload.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__,
    "useDownload",
    ()=>useDownload,
    "useDownloadFile",
    ()=>useDownloadFile
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/apps/frontend/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
;
function useDownload() {
    _s();
    const [state, setState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        isDownloading: false,
        error: null,
        progress: 0
    });
    const reset = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[reset]": ()=>{
            setState({
                isDownloading: false,
                error: null,
                progress: 0
            });
        }
    }["useDownload.useCallback[reset]"], []);
    const createDownloadLink = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[createDownloadLink]": (data, mimeType)=>{
            let blob;
            let filename;
            if (typeof data === 'string') {
                blob = new Blob([
                    data
                ], {
                    type: mimeType
                });
                filename = `download-${Date.now()}.${mimeType.split('/')[1] || 'txt'}`;
            } else {
                blob = data;
                filename = `download-${Date.now()}.${mimeType.split('/')[1] || 'bin'}`;
            }
            const url = URL.createObjectURL(blob);
            return {
                url,
                filename
            };
        }
    }["useDownload.useCallback[createDownloadLink]"], []);
    const triggerDownload = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[triggerDownload]": (url, filename)=>{
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    }["useDownload.useCallback[triggerDownload]"], []);
    const download = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[download]": (data, options = {})=>{
            const { filename, mimeType = 'text/plain', autoDownload = true } = options;
            try {
                const { url, filename: generatedFilename } = createDownloadLink(data, mimeType);
                const finalFilename = filename || generatedFilename;
                if (autoDownload) {
                    triggerDownload(url, finalFilename);
                }
                setState({
                    isDownloading: false,
                    error: null,
                    progress: 100
                });
            } catch (err) {
                setState({
                    "useDownload.useCallback[download]": (prev)=>({
                            ...prev,
                            error: err instanceof Error ? err : new Error('Download failed')
                        })
                }["useDownload.useCallback[download]"]);
            }
        }
    }["useDownload.useCallback[download]"], [
        createDownloadLink,
        triggerDownload
    ]);
    const downloadFromUrl = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[downloadFromUrl]": async (url, options = {})=>{
            setState({
                isDownloading: true,
                error: null,
                progress: 0
            });
            try {
                const response = await fetch(url, {
                    mode: 'cors'
                });
                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
                }
                const blob = await response.blob();
                const mimeType = options.mimeType || blob.type || 'application/octet-stream';
                setState({
                    isDownloading: true,
                    error: null,
                    progress: 50
                });
                const { url: objectUrl, filename: generatedFilename } = createDownloadLink(blob, mimeType);
                const filename = options.filename || generatedFilename;
                if (options.autoDownload !== false) {
                    triggerDownload(objectUrl, filename);
                }
                setState({
                    isDownloading: false,
                    error: null,
                    progress: 100
                });
            } catch (err) {
                setState({
                    "useDownload.useCallback[downloadFromUrl]": (prev)=>({
                            ...prev,
                            isDownloading: false,
                            error: err instanceof Error ? err : new Error('Download from URL failed')
                        })
                }["useDownload.useCallback[downloadFromUrl]"]);
            }
        }
    }["useDownload.useCallback[downloadFromUrl]"], [
        createDownloadLink,
        triggerDownload
    ]);
    const downloadFile = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownload.useCallback[downloadFile]": async (filePath, options = {})=>{
            setState({
                isDownloading: true,
                error: null,
                progress: 0
            });
            try {
                const response = await fetch(filePath);
                if (!response.ok) {
                    throw new Error(`Failed to fetch file: ${response.status}`);
                }
                const blob = await response.blob();
                const mimeType = options.mimeType || blob.type || 'application/octet-stream';
                setState({
                    isDownloading: true,
                    error: null,
                    progress: 75
                });
                const { url, filename: generatedFilename } = createDownloadLink(blob, mimeType);
                const filename = options.filename || filePath.split('/').pop() || generatedFilename;
                if (options.autoDownload !== false) {
                    triggerDownload(url, filename);
                }
                setState({
                    isDownloading: false,
                    error: null,
                    progress: 100
                });
            } catch (err) {
                setState({
                    "useDownload.useCallback[downloadFile]": (prev)=>({
                            ...prev,
                            isDownloading: false,
                            error: err instanceof Error ? err : new Error('Download file failed')
                        })
                }["useDownload.useCallback[downloadFile]"]);
            }
        }
    }["useDownload.useCallback[downloadFile]"], [
        createDownloadLink,
        triggerDownload
    ]);
    return {
        download,
        downloadFromUrl,
        downloadFile,
        state,
        reset
    };
}
_s(useDownload, "MecpYobIMamMfNSFEDvr6AEhj5E=");
function useDownloadFile() {
    _s1();
    const { download, downloadFromUrl, state, reset } = useDownload();
    const downloadCSV = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownloadFile.useCallback[downloadCSV]": (data, filename)=>{
            const csvData = typeof data === 'string' ? data : convertToCSV(data);
            download(csvData, {
                filename: filename.endsWith('.csv') ? filename : `${filename}.csv`,
                mimeType: 'text/csv'
            });
        }
    }["useDownloadFile.useCallback[downloadCSV]"], [
        download
    ]);
    const downloadJSON = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownloadFile.useCallback[downloadJSON]": (data, filename, indent = 2)=>{
            const jsonData = JSON.stringify(data, null, indent);
            download(jsonData, {
                filename: filename.endsWith('.json') ? filename : `${filename}.json`,
                mimeType: 'application/json'
            });
        }
    }["useDownloadFile.useCallback[downloadJSON]"], [
        download
    ]);
    const downloadExcel = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownloadFile.useCallback[downloadExcel]": (data, filename)=>{
            download(data, {
                filename: filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`,
                mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
        }
    }["useDownloadFile.useCallback[downloadExcel]"], [
        download
    ]);
    const downloadText = (0, __TURBOPACK__imported__module__$5b$project$5d2f$apps$2f$frontend$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useDownloadFile.useCallback[downloadText]": (data, filename, mimeType = 'text/plain')=>{
            download(data, {
                filename,
                mimeType
            });
        }
    }["useDownloadFile.useCallback[downloadText]"], [
        download
    ]);
    return {
        downloadCSV,
        downloadJSON,
        downloadExcel,
        downloadText,
        downloadFromUrl,
        ...state,
        reset
    };
}
_s1(useDownloadFile, "0QI8InjUYzlRZXV3153/fo5gO/E=", false, function() {
    return [
        useDownload
    ];
});
function convertToCSV(data) {
    if (data.length === 0) return '';
    const headers = Object.keys(data[0]);
    const rows = data.map((row)=>headers.map((header)=>{
            const value = row[header];
            const stringValue = String(value ?? '');
            const escaped = stringValue.replace(/"/g, '""');
            return `"${escaped}"`;
        }).join(','));
    return [
        headers.join(','),
        ...rows
    ].join('\n');
}
const __TURBOPACK__default__export__ = useDownload;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=apps_frontend_src_2f4c2beb._.js.map