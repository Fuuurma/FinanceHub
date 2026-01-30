# FinanceHub - Complete Data Providers & Population Scripts Guide

## 📊 All Available Data Providers

### 🆓 FREE TIER (No API Key Required)

#### 1. Yahoo Finance (yfinance)
**Location**: `Backend/src/data/data_providers/yahooFinance/`
**Free Tier**: ✅ **UNLIMITED** (No API key needed!)
**Data Types**:
- Stock prices (real-time & historical)
- ETF data
- Index data
- Forex pairs
- Cryptocurrency prices
- Company fundamentals
- Financial statements

**Rate Limits**: None (free tier is unlimited)

**Scripts Available**:
- `populate_yfinance.py` - Main population script
- `yfinance_populator.py` - Full database population
- `populate_stocks.py` - Stock-specific population
- `populate_etfs.py` - ETF population
- `populate_forex.py` - Forex pair population
- `populate_indices.py` - Market indices population

**Usage**:
```bash
cd Backend/src
python manage.py populate_yfinance --phase setup
```

---

#### 2. CoinGecko
**Location**: `Backend/src/data/data_providers/coingecko/`
**Free Tier**: ✅ **30 calls/minute** (250K/month free)
**Data Types**:
- Cryptocurrency prices (real-time & historical)
- Market cap rankings
- Trading volume
- Price changes (1h, 24h, 7d, 30d)
- Crypto metadata
- Exchange data
- Developer data
- Community data

**Rate Limits**:
- 30 calls/minute
- 250,000 calls/month (free tier)

**Scripts Available**:
- `fetch_top_cryptos.py` - Fetch top 100-500 cryptos
- `populate_crypto.py` - Full crypto population

**Usage**:
```bash
cd Backend/src
python manage.py fetch_top_cryptos --limit 100

# Or use background jobs
./manage_jobs.sh start
```

---

### 🔑 API KEY REQUIRED (Free Tier Available)

#### 3. Alpha Vantage
**Location**: `Backend/src/data/data_providers/alphaVantage/`
**Free Tier**: 25 calls/day (requires free API key)
**Data Types**:
- Stock prices
- Forex rates
- Cryptocurrency
- Technical indicators
- Fundamental data
- Economic indicators
- News & sentiment

**Rate Limits**:
- 25 calls/day (free tier)
- 500 requests/day (paid tier starts at free)

**Setup Required**:
```bash
# Get free API key from: https://www.alphavantage.co/support/#api-key
# Add to .env file:
ALPHA_VANTAGE_API_KEY=your_key_here
```

---

#### 4. FRED (Federal Reserve Economic Data)
**Location**: `Backend/src/data/data_providers/fred/`
**Free Tier**: 120 requests/day (requires free API key)
**Data Types**:
- Economic indicators (GDP, CPI, unemployment)
- Interest rates
- Exchange rates
- Financial market data
- Regional data
- International data

**Rate Limits**: 120 requests/day (free tier)

**Scripts Available**:
- `seed_economic_data.py` - Seed popular economic indicators

**Usage**:
```bash
cd Backend/src
python manage.py seed_economic_data --fetch-data --limit 50
```

---

#### 5. Finnhub
**Location**: `Backend/src/data/data_providers/finnHub/`
**Free Tier**: 60 calls/minute (requires free API key)
**Data Types**:
- Stock prices
- News
- Company fundamentals
- Insider trading
- Earnings calendar
- Financials
- IPO calendar
- Economic data

**Rate Limits**: 60 calls/minute (free tier)

---

#### 6. IEX Cloud
**Location**: `Backend/src/data/data_providers/iex_cloud/`
**Free Tier**: 500,000 calls/month (requires free API key)
**Data Types**:
- Stock prices
- Company data
- News
- CEO compensation
- Cryptocurrency
- Forex
- Market data

**Rate Limits**: 500,000 calls/month (generous free tier!)

---

#### 7. Polygon.io
**Location**: `Backend/src/data/data_providers/polygon_io/`
**Free Tier**: 5 calls/minute (very limited)
**Data Types**:
- Stock prices
- Forex
- Crypto
- News

**Rate Limits**: 5 calls/minute (free tier)

---

#### 8. NewsAPI
**Location**: `Backend/src/data/data_providers/newsapi/`
**Free Tier**: 100 requests/day (requires free API key)
**Data Types**:
- Financial news
- Business news
- Tech news
- General news

**Rate Limits**: 100 requests/day (free tier)

---

#### 9. Binance
**Location**: `Backend/src/data/data_providers/binance/`
**Free Tier**: 1,200 calls/minute (no API key for public data!)
**Data Types**:
- Crypto prices (real-time)
- Order book depth
- Trade history
- Klines (candlestick data)
- 24hr ticker statistics

**Rate Limits**: 1,200 calls/minute (generous!)

---

#### 10. CoinMarketCap
**Location**: `Backend/src/data/data_providers/coinmarketcap/`
**Free Tier**: 10,000 calls/day (requires free API key)
**Data Types**:
- Crypto prices
- Market cap rankings
- Metadata
- Exchange data

**Rate Limits**: 10,000 calls/day (free tier)

---

## 🚀 Population Scripts Available

### Core Management Commands

#### 1. Reference Data Seeding
**File**: `Backend/src/utils/management/commands/seed_reference_data.py`
**Purpose**: Seeds GICS sectors, industries, timezones
**Usage**:
```bash
cd Backend/src
python manage.py seed_reference_data
python manage.py seed_reference_data --sectors-only
python manage.py seed_reference_data --timezones-only
python manage.py seed_reference_data --reset
```

---

#### 2. Top Cryptos Fetch
**File**: `Backend/src/core/management/commands/fetch_top_cryptos.py`
**Purpose**: Fetch top 100-500 cryptocurrencies from CoinGecko
**Usage**:
```bash
cd Backend/src
python manage.py fetch_top_cryptos --limit 100
python manage.py fetch_top_cryptos --limit 250 --vs-currency usd
```

---

#### 3. Economic Data Seeding
**File**: `Backend/src/investments/management/commands/seed_economic_data.py`
**Purpose**: Seed FRED economic indicators
**Usage**:
```bash
cd Backend/src
python manage.py seed_economic_data
python manage.py seed_economic_data --fetch-data --limit 50
```

---

### Population Scripts (Services)

#### 4. Yahoo Finance Populator
**File**: `Backend/src/utils/services/yfinance_populator.py`
**Purpose**: Complete database population with Yahoo Finance data
**Features**:
- Setup reference data (asset classes, types, countries, currencies, exchanges)
- Populate stocks with historical data
- Populate ETFs
- Populate forex pairs
- Populate indices

**Usage**:
```bash
cd Backend/src
python manage.py shell
>>> import asyncio
>>> from utils.services.yfinance_populator import run_full_population
>>> asyncio.run(run_full_population())
```

---

#### 5. Stock Populator
**File**: `Backend/src/utils/services/populate_stocks.py`
**Purpose**: Populate stock data specifically
**Stocks Covered**: 100+ major stocks (Dow Jones, S&P 500, Nasdaq 100)

---

#### 6. Crypto Populator
**File**: `Backend/src/utils/services/populate_crypto.py`
**Purpose**: Populate cryptocurrency data

---

#### 7. ETF Populator
**File**: `Backend/src/utils/services/populate_etfs.py`
**Purpose**: Populate ETF data

---

#### 8. Forex Populator
**File**: `Backend/src/utils/services/populate_forex.py`
**Purpose**: Populate forex pairs

---

#### 9. Indices Populator
**File**: `Backend/src/utils/services/populate_indices.py`
**Purpose**: Populate market indices

---

## 🔧 Service Files (Advanced)

### Data Processing Services

1. **`yahoo_batch_optimizer.py`** - Optimize Yahoo Finance batch requests
2. **`yahoo_rate_limiter.py`** - Rate limiting for Yahoo Finance
3. **`call_planner.py`** - API call planning and rate limiting
4. **`cache_manager.py`** - Data caching layer
5. **`data_orchestrator.py`** - Orchestrate data fetching from multiple sources
6. **`technical_indicators.py`** - Calculate technical indicators
7. **`fundamental_service.py`** - Fundamental data processing
8. **`currency_service.py`** - Currency exchange rates
9. **`exchange_rate_fetcher.py`** - Exchange rate data fetching

---

## 📋 Test Scripts for Each Provider

All test scripts are in: `Backend/src/investments/management/commands/`

```bash
# Test each provider
python manage.py test_alpha_vantage
python manage.py test_coingecko
python manage.py test_coinmarketcap
python manage.py test_finnhub
python manage.py test_fred
python manage.py test_iex_cloud
python manage.py test_polygon
python manage.py test_news
python manage.py test_sec_edgar
```

---

## 🎯 Recommended Data Population Strategy

### Phase 1: Setup Reference Data (No API Key)
```bash
cd Backend/src
python manage.py seed_reference_data --reset
```

### Phase 2: Populate with Free Tiers (No API Key)

#### Yahoo Finance (UNLIMITED - FREE)
```bash
python manage.py populate_yfinance --phase setup
```

#### CoinGecko (30 calls/min - 250K/month)
```bash
python manage.py fetch_top_cryptos --limit 100
```

#### Binance (1,200 calls/min - FREE)
```bash
# Use through background jobs
cd Backend
./manage_jobs.sh start
```

### Phase 3: Add API Keys (Optional)

1. **Get Free API Keys**:
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key
   - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
   - Finnhub: https://finnhub.io/register
   - IEX Cloud: https://iexcloud.io/pricing
   - NewsAPI: https://newsapi.org/register

2. **Add to `.env` file**:
```bash
cd Backend
cat .env
```

3. **Run population scripts**:
```bash
# Alpha Vantage stocks
python manage.py test_alpha_vantage

# FRED economic data
python manage.py seed_economic_data --fetch-data

# News
python manage.py test_news
```

---

## 📊 What Data You Can Get RIGHT NOW (Without API Keys)

### ✅ Immediately Available

1. **Stock Data** (Yahoo Finance - UNLIMITED):
   - 100+ major stocks
   - Historical prices
   - Real-time quotes
   - Company fundamentals
   - Financial statements

2. **Cryptocurrency** (CoinGecko - 30/min, Binance - 1,200/min):
   - Top 100-500 cryptos by market cap
   - Real-time prices
   - Historical data
   - Market cap rankings

3. **ETFs** (Yahoo Finance - UNLIMITED):
   - Top ETFs
   - Historical data
   - Holdings data

4. **Forex** (Yahoo Finance - UNLIMITED):
   - Major pairs
   - Historical rates
   - Real-time quotes

5. **Indices** (Yahoo Finance - UNLIMITED):
   - S&P 500
   - Dow Jones
   - Nasdaq
   - Global indices

---

## 🚀 Quick Start Commands

### Option 1: Full Population (Yahoo Finance + CoinGecko)
```bash
cd Backend/src

# 1. Setup reference data
python manage.py seed_reference_data --reset

# 2. Populate with Yahoo Finance (unlimited)
python manage.py populate_yfinance --phase setup

# 3. Add top cryptos from CoinGecko
python manage.py fetch_top_cryptos --limit 100

# 4. Start background jobs for continuous updates
cd ../
./manage_jobs.sh start
```

### Option 2: Background Jobs Only (Already Running!)
```bash
cd Backend
./manage_jobs.sh status    # Check status
./manage_jobs.sh monitor   # Live dashboard
```

---

## 📈 Monitoring Your Data Population

### Check Database Contents
```sql
-- Count assets by type
SELECT asset_type_id, COUNT(*) FROM assets_asset GROUP BY asset_type_id;

-- Check latest prices
SELECT symbol, MAX(timestamp) as latest_update 
FROM assets_assetpriceshistoric 
GROUP BY symbol 
ORDER BY latest_update DESC 
LIMIT 20;

-- Total records
SELECT COUNT(*) FROM assets_assetpriceshistoric;
```

### Using Django Shell
```bash
cd Backend/src
python manage.py shell

>>> from assets.models.asset import Asset
>>> from assets.models.historic.prices import AssetPricesHistoric

# Count assets
>>> Asset.objects.count()

# Count price records
>>> AssetPricesHistoric.objects.count()

# Latest BTC price
>>> btc = Asset.objects.get(symbol='BTC')
>>> btc.prices.order_by('-timestamp').first()
```

---

## 🔥 Top Recommendations

### 1. Start with Yahoo Finance (UNLIMITED + NO API KEY)
```bash
cd Backend/src
python manage.py populate_yfinance --phase setup
```

### 2. Add Cryptos (CoinGecko FREE TIER)
```bash
python manage.py fetch_top_cryptos --limit 250
```

### 3. Enable Background Jobs (ALREADY RUNNING!)
```bash
cd Backend
./manage_jobs.sh status
```

### 4. Add API Keys Later (When Needed)
- Get free API keys
- Add to `.env`
- Run specific population scripts

---

## 📊 Summary Table

| Provider | Free Tier | API Key | Rate Limit | Data Types | Recommended |
|----------|-----------|----------|------------|------------|-------------|
| **Yahoo Finance** | ✅ UNLIMITED | ❌ No | None | Stocks, ETFs, Forex, Indices, Crypto | ⭐⭐⭐⭐⭐ |
| **CoinGecko** | ✅ 250K/month | ❌ No | 30/min | Crypto | ⭐⭐⭐⭐⭐ |
| **Binance** | ✅ FREE | ❌ No | 1,200/min | Crypto | ⭐⭐⭐⭐⭐ |
| **Alpha Vantage** | ✅ 25/day | ⚠️ Yes | 25/day | Stocks, Forex, Indicators | ⭐⭐⭐ |
| **FRED** | ✅ 120/day | ⚠️ Yes | 120/day | Economic Indicators | ⭐⭐⭐⭐ |
| **Finnhub** | ✅ 60/min | ⚠️ Yes | 60/min | Stocks, News | ⭐⭐⭐ |
| **IEX Cloud** | ✅ 500K/month | ⚠️ Yes | Varies | Stocks, Crypto, News | ⭐⭐⭐⭐ |
| **CoinMarketCap** | ✅ 10K/day | ⚠️ Yes | 10K/day | Crypto | ⭐⭐⭐ |
| **Polygon.io** | ⚠️ 5/min | ⚠️ Yes | 5/min | Stocks, Crypto | ⭐⭐ |
| **NewsAPI** | ✅ 100/day | ⚠️ Yes | 100/day | News | ⭐⭐⭐ |

---

## 🎉 Conclusion

You have **3 EXCELLENT options** that work RIGHT NOW without any API keys:

1. ✅ **Yahoo Finance** - UNLIMITED stocks, ETFs, forex, indices
2. ✅ **CoinGecko** - 250K/month cryptocurrency data
3. ✅ **Binance** - 1,200/minute crypto data

Your background jobs are **already running** and using these free tiers!

**Next Steps**:
1. ✅ Background jobs are running (check: `./manage_jobs.sh status`)
2. 📊 Monitor growth: `./manage_jobs.sh monitor`
3. 💾 Query your database for insights
4. 🔑 Add API keys later when needed for enhanced features

🚀 **Your FinanceHub database is being populated automatically!**
