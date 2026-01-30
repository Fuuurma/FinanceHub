# FinanceHub Backend - Tasks & Issues List

**Last Updated:** January 30, 2026  
**Status:** Backend Analysis Complete  
**Source Analysis:** Codebase exploration, API endpoints review

---

## 🚨 CRITICAL BAD PRACTICES (High Priority)

### 1. Bare except Clauses (4 occurrences)

**Priority:** High  
**Impact:** Silent failures, hidden bugs, security risks  
**Files Affected:**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| `data/processing/pipeline.py` | 192 | Bare `except:` clause | Catch specific exceptions |
| `data/processing/pipeline.py` | 206 | Bare `except:` clause | Catch specific exceptions |
| `data/data_providers/coingecko/base.py` | 70 | Bare `except:` clause | Catch specific exceptions |
| `data/data_providers/coinmarketcap/base.py` | 69 | Bare `except:` clause | Catch specific exceptions |

### 2. Type Annotation Issues (30+ errors)

**Priority:** High  
**Impact:** Type safety compromised, runtime errors likely  
**Files Affected:**

| File | Errors | Issue |
|------|--------|-------|
| `api/analytics.py` | 15 | `Annotated` type issues, undefined variables (`pl`) |
| `api/market_overview.py` | 30+ | `DataOrchestrator` missing methods |
| `trading/api/trading.py` | 10 | `Annotated` type issues, `DoesNotExist` issues |
| `assets/models/asset.py` | 5 | `Meta` class conflicts |
| `portfolios/models/portfolio.py` | 8 | `Meta` class, ForeignKey issues |

**Examples of Issues Found:**
```python
# analytics.py
ERROR: Object of type "Annotated" is not callable
ERROR: "pl" is not defined

# market_overview.py
ERROR: Cannot access attribute "get_top_movers" for class "DataOrchestrator"
ERROR: Cannot access attribute "get_current_price" for class "DataOrchestrator"

# trading.py
ERROR: Cannot access attribute "DoesNotExist" for class "Order"
ERROR: Object of type "Annotated" is not callable

# models
ERROR: "Meta" overrides symbol of same name in class "UUIDModel"
```

### 3. Missing Type Hints in API Functions (Multiple)

**Priority:** High  
**Impact:** Type safety compromised, IDE support limited  
**Files Affected:** All API files

**Examples:**
```python
# Before (no type hints)
async def list_alerts(request):
async def get_performance(request):
async def get_risk_adjusted(request):

# After (with type hints)
async def list_alerts(request: Request) -> JSONResponse:
async def get_performance(request: Request, portfolio_id: str) -> dict:
async def get_risk_adjusted(request: Request, portfolio_id: str, period: str) -> dict:
```

---

### 3. Missing Input Validation

**Priority:** High  
**Impact:** Security vulnerabilities, data corruption  
**Files Affected:** All API endpoints accepting user input

**Examples:**
```python
# Before (no validation)
async def get_portfolio(portfolio_id: str):
    return await Portfolio.objects.get(id=portfolio_id)

# After (with validation)
from pydantic import BaseModel

class PortfolioGet(BaseModel):
    portfolio_id: str

async def get_portfolio(request: Request, data: PortfolioGet):
    return await Portfolio.objects.get(id=data.portfolio_id)
```

---

## 📋 MISSING API ENDPOINTS

### Critical Missing Endpoints (P0)

| Endpoint | Method | Description | Frontend Need |
|----------|--------|-------------|---------------|
| `/api/v1/trading/orders/history/` | GET | Trade history with filters | TradeHistory.tsx |
| `/api/v1/trading/orders/list/` | GET | Active/pending orders | OrderList.tsx |
| `/api/v1/risk/position/{id}/` | GET | Position risk analysis | PositionRiskCard.tsx |
| `/api/v1/risk/greeks/` | POST | Options Greeks calculation | GreeksCalculator.tsx |
| `/api/v1/risk/stress-test/` | POST | Stress testing scenarios | StressTestPanel.tsx |
| `/api/v1/portfolio/performance/` | GET | Performance vs benchmark | PerformanceChart.tsx |
| `/api/v1/portfolio/rebalance/` | POST | Rebalancing suggestions | RebalancingTool.tsx |
| `/api/v1/research/insider-trading/` | GET | Insider transactions | InsiderTradingPanel.tsx |
| `/api/v1/research/institutional-holdings/` | GET | 13F institutional data | InstitutionalHoldingsPanel.tsx |
| `/api/v1/charts/volume-profile/` | GET | Volume profile data | VolumeProfileChart.tsx |
| `/api/v1/charts/depth/` | GET | Market depth data | DepthChart.tsx |

### High Priority Endpoints (P1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/economics/indicators/{id}/` | GET | Economic indicator history |
| `/api/v1/fundamentals/financials/` | GET | Company financial statements |
| `/api/v1/fundamentals/company/` | GET | Company profile |
| `/api/v1/options/stats/` | GET | Options statistics |
| `/api/v1/options/payoff/` | POST | Options payoff calculation |
| `/api/v1/analytics/attribution/` | GET | Performance attribution |
| `/api/v1/analytics/factors/` | GET | Factor analysis |
| `/api/v1/analytics/rolling-correlation/` | GET | Rolling correlation |
| `/api/v1/analytics/tax-lots/` | GET | Tax lot information |
| `/api/v1/ai/price-prediction/` | POST | AI price prediction |
| `/api/v1/ai/backtest-results/` | POST | AI strategy backtesting |
| `/api/v1/ai/sentiment/` | GET | Market sentiment analysis |
| `/api/v1/research/earnings/` | GET | Earnings estimates |
| `/api/v1/research/price-targets/` | GET | Analyst price targets |
| `/api/v1/research/sec-filings/` | GET | SEC filings list |

---

## 🗄️ DATABASE SCHEMA ISSUES

### Missing Indexes

**Priority:** High  
**Impact:** Slow queries on large datasets

| Table | Column | Query Pattern | Fix |
|-------|--------|---------------|-----|
| `holdings` | `portfolio_id`, `created_at` | Portfolio history queries | Add composite index |
| `transactions` | `symbol`, `executed_at` | Symbol-based queries | Add index |
| `price_data` | `timestamp`, `symbol` | Time-series queries | Add composite index |
| `orders` | `status`, `user_id` | Order list queries | Add index |
| `alerts` | `user_id`, `is_active` | Alert retrieval | Add index |

---

### Missing Foreign Key Relationships

**Priority:** Medium

| Table | Missing FK To | Impact |
|-------|---------------|--------|
| `trades` | `orders` table | Data integrity risk |
| `position_risk` | `positions` table | Orphaned records |
| `stress_test_results` | `portfolios` table | Orphaned records |

---

## 🔧 PERFORMANCE ISSUES

### Missing Caching

**Priority:** High

| Endpoint | Cache Key | TTL |
|----------|-----------|-----|
| `/api/v1/market/overview/` | `market:overview:{timestamp}` | 60s |
| `/api/v1/fundamentals/{symbol}/` | `fundamentals:{symbol}` | 3600s |
| `/api/v1/economic/calendar/` | `economic:calendar:{date}` | 3600s |
| `/api/v1/analytics/correlation/` | `correlation:{portfolio_id}:{tf}` | 300s |

**Solution:** Use Redis for caching

```python
# Example caching pattern
async def get_market_overview() -> dict:
    cache_key = f"market:overview:{get_current_timestamp()}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    data = await fetch_market_data()
    await redis.setex(cache_key, 60, json.dumps(data))
    return data
```

---

### Synchronous Operations That Should Be Async

**Priority:** Medium

| File | Function | Issue |
|------|----------|-------|
| `data/data_providers/*` | All `fetch_*` functions | Blocking HTTP calls |
| `portfolios/services/*` | Portfolio calculations | CPU-bound operations |
| `analytics/services/*` | Analytics calculations | CPU-bound operations |

**Solution:** Move to Celery tasks or use async libraries

---

## 📁 CODE ORGANIZATION ISSUES

### Duplicate Code Patterns

**Priority:** Medium

| Pattern | Files | Solution |
|---------|-------|----------|
| Data fetching | `data_providers/coingecko/`, `data_providers/coinmarketcap/` | Create abstract base class |
| API response formatting | All API files | Create response serializers |
| Error handling | All API files | Create exception handlers |

---

### Functions Too Long

**Priority:** Medium

| File | Function | Lines | Should Be |
|------|----------|-------|----------|
| `api/advanced_portfolio_optimization.py` | `optimize_portfolio()` | 150+ | Split into smaller functions |
| `api/ai_enhanced.py` | `get_market_summary()` | 100+ | Split into smaller functions |
| `data/processing/pipeline.py` | `process_data()` | 200+ | Split into smaller functions |

---

## 🧪 TESTING GAPS

### Missing Tests

**Priority:** High

| Category | Coverage | Files to Test |
|----------|----------|---------------|
| API Endpoints | ~20% | All endpoint files |
| Services | ~10% | All service files |
| Data Providers | ~15% | All provider files |
| Utils | ~5% | Helper functions |

**Required Test Files:**
- `tests/api/test_trading.py` - Trading endpoints
- `tests/api/test_risk.py` - Risk endpoints
- `tests/api/test_research.py` - Research endpoints
- `tests/services/test_portfolio.py` - Portfolio services
- `tests/services/test_risk.py` - Risk services

---

## 📋 BACKEND TASK LIST

### Critical Tasks (P0)

| B1 | Fix bare except clauses | data/processing/pipeline.py, data providers | Fix 4 bare except clauses |
|----|-------------------------|---------------------------------------------|---------------------------|
| B2 | Add type hints | All API endpoints | Add type hints to 50+ functions |
| B3 | Input validation | All API endpoints | Add Pydantic models for input |
| B4 | Trade history endpoint | `/api/v1/trading/orders/history/` | Create new endpoint |
| B5 | Order list endpoint | `/api/v1/trading/orders/list/` | Create new endpoint |
| B6 | Position risk endpoint | `/api/v1/risk/position/{id}/` | Create new endpoint |
| B7 | Greeks calculation endpoint | `/api/v1/risk/greeks/` | Create new endpoint |
| B8 | Stress test endpoint | `/api/v1/risk/stress-test/` | Create new endpoint |
| B9 | Volume profile endpoint | `/api/v1/charts/volume-profile/` | Create new endpoint |
| B10 | Depth chart endpoint | `/api/v1/charts/depth/` | Create new endpoint |

### High Priority Tasks (P1)

| B11 | Performance endpoint | `/api/v1/portfolio/performance/` | New endpoint |
|-----|----------------------|----------------------------------|--------------|
| B12 | Rebalancing endpoint | `/api/v1/portfolio/rebalance/` | New endpoint |
| B13 | Insider trading endpoint | `/api/v1/research/insider-trading/` | New endpoint |
| B14 | Institutional holdings endpoint | `/api/v1/research/institutional-holdings/` | New endpoint |
| B15 | Redis caching | Market overview, fundamentals | Add caching layer |
| B16 | Database indexes | holdings, transactions, price_data | Add missing indexes |
| B17 | API tests | Trading, Risk, Research | Add test coverage |

### Medium Priority Tasks (P2)

| B18 | Economics indicators | `/api/v1/economics/indicators/` | New endpoint |
|-----|----------------------|----------------------------------|--------------|
| B19 | Financial statements | `/api/v1/fundamentals/financials/` | New endpoint |
| B20 | Company profile | `/api/v1/fundamentals/company/` | New endpoint |
| B21 | Options stats | `/api/v1/options/stats/` | New endpoint |
| B22 | Options payoff | `/api/v1/options/payoff/` | New endpoint |
| B23 | Attribution analysis | `/api/v1/analytics/attribution/` | New endpoint |
| B24 | Factor analysis | `/api/v1/analytics/factors/` | New endpoint |
| B25 | Tax lots | `/api/v1/analytics/tax-lots/` | New endpoint |
| B26 | AI price prediction | `/api/v1/ai/price-prediction/` | New endpoint |
| B27 | AI backtest results | `/api/v1/ai/backtest-results/` | New endpoint |
| B28 | Sentiment analysis | `/api/v1/ai/sentiment/` | New endpoint |
| B29 | Earnings estimates | `/api/v1/research/earnings/` | New endpoint |
| B30 | Price targets | `/api/v1/research/price-targets/` | New endpoint |
| B31 | SEC filings | `/api/v1/research/sec-filings/` | New endpoint |

---

## 📁 BACKEND DIRECTORY STRUCTURE

```
Backend/src/
├── api/                          # 30+ API files
│   ├── trading/
│   │   ├── orders.py             # Order endpoints (existing)
│   │   ├── trades.py             # Trade endpoints (MISSING - B4)
│   │   └── history.py            # Order history (MISSING - B5)
│   ├── risk/
│   │   ├── var.py                # VaR endpoints (existing)
│   │   ├── position_risk.py      # Position risk (MISSING - B6)
│   │   ├── greeks.py             # Greeks calculation (MISSING - B7)
│   │   └── stress_test.py        # Stress testing (MISSING - B8)
│   ├── charts/
│   │   ├── volume_profile.py     # Volume profile (MISSING - B9)
│   │   └── depth.py              # Market depth (MISSING - B10)
│   ├── portfolio/
│   │   ├── performance.py        # Performance (MISSING - B11)
│   │   └── rebalancing.py        # Rebalancing (MISSING - B12)
│   ├── research/
│   │   ├── insider_trading.py    # Insider trading (MISSING - B13)
│   │   ├── institutional.py      # Institutional holdings (MISSING - B14)
│   │   ├── earnings.py           # Earnings estimates (MISSING - B29)
│   │   ├── price_targets.py      # Price targets (MISSING - B30)
│   │   └── sec_filings.py        # SEC filings (MISSING - B31)
│   ├── analytics/
│   │   ├── attribution.py        # Attribution (MISSING - B23)
│   │   ├── factors.py            # Factor analysis (MISSING - B24)
│   │   └── tax_lots.py           # Tax lots (MISSING - B25)
│   ├── options/
│   │   ├── stats.py              # Options stats (MISSING - B21)
│   │   └── payoff.py             # Payoff chart (MISSING - B22)
│   ├── ai/
│   │   ├── prediction.py         # Price prediction (MISSING - B26)
│   │   ├── backtest.py           # Backtest results (MISSING - B27)
│   │   └── sentiment.py          # Sentiment (MISSING - B28)
│   ├── economics/
│   │   ├── indicators.py         # Economic indicators (MISSING - B18)
│   │   └── calendar.py           # Calendar (existing)
│   └── fundamentals/
│       ├── financials.py         # Financial statements (MISSING - B19)
│       └── company.py            # Company profile (MISSING - B20)
│
├── models/                        # Database models
│   ├── portfolios/               # Portfolio models (existing)
│   ├── trading/                  # Trading models (existing)
│   ├── risk/                     # Risk models (existing)
│   └── ...                       
│
├── services/                      # Business logic
│   ├── trading/                  # Trading services
│   ├── risk/                     # Risk services (existing)
│   ├── analytics/                # Analytics services
│   └── ...                       
│
├── tasks/                        # Celery tasks
│   ├── data_fetcher.py          # Data fetching
│   ├── scheduler_tasks.py       # Scheduled tasks
│   └── ...                       
│
└── utils/
    ├── caching.py               # Caching utilities (MISSING - B15)
    └── helpers/
        └── models/              # Model helpers
```

---

## 🔗 FRONTEND-BACKEND MAPPING

### Frontend Components → Backend Endpoints

| Frontend Component | Backend API Needed | Status |
|--------------------|-------------------|--------|
| `TradeHistory.tsx` | `/api/v1/trading/orders/history/` | MISSING (B4) |
| `OrderList.tsx` | `/api/v1/trading/orders/list/` | MISSING (B5) |
| `PositionRiskCard.tsx` | `/api/v1/risk/position/{id}/` | MISSING (B6) |
| `GreeksCalculator.tsx` | `/api/v1/risk/greeks/` | MISSING (B7) |
| `StressTestPanel.tsx` | `/api/v1/risk/stress-test/` | MISSING (B8) |
| `PerformanceChart.tsx` | `/api/v1/portfolio/performance/` | MISSING (B11) |
| `RebalancingTool.tsx` | `/api/v1/portfolio/rebalance/` | MISSING (B12) |
| `InsiderTradingPanel.tsx` | `/api/v1/research/insider-trading/` | MISSING (B13) |
| `InstitutionalHoldingsPanel.tsx` | `/api/v1/research/institutional-holdings/` | MISSING (B14) |
| `VolumeProfileChart.tsx` | `/api/v1/charts/volume-profile/` | MISSING (B9) |
| `DepthChart.tsx` | `/api/v1/charts/depth/` | MISSING (B10) |

---

## 📊 TESTING PRIORITY

### Unit Tests Needed (P0)

| Test File | Functions to Test |
|-----------|-------------------|
| `tests/api/test_trading.py` | order CRUD, trade history, order list |
| `tests/api/test_risk.py` | VaR, CVaR, position risk, Greeks, stress test |
| `tests/api/test_portfolio.py` | performance, rebalancing |
| `tests/api/test_research.py` | insider trading, institutional holdings |

### Integration Tests Needed (P1)

| Test File | Endpoints to Test |
|-----------|-------------------|
| `tests/integration/test_portfolio_flow.py` | Portfolio creation → holdings → performance |
| `tests/integration/test_trading_flow.py` | Order placement → execution → history |
| `tests/integration/test_risk_flow.py` | Position import → risk calculation → stress test |

---

## 🚀 NEXT STEPS

1. **Complete Backend Analysis** - Explore more files for bad practices
2. **Create Backend Tasks** - Add to BACKEND_TASKS.md
3. **Fix Critical Issues** - Bare except, type hints, input validation
4. **Create Missing Endpoints** - Start with P0 tasks (B4-B10)
5. **Add Tests** - Critical API endpoint tests
6. **Optimize Performance** - Caching, indexes, async operations

---

**Document Version:** 1.0  
**Last Updated:** January 30, 2026  
**Next Review:** After fixing B1-B3 (critical bad practices)  
**Related:** See `tasks.md` for Frontend tasks
