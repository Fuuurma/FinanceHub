# 🚨 PHASE 0: SEED BASE DATA - STARTED JAN 30, 2026

**Objective:** Expand from ~300 to 31,000+ assets with complete reference data

**Strategy:** 
1. Seed top 1,000 assets first (immediate value)
2. Background seed remaining 30,000+ assets
3. Populate ALL reference tables (countries, currencies, exchanges)
4. Save ALL fetched data to respective models (NO WASTED DATA!)

---

## ✅ PHASE 0 TASKS

### Task 0.1: Seed Countries (ISO 3166)
**Status:** PENDING
**Priority:** P0 - BLOCKS other assets
**File:** `Backend/src/utils/management/commands/seed_countries.py`
**Count:** 250+ countries
**Time Estimate:** 2 hours

**Data to Save:**
- code (ISO 2-letter)
- name
- alpha_3 (ISO 3-letter)
- numeric_code
- region
- subregion

**Command:**
```bash
python manage.py seed_countries
```

---

### Task 0.2: Seed Currencies (ISO 4217)
**Status:** PENDING
**Priority:** P0 - BLOCKS asset pricing
**File:** `Backend/src/utils/management/commands/seed_currencies.py`
**Count:** 180+ currencies
**Time Estimate:** 2 hours

**Data to Save:**
- code (ISO 3-letter)
- name
- symbol
- is_crypto
- decimals
- numeric_code

**Command:**
```bash
python manage.py seed_currencies
```

---

### Task 0.3: Seed Exchanges
**Status:** PENDING
**Priority:** P1
**File:** `Backend/src/utils/management/commands/seed_exchanges.py`
**Count:** 75+ exchanges
**Time Estimate:** 3 hours

**Data to Save:**
- code (MIC code)
- name
- country (FK to Country)
- timezone
- mic
- operating_hours

**Command:**
```bash
python manage.py seed_exchanges
```

---

### Task 0.4: Seed Benchmarks
**Status:** PENDING
**Priority:** P1
**File:** `Backend/src/utils/management/commands/seed_benchmarks.py`
**Count:** 20 benchmarks
**Time Estimate:** 1 hour

**Data to Save:**
- name
- ticker
- description
- asset_type

**Command:**
```bash
python manage.py seed_benchmarks
```

---

### Task 0.5: SEED TOP 1,000 STOCKS (Polygon.io) - IMMEDIATE PRIORITY 🚨
**Status:** PENDING
**Priority:** P0 - CRITICAL
**File:** `Backend/src/utils/management/commands/seed_top_stocks.py`
**Count:** 1,000 top stocks (market cap)
**Time Estimate:** 4 hours

**Data to Save (from Polygon.io):**
- ticker
- name
- market
- locale
- active
- currency
- cik
- composite_figi
- share_class_figi
- market_cap
- description
- primary_exchange
- type
- FIGI
- CIK

**Additional Data to Fetch & Save:**
- Company logo (from Clearbit/IEX)
- Sector/Industry (from IEX Cloud)
- Country (from SEC EDGAR)
- Website (from company data)
- Employee count
- Headquarters location

**Command:**
```bash
python manage.py seed_top_stocks --limit 1000
```

---

### Task 0.6: SEED TOP 500 CRYPTOS (CoinGecko) - IMMEDIATE PRIORITY 🚨
**Status:** PENDING
**Priority:** P0 - CRITICAL
**File:** `Backend/src/utils/management/commands/seed_top_cryptos.py`
**Count:** 500 top cryptos (market cap)
**Time Estimate:** 3 hours

**Data to Save (from CoinGecko):**
- ticker (symbol)
- name
- coingecko_id
- market_cap
- market_cap_rank
- current_price
- 24h_volume
- circulating_supply
- total_supply
- max_supply
- ath (all-time high)
- ath_date
- atl (all-time low)
- atl_date
- roi (return on investment)
- market_cap_change_24h
- price_change_percentage_24h
- hashing_algorithm
- categories (DeFi, NFT, etc.)
- description
- links (homepage, blockchain_site, forums, etc.)
- genesis_date
- sentiment (upvotes/downvotes)

**Additional Data to Fetch:**
- Historical prices (OHLCV)
- Market data pairs
- Exchange listings

**Command:**
```bash
python manage.py seed_top_cryptos --limit 500
```

---

### Task 0.7: SEED TOP 200 ETFS (Polygon.io)
**Status:** PENDING
**Priority:** P1
**File:** `Backend/src/utils/management/commands/seed_top_etfs.py`
**Count:** 200 top ETFs (AUM)
**Time Estimate:** 2 hours

**Data to Save:**
- ticker
- name
- market_cap (AUM)
- expense_ratio
- fund_family
- category
- holdings_count
- description
- inception_date

**Command:**
```bash
python manage.py seed_top_etfs --limit 200
```

---

### Task 0.8: SEED COMMODITIES, BONDS, FOREX
**Status:** PENDING
**Priority:** P2
**File:** `Backend/src/utils/management/commands/seed_other_assets.py`
**Count:** 100 additional assets
**Time Estimate:** 2 hours

**Data to Save:**
- Commodities (Gold, Silver, Oil, etc.)
- Bonds (Treasury, Corporate)
- Forex pairs

**Command:**
```bash
python manage.py seed_other_assets
```

---

### Task 0.9: Verify Asset Relationships
**Status:** PENDING
**Priority:** P0
**File:** `Backend/src/utils/management/commands/verify_asset_relationships.py`
**Time Estimate:** 2 hours

**Checks:**
- All assets have valid sector_fk/industry_fk
- All assets have valid country_fk
- All assets have valid currency
- All FK relationships exist
- No orphaned assets

**Command:**
```bash
python manage.py verify_asset_relationships
```

---

## 🔄 BACKGROUND TASKS (After Top 1,000)

### Task 0.10: Seed Remaining 9,000+ Stocks (Background)
**Status:** BLOCKED (waiting for 0.5)
**Priority:** P2
**File:** `Backend/src/utils/management/commands/seed_all_stocks.py`

---

### Task 0.11: Seed Remaining 17,500+ Cryptos (Background)
**Status:** BLOCKED (waiting for 0.6)
**Priority:** P2
**File:** `Backend/src/utils/management/commands/seed_all_cryptos.py`

---

### Task 0.12: Seed Remaining 2,800+ ETFs (Background)
**Status:** BLOCKED (waiting for 0.7)
**Priority:** P2
**File:** `Backend/src/utils/management/commands/seed_all_etfs.py`

---

## ⚡ PERFORMANCE OPTIMIZATION TASKS (RUST/C BASED)

### Task OPT-1: Replace json with orjson (14 files) 🚨
**Status:** PENDING
**Priority:** P0 - QUICK WIN
**Time Estimate:** 4 hours
**Speedup:** 2-4x JSON parsing

**Files to Update:**
1. `Backend/src/utils/pickle_cache.py`
2. `Backend/src/utils/services/cache_manager.py`
3. `Backend/src/consumers/market_data.py`
4. `Backend/src/utils/services/coingecko_websocket.py`
5. `Backend/src/utils/services/finnhub_websocket.py`
6. `Backend/src/data/data_providers/binance/websocket_client.py`
7. `Backend/src/investments/services/atlas_news_adapter.py`
8. `Backend/src/utils/services/ai_content_generator.py`
9. `Backend/src/utils/services/llm_advisor/ai_advisor.py`
10-14. (5 more files)

**Action:** Replace `import json` with `import orjson as json`

---

### Task OPT-2: Replace Pandas with Polars (8 files)
**Status:** PENDING
**Priority:** P1
**Time Estimate:** 8 hours
**Speedup:** 10-100x data processing

**Files to Update:**
1. `Backend/src/utils/services/populate_etfs.py`
2. `Backend/src/utils/services/populate_forex.py`
3. `Backend/src/utils/services/populate_crypto.py`
4. `Backend/src/utils/services/populate_indices.py`
5. `Backend/src/data/processing/pipeline.py`
6. `Backend/src/data/data_providers/yahooFinance/base.py`
7-8. (2 more files)

---

### Task OPT-3: Add Numexpr for Array Operations
**Status:** PENDING
**Priority:** P1
**Time Estimate:** 3 hours
**Speedup:** 2-5x NumPy operations

**Files to Update:**
1. `Backend/src/utils/services/technical_indicators.py`
2. `Backend/src/utils/services/risk/analyzer.py`
3. `Backend/src/api/analytics.py`

---

### Task OPT-4: Create Rust Extension - Technical Indicators 🔨
**Status:** PENDING
**Priority:** P0 - HIGH IMPACT
**Time Estimate:** 16 hours
**Speedup:** 10-50x indicator calculations

**File:** `Backend/src/rust_extensions/indicators.rs`

**Functions to Rewrite in Rust:**
- calculate_rsi()
- calculate_macd()
- calculate_bollinger_bands()
- calculate_stochastic()
- calculate_williams_r()
- calculate_ema()
- calculate_sma()

---

### Task OPT-5: Create Rust Extension - Correlation Analysis 🔨
**Status:** PENDING
**Priority:** P1
**Time Estimate:** 12 hours
**Speedup:** 5-20x correlation calculations

**File:** `Backend/src/rust_extensions/correlation.rs`

---

### Task OPT-6: Add Numba JIT for Indicators
**Status:** PENDING
**Priority:** P2 (alternative to Rust)
**Time Estimate:** 8 hours

---

### Task OPT-7: Optimize Database Queries
**Status:** PENDING
**Priority:** P0
**Time Estimate:** 6 hours
**Speedup:** 2-5x queries

**Optimizations:**
- Use bulk_create() for batch inserts
- Add select_related() for FK relationships
- Add database indexes
- Use only() for specific fields
- Use iterator() for large result sets

---

## 📊 SUMMARY

**Total Phase 0 Tasks:** 12 immediate + 3 background  
**Total Time:** 21 hours (immediate) + 18 hours (background)  
**Assets After Phase 0:** 1,800 top assets (ready for production)  
**Assets After Background:** 31,000+ total assets  

**Total Optimization Tasks:** 7 tasks  
**Total Time:** 57 hours  
**Expected Performance:** 5-20x system-wide improvement

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Next Action:** Start Task 0.1 (Seed Countries)
