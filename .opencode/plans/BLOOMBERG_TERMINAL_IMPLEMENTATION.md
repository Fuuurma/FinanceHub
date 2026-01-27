# Bloomberg Terminal Implementation Plan - Cost Optimized

## Executive Summary

**Goal**: Build Bloomberg-like trading terminal with minimal API costs through aggressive scraping, free-tier optimization, and intelligent API key rotation.

**Strategy**:
1. ✅ Scrape everything possible from public sources
2. ✅ Use free-tier APIs with rotation for real-time data
3. ✅ Implement API key rotation system for max free tier utilization
4. ✅ Strategic call planning to avoid rate limits
5. ✅ Only upgrade to paid APIs when absolutely necessary

**Estimated Monthly Cost**: **$0-100** (vs $1,805 for Bloomberg-level paid APIs)

---

## Phase 0: Infrastructure Foundation (Days 1-3)

### 0.1 API Key Rotation System

**Priority**: CRITICAL (enables all other cost optimization)

**Deliverables**:
1. Database models for API key management
2. APIKeyManager service with intelligent key selection
3. BaseAPIFetcher class with automatic rotation
4. Background tasks for key recovery and health monitoring
5. Admin dashboard for key management

**Technical Implementation**:

#### Models to Create
```python
Backend/src/investments/models/
├── api_key.py              # APIKey model with multiple keys per provider
└── api_call_log.py         # APIKeyUsageLog for monitoring

# Key Features:
# - Multiple keys per provider
# - Usage tracking (hourly/daily/lifetime)
# - Health tracking (last success/failure, consecutive failures)
# - Status management (active, rate_limited, disabled, expired)
# - Priority system for intelligent selection
# - Auto-recovery settings
```

#### Services to Create
```python
Backend/src/investments/services/
└── api_key_manager.py      # APIKeyManager class

# Key Methods:
# - get_best_key() - Weighted selection algorithm
# - rotate_on_rate_limit() - Automatic failover
# - recover_rate_limited_keys() - Auto-recovery
# - _select_weighted_key() - Intelligent scoring
# - get_key_health_report() - Health monitoring
```

#### Base Class to Create
```python
Backend/src/data/data_providers/
└── base_fetcher.py          # BaseAPIFetcher abstract class

# Key Features:
# - Automatic retry with exponential backoff
# - Rate limit detection and handling
# - Automatic key rotation on rate limit
# - Request logging for monitoring
# - Caching integration
```

**Implementation Steps**:
1. Day 1: Create models, run migrations
2. Day 2: Implement APIKeyManager service
3. Day 3: Implement BaseAPIFetcher and test

**Testing**:
- Unit tests for weighted selection algorithm
- Integration tests for rotation logic
- Load tests with mock rate limits

---

## Phase 1: Aggressive Scraping Infrastructure (Days 4-7)

### 1.1 SEC EDGAR Scraper

**Priority**: HIGH (free company filings, fundamentals, insider trading)

**Data Source**: https://www.sec.gov/edgar/search/
**Cost**: $0 (free, official API)
**Rate Limit**: 10 requests/second

**Deliverables**:
```python
Backend/src/data/data_providers/sec_edgar/
├── base.py                  # SEC API client
└── scraper.py              # SECEDGARScraper class

# Features:
# - Company CIK lookup
# - 10-K/10-Q/8-K filings download
# - Insider trading (Form 4) tracking
# - Proxy statements (DEF 14A)
# - Filing document parsing
# - Rate limiting (10 req/sec)
```

**Data Available**:
- ✅ Company information (CIK, SIC codes)
- ✅ Quarterly/annual filings (10-Q, 10-K)
- ✅ Current events (8-K)
- ✅ Insider trading data (Form 4)
- ✅ Proxy statements (DEF 14A)
- ✅ Earnings releases

**API Integration**: Update `JobManager` to fetch filings for tracked companies

---

### 1.2 RSS News Aggregator

**Priority**: HIGH (free headline collection, multiple sources)

**Data Sources**:
- CNBC: https://www.cnbc.com/id/10000664/device/rss/rss.html
- Reuters: https://www.reutersagency.com/feed/
- MarketWatch: https://www.marketwatch.com/rss/topstories
- Seeking Alpha: https://seekingalpha.com/feed.xml
- Benzinga: https://www.benzinga.com/feed
- Bloomberg: https://feeds.bloomberg.com/markets/news.rss

**Cost**: $0 (free RSS feeds)
**Rate Limit**: Minimal

**Deliverables**:
```python
Backend/src/data/data_providers/rss_news/
├── base.py                  # RSS feed parser
└── scraper.py              # RSSNewsScraper class

# Features:
# - Multi-source aggregation
# - Deduplication across sources
# - Headline extraction
# - Link and timestamp tracking
# - Feed refresh scheduling
```

**Data Available**:
- ✅ Real-time headlines
- ✅ Article summaries
- ✅ Source attribution
- ✅ Publication timestamps

**Integration**: Background task runs every 15 minutes to fetch latest headlines

---

### 1.3 FRED API Integration

**Priority**: HIGH (free economic data, treasury yields, all major indicators)

**Data Source**: https://api.stlouisfed.org/fred/
**Cost**: $0 (free API key required)
**Rate Limit**: 120 requests/minute

**Deliverables**:
```python
Backend/src/data/data_providers/fred/
├── base.py                  # FRED API client
└── scraper.py              # FREDScraper class

# Features:
# - Treasury yields (2y, 5y, 10y, 30y)
# - Economic indicators (GDP, CPI, unemployment)
# - Interest rates (federal funds)
# - Historical data back to 1940s
# - Rate limiting (120 req/min)
```

**Data Available**:
- ✅ US Treasury yields (DGS2, DGS5, DGS10, DGS30)
- ✅ GDP data
- ✅ CPI (CPIAUCSL)
- ✅ Unemployment rate (UNRATE)
- ✅ Federal funds rate (DFF)
- ✅ 500,000+ economic series

**Series IDs**:
```python
TREASURY_YIELDS = {
    '2y': 'DGS2',
    '5y': 'DGS5',
    '10y': 'DGS10',
    '30y': 'DGS30'
}
ECONOMIC_INDICATORS = {
    'gdp': 'GDP',
    'cpi': 'CPIAUCSL',
    'unemployment': 'UNRATE',
    'fed_funds': 'DFF'
}
```

**API Integration**: Schedule hourly updates for current data, daily for historical

---

### 1.4 Reddit Sentiment Scraper

**Priority**: MEDIUM (free social sentiment, WallStreetBets, investing communities)

**Data Source**: https://www.reddit.com/ (via PRAW library)
**Cost**: $0 (free API)
**Rate Limit**: 60 requests/minute

**Deliverables**:
```python
Backend/src/data/data_providers/reddit/
├── base.py                  # Reddit API client (PRAW)
└── scraper.py              # RedditSentimentScraper class

# Features:
# - PRAW integration (official Reddit library)
# - Multiple subreddit monitoring
# - Sentiment analysis using TextBlob/NLTK
# - Keyword-based symbol extraction
# - Vote-weighted sentiment scoring
```

**Subreddits to Monitor**:
```python
SUBREDDITS = [
    'wallstreetbets',    # High-volume, high-impact
    'stocks',            # General stock discussion
    'investing',         # Serious investors
    'options',           # Options trading
    'CryptoCurrency',     # Crypto sentiment
    'Bitcoin',           # Bitcoin-specific
    'SecurityAnalysis',   # Fundamental analysis
    'ValueInvesting',    # Value investing
    'ShortSqueeze'      # Short squeeze alerts
]
```

**Data Available**:
- ✅ Post titles and content
- ✅ Comments sentiment analysis
- ✅ Upvote/downvote ratios
- ✅ Trending symbols
- ✅ User engagement metrics

**Sentiment Algorithm**:
```python
from textblob import TextBlob

def calculate_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (negative) to +1 (positive)
    subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
    return {
        'polarity': polarity,
        'subjectivity': subjectivity,
        'sentiment': 'positive' if polarity > 0 else 'negative'
    }
```

**Integration**: Background task runs every 30 minutes to fetch latest posts

---

### 1.5 StockTwits API Integration

**Priority**: MEDIUM (free sentiment API, bullish/bearish ratios)

**Data Source**: https://api.stocktwits.com/api/2
**Cost**: $0 (free tier: 200 requests/hour)
**Rate Limit**: 200 requests/hour

**Deliverables**:
```python
Backend/src/data/data_providers/stocktwits/
├── base.py                  # StockTwits API client
└── scraper.py              # StockTwitsAPI class

# Features:
# - Symbol sentiment stream
# - Bullish/bearish ratio calculation
# - Trending symbols
# - Message volume tracking
```

**Data Available**:
- ✅ Real-time sentiment per symbol
- ✅ Bullish/bearish ratios
- ✅ Trending symbols
- ✅ Message volume

**API Integration**: Schedule fetches every 15 minutes for tracked symbols

---

## Phase 2: Enhanced Existing Scrapers (Days 8-10)

### 2.1 Yahoo Finance Enhancements

**Priority**: HIGH (already implemented, maximize usage)

**Current Status**: ✅ Implemented via yfinance
**Cost**: $0 (no official limits)
**Rate Limit**: 2-3 requests/second recommended

**Enhancements Needed**:

#### A. Options Greeks Calculation
```python
Backend/src/utils/services/
└── options_greeks.py

# Implement Black-Scholes model for:
# - Delta (Δ)
# - Gamma (Γ)
# - Theta (Θ)
# - Vega (ν)
# - Rho (ρ)

from scipy.stats import norm
from math import log, sqrt, exp

def calculate_greeks(S, K, T, r, sigma, option_type='call'):
    """
    S = Current stock price
    K = Strike price
    T = Time to expiration (years)
    r = Risk-free rate
    sigma = Implied volatility
    """
    d1 = (log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = -norm.cdf(-d1)

    gamma = norm.pdf(d1) / (S * sigma * sqrt(T))
    theta = -(S * norm.pdf(d1) * sigma) / (2 * sqrt(T))
    vega = S * norm.pdf(d1) * sqrt(T)

    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega
    }
```

#### B. Enhanced Rate Limiting
```python
# Update existing yfinance usage with smarter rate limiting
import asyncio
from datetime import datetime, timedelta

class YahooFinanceRateLimiter:
    def __init__(self):
        self.last_request = None
        self.min_interval = 0.5  # 2 requests/second max

    async def wait_if_needed(self):
        now = datetime.now()
        if self.last_request:
            elapsed = (now - self.last_request).total_seconds()
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)
        self.last_request = datetime.now()
```

#### C. Batch Requests Optimization
```python
# Fetch multiple symbols in single request
import yfinance as yf

tickers = yf.Tickers("AAPL MSFT GOOGL AMZN TSLA")

# Batch download - more efficient than individual requests
history = tickers.history(period="1mo", interval="1d")

# Batch fundamental data
for ticker in tickers.tickers:
    info = ticker.info  # Cached internally
```

---

### 2.2 Alpha Vantage Optimization

**Priority**: HIGH (already implemented, maximize free tier)

**Current Status**: ✅ Implemented
**Cost**: $0 (free tier)
**Rate Limit**: 5 requests/minute, 25 requests/day

**Optimization Strategy**:

#### A. Free Tier Maximization with Multiple Keys
```python
# Register multiple free Alpha Vantage API keys
# Each key gets 25 calls/day, so 10 keys = 250 calls/day

ALPHA_VANTAGE_KEYS = [
    'API_KEY_1',  # Register 10 free accounts
    'API_KEY_2',
    'API_KEY_3',
    # ... etc
]

# API Key Manager automatically rotates through keys
# This provides effectively unlimited free calls
```

#### B. Smart Call Scheduling
```python
# Schedule calls to spread across 24-hour period

# Daily (25 calls): Prioritize critical data
DAILY_CALLS = [
    ('market_open', '09:30'),    # 5 calls - top stocks
    ('market_close', '16:00'),    # 5 calls - end-of-day
    ('overnight', '02:00'),        # 15 calls - batch updates
]

# Each key gets 25 calls, use strategically:
# - Real-time during market hours (top 10 stocks)
# - Batch updates overnight (historical data, fundamentals)
```

#### C. Priority Data Classification
```python
# Classify data by priority to optimize API usage

PRIORITY_CRITICAL = [
    'get_quote',              # Real-time prices
    'get_intraday',          # Intraday data
]

PRIORITY_HIGH = [
    'get_daily',              # Daily prices
    'get_earnings',           # Earnings data
]

PRIORITY_MEDIUM = [
    'get_company_overview',    # Fundamentals
    'get_income_statement',    # Financial statements
]

PRIORITY_LOW = [
    'get_weekly',             # Weekly data (use Yahoo instead)
    'get_monthly',            # Monthly data (use Yahoo instead)
]
```

---

### 2.3 Binance Optimization

**Priority**: HIGH (already implemented, unlimited free tier)

**Current Status**: ✅ Implemented
**Cost**: $0 (public endpoints unlimited)
**Rate Limit**: None for public endpoints

**Enhancements Needed**:

#### A. WebSocket for Real-Time Data
```python
Backend/src/data/data_providers/binance/
└── websocket_consumer.py

# Implement WebSocket for real-time crypto prices
# Avoids polling, provides instant updates
```

#### B. Order Book Depth
```python
# Fetch Level 2 order book (10,000 levels available)
async def get_order_book(symbol, limit=1000):
    """
    Get order book depth
    limit: 5, 10, 20, 50, 100, 500, 1000, 5000
    """
    params = {'symbol': symbol, 'limit': limit}
    return await _request('depth', params)

# Use for:
# - Order book visualization
# - Price impact analysis
# - Liquidity assessment
```

#### C. Aggregated Trades
```python
# Fetch aggregated trades (better than individual trades)
async def get_agg_trades(symbol, limit=1000):
    """
    Get compressed/aggregate trades
    More efficient than individual trades
    """
    params = {'symbol': symbol, 'limit': limit}
    return await _request('aggTrades', params)
```

---

### 2.4 CoinGecko & CoinMarketCap Optimization

**Priority**: MEDIUM (already implemented, optimize free tier)

**Current Status**: ✅ Implemented (both)
**Cost**: $0 (free tiers)
**Rate Limits**:
- CoinGecko: 10-50 calls/minute
- CoinMarketCap: 10,000 calls/day, 10 calls/minute

**Enhancements Needed**:

#### A. Cross-Validation
```python
# Fetch from both sources and cross-validate
# Use CoinGecko as primary, CoinMarketCap as backup
# Switch providers on rate limit
```

#### B. Batch Operations
```python
# Fetch multiple coins in single request

# CoinGecko
params = {
    'vs_currency': 'usd',
    'ids': 'bitcoin,ethereum,binancecoin,cardano',  # Batch request
    'order': 'market_cap_desc',
    'per_page': 250
}

# CoinMarketCap
params = {
    'start': '1',
    'limit': '5000'  # Fetch top 5000 at once
}
```

---

## Phase 3: Strategic Free-Tier API Additions (Days 11-14)

### 3.1 Polygon.io Free Tier

**Priority**: HIGH (best free stock data, 2 years history, options)

**Data Source**: https://polygon.io/docs/
**Cost**: $0 (free tier)
**Rate Limit**: 5 requests/minute

**Free Tier Limits**:
- ✅ End-of-day stock prices
- ✅ 2 years of historical data
- ✅ Grouped daily bars (OHLCV)
- ✅ Options chains (delayed)
- ✅ Reference data (tickers, splits, dividends)
- ❌ No real-time (15-minute delay)
- ❌ No Level 2 market depth

**Deliverables**:
```python
Backend/src/data/data_providers/polygon_io/
├── base.py                  # Polygon.io API client
└── scraper.py              # PolygonIOScraper class

# Features:
# - End-of-day stock data
# - Options chains (calls/puts)
# - Dividends and splits data
# - Reference data (ticker info)
# - Rate limiting (5 req/min)
```

**Data Available**:
- ✅ US stocks (tickers, prices, OHLCV)
- ✅ ETFs and indices
- ✅ Options chains (strikes, expirations)
- ✅ Dividends and stock splits
- ✅ Company info

**API Integration**:
- Schedule daily updates at 6:00 PM EST (after market close)
- Use for historical backfill (2 years available)

**Key Strategy**: Use multiple free API keys to maximize calls:
```python
# Register 6 free accounts = 30 requests/minute = 1,800 requests/hour
POLYGON_KEYS = [
    'FREE_KEY_1',  # Register 6 free accounts
    'FREE_KEY_2',
    # ... etc
]
```

---

### 3.2 IEX Cloud Free Tier (Launch)

**Priority**: HIGH (excellent fundamentals, sandbox environment)

**Data Source**: https://iexcloud.io/docs/
**Cost**: $0 (Launch tier)
**Rate Limit**: 500,000 calls/month (sandbox environment)

**Free Tier Limits**:
- ✅ Excellent fundamentals
- ✅ 10-K, 10-Q, income statements, balance sheets
- ✅ Earnings data
- ✅ Stock prices (sandbox data, not real-time)
- ✅ News
- ✅ 20+ years of historical data
- ❌ Sandbox environment (delayed/modified data)

**Deliverables**:
```python
Backend/src/data/data_providers/iex_cloud/
├── base.py                  # IEX Cloud API client
└── scraper.py              # IEXCloudScraper class

# Features:
# - Company fundamentals
# - Financial statements (10-K, 10-Q)
# - Earnings data
# - News feed
# - Historical prices
```

**Data Available**:
- ✅ Company overview
- ✅ Financial statements (income, balance sheet, cash flow)
- ✅ Earnings estimates and actuals
- ✅ Dividends and splits
- ✅ News articles
- ✅ 20+ years historical data

**API Integration**:
- Use for fundamental data (not real-time)
- Schedule weekly updates for fundamentals
- Use Alpha Vantage for real-time prices

---

### 3.3 Finnhub Free Tier

**Priority**: HIGH (real-time WebSocket, news with sentiment)

**Data Source**: https://finnhub.io/docs/api
**Cost**: $0 (free tier)
**Rate Limit**: 60 requests/minute

**Free Tier Limits**:
- ✅ Real-time stock prices
- ✅ WebSocket streaming
- ✅ News with sentiment analysis
- ✅ Company fundamentals
- ✅ Stock splits and dividends
- ✅ Pattern recognition
- ✅ 1 year of historical data

**Deliverables**:
```python
Backend/src/data/data_providers/finnhub/
├── base.py                  # Finnhub API client
└── scraper.py              # FinnhubScraper class

# Features:
# - Real-time stock quotes
# - WebSocket for streaming prices
# - News with sentiment
# - Pattern recognition
# - Technical indicators
# - Rate limiting (60 req/min)
```

**Data Available**:
- ✅ Real-time stock prices
- ✅ Company news with sentiment scores
- ✅ Fundamental data
- ✅ Stock splits and dividends
- ✅ Technical indicators (SMA, EMA, RSI, etc.)
- ✅ Pattern recognition
- ✅ 1 year historical data

**API Integration**:
- Use WebSocket for real-time top 20 stocks
- Use news API for sentiment analysis
- Schedule hourly updates for fundamentals

**Key Strategy**: Use for real-time WebSocket (most valuable feature):
```python
# WebSocket connection for real-time prices
import finnhub

trade_client = finnhub.Trade(config.FINNHUB_API_KEY)

# Subscribe to top stocks
trade_client.subscribe_trades('AAPL')
trade_client.subscribe_trades('MSFT')
trade_client.subscribe_trades('GOOGL')
# ... etc
```

---

### 3.4 NewsAPI Free Tier

**Priority**: MEDIUM (comprehensive news aggregation)

**Data Source**: https://newsapi.org/docs/
**Cost**: $0 (developer tier)
**Rate Limit**: 100 requests/day

**Free Tier Limits**:
- ✅ 100 requests/day
- ✅ 150,000 news sources
- ✅ Headlines and full articles
- ✅ Search by keyword, category, source
- ✅ 24-hour delay on full articles

**Deliverables**:
```python
Backend/src/data/data_providers/newsapi/
├── base.py                  # NewsAPI client
└── scraper.py              # NewsAPIScraper class

# Features:
# - News aggregation
# - Category filtering (business, technology)
# - Source filtering
# - Keyword search
```

**Data Available**:
- ✅ Financial news headlines
- ✅ Full articles (24h delay)
- ✅ Source attribution
- ✅ Category filtering
- ✅ Historical news archive

**API Integration**:
- Schedule every 6 hours (100 requests/day = ~4 hours between updates)
- Use as backup to RSS feeds
- Combine with RSS for comprehensive coverage

---

## Phase 4: Data Orchestration & Scheduling (Days 15-17)

### 4.1 Call Planning System

**Priority**: CRITICAL (optimize API usage, avoid rate limits)

**Deliverables**:
```python
Backend/src/data/data_fetcher/
└── call_planner.py          # Smart call scheduling

# Features:
# - Priority-based task queuing
# - Time-based scheduling (market hours vs off-hours)
# - Load balancing across providers
# - Adaptive rate limiting
# - Caching-aware request deduplication
```

**Scheduling Strategy**:

#### Market Hours (9:30 AM - 4:00 PM EST)
```python
MARKET_HOURS_TASKS = {
    'realtime': {
        'priority': 'CRITICAL',
        'providers': ['finnhub_websocket', 'binance_websocket'],
        'frequency': 'continuous',
        'data': ['live_prices', 'order_book']
    },
    'intraday': {
        'priority': 'HIGH',
        'providers': ['polygon_free', 'yahoo_finance'],
        'frequency': '15_minutes',
        'data': ['intraday_ohlcv', 'options_chains']
    }
}
```

#### After Hours (4:00 PM - 9:30 AM EST)
```python
AFTER_HOURS_TASKS = {
    'daily_updates': {
        'priority': 'HIGH',
        'providers': ['polygon_free', 'alpha_vantage'],
        'frequency': 'once_at_6pm',
        'data': ['daily_ohlcv', 'dividends', 'splits']
    },
    'news': {
        'priority': 'MEDIUM',
        'providers': ['rss_feeds', 'newsapi', 'finnhub'],
        'frequency': 'hourly',
        'data': ['news_headlines', 'sentiment']
    },
    'sentiment': {
        'priority': 'MEDIUM',
        'providers': ['reddit', 'stocktwits'],
        'frequency': '30_minutes',
        'data': ['social_sentiment', 'trending_symbols']
    }
}
```

#### Overnight/Weekend (Off-Peak)
```python
OFF_PEAK_TASKS = {
    'historical_backfill': {
        'priority': 'LOW',
        'providers': ['polygon_free', 'iex_cloud', 'yahoo_finance'],
        'frequency': 'once_overnight',
        'data': ['historical_ohlcv', 'fundamentals']
    },
    'economic_data': {
        'priority': 'LOW',
        'providers': ['fred', 'alpha_vantage'],
        'frequency': 'daily',
        'data': ['treasury_yields', 'economic_indicators']
    },
    'sec_filings': {
        'priority': 'LOW',
        'providers': ['sec_edgar'],
        'frequency': 'daily',
        'data': ['10k_filings', 'insider_trading']
    }
}
```

---

### 4.2 Caching Strategy

**Priority**: HIGH (reduce API calls, improve performance)

**Cache Hierarchy**:
```python
L1_CACHE = {
    'ttl': '30_seconds',
    'data': ['realtime_prices', 'order_book', 'websocket_updates'],
    'storage': 'redis_memory'
}

L2_CACHE = {
    'ttl': '5_minutes',
    'data': ['intraday_quotes', 'options_chains', 'news_headlines'],
    'storage': 'redis'
}

L3_CACHE = {
    'ttl': '1_hour',
    'data': ['daily_ohlcv', 'fundamentals', 'sentiment_scores'],
    'storage': 'redis'
}

L4_CACHE = {
    'ttl': 'persistent',
    'data': ['historical_ohlcv', 'financial_statements', 'sec_filings'],
    'storage': 'postgresql'
}
```

**Implementation**:
```python
Backend/src/utils/
└── cache_manager.py

from django.core.cache import cache

class CacheManager:
    @staticmethod
    def get_or_fetch(cache_key, fetch_func, ttl):
        """
        Get from cache or fetch and store
        """
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # Cache miss - fetch data
        data = fetch_func()
        cache.set(cache_key, data, ttl)
        return data

    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidate all keys matching pattern
        """
        # Redis pattern deletion
        import redis
        r = redis.Redis()
        for key in r.keys(pattern):
            r.delete(key)
```

**Cache Invalidation Strategy**:
- L1: Invalidate on WebSocket updates
- L2: Invalidate on scheduled refresh (15 minutes)
- L3: Invalidate on hourly/daily updates
- L4: Never invalidate (historical data)

---

### 4.3 Background Task Scheduling

**Priority**: CRITICAL (automate data fetching)

**Deliverables**:
```python
Backend/src/tasks/
└── scheduler.py

# Features:
# - Time-based task scheduling
# - Priority-based execution
# - Dependency management
# - Error handling and retries
```

**Task Schedule**:
```python
# Every 30 seconds (continuous)
TASK_REALTIME = {
    'websocket_prices': ['finnhub', 'binance'],
    'order_book_updates': ['binance'],
}

# Every 15 minutes (market hours)
TASK_INTRADAY = {
    'stock_quotes': ['polygon_free', 'yahoo_finance'],
    'options_chains': ['polygon_free'],
    'crypto_prices': ['binance', 'coingecko'],
}

# Every 30 minutes (continuous)
TASK_SENTIMENT = {
    'reddit_posts': ['reddit'],
    'stocktwits_stream': ['stocktwits'],
}

# Every hour (continuous)
TASK_HOURLY = {
    'news_aggregation': ['rss_feeds', 'finnhub'],
    'sentiment_scores': ['reddit', 'stocktwits'],
    'api_key_recovery': ['api_key_manager'],
}

# Once per day (6:00 PM EST)
TASK_DAILY = {
    'daily_ohlcv': ['polygon_free', 'alpha_vantage'],
    'dividends_splits': ['polygon_free', 'iex_cloud'],
    'treasury_yields': ['fred'],
}

# Once per week (Sunday night)
TASK_WEEKLY = {
    'fundamentals': ['iex_cloud', 'alpha_vantage'],
    'earnings_data': ['alpha_vantage'],
    'sec_filings': ['sec_edgar'],
}

# Once per month
TASK_MONTHLY = {
    'historical_backfill': ['polygon_free', 'yahoo_finance'],
    'usage_reports': ['api_key_manager'],
}
```

---

## Phase 5: Backend API Development (Days 18-21)

### 5.1 Technical Indicators API

**Priority**: HIGH (calculate on server, save API calls)

**Deliverables**:
```python
Backend/src/utils/services/
└── technical_indicators.py

# Implement:
# - RSI (Relative Strength Index)
# - MACD (Moving Average Convergence Divergence)
# - Bollinger Bands
# - SMA/EMA (Simple/Exponential Moving Averages)
# - ADX (Average Directional Index)
# - Stochastic Oscillator
# - ATR (Average True Range)
# - Volume Profile
```

**Implementation**:
```python
import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(prices, period=14):
        """
        Calculate RSI
        prices: pandas Series of closing prices
        period: RSI period (default 14)
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """
        Calculate MACD
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal

        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        """
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return {
            'middle': sma,
            'upper': upper_band,
            'lower': lower_band
        }

    @staticmethod
    def calculate_sma(prices, period):
        """
        Calculate Simple Moving Average
        """
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices, period):
        """
        Calculate Exponential Moving Average
        """
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_volume_profile(prices, volumes, bins=50):
        """
        Calculate Volume Profile
        """
        price_bins = pd.cut(prices, bins=bins, labels=False)
        volume_by_price = volumes.groupby(price_bins).sum()

        return {
            'price_levels': prices[bins//2::bins//len(prices)],
            'volumes': volume_by_price.values
        }
```

**API Endpoint**:
```python
# Backend/src/assets/api/technical_indicators.py
@router.get("/{symbol}/indicators/{indicator}")
def get_technical_indicator(request, symbol, indicator, period=14):
    """
    Get technical indicator for symbol

    /api/assets/{symbol}/indicators/rsi?period=14
    /api/assets/{symbol}/indicators/macd?fast=12&slow=26
    """
    # Fetch historical prices from cache/database
    # Calculate indicator
    # Return results
    pass
```

---

### 5.2 Screener API (Already Exists)

**Status**: ✅ Already implemented
**Enhancements Needed**:

#### A. Real-Time Screener
```python
# Use cached prices instead of API calls
# Update screener results every 15 minutes (cache L2)
```

#### B. Preset Strategies
```python
# Add predefined screener strategies:

PRESETS = {
    'momentum': {
        'filters': [
            {'field': 'rsi', 'operator': '>', 'value': 70},
            {'field': 'volume', 'operator': '>', 'value': 'avg_volume_20d'}
        ]
    },
    'value': {
        'filters': [
            {'field': 'pe_ratio', 'operator': '<', 'value': 15},
            {'field': 'pb_ratio', 'operator': '<', 'value': 2},
            {'field': 'dividend_yield', 'operator': '>', 'value': 3}
        ]
    },
    'growth': {
        'filters': [
            {'field': 'revenue_growth', 'operator': '>', 'value': 10},
            {'field': 'eps_growth', 'operator': '>', 'value': 10}
        ]
    }
}
```

---

### 5.3 Market Data Aggregation API

**Priority**: HIGH (unify data from all sources)

**Deliverables**:
```python
# Backend/src/assets/api/market_data.py

@router.get("/market/overview")
def get_market_overview():
    """
    Get comprehensive market overview
    Aggregates data from all providers

    Returns:
    - Indices (S&P 500, Nasdaq, Dow Jones)
    - Top movers (gainers/losers)
    - Sector performance
    - Market cap
    - Volume
    """
    # Fetch from cache (L2)
    # Aggregate data
    # Return unified response
    pass

@router.get("/market/heatmap")
def get_market_heatmap():
    """
    Get market heatmap data
    """
    pass

@router.get("/market/movers")
def get_market_movers(direction='gainers', limit=10):
    """
    Get top gainers or losers
    """
    pass
```

---

### 5.4 News & Sentiment API

**Priority**: HIGH (unify news from multiple sources)

**Deliverables**:
```python
# Backend/src/assets/api/news.py

@router.get("/news")
def get_news(limit=20, symbol=None):
    """
    Get aggregated news from multiple sources

    Aggregates from:
    - RSS feeds
    - NewsAPI
    - Finnhub
    - Alpha Vantage

    Includes sentiment scores from:
    - Finnhub (built-in)
    - Custom NLP pipeline
    """
    pass

@router.get("/news/{symbol}")
def get_symbol_news(symbol, limit=20):
    """
    Get news for specific symbol
    """
    pass

@router.get("/sentiment/{symbol}")
def get_symbol_sentiment(symbol):
    """
    Get sentiment score for symbol

    Aggregates from:
    - Reddit (PRAW + TextBlob)
    - StockTwits (bullish/bearish ratio)
    - News (NLP sentiment analysis)
    """
    pass
```

---

### 5.5 Economic Data API

**Priority**: MEDIUM (economic calendar and indicators)

**Deliverables**:
```python
# Backend/src/assets/api/economic.py

@router.get("/economic/calendar")
def get_economic_calendar():
    """
    Get economic calendar from FRED

    Returns:
    - Upcoming economic events
    - Consensus estimates
    - Previous values
    - Impact level
    """
    pass

@router.get("/economic/indicators")
def get_economic_indicators():
    """
    Get economic indicators

    Returns:
    - Treasury yields (2y, 5y, 10y, 30y)
    - GDP
    - CPI
    - Unemployment
    - Federal Funds Rate
    """
    pass

@router.get("/economic/treasury-yields")
def get_treasury_yields():
    """
    Get current treasury yields from FRED
    """
    pass
```

---

## Phase 6: Frontend Development (Days 22-35)

### 6.1 Market Intelligence Dashboard

**Priority**: CRITICAL (main Bloomberg-like interface)

**Page**: `/dashboard/intelligence`

**Components**:
- Market overview cards (indices, market cap, volume)
- Top movers (gainers/losers)
- Sector heatmap
- Treasury yields
- Economic calendar widget

**Data Sources**:
- Cached market data (L2 cache)
- FRED API (treasury yields)
- Scraped news headlines (RSS)

---

### 6.2 TradingView Chart Integration

**Priority**: CRITICAL (professional charting)

**Library**: `lightweight-charts` (free, open-source)

**Components**:
- Candlestick chart with real-time updates
- Technical indicator overlays (RSI, MACD, Bollinger Bands)
- Volume bars
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d, 1w)
- Drawing tools (trendlines, Fibonacci)
- Comparison mode (multiple assets)

**Data Sources**:
- WebSocket streaming (Finnhub, Binance)
- Cached historical data (PostgreSQL)

---

### 6.3 Order Book & Time & Sales

**Priority**: HIGH (Level 2 market depth)

**Components**:
- Order book visualization (bids/asks depth)
- Time & sales table (recent trades)
- Volume profile chart

**Data Sources**:
- Binance order book API (10,000 levels)
- Polygon.io order book (when upgraded)

---

### 6.4 News & Sentiment Dashboard

**Priority**: HIGH (intelligence feed)

**Page**: `/dashboard/news`

**Components**:
- Real-time news feed with sentiment badges
- Sentiment gauge per symbol
- Reddit/StockTwits sentiment stream
- News source filter

**Data Sources**:
- RSS feeds (free)
- NewsAPI (free tier)
- Reddit sentiment scraper
- StockTwits API (free)

---

### 6.5 Economic Calendar

**Priority**: MEDIUM (economic events)

**Page**: `/dashboard/economic-calendar`

**Components**:
- Calendar view of economic events
- Countdown timers to releases
- Consensus vs actual
- Impact indicators (High/Medium/Low)

**Data Sources**:
- FRED API (free)

---

### 6.6 Screener UI

**Priority**: MEDIUM (stock screening)

**Page**: `/dashboard/screener`

**Components**:
- Filter builder UI
- Preset strategies selector
- Results table with sorting/pagination
- Quick chart preview
- Export to CSV

**Data Sources**:
- Screener API (already exists)
- Cached market data

---

## Phase 7: Paper Trading System (Days 36-45)

### 7.1 Order Management Models

**Deliverables**:
```python
Backend/src/trading/models/
├── order.py                 # Order model (market, limit, stop)
├── position.py              # Position model (holdings, P&L)
└── paper_trading_account.py # Paper trading account model
```

---

### 7.2 Paper Trading Execution Engine

**Deliverables**:
```python
Backend/src/trading/services/
└── paper_trading_engine.py

# Features:
# - Order matching (simulated fills)
# - Position tracking
# - Real-time P&L calculation
# - Risk management (position limits, max drawdown)
```

---

### 7.3 Trading UI

**Priority**: HIGH (paper trading interface)

**Page**: `/dashboard/trading`

**Components**:
- Order entry forms (limit, market, stop)
- Quick buy/sell buttons
- Open positions table with real-time P&L
- Order history
- Account balance/margin overview

**Data Sources**:
- Real-time prices (WebSocket)
- Paper trading engine

---

## Cost Summary

### Free Tier Utilization

| Provider | Free Tier | Daily Calls | Strategy | Keys Needed |
|----------|-----------|--------------|-----------|--------------|
| **Polygon.io** | 5 req/min | 7,200/day | Register 6 free accounts | 6 keys = 30 req/min |
| **IEX Cloud** | 500K/month | 16,666/day | Use for fundamentals | 1 key |
| **Finnhub** | 60 req/min | 86,400/day | Use WebSocket for real-time | 1 key |
| **Alpha Vantage** | 25 req/day | 25/day | Register 10 free accounts | 10 keys = 250/day |
| **CoinGecko** | 50 req/min | 72,000/day | Register 3 free accounts | 3 keys = 150 req/min |
| **CoinMarketCap** | 10K/day | 10,000/day | Use as backup | 1 key |
| **NewsAPI** | 100 req/day | 100/day | Schedule every 6 hours | 1 key |
| **Yahoo Finance** | Unlimited | Unlimited | Use for historical data | N/A |
| **Binance** | Unlimited | Unlimited | Use for crypto real-time | N/A |
| **SEC EDGAR** | 10 req/sec | 864,000/day | Rate limiting built-in | N/A |
| **FRED** | 120 req/min | 172,800/day | Free API key | 1 key |
| **Reddit** | 60 req/min | 86,400/day | Free API | 1 key |
| **StockTwits** | 200 req/hour | 4,800/day | Free API | 1 key |

**Total Monthly API Cost**: **$0**

**Total Free API Keys to Register**: ~25 keys across all providers

---

### Cost-Optimized Paid Upgrades (Optional)

| Provider | Upgrade Cost | When to Upgrade | Why |
|----------|--------------|------------------|-----|
| **Polygon.io Pro** | $199/month | When real-time needed | Real-time prices, Level 2 |
| **Alpha Vantage Premium** | $499/year | When 250/day insufficient | Higher rate limits |
| **CoinGecko Pro** | $79/month | When 150/min insufficient | Unlimited calls |
| **Finnhub Plus** | $60/month | When 60/min insufficient | More calls |
| **NewsAPI Business** | $449/month | When 100/day insufficient | More sources, no delay |

**Incremental Upgrade Path**: Start free, upgrade specific providers as needed

---

## Implementation Timeline

### Week 1: Foundation (Days 1-7)
- Days 1-3: API Key Rotation System
- Days 4-5: SEC EDGAR Scraper
- Days 6-7: RSS News Aggregator

### Week 2: Scraping Enhancement (Days 8-14)
- Days 8-9: FRED API Integration
- Days 10-11: Reddit Sentiment Scraper
- Days 12-13: StockTwits API Integration
- Day 14: Yahoo Finance Enhancements

### Week 3: Free Tier APIs (Days 15-21)
- Days 15-16: Polygon.io Free Tier
- Days 17-18: IEX Cloud Free Tier
- Days 19-20: Finnhub Free Tier
- Day 21: NewsAPI Free Tier

### Week 4: Backend Development (Days 22-28)
- Days 22-24: Technical Indicators Service
- Days 25-27: Market Data Aggregation API
- Day 28: News & Sentiment API

### Week 5: Backend Continued (Days 29-35)
- Days 29-30: Economic Data API
- Days 31-33: Call Planning & Scheduling
- Days 34-35: Testing & Optimization

### Week 6: Frontend Development (Days 36-42)
- Days 36-38: Market Intelligence Dashboard
- Days 39-40: TradingView Chart Integration
- Day 41-42: Order Book & Time & Sales

### Week 7: Frontend Continued (Days 43-49)
- Days 43-45: News & Sentiment Dashboard
- Days 46-47: Economic Calendar
- Days 48-49: Screener UI

### Week 8: Paper Trading (Days 50-56)
- Days 50-53: Order Management & Paper Trading Engine
- Days 54-56: Trading UI

---

## Success Metrics

### Data Coverage
- ✅ 95%+ of US stocks (via multiple providers)
- ✅ 100% of major indices
- ✅ 100% of top 100 cryptos
- ✅ 95%+ of major FX pairs
- ✅ 100% of US treasuries
- ✅ 50+ economic indicators

### Data Freshness
- ✅ Real-time prices (WebSocket) for top 20 stocks/crypto
- ✅ 15-minute delay for all other stocks
- ✅ Hourly news updates
- ✅ Daily fundamentals updates

### Cost Optimization
- ✅ $0 monthly API cost (free tiers only)
- ✅ <5% API rate limit failures
- ✅ >90% cache hit rate

### Performance
- ✅ <500ms API response time (cached)
- ✅ <2s page load time
- ✅ 99.9% uptime

---

## Next Steps

**Immediate Actions**:
1. Register free API accounts (25 keys total)
2. Create development environment
3. Start Phase 0 (API Key Rotation System)
4. Begin scraping infrastructure

**Questions for User**:
1. Do you want me to start implementing Phase 0 (API Key Rotation System)?
2. Should I create the database migration scripts for the new models?
3. Would you like me to generate registration links for all free API providers?
4. Should we prioritize real-time WebSocket streaming or historical data first?

This plan provides a complete path to build a Bloomberg-like terminal with **$0 monthly API costs** through aggressive scraping, free-tier optimization, and intelligent API key rotation.
