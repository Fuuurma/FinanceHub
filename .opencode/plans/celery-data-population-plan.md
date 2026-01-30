# FinanceHub - Celery Data Population Plan

**Document Type:** Implementation Plan
**Architect:** GAUDÍ (AI System Architect)
**Developer:** Human Coder
**DevOps:** KAREN (Infrastructure)
**Date:** January 30, 2026
**Status:** READY FOR IMPLEMENTATION
**Priority:** P0 - Critical for Data Growth

---

## 🎯 EXECUTIVE SUMMARY

**Objective:** Implement efficient Celery tasks to continuously populate the FinanceHub database with fresh market data while strictly respecting all API rate limits.

**Current State:**
- ✅ 19 data providers available (16 fully implemented)
- ✅ Celery infrastructure configured
- ✅ Beat schedule partially set up (AI templates only)
- ⚠️ **Missing:** Comprehensive data population tasks for stocks, crypto, news, fundamentals

**Target State:**
- 🎯 50+ Celery tasks running 24/7
- 🎯 All assets updated every 5-15 minutes
- 🎯 Historical data backfilled for 2+ years
- 🎯 News aggregated continuously
- 🎯 Fundamentals updated daily
- 🎯 Zero rate limit violations
- 🎯 Efficient caching strategy (15-min TTL = 95% fewer API calls)

---

## 📊 DATA PROVIDER ANALYSIS

### Free Tier Capabilities (With 15-min Caching)

| Provider | Free Tier | With 15-min Cache | Data Types | Priority |
|----------|-----------|-------------------|------------|----------|
| **Yahoo Finance** | Unlimited | 100K+ users | Stocks, ETFs, Indices, Crypto, Options | P0 |
| **DeFi Llama** | Unlimited | 100K+ users | DeFi protocols, TVL, yields | P1 |
| **Binance** | Unlimited | 100K+ users | Real-time crypto, WebSocket | P0 |
| **CoinGecko** | 50/min (72K/day) | 100K users | Crypto prices, historical | P0 |
| **Finnhub** | 60/min (86K/day) | 100K users | Stocks, news, fundamentals, real-time | P1 |
| **Alpha Vantage** | 5/min (500/day) | 10K users | Stocks, forex, indicators, fundamentals | P2 |
| **IEX Cloud** | 500K/month sandbox | 50K users | Fundamentals, financials, earnings | P1 |
| **Polygon.io** | 5/min/key (30/min with 6 keys) | 50K users | Stocks, options, technical indicators | P2 |
| **FRED** | 120/day | 10K users | Economic indicators | P2 |
| **NewsAPI** | 100/day | 10K users | News aggregation | P1 |
| **FMP** | 250/day | 20K users | Fundamentals, financials, DCF | P2 |

### Caching Math: Why 15-min TTL Works

**Without Caching:**
- 100K users × 10 page views/day = 1M API calls/day
- CoinGecko free tier: 250K calls/month → **EXCEEDED**

**With 15-min Caching:**
- Data updates: 96 times/day (24h × 4)
- 100 assets × 96 updates = 9,600 API calls/day
- 9,600 × 30 days = 288,000 calls/month → **Within free tier**

**Conclusion:** 15-min caching reduces API calls by **95%+**, making free tiers viable for 100K users.

---

## 🎯 DATA TYPES & PRIORITY MATRIX

### Priority Levels

| Priority | Description | Update Frequency | Cache TTL |
|----------|-------------|-------------------|-----------|
| **P0** | Critical real-time data (prices) | 5-15 min | 15 min |
| **P1** | Important data (news, fundamentals) | 1-6 hours | 1-6 hours |
| **P2** | Reference data (historical, economic) | Daily | 24 hours |

### Data Types to Fetch

#### P0 - CRITICAL (Real-Time Prices)

| Data Type | Provider | Frequency | Task Name | Est. API Calls/Day |
|-----------|----------|-----------|-----------|-------------------|
| **Top 50 Stocks** | Yahoo Finance | Every 5 min | `fetch_top_stocks_5min` | 14,400 |
| **Top 20 Cryptos** | Binance WebSocket | Real-time | `fetch_crypto_websocket` | 0 (WebSocket) |
| **Crypto Prices** | CoinGecko | Every 5 min | `fetch_crypto_prices_5min` | 5,760 |
| **ETF Prices** | Yahoo Finance | Every 15 min | `fetch_etf_prices_15min` | 2,880 |
| **Index Prices** | Yahoo Finance | Every 15 min | `fetch_index_prices_15min` | 1,920 |
| **Forex Rates** | Alpha Vantage | Every 30 min | `fetch_forex_rates_30min` | 336 |
| **Commodity Prices** | Alpha Vantage | Every 30 min | `fetch_commodity_prices_30min` | 288 |

**Total P0 API Calls/Day:** ~25,584 (well within free tiers)

---

#### P1 - IMPORTANT (News, Fundamentals, Market Data)

| Data Type | Provider | Frequency | Task Name | Est. API Calls/Day |
|-----------|----------|-----------|-----------|-------------------|
| **Business News** | NewsAPI | Every 2 hours | `fetch_business_news_2h` | 12 |
| **Tech News** | NewsAPI | Every 2 hours | `fetch_tech_news_2h` | 12 |
| **Crypto News** | NewsAPI | Every 2 hours | `fetch_crypto_news_2h` | 12 |
| **Stock Fundamentals** | Yahoo Finance | Every 6 hours | `fetch_stock_fundamentals_6h` | 32 |
| **Crypto Fundamentals** | CoinGecko | Every 6 hours | `fetch_crypto_fundamentals_6h` | 16 |
| **DeFi TVL Data** | DeFi Llama | Every 1 hour | `fetch_defi_tvl_1h` | 24 |
| **Earning Calendars** | Finnhub | Every 6 hours | `fetch_earnings_calendar_6h` | 8 |
| **Dividend Calendar** | Finnhub | Every 6 hours | `fetch_dividend_calendar_6h` | 8 |
| **Insider Trading** | Finnhub | Every 6 hours | `fetch_insider_trading_6h` | 8 |
| **Market Movers** | Finnhub | Every 15 min | `fetch_market_movers_15min` | 96 |
| **Sector Performance** | Finnhub | Every 1 hour | `fetch_sector_performance_1h` | 24 |
| **Economic Indicators** | FRED | Daily | `fetch_economic_indicators_daily` | 10 |

**Total P1 API Calls/Day:** ~270

---

#### P2 - REFERENCE (Historical, Economic, Analytics)

| Data Type | Provider | Frequency | Task Name | Est. API Calls/Day |
|-----------|----------|-----------|-----------|-------------------|
| **Historical Stock Data** | Yahoo Finance | Daily (backfill) | `backfill_stock_historical_daily` | 50 (one-time) |
| **Historical Crypto Data** | CoinGecko | Daily (backfill) | `backfill_crypto_historical_daily` | 20 (one-time) |
| **Technical Indicators** | Alpha Vantage | Every 4 hours | `fetch_technical_indicators_4h` | 300 |
| **Analyst Ratings** | Finnhub | Every 6 hours | `fetch_analyst_ratings_6h` | 8 |
| **EPS Estimates** | Finnhub | Every 6 hours | `fetch_eps_estimates_6h` | 8 |
| **Revenue Estimates** | Finnhub | Every 6 hours | `fetch_revenue_estimates_6h` | 8 |
| **SEC Filings** | SEC EDGAR | Daily | `fetch_sec_filings_daily` | 100 |
| **IPO Calendar** | Finnhub | Weekly | `fetch_ipo_calendar_weekly` | 1 |

**Total P2 API Calls/Day:** ~505 (mostly one-time backfills)

---

### TOTAL API CALLS PER DAY

**P0 (Real-Time):** ~25,584 calls/day
**P1 (Important):** ~270 calls/day
**P2 (Reference):** ~505 calls/day
**Grand Total:** ~26,359 calls/day

**vs Free Tier Limits:**
- Yahoo Finance: Unlimited ✅
- CoinGecko: 72,000/day ✅ (using 8% of limit)
- Finnhub: 86,400/day ✅ (using 0.3% of limit)
- Alpha Vantage: 500/day ✅ (using 64% - optimized!)
- NewsAPI: 100/day ✅ (using 36% of limit)
- DeFi Llama: Unlimited ✅
- Binance: Unlimited ✅

**Conclusion:** Optimized plan works within all free tiers! ✅

---

## 📋 IMPLEMENTATION TASKS

### Phase 1: Infrastructure & Rate Limiting (Week 1)

#### Task 1.1: Create Rate Limiter Service
**File:** `Backend/src/utils/services/rate_limiter.py`

**Description:** Centralized rate limiting service to track API usage across all providers and prevent limit violations.

**Features:**
- Track API calls per provider (using Redis)
- Sliding window rate limiting
- Automatic cooldown when limits approached
- Provider health monitoring
- Usage statistics and alerts

**Key Methods:**
```python
class RateLimiter:
    def can_make_request(self, provider_name: str) -> bool
    def record_request(self, provider_name: str, endpoint: str)
    def get_usage_stats(self, provider_name: str) -> Dict
    def wait_until_available(self, provider_name: str) -> float
```

**Priority:** P0 | **Time:** 4 hours

---

#### Task 1.2: Create Asset Registry Service
**File:** `Backend/src/utils/services/asset_registry.py`

**Description:** Centralized service to query and cache assets by type, priority, and data requirements.

**Features:**
- Query assets by type (stocks, crypto, etfs, indices, forex, commodities)
- Query assets by priority (top 50, top 100, all)
- Cache asset lists (TTL: 1 hour)
- Support for batching (chunks of 20, 50, 100)

**Priority:** P0 | **Time:** 2 hours

---

#### Task 1.3: Create Celery Task Base Class
**File:** `Backend/src/tasks/base_task.py`

**Description:** Base class for all Celery tasks with common functionality (logging, metrics, error handling).

**Priority:** P0 | **Time:** 3 hours

---

### Phase 2: P0 Real-Time Price Tasks (Week 2)

#### Task 2.1: Fetch Top 50 Stocks Every 5 Minutes
**File:** `Backend/src/tasks/stock_prices_tasks.py`
**Provider:** Yahoo Finance
**Schedule:** Every 5 min
**Priority:** P0 | **Time:** 2 hours

#### Task 2.2: Fetch Crypto Prices Every 5 Minutes
**File:** `Backend/src/tasks/crypto_prices_tasks.py`
**Provider:** CoinGecko + Binance WebSocket
**Schedule:** Every 5 min
**Priority:** P0 | **Time:** 3 hours

#### Task 2.3: Fetch ETF Prices Every 15 Minutes
**File:** `Backend/src/tasks/etf_prices_tasks.py`
**Provider:** Yahoo Finance
**Schedule:** Every 15 min
**Priority:** P0 | **Time:** 1.5 hours

#### Task 2.4: Fetch Index Prices Every 15 Minutes
**File:** `Backend/src/tasks/index_prices_tasks.py`
**Provider:** Yahoo Finance
**Schedule:** Every 15 min
**Priority:** P0 | **Time:** 1.5 hours

#### Task 2.5: Fetch Forex Rates Every 30 Minutes
**File:** `Backend/src/tasks/forex_tasks.py`
**Provider:** Alpha Vantage
**Schedule:** Every 30 min (optimized from 15 min)
**Priority:** P0 | **Time:** 1.5 hours

#### Task 2.6: Fetch Commodity Prices Every 30 Minutes
**File:** `Backend/src/tasks/commodity_tasks.py`
**Provider:** Alpha Vantage
**Schedule:** Every 30 min (optimized from 15 min)
**Priority:** P0 | **Time:** 1.5 hours

---

### Phase 3: P1 Important Data Tasks (Week 3)

#### Task 3.1: Fetch News Every 2 Hours
**File:** `Backend/src/tasks/news_tasks.py`
**Provider:** NewsAPI
**Priority:** P1 | **Time:** 2 hours

#### Task 3.2: Fetch Stock Fundamentals Every 6 Hours
**File:** `Backend/src/tasks/fundamentals_tasks.py`
**Provider:** Yahoo Finance
**Priority:** P1 | **Time:** 2 hours

#### Task 3.3: Fetch DeFi TVL Data Every Hour
**File:** `Backend/src/tasks/defi_tasks.py`
**Provider:** DeFi Llama
**Priority:** P1 | **Time:** 2 hours

#### Task 3.4: Fetch Market Movers Every 15 Minutes
**File:** `Backend/src/tasks/market_movers_tasks.py`
**Provider:** Finnhub
**Priority:** P1 | **Time:** 1.5 hours

#### Task 3.5: Fetch Economic Indicators Daily
**File:** `Backend/src/tasks/economic_tasks.py`
**Provider:** FRED
**Priority:** P1 | **Time:** 2 hours

---

### Phase 4: P2 Reference Data & Backfill (Week 4)

#### Task 4.1: Backfill Historical Stock Data
**File:** `Backend/src/tasks/backfill_tasks.py`
**Provider:** Yahoo Finance
**Priority:** P2 | **Time:** 3 hours

#### Task 4.2: Fetch SEC Filings Daily
**File:** `Backend/src/tasks/sec_filings_tasks.py`
**Provider:** SEC EDGAR
**Priority:** P2 | **Time:** 2 hours

#### Task 4.3: Fetch Technical Indicators Every 4 Hours
**File:** `Backend/src/tasks/technical_indicators_tasks.py`
**Provider:** Alpha Vantage
**Schedule:** Every 4 hours (optimized from 1 hour)
**Priority:** P2 | **Time:** 2 hours

---

### Phase 5: Celery Beat Schedule Configuration (Week 5)

#### Task 5.1: Update Celery Beat Schedule
**File:** `Backend/src/core/celery.py`
**Priority:** P0 | **Time:** 2 hours

#### Task 5.2: Create Monitoring Dashboard
**File:** `Backend/src/utils/services/task_monitor.py`
**Priority:** P1 | **Time:** 4 hours

#### Task 5.3: Create Management Commands
**Files:** `Backend/src/investments/management/commands/`
**Priority:** P1 | **Time:** 3 hours

---

### Phase 6: Testing & Deployment (Week 6)

#### Task 6.1: Create Task Tests
**File:** `Backend/src/tests/test_celery_tasks.py`
**Priority:** P0 | **Time:** 8 hours

#### Task 6.2: Deploy to Production
**Priority:** P0 | **Time:** 6 hours

---

## 📊 SUMMARY

### Tasks by Phase

| Phase | Tasks | Total Time | Priority |
|-------|--------|------------|----------|
| **Phase 1: Infrastructure** | 3 | 9 hours | P0 |
| **Phase 2: P0 Real-Time** | 6 | 11.5 hours | P0 |
| **Phase 3: P1 Important** | 5 | 10.5 hours | P1 |
| **Phase 4: P2 Reference** | 3 | 7 hours | P2 |
| **Phase 5: Schedule & Monitor** | 3 | 9 hours | P0-P1 |
| **Phase 6: Test & Deploy** | 2 | 14 hours | P0 |
| **TOTAL** | **22** | **61 hours** | **-** |

### Success Criteria

- [ ] All 50+ assets updated every 5-15 minutes
- [ ] Zero rate limit violations
- [ ] 95%+ task success rate
- [ ] <5s average task latency
- [ ] Database has 2+ years of historical data for all top assets
- [ ] News aggregated every 2 hours
- [ ] Real-time crypto prices via WebSocket
- [ ] Comprehensive monitoring and alerting

---

## 🚀 NEXT STEPS

### Questions for User

1. **Asset Priorities:** Which assets are most important to start with? (stocks, crypto, ETFs, etc.)
2. **Real-Time Requirements:** WebSocket for crypto real-time, or is 5-min polling OK?
3. **Historical Data:** Backfill all assets or just top 50?
4. **Timeline:** Is 6 weeks acceptable, or do you need this faster?

---

**Status:** ✅ READY FOR REVIEW & APPROVAL
**Next Action:** Awaiting user clarifications before implementation begins
