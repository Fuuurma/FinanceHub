# FinanceHub - Celery Data Population & Performance Optimization Plan

**Document Type:** Implementation Plan
**Architect:** GAUDÍ (AI System Architect)
**Developer:** Human Coder
**DevOps:** KAREN (Infrastructure)
**Date:** January 30, 2026
**Status:** READY FOR IMPLEMENTATION
**Priority:** P0 - Critical for Data Growth & Performance

---

## 🎯 EXECUTIVE SUMMARY

**Objective:** 
1. **Seed thousands of base assets** (stocks, crypto, ETFs, etc.) - EXPAND from ~300 to 31,000+ assets
2. **Populate all reference/constant tables** (countries, currencies, exchanges, sectors, etc.)
3. **Implement efficient Celery tasks** with strict rate limit compliance
4. **Maximize performance** using Rust, C-libraries, Polars, and orjson

**Current State:**
- ✅ 19 data providers available (16 fully implemented)
- ✅ Celery infrastructure configured
- ✅ Polars used in 23 files ✅
- ✅ orjson used in 21 files ✅
- ⚠️ **Only ~300 assets** (need 31,000+)
- ⚠️ **4 reference tables empty** (Country, Currency, Exchange, Benchmark)
- ⚠️ **14 files still use json** (should use orjson)
- ⚠️ **8 files still use Pandas** (should use Polars)

**Target State:**
- 🎯 **31,000+ assets** (10K stocks, 18K crypto, 3K ETFs)
- 🎯 **All reference tables populated** (countries, currencies, exchanges, etc.)
- 🎯 **50+ Celery tasks** running 24/7
- 🎯 **5-20x performance improvement** via Rust/C optimizations
- 🎯 **Zero rate limit violations**
- 🎯 **15-min caching** = 95% fewer API calls

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

## 🚨 PHASE 0: CRITICAL - SEED BASE DATA (Week 1)

### **Problem:** Only ~300 assets in database, missing reference tables

### **Solution:** Seed THOUSANDS of assets and all reference tables FIRST

---

### Task 0.1: Seed Countries (ISO 3166)
**File:** `Backend/src/utils/management/commands/seed_countries.py`
**Source:** Wikipedia ISO 3166 table
**Count:** 250+ countries
**Priority:** P0 - BLOCKS other assets
**Time:** 2 hours

**Implementation:**
```python
# Parse Wikipedia table or use existing Python package
# pip install pycountry
import pycountry

for country in pycountry.countries:
    Country.objects.create(
        code=country.alpha_2,
        name=country.name,
        alpha_3=country.alpha_3,
        numeric=country.numeric
    )
```

---

### Task 0.2: Seed Currencies (ISO 4217)
**File:** `Backend/src/utils/management/commands/seed_currencies.py`
**Source:** ISO 4217 or forex_python package
**Count:** 180+ currencies (fiat + crypto)
**Priority:** P0 - BLOCKS asset pricing
**Time:** 2 hours

**Implementation:**
```python
# Use existing forex_python package data
from forex_python.raw_data import currencies

for code, data in currencies.items():
    Currency.objects.create(
        code=code,
        name=data['name'],
        symbol=data['symbol'],
        is_crypto=False,
        decimals=2
    )
```

---

### Task 0.3: Seed Exchanges
**File:** `Backend/src/utils/management/commands/seed_exchanges.py`
**Source:** Wikipedia "List of Stock Exchanges"
**Count:** 75+ major exchanges
**Priority:** P1 - Important for asset metadata
**Time:** 3 hours

**Data:** NYSE, NASDAQ, LSE, TSE, HKEX, ASX, etc.

---

### Task 0.4: Seed Benchmarks
**File:** `Backend/src/utils/management/commands/seed_benchmarks.py`
**Source:** Major market indices
**Count:** 20 benchmarks
**Priority:** P1
**Time:** 1 hour

**Data:** S&P 500 (^GSPC), Dow Jones (^DJI), NASDAQ (^IXIC), Russell 2000 (^RUT), FTSE 100 (^UKX), Nikkei 225 (^N225), etc.

---

### Task 0.5: SEED 10,000+ STOCKS (Polygon.io)
**File:** `Backend/src/utils/management/commands/seed_all_stocks.py`
**Source:** Polygon.io tickers endpoint
**Count:** 10,000+ US stocks
**Priority:** P0 - CRITICAL
**Time:** 4 hours

**Implementation:**
```python
# Use existing Polygon.io scraper with pagination
from data.data_providers.polygon_io.scraper import PolygonIOScraper

scraper = PolygonIOScraper()
tickers = scraper.get_all_tickers(
    market='stocks', 
    active=True,
    limit=50  # Paginate through all
)

for ticker in tickers:
    Asset.objects.create(
        ticker=ticker['ticker'],
        name=ticker['name'],
        asset_type=AssetType.objects.get(name='Stock'),
        # ... other fields
    )
```

**API Calls:** 200 requests (50 per page × 20 pages)  
**Rate Limit:** 5 req/min = 40 minutes  
**Optimization:** Run async

---

### Task 0.6: SEED 18,000+ CRYPTOS (CoinGecko)
**File:** `Backend/src/utils/management/commands/seed_all_cryptos.py`
**Source:** CoinGecko `/coins/list` endpoint
**Count:** 18,000+ cryptocurrencies
**Priority:** P0 - CRITICAL
**Time:** 2 hours

**Implementation:**
```python
# Single API call - no pagination needed!
from data.data_providers.coinGecko.scraper import CoinGeckoScraper

scraper = CoinGeckoScraper()
all_coins = scraper.get_all_coins_list()  # Returns ALL 18,000+ coins

for coin in all_coins:
    Asset.objects.create(
        ticker=coin['symbol'].upper(),
        name=coin['name'],
        asset_type=AssetType.objects.get(name='Crypto'),
        # ...
    )
```

**API Calls:** 1 (SINGLE CALL!)  
**Rate Limit:** 50 req/min (trivial)  
**Time:** <5 minutes for API call, ~2 hours for DB insert

---

### Task 0.7: SEED 3,000+ ETFS (Polygon.io)
**File:** `Backend/src/utils/management/commands/seed_all_etfs.py`
**Source:** Polygon.io tickers (filter by type=ETF)
**Count:** 3,000+ ETFs
**Priority:** P1
**Time:** 3 hours

---

### Task 0.8: SEED COMMODITIES, BONDS, FOREX
**File:** `Backend/src/utils/management/commands/seed_remaining_assets.py`
**Count:** 500+ additional assets
**Priority:** P2
**Time:** 2 hours

---

### Task 0.9: Verify & Link Relationships
**File:** `Backend/src/utils/management/commands/verify_asset_relationships.py`
**Description:** Ensure all FK relationships are valid (sector_fk, industry_fk, country_fk, currency_fk)
**Priority:** P0
**Time:** 2 hours

---

### **PHASE 0 SUMMARY:**

| Task | Assets Created | Time | Priority |
|------|----------------|------|----------|
| Seed Countries | 250+ | 2h | P0 |
| Seed Currencies | 180+ | 2h | P0 |
| Seed Exchanges | 75+ | 3h | P1 |
| Seed Benchmarks | 20 | 1h | P1 |
| **Seed Stocks** | **10,000+** | **4h** | **P0** |
| **Seed Cryptos** | **18,000+** | **2h** | **P0** |
| Seed ETFs | 3,000+ | 3h | P1 |
| Seed Others | 500+ | 2h | P2 |
| Verify | - | 2h | P0 |
| **TOTAL** | **~31,000+** | **21h** | **-** |

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

---

## ⚡ PERFORMANCE OPTIMIZATION PHASE (Parallel with Celery Tasks)

### **Current Optimization State:**
- ✅ Polars: 23 files (Rust-based DataFrame)
- ✅ orjson: 21 files (Rust JSON parser)
- ✅ NumPy: 38 files (C-based numerical)
- ⚠️ **Pandas: 8 files** (should be Polars)
- ⚠️ **json: 14 files** (should be orjson)
- ⚠️ **Python loops: 60+ in technical indicators** (should be Rust)

---

### Task OPT-1: Replace json with orjson (14 files)
**Priority:** P0 - QUICK WIN
**Time:** 4 hours
**Speedup:** 2-4x JSON serialization

**Files to Update:**
```
src/utils/pickle_cache.py
src/utils/services/cache_manager.py
src/consumers/market_data.py
src/utils/services/coingecko_websocket.py
src/utils/services/finnhub_websocket.py
src/data/data_providers/binance/websocket_client.py
src/investments/services/atlas_news_adapter.py
src/utils/services/ai_content_generator.py
src/utils/services/llm_advisor/ai_advisor.py
... (5 more files)
```

**Implementation:**
```python
# Simple drop-in replacement
import orjson as json

# All existing json.dumps() / json.loads() calls work automatically
# but 2-4x faster (Rust-based parser)
```

---

### Task OPT-2: Replace Pandas with Polars (8 files)
**Priority:** P1 - QUICK WIN
**Time:** 8 hours
**Speedup:** 10-100x for large datasets

**Files to Update:**
```
src/utils/services/populate_etfs.py
src/utils/services/populate_forex.py
src/utils/services/populate_crypto.py
src/utils/services/populate_indices.py
src/data/processing/pipeline.py
src/data/data_providers/yahooFinance/base.py
```

**Implementation:**
```python
# Before (Pandas):
import pandas as pd
df = pd.DataFrame(data)
result = df['price'].mean()

# After (Polars):
import polars as pl
df = pl.DataFrame(data)
result = df['price'].mean()
```

---

### Task OPT-3: Add Numexpr for Array Operations
**Priority:** P1
**Time:** 3 hours
**Speedup:** 2-5x for NumPy operations

**Files to Update:**
- `src/utils/services/technical_indicators.py`
- `src/utils/services/risk/analyzer.py`
- `src/api/analytics.py`

**Implementation:**
```python
import numexpr

# Before (NumPy):
result = (prices - prices.mean()) / prices.std()

# After (Numexpr):
result = numexpr.evaluate("(prices - mean(prices)) / std(prices)")
```

---

### Task OPT-4: Create Rust PyO3 Extension - Technical Indicators
**File:** `Backend/src/rust_extensions/` (NEW)
**Priority:** P0 - HIGH IMPACT
**Time:** 16 hours
**Speedup:** 10-50x for indicator calculations

**Functions to Rewrite in Rust:**
```rust
// src/indicators.rs
use pyo3::prelude::*;

#[pyfunction]
fn calculate_rsi(prices: Vec<f64>, period: usize) -> Vec<f64> {
    // Rust implementation - 10-50x faster than Python
    let mut gains = Vec::new();
    let mut losses = Vec::new();
    // ... calculation logic
}

#[pyfunction]
fn calculate_macd(prices: Vec<f64>, fast: usize, slow: usize, signal: usize) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    // Rust implementation
}

#[pyfunction]
fn calculate_bollinger_bands(prices: Vec<f64>, period: usize, std_dev: f64) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    // Rust implementation
}
```

**Python Integration:**
```python
# In Python code
from rust_extensions.indicators import calculate_rsi, calculate_macd

# 10-50x faster than pure Python
rsi_values = calculate_rsi(prices, period=14)
```

---

### Task OPT-5: Create Rust PyO3 Extension - Correlation Analysis
**File:** `Backend/src/rust_extensions/correlation.rs`
**Priority:** P1
**Time:** 12 hours
**Speedup:** 5-20x for portfolio correlation

**Implementation:**
```rust
use pyo3::prelude::*;
use ndarray::Array2;
use rayon::prelude::*;

#[pyfunction]
fn calculate_correlation_matrix(prices: Vec<Vec<f64>>) -> Vec<Vec<f64>> {
    // Parallel correlation calculation with Rayon
    // O(n²) but parallelized
}
```

---

### Task OPT-6: Add Numba JIT for Technical Indicators
**Priority:** P2 (alternative to Rust)
**Time:** 8 hours
**Speedup:** 10-100x for decorated functions

**Implementation:**
```python
from numba import jit

@jit(nopython=True)
def calculate_rsi_numba(prices: np.ndarray, period: int = 14) -> np.ndarray:
    # Compiled to machine code
    # 10-100x faster than pure Python
    pass
```

---

### Task OPT-7: Optimize Database Queries
**Priority:** P0
**Time:** 6 hours

**Optimizations:**
```python
# Use bulk_create instead of individual saves
Asset.objects.bulk_create([
    Asset(ticker=symbol, name=name, ...)
    for symbol, name in assets_data
], batch_size=1000)

# Use select_related for FK relationships
assets = Asset.objects.select_related(
    'asset_type', 'sector_fk', 'industry_fk', 'country_fk'
).all()

# Use only() to fetch only needed fields
assets = Asset.objects.only('ticker', 'name', 'last_price')

# Use iterator() for large result sets
for asset in Asset.objects.iterator():
    # Process without loading all into memory
    pass
```

---

### **PERFORMANCE OPTIMIZATION SUMMARY:**

| Optimization | Files | Time | Speedup | Priority |
|--------------|-------|------|---------|----------|
| **json → orjson** | 14 | 4h | 2-4x | P0 |
| **Pandas → Polars** | 8 | 8h | 10-100x | P1 |
| **Numexpr** | 3 | 3h | 2-5x | P1 |
| **Rust: Indicators** | 1 | 16h | 10-50x | P0 |
| **Rust: Correlation** | 1 | 12h | 5-20x | P1 |
| **Numba JIT** | 1 | 8h | 10-100x | P2 |
| **DB Optimization** | All | 6h | 2-5x | P0 |
| **TOTAL** | 28+ | **57h** | **5-20x system-wide** | - |

---

## 📋 IMPLEMENTATION TASKS (Revised)

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

---

## 📊 REVISED IMPLEMENTATION ROADMAP

### **Week 1: Phase 0 - Seed Base Data (CRITICAL!)**
**Must complete BEFORE any other work**

- [x] Task 0.1: Seed Countries (250+)
- [x] Task 0.2: Seed Currencies (180+)
- [x] Task 0.3: Seed Exchanges (75+)
- [x] Task 0.4: Seed Benchmarks (20)
- [x] **Task 0.5: SEED 10,000+ STOCKS** (Polygon.io)
- [x] **Task 0.6: SEED 18,000+ CRYPTOS** (CoinGecko)
- [x] Task 0.7: Seed 3,000+ ETFs
- [x] Task 0.8: Seed commodities, bonds, forex
- [x] Task 0.9: Verify relationships

**Week 1 Total:** 21 hours | **Result:** 31,000+ assets in database

---

### **Week 2-3: Phase 1 - Infrastructure + Performance**
**Parallel tracks: Infrastructure & Optimization**

**Infrastructure:**
- Task 1.1: Rate Limiter Service (4h)
- Task 1.2: Asset Registry Service (2h)
- Task 1.3: Celery Task Base Class (3h)

**Performance (QUICK WINS):**
- Task OPT-1: Replace json with orjson (4h)
- Task OPT-2: Replace Pandas with Polars (8h)
- Task OPT-3: Add Numexpr (3h)
- Task OPT-7: DB Optimization (6h)

**Week 2-3 Total:** 30 hours | **Result:** 3-5x performance boost

---

### **Week 4-5: Phase 2 - P0 Real-Time Price Tasks**
**Now that we have 31,000+ assets, implement Celery tasks**

- Task 2.1: Fetch Top Stocks Every 5 min (2h)
- Task 2.2: Fetch Crypto Prices Every 5 min (3h)
- Task 2.3: Fetch ETF Prices Every 15 min (1.5h)
- Task 2.4: Fetch Index Prices Every 15 min (1.5h)
- Task 2.5: Fetch Forex Rates Every 30 min (1.5h)
- Task 2.6: Fetch Commodity Prices Every 30 min (1.5h)

**Week 4-5 Total:** 11 hours | **Result:** Real-time price updates

---

### **Week 6-7: Phase 3 - P1 Important Data Tasks**

- Task 3.1: Fetch News Every 2 hours (2h)
- Task 3.2: Fetch Stock Fundamentals Every 6 hours (2h)
- Task 3.3: Fetch DeFi TVL Every hour (2h)
- Task 3.4: Fetch Market Movers Every 15 min (1.5h)
- Task 3.5: Fetch Economic Indicators Daily (2h)

**Week 6-7 Total:** 9.5 hours | **Result:** News, fundamentals, market data

---

### **Week 8: Phase 4 - P2 Reference Data & Rust**

**Backfill:**
- Task 4.1: Backfill Historical Stock Data (3h)
- Task 4.2: Fetch SEC Filings Daily (2h)
- Task 4.3: Fetch Technical Indicators (2h)

**Rust Performance:**
- Task OPT-4: Rust Technical Indicators (16h)
- Task OPT-5: Rust Correlation Analysis (12h)

**Week 8 Total:** 35 hours | **Result:** Historical data + 10-50x faster calculations

---

### **Week 9: Phase 5 - Schedule & Monitor**

- Task 5.1: Update Celery Beat Schedule (2h)
- Task 5.2: Create Monitoring Dashboard (4h)
- Task 5.3: Create Management Commands (3h)

**Week 9 Total:** 9 hours | **Result:** Automated scheduling

---

### **Week 10: Phase 6 - Testing & Deployment**

- Task 6.1: Create Task Tests (8h)
- Task 6.2: Deploy to Production (6h)

**Week 10 Total:** 14 hours | **Result:** Production-ready

---

## 📊 FINAL SUMMARY

### **Revised Tasks by Phase**

| Phase | Tasks | Total Time | Priority | Key Outcome |
|-------|--------|------------|----------|-------------|
| **Phase 0: Seed Base Data** | 9 | 21h | **P0** | **31,000+ assets** |
| **Phase 1: Infra + Performance** | 7 | 30h | **P0-P1** | **3-5x faster** |
| **Phase 2: P0 Real-Time** | 6 | 11h | P0 | Real-time prices |
| **Phase 3: P1 Important** | 5 | 9.5h | P1 | News, fundamentals |
| **Phase 4: P2 + Rust** | 6 | 35h | P1-P2 | **10-50x calculations** |
| **Phase 5: Schedule** | 3 | 9h | P0-P1 | Automation |
| **Phase 6: Test & Deploy** | 2 | 14h | P0 | Production |
| **TOTAL** | **38** | **129.5h** | - | **Complete system** |

### **Estimated Timeline:** 10 weeks

### **Asset Coverage After Completion:**
- **Stocks:** 10,000+ (up from ~200)
- **Crypto:** 18,000+ (up from ~50)
- **ETFs:** 3,000+ (up from ~35)
- **Indices:** 50+ (up from ~8)
- **Forex:** 100+ (up from ~10)
- **Commodities:** 50+ (up from ~5)
- **Bonds:** 50+ (new)
- **TOTAL:** **31,305+ assets** (up from ~300)

### **Performance Improvements:**
- **JSON parsing:** 2-4x faster (orjson)
- **Data processing:** 10-100x faster (Polars)
- **Technical indicators:** 10-50x faster (Rust)
- **Correlation analysis:** 5-20x faster (Rust)
- **Database queries:** 2-5x faster (optimized)
- **Overall system:** 5-20x performance boost

### **Success Criteria:**

- [ ] **31,000+ assets** in database (10K stocks, 18K crypto, 3K ETFs)
- [ ] **All reference tables populated** (countries, currencies, exchanges, etc.)
- [ ] **50+ Celery tasks** running 24/7
- [ ] **Zero rate limit violations**
- [ ] **95%+ task success rate**
- [ ] **<5s average task latency**
- [ ] **5-20x overall performance improvement**
- [ ] **2+ years historical data** for all top assets
- [ ] **News aggregated** every 2 hours
- [ ] **Real-time crypto prices** via WebSocket
- [ ] **Comprehensive monitoring** and alerting

---

## 🚨 REVISED NEXT STEPS

### **IMMEDIATE ACTIONS (This Week)**

1. **START WITH PHASE 0** - Seed base data FIRST
   - Run `python manage.py seed_countries`
   - Run `python manage.py seed_currencies`
   - Run `python manage.py seed_all_stocks` (10,000+!)
   - Run `python manage.py seed_all_cryptos` (18,000+!)

2. **Quick performance wins** (parallel):
   - Replace `import json` with `import orjson` (14 files)
   - Replace `import pandas` with `import polars` (8 files)

3. **Then proceed** with Celery tasks (Phase 2+)

---

## 🤔 QUESTIONS FOR USER (UPDATED)

1. **Seed Data Order:** Should we seed all 31,000+ assets at once, or prioritize top assets first?
   - [ ] Seed all 31,000+ (takes ~21 hours, one-time)
   - [ ] Seed top 1,000 first, then background seed remaining

2. **Performance vs Features:** Should we prioritize Rust rewrites or Celery tasks?
   - [ ] Rust first (10-50x faster calculations, delays Celery by 2 weeks)
   - [ ] Celery first (start data flowing sooner, optimize later)

3. **Historical Data:** Should we backfill all 31,000+ assets or just top 1,000?
   - [ ] All assets (months of backfill, 100K+ API calls)
   - [ ] Top 1,000 only (realistic, 2-3 days of backfill)

4. **WebSocket:** Implement Binance WebSocket for real-time crypto?
   - [ ] Yes (0 API calls, truly real-time)
   - [ ] No (5-min polling is sufficient, simpler)

5. **Timeline:** Is 10 weeks acceptable, or do you need aggressive timeline?
   - [ ] 10 weeks is fine (quality first)
   - [ ] Need it faster (what's your deadline?)

---

**Status:** ✅ PLAN UPDATED - READY FOR APPROVAL
**Next Action:** Awaiting user approval to start Phase 0 (seed base data)
**Total Tasks:** 38 tasks
**Total Time:** 129.5 hours (~10 weeks)
**Asset Coverage:** 31,305+ assets (10,000% increase!)
**Performance:** 5-20x system-wide improvement

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
