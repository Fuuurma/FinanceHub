# FinanceHub Data Pipeline - Complete Architecture Documentation

**Session Date:** January 30, 2026
**Location:** `/Users/sergi/Desktop/Projects/FinanceHub`
**Status:** ✅ Full exploration completed

---

## 🎯 EXECUTIVE SUMMARY

FinanceHub implements a **production-grade data pipeline** with:
- ✅ Automated web scraping (SEC EDGAR, NewsAPI, RSS)
- ✅ Real-time data collection (Dramatiq + Celery)
- ✅ High-performance caching (gzip-compressed pickle files)
- ✅ Data normalization and enrichment (Polars-based)
- ✅ Technical indicator calculation
- ✅ Cross-validation between providers
- ✅ Anomaly detection
- ✅ **100% FREE** - No API costs

---

## 📊 DATA PIPELINE ARCHITECTURE

### 1. Data Ingestion Layer

**File:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/data/data_fetcher/`

#### JobManager (`manager.py`)
```python
# Orchestrates all scheduled data collection
class JobManager:
    async def run_daily_jobs()      # 6 PM EST - market close
    async def run_weekly_jobs()     # Sunday
    async def run_quarterly_jobs()  # Earnings season
    async def run_initial_setup()   # One-time asset setup
    async def run_historical_backfill()
```

**Current Implementation:** Alpha Vantage integration (extensible to other providers)

---

### 2. Data Provider Layer

**Directory:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/data/data_providers/`

#### Providers Available (24 total):

**Stock Market Data:**
- `yahooFinance/` - Unlimited free stock data (yfinance)
- `alphaVantage/` - 25 calls/day free tier
- `finnHub/` - Real-time stock data
- `polygon_io/` - Stock market data
- `iex_cloud/` - Stock data
- `fmp/` - Financial Modeling Prep

**Cryptocurrency:**
- `binance/` - Real-time crypto prices
- `coingecko/` - 30 calls/min (250K/month free)
- `coinmarketcap/` - Crypto market data
- `defi_llama/` - DeFi protocols

**Economic Data:**
- `fred/` - Federal Reserve Economic Data

**News & Sentiment:**
- `newsapi/` - 150K+ news sources
- `rss_news/` - RSS feed scraper
- `reddit/` - Reddit sentiment
- `stocktwits/` - Social sentiment

**Regulatory Filings:**
- `sec_edgar/` - SEC filings scraper ⭐

**Exchange Rates:**
- `exchangeRate.Host/`

#### Key Provider: SEC EDGAR Scraper

**File:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/data/data_providers/sec_edgar/scraper.py`

**Features:**
```python
class SECEDGARScraper:
    def get_company_filings(ticker, filing_type="10-K")
    def get_cik(ticker)  # Maps ticker to CIK
    def get_filing_document(url)  # Downloads full filing
    def get_company_info(ticker)  # Company metadata
    def search_company_filings(ticker, forms, start_date, end_date)
    def get_insider_transactions(ticker)  # Form 4
    def get_annual_reports(ticker)  # 10-K
    def get_quarterly_reports(ticker)  # 10-Q
    def get_current_reports(ticker)  # 8-K
    def get_proxy_statements(ticker)  # DEF 14A
    def get_filings_summary(ticker)
```

**Supported Tickers:** 45+ pre-mapped (AAPL, MSFT, GOOGL, AMZN, TSLA, etc.)

**Example Usage:**
```python
scraper = SECEDGARScraper()
filings = scraper.get_annual_reports("AAPL", count=5)
# Returns list of 10-K filings with URLs, dates, accession numbers
```

---

### 3. Data Processing Layer

**File:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/data/processing/pipeline.py`
**Lines:** 615
**Technology:** Polars (high-performance DataFrame library)

#### Core Classes:

**DataProcessor** (Base)
```python
class DataProcessor:
    def normalize_symbol(symbol) -> str
    def validate_price_data(price) -> bool
    def validate_volume(volume) -> bool
    def validate_timestamp(timestamp) -> bool
    def calculate_change_percent(current, previous) -> float
    def detect_anomalies(prices) -> List[int]  # Z-score method
```

**PriceDataProcessor**
```python
class PriceDataProcessor(DataProcessor):
    def normalize_price_data(raw_data, source) -> Dict
    def process_historical_data(raw_data, source) -> List[Dict]
    def enrich_price_data(price_data) -> Dict
```

**Supported Sources:**
- Yahoo Finance
- Alpha Vantage
- Binance
- CoinGecko
- CoinMarketCap

**TechnicalIndicatorsCalculator** ⭐
```python
class TechnicalIndicatorsCalculator:
    def calculate_all_indicators(price_data) -> Dict
    # Calculates:
    # - Moving Averages (5, 10, 20, 50, 100, 200)
    # - Exponential Moving Averages (12, 26, 50, 200)
    # - RSI (14-period)
    # - MACD (12, 26, 9)
    # - Bollinger Bands (20, 2 std)
    # - Average True Range (ATR)
    # - Volume MA (20, 50)
    # - Support/Resistance levels
```

**DataPipeline** (Orchestrator)
```python
class DataPipeline:
    def process_raw_data(raw_data, source, asset_type) -> ProcessedAssetData
    def process_with_indicators(historical_data, source) -> Dict
    def save_to_database(processed_data) -> bool
```

#### Data Flow:
```
Raw Data → Normalize → Validate → Enrich → Calculate Indicators → Save to DB
```

---

### 4. Pickle Cache Layer ⭐

**File:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/utils/pickle_cache.py`
**Lines:** 404
**Purpose:** High-performance batch storage for analytics/ML workloads

#### Features:
- ✅ **Compressed pickle files** (gzip)
- ✅ **Hourly snapshots**
- ✅ **Fast lookup** by symbol, category, sentiment
- ✅ **30-day TTL** with automatic cleanup
- ✅ **Integrity checksums**
- ✅ **Symbol indexing**
- ✅ **Batch writer** for efficient updates

#### Key Classes:

**NewsPickleCache**
```python
class NewsPickleCache:
    def save_articles(articles, timestamp) -> str  # Saves to .pkl.gz
    def load_articles(filepath) -> List[Dict]
    def load_latest_by_symbol(symbol, limit) -> List[Dict]
    def load_latest_by_sentiment(sentiment, limit) -> List[Dict]
    def load_latest_by_category(category, limit) -> List[Dict]
    def get_cache_stats() -> Dict  # file_count, total_articles, cache_size_mb
    def cleanup_expired() -> int  # Removes files older than TTL
    def create_backup(name) -> str
    def export_to_json(filepath) -> str  # For debugging
    def get_symbol_index() -> Dict[str, List[str]]  # Symbol -> URLs
```

**Cache Location:**
```
/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/media/news_cache/
├── news_cache_20260130_120000.pkl.gz
├── news_cache_20260130_130000.pkl.gz
└── backups/
    ├── backup_20260130.pkl.gz
    └── ...
```

**Cache Header Metadata:**
```python
@dataclass
class NewsCacheHeader:
    timestamp: str
    article_count: int
    categories: Dict[str, int]  # category -> count
    sources: List[str]
    symbols: List[str]  # Top 20 mentioned
    sentiment_distribution: Dict[str, int]  # pos/neg/neutral -> count
    file_size_bytes: int
    checksum: str  # MD5
```

**Batch Writer:**
```python
class NewsCacheBatchWriter:
    def __init__(cache, batch_size=1000)
    def add_article(article)
    def add_articles(articles)
    def flush()  # Writes buffered articles
    # Context manager support
```

**Usage in Tasks:**
```python
from utils.pickle_cache import get_pickle_cache

# Save to pickle
cache = get_pickle_cache()
cache.save_articles(articles)

# Load by symbol
btc_articles = cache.load_latest_by_symbol("BTC", limit=100)

# Get stats
stats = cache.get_cache_stats()
# Returns: {file_count: 5, total_articles: 5000, cache_size_mb: 125.5}
```

---

### 5. Background Jobs Layer

**File:** `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/tasks/`

#### Task Files:

**celery_tasks.py** (633 lines)
- Yahoo Finance, Alpha Vantage stock fetchers
- Binance, CoinGecko, CoinMarketCap crypto fetchers
- All markets fetch task
- Technical indicator calculations
- Data cleanup tasks
- Health checks
- Configured with `beat_schedule`

**crypto_data_tasks.py** (454 lines)
- UnifiedCryptoProvider integration
- Cross-validation between providers
- Anomaly detection
- Provider health monitoring
- Batch fetching top 50 cryptos
- Trending cryptos fetch

**scheduler_tasks.py** (368 lines)
- Dramatiq-based scheduler
- Crypto/stock price fetches
- Historical data tasks
- News fetching
- Technical indicators
- Cache warming
- Health checks
- Batch updates for popular assets

**news_tasks.py**
```python
@shared_task
def fetch_newsapi_news(category="business", limit=100)
# Normalizes news, extracts symbols, analyzes sentiment
# Saves to database AND pickle cache
```

#### Current Schedule:
```
Every 2 minutes:  Fetch 30 crypto prices
Every 5 minutes:  Fetch 10 stock prices
Every 10 minutes: Data validation
Every 15 minutes: Trending cryptos
Every 30 minutes: Market rankings
Daily:            Clean old data (365-day retention)
```

---

## 🌐 WEB CRAWLER IMPLEMENTATION

### 1. SEC EDGAR Crawler ⭐

**File:** `sec_edgar/scraper.py` (344 lines)

**Crawler Type:** API-based scraper (not traditional web scraping)

**Key Features:**
- Fetches company filings (10-K, 10-Q, 8-K, 4, DEF 14A, S-1, etc.)
- Downloads full filing documents
- CIK mapping for 45+ tickers
- Rate limiting built-in
- Search by date range, filing type
- Insider transaction tracking

**Supported Filings:**
- **10-K** - Annual reports
- **10-Q** - Quarterly reports
- **8-K** - Current reports (material events)
- **4** - Insider transactions
- **DEF 14A** - Proxy statements
- **S-1, S-3, S-8** - Registration statements

**Usage Example:**
```python
from data.data_providers.sec_edgar.scraper import SECEDGARScraper

scraper = SECEDGARScraper()

# Get annual reports
reports = scraper.get_annual_reports("AAPL", count=5)

# Get insider transactions
insider = scraper.get_insider_transactions("TSLA", count=50)

# Get recent 8-K filings
recent_8k = scraper.get_8k_filings("NVDA", count=20)

# Download full filing
filing_url = reports[0]['url']
document = scraper.get_filing_document(filing_url)
```

### 2. NewsAPI Scraper

**File:** `newsapi/scraper.py`

**Features:**
- 150,000+ news sources
- Search by keyword, category, source, domain
- Async HTTP requests (aiohttp)
- Key rotation support (via BaseAPIFetcher)
- orjson for fast JSON parsing

**Usage:**
```python
from data.data_providers.newsapi.scraper import NewsAPIScraper

scraper = NewsAPIScraper()
async with scraper:
    news = await scraper.get_headlines_by_category(
        category="business",
        page=1,
        page_size=100
    )
```

### 3. RSS News Scraper

**File:** `rss_news/`

**Purpose:** Scrape RSS feeds from financial news sites

---

## 💾 GET-SET DATA PATTERN

### Pattern Implementation:

**1. GET** - Fetch from external sources
```python
# Provider scrapes data
scraper = SECEDGARScraper()
filings = scraper.get_annual_reports("AAPL")
```

**2. SET** - Store in multiple formats
```python
# A. Database (PostgreSQL)
AssetPricesHistoric.objects.create(...)

# B. Pickle Cache (for ML/analytics)
cache = get_pickle_cache()
cache.save_articles(articles)  # .pkl.gz
```

**3. EXPORT** - External file export
```python
# Option 1: Pickle export (default)
cache.save_articles(articles)  # Creates .pkl.gz

# Option 2: JSON export (for debugging/portability)
cache.export_to_json(filepath)  # Creates .json

# Option 3: Named backup
cache.create_backup(name="before_maintenance")
```

### Data Flow:
```
External Source → Normalize → Validate
                           ↓
                    ┌────────┴────────┐
                    ↓                 ↓
              PostgreSQL      Pickle Cache (.pkl.gz)
              (Real-time)      (Analytics/ML)
                    ↓                 ↓
              Django ORM      Fast load by symbol/
              Queries         sentiment/category
```

---

## 📁 KEY FILE LOCATIONS

### Data Pipeline:
```
/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/data/
├── processing/
│   └── pipeline.py              # 615 lines - Main pipeline
├── data_fetcher/
│   ├── manager.py               # 116 lines - Job orchestrator
│   └── base.py                  # 73 lines - Base job class
└── data_providers/
    ├── sec_edgar/
    │   └── scraper.py           # 344 lines - SEC crawler
    ├── newsapi/
    │   └── scraper.py           # News scraper
    ├── yahooFinance/
    ├── binance/
    ├── coingecko/
    └── ... (21 more providers)
```

### Pickle Cache:
```
/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/utils/
└── pickle_cache.py              # 404 lines - Cache implementation

Cache files location:
/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/media/news_cache/
├── news_cache_YYYYMMDD_HHMMSS.pkl.gz
└── backups/
```

### Background Tasks:
```
/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/tasks/
├── celery_tasks.py              # 633 lines
├── crypto_data_tasks.py         # 454 lines
├── scheduler_tasks.py           # 368 lines
└── news_tasks.py                # News ingestion
```

### Documentation:
```
/Users/sergi/Desktop/Projects/FinanceHub/Backend/
├── BACKGROUND_JOBS_README.md    # 265 lines
├── QUICKSTART.md                # 244 lines
└── start_background_jobs.py     # Main entry point
```

---

## 🚀 CURRENT STATUS

### Running Services:
✅ **Background jobs active** (since 2026-01-30 03:51:55)
✅ **Collecting data from:**
   - 42 stocks (S&P 500 leaders)
   - 23 cryptos (top market cap)
   - News from multiple sources
   - SEC filings

### Data Volume:
- **~24,545 records/day**
- **~736K records/month**
- **365-day retention**
- **Automatic cleanup**

### Monitoring:
```bash
# Check status
cd Backend
./manage_jobs.sh status

# Live monitoring
./manage_jobs.sh monitor

# View logs
./manage_jobs.sh logs
```

---

## 🔧 CONFIGURATION

### Add More Assets:

Edit `Backend/start_background_jobs.py`:
```python
# Line ~72: Add stocks
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL",
    "YOUR_STOCK_1", "YOUR_STOCK_2",
]

# Line ~84: Add cryptos
POPULAR_CRYPTOS = [
    "BTC", "ETH", "BNB",
    "YOUR_CRYPTO_1", "YOUR_CRYPTO_2",
]
```

### Change Update Frequency:

Edit `Backend/start_background_jobs.py`:
```python
# Line ~180: Change from 2 min to 5 min
fetch_crypto_batch.send_with_options(
    delay=1000 * 60 * 5,  # Adjust frequency
    repeat=True
)
```

### Adjust Rate Limits:

Edit `Backend/src/utils/services/call_planner.py`:
```python
'coingecko': {
    'calls_per_window': 30,  # Adjust
    'batch_delay_seconds': 2,  # Adjust
}
```

---

## 📊 DATA SCHEMA

### ProcessedAssetData:
```python
@dataclass
class ProcessedAssetData:
    symbol: str
    source: str
    raw_data: Dict[str, Any]
    normalized_data: Optional[Dict]
    enriched_data: Optional[Dict]
    technical_indicators: Optional[Dict]
    validation_errors: List[str]
    is_valid: bool
    processed_at: datetime
```

### NewsCacheHeader:
```python
@dataclass
class NewsCacheHeader:
    timestamp: str
    article_count: int
    categories: Dict[str, int]
    sources: List[str]
    symbols: List[str]
    sentiment_distribution: Dict[str, int]
    file_size_bytes: int
    checksum: str
```

---

## 🎓 KEY INSIGHTS

### 1. No Traditional Web Scraping Framework
- ❌ No Scrapy implementation found
- ✅ Instead: API-based scrapers (cleaner, faster)
- ✅ SEC EDGAR uses official API
- ✅ NewsAPI uses official API

### 2. Pickle Strategy
- **Purpose:** Fast batch loading for ML/analytics
- **Not for:** Real-time queries (use PostgreSQL)
- **Compression:** gzip (reduces size by ~80%)
- **TTL:** 30 days auto-cleanup
- **Format:** `.pkl.gz` files with metadata header

### 3. Provider Architecture
- **Base Pattern:** All providers extend BaseAPIFetcher
- **Key Rotation:** Automatic API key management
- **Rate Limiting:** Built-in via call_planner
- **Error Handling:** Retry logic, health checks
- **Normalization:** Common data format via pipeline.py

### 4. Task Orchestration
- **Dual Queue:** Celery (long-running) + Dramatiq (real-time)
- **Scheduling:** Django Celery Beat + Dramatiq repeat
- **Priority:** Health checks > Price updates > Historical
- **Monitoring:** Comprehensive logging + stats

---

## 🔮 FUTURE ENHANCEMENTS

### Potential Additions:
1. **Scrapy Integration** - For sites without APIs
2. **More Pickle Caches** - Price data, technical indicators
3. **Parquet Export** - For data science workflows
4. **Real-time Streaming** - WebSocket data ingestion
5. **ML Pipeline** - Train models on pickled data
6. **Sentiment Analysis** - NLP on news/Reddit/StockTwits
7. **Correlation Matrix** - Asset correlation from historical data
8. **Backtesting Engine** - Use historical data for strategy testing

---

## 📞 QUICK COMMANDS

### Start Data Collection:
```bash
cd Backend
./manage_jobs.sh start
```

### Check Redis:
```bash
redis-cli ping  # Should return PONG
redis-cli KEYS dramatiq:*
```

### Query Database:
```sql
-- Total records
SELECT COUNT(*) FROM assets_assetpriceshistoric;

-- Latest prices
SELECT symbol, MAX(timestamp) as latest
FROM assets_assetpriceshistoric
GROUP BY symbol
ORDER BY latest DESC;

-- Records in last hour
SELECT COUNT(*) FROM assets_assetpriceshistoric
WHERE timestamp >= NOW() - INTERVAL '1 hour';
```

### Load Pickle Cache:
```python
from utils.pickle_cache import get_pickle_cache

cache = get_pickle_cache()

# Load latest
articles = cache.load_articles()

# Load by symbol
btc_news = cache.load_latest_by_symbol("BTC", limit=100)

# Get stats
stats = cache.get_cache_stats()
print(f"Files: {stats['file_count']}")
print(f"Articles: {stats['total_articles']}")
print(f"Size: {stats['cache_size_mb']} MB")
```

---

## ✅ COMPLETION CHECKLIST

- [x] Data processing pipeline explored
- [x] Pickle cache implementation understood
- [x] Web crawler implementation found
- [x] Background tasks architecture documented
- [x] Provider system understood
- [x] Get-set data pattern confirmed
- [x] File locations documented
- [x] Configuration options identified
- [x] Current status verified

---

**Session Summary:**
FinanceHub has a **sophisticated, production-ready data pipeline** that:
1. Scrapes data from 24+ providers (API-based, not traditional web scraping)
2. Processes and normalizes data using Polars
3. Calculates technical indicators
4. Stores in PostgreSQL for real-time queries
5. Exports to gzip-compressed pickle files for ML/analytics
6. Runs on automated schedule (Celery + Dramatiq)
7. Cross-validates data between providers
8. Detects anomalies and handles errors gracefully

**Status:** ✅ **Fully operational and documented**

**Next Steps:**
- Monitor data collection
- Add more assets as needed
- Build ML models on pickled data
- Create dashboards using real-time PostgreSQL data

---

**End of Documentation**
Generated: 2026-01-30
Total Lines of Code Analyzed: ~2,500+
Files Read: 15+
Documentation Pages: 3
