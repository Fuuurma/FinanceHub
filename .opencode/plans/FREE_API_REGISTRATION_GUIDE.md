# Free API Key Registration Guide

## Quick Reference - All Free API Accounts to Register

This guide provides direct links to register all free API accounts needed for the cost-optimized Bloomberg Terminal.

---

## 1. Stock Data Providers

### Polygon.io (Free Tier)
**Registration**: https://polygon.io/
**Free Tier**: 5 requests/minute
**Benefits**: End-of-day stocks, 2 years historical, options chains, dividends/splits
**Strategy**: Register 6 free accounts = 30 requests/minute

**Registration Steps**:
1. Go to https://polygon.io/
2. Click "Start Building" → "Sign Up"
3. Use email +1 (e.g., your-email+1@domain.com)
4. Verify email
5. Go to Dashboard → API Keys
6. Copy API Key
7. Repeat for 6 accounts (your-email+1, +2, +3, +4, +5, +6)

**Key Management**: Store in Backend/.env as:
```bash
POLYGON_API_KEY_1=key1
POLYGON_API_KEY_2=key2
POLYGON_API_KEY_3=key3
POLYGON_API_KEY_4=key4
POLYGON_API_KEY_5=key5
POLYGON_API_KEY_6=key6
```

---

### IEX Cloud (Launch Tier - Free)
**Registration**: https://iexcloud.io/pricing/
**Free Tier**: 500,000 calls/month (sandbox environment)
**Benefits**: Excellent fundamentals, 10-K/10-Q, earnings, financial statements
**Strategy**: 1 account sufficient for fundamentals (not real-time)

**Registration Steps**:
1. Go to https://iexcloud.io/pricing/
2. Scroll to "Launch" tier (FREE)
3. Click "Start Free Trial" → "Sign Up"
4. Create account with email/password
5. Verify email
6. Go to Console → API Tokens
7. Copy Publishable Token
8. Store in Backend/.env as `IEX_API_KEY=your_key`

---

### Finnhub (Free Tier)
**Registration**: https://finnhub.io/
**Free Tier**: 60 requests/minute, unlimited daily
**Benefits**: Real-time WebSocket, news with sentiment, technical indicators, pattern recognition
**Strategy**: 1 account sufficient for real-time streaming

**Registration Steps**:
1. Go to https://finnhub.io/
2. Click "Get Free API Key"
3. Sign up with email/password
4. Verify email
5. Go to Dashboard → API Key
6. Copy API Key
7. Store in Backend/.env as `FINNHUB_API_KEY=your_key`

**WebSocket Connection**:
```python
import finnhub
trade_client = finnhub.Trade('your_api_key')
trade_client.subscribe_trades('AAPL')
```

---

### Alpha Vantage (Free Tier)
**Registration**: https://www.alphavantage.co/support/#api-key
**Free Tier**: 25 requests/day, 5 requests/minute
**Benefits**: Stocks, forex, crypto, commodities, technical indicators, fundamentals
**Strategy**: Register 10 free accounts = 250 requests/day

**Registration Steps**:
1. Go to https://www.alphavantage.co/support/#api-key
2. Scroll to "Get Your Free API Key Today" section
3. Enter email (use your-email+1@domain.com)
4. Click "Get Free API Key"
5. Verify email
6. Copy API Key
7. Repeat for 10 accounts (your-email+1 through +10)
8. Store in Backend/.env as:
```bash
ALPHA_VANTAGE_API_KEY_1=key1
ALPHA_VANTAGE_API_KEY_2=key2
# ... through 10
```

**Limitations**: Very restrictive, use for:
- Critical real-time data (top 5 stocks)
- Overnight batch updates
- Backup to other providers

---

## 2. Crypto Data Providers

### Binance (Free - Public Endpoints)
**Registration**: https://www.binance.com/en/support/faq/360002502072
**Free Tier**: Unlimited public endpoints
**Benefits**: Real-time crypto prices, order book (10,000 levels), WebSocket
**Strategy**: No API key needed for public endpoints

**No Registration Needed**:
- Use public API: https://api.binance.com/api/v3
- Use WebSocket: wss://stream.binance.com:9443/ws

**Optional**: Register for authenticated endpoints (optional, not needed initially)

---

### CoinGecko (Free Tier)
**Registration**: https://www.coingecko.com/en/api
**Free Tier**: 10-50 requests/minute
**Benefits**: Market data, historical prices, top 100 cryptos
**Strategy**: Register 3 free accounts = 150 requests/minute

**Registration Steps**:
1. Go to https://www.coingecko.com/en/api
2. Click "Create a CoinGecko account" link
3. Sign up with email/password
4. Verify email
5. Go to API Keys page
6. Click "Create API Key" (free tier)
7. Copy API Key
8. Repeat for 3 accounts
9. Store in Backend/.env as:
```bash
COINGECKO_API_KEY_1=key1
COINGECKO_API_KEY_2=key2
COINGECKO_API_KEY_3=key3
```

---

### CoinMarketCap (Free Tier)
**Registration**: https://coinmarketcap.com/api/
**Free Tier**: 10,000 requests/day, 10 requests/minute
**Benefits**: Crypto data, market cap, rankings
**Strategy**: Use as backup to CoinGecko

**Registration Steps**:
1. Go to https://coinmarketcap.com/api/
2. Click "Get Started" → "Basic Plan" (FREE)
3. Create account
4. Verify email
5. Go to Dashboard → API Keys
6. Copy API Key
7. Store in Backend/.env as `COINMARKETCAP_API_KEY=your_key`

---

### CryptoCompare (Free Tier - Optional Upgrade)
**Registration**: https://min-api.cryptocompare.com/
**Free Tier**: Limited free tier
**Pro Tier**: $79/month (consider upgrading later)
**Benefits**: Social sentiment data, excellent crypto data
**Strategy**: Start with free tier, upgrade if needed

**Registration Steps**:
1. Go to https://min-api.cryptocompare.com/
2. Click "Sign Up" → "Developer"
3. Create account (free tier)
4. Verify email
5. Go to Dashboard → API Keys
6. Copy API Key
7. Store in Backend/.env as `CRYPTOCOMPARE_API_KEY=your_key`

---

## 3. Forex Data

### CurrencyLayer (Free Tier)
**Registration**: https://currencylayer.com/
**Free Tier**: 1,000 requests/month
**Benefits**: 168 currencies, live rates, historical data
**Strategy**: Use as backup to Alpha Vantage

**Registration Steps**:
1. Go to https://currencylayer.com/
2. Scroll to "Free Subscription"
3. Click "Get Started for Free"
4. Create account
5. Verify email
6. Go to Dashboard → API Keys
7. Copy API Access Key
8. Store in Backend/.env as `CURRENCYLAYER_API_KEY=your_key`

---

### OANDA (Optional - Free Practice Account)
**Registration**: https://www.oanda.com/
**Free Tier**: Practice account (simulated data)
**Strategy**: Use only if real FX data critical

**Registration Steps**:
1. Go to https://www.oanda.com/
2. Click "Open an Account" → "Practice Account"
3. Create account
4. Get API token from developer portal
5. Store in Backend/.env as `OANDA_API_KEY=your_key`

---

## 4. Economic Data

### FRED (Federal Reserve - Free)
**Registration**: https://fred.stlouisfed.org/docs/api/api_key.html
**Free Tier**: 120 requests/minute
**Benefits**: Treasury yields, GDP, CPI, unemployment, 500,000+ indicators
**Strategy**: Excellent source, 1 account sufficient

**Registration Steps**:
1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
2. Scroll to "Request an API Key" section
3. Click "Request API Key"
4. Fill out form (email, name, organization)
5. Submit
6. Receive API key via email (immediate)
7. Store in Backend/.env as `FRED_API_KEY=your_key`

**Popular Series IDs**:
```python
TREASURY_YIELDS = {
    '2y': 'DGS2',    # 2-Year Treasury
    '5y': 'DGS5',    # 5-Year Treasury
    '10y': 'DGS10',   # 10-Year Treasury
    '30y': 'DGS30'    # 30-Year Treasury
}

ECONOMIC_INDICATORS = {
    'gdp': 'GDP',           # Gross Domestic Product
    'cpi': 'CPIAUCSL',      # CPI for All Urban Consumers
    'unemployment': 'UNRATE', # Unemployment Rate
    'fed_funds': 'DFF',     # Federal Funds Rate
}
```

---

### BLS (Bureau of Labor Statistics - Free)
**Registration**: https://www.bls.gov/developers/
**Free Tier**: No rate limit (public API)
**Benefits**: Unemployment, CPI, wage data
**Strategy**: Optional, FRED is better

**Registration Steps**:
1. Go to https://www.bls.gov/developers/
2. No registration required for most endpoints
3. For premium features, register for API key
4. Store in Backend/.env as `BLS_API_KEY=your_key` (if registered)

---

## 5. News Data

### NewsAPI (Developer Tier - Free)
**Registration**: https://newsapi.org/
**Free Tier**: 100 requests/day
**Benefits**: 150,000 news sources, headlines, full articles (24h delay)
**Strategy**: Schedule every 6 hours to maximize free tier

**Registration Steps**:
1. Go to https://newsapi.org/
2. Click "Get API Key"
3. Fill out registration form
4. Verify email
5. Go to Dashboard → API Key
6. Copy API Key
7. Store in Backend/.env as `NEWSAPI_KEY=your_key`

**Limitations**:
- 24-hour delay on full articles
- Use headlines only for real-time
- Combine with RSS feeds for better coverage

---

### RSS Feeds (No Registration Required)
**Sources**: Completely free, no API key needed

**Feeds to Use**:
```python
RSS_SOURCES = {
    'CNBC': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
    'Reuters': 'https://www.reutersagency.com/feed/',
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
    'Benzinga': 'https://www.benzinga.com/feed',
    'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss'
}
```

**No Registration Needed** - Just implement RSS parser

---

## 6. Social Sentiment Data

### Reddit (PRAW - Free)
**Registration**: https://www.reddit.com/prefs/apps
**Free Tier**: 60 requests/minute
**Benefits**: r/wallstreetbets, r/stocks, real-time sentiment
**Strategy**: Official API with PRAW library

**Registration Steps**:
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to "are you a developer?"
3. Click "create another app"
4. Fill out form:
   - Name: "FinanceHub"
   - About URL: "https://yourdomain.com"
   - Redirect URI: "http://localhost:8000"
5. Save
6. Copy client_id and client_secret
7. Store in Backend/.env as:
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT='FinanceHub/1.0 (your-email@domain.com)'
```

**Installation**:
```bash
pip install praw
```

---

### StockTwits (Free Tier)
**Registration**: https://api.stocktwits.com/developers
**Free Tier**: 200 requests/hour
**Benefits**: Bullish/bearish sentiment, trending symbols
**Strategy**: Use as primary sentiment source

**Registration Steps**:
1. Go to https://api.stocktwits.com/developers
2. Click "Get Access Token"
3. Create account
4. Verify email
5. Go to Dashboard → Access Tokens
6. Copy Access Token
7. Store in Backend/.env as `STOCKTWITS_ACCESS_TOKEN=your_token`

**No API Key Needed** - Use access token for API calls

---

## 7. Government Data Sources

### SEC EDGAR (Free - No API Key Required)
**Registration**: Not required, but recommended to register email
**Benefits**: Company filings, 10-K/10-Q, insider trading
**Strategy**: Use official API, rate limit is 10 requests/second

**User-Agent Requirement**:
SEC requires User-Agent header with email:
```python
headers = {
    'User-Agent': 'FinanceHub/1.0 (your-email@domain.com)',
    'Accept': 'application/json'
}
```

**Optional Registration**:
1. Go to https://www.sec.gov/edgar/search-filings
2. Create account for email notifications
3. Not required for API access

---

### EIA (Energy Information Administration - Free)
**Registration**: https://www.eia.gov/opendata/
**Free Tier**: Free API key required
**Benefits**: Energy commodities, crude oil, natural gas
**Strategy**: Register for API key

**Registration Steps**:
1. Go to https://www.eia.gov/opendata/
2. Click "Register"
3. Create account
4. Verify email
5. Go to Profile → API Keys
6. Copy API Key
7. Store in Backend/.env as `EIA_API_KEY=your_key`

---

## 8. Complete .env File Template

```bash
# Backend/.env

# ===== DATA PROVIDERS =====

# Polygon.io (6 free keys for rotation)
POLYGON_API_KEY_1=your_polygon_key_1
POLYGON_API_KEY_2=your_polygon_key_2
POLYGON_API_KEY_3=your_polygon_key_3
POLYGON_API_KEY_4=your_polygon_key_4
POLYGON_API_KEY_5=your_polygon_key_5
POLYGON_API_KEY_6=your_polygon_key_6

# IEX Cloud (1 key for fundamentals)
IEX_API_KEY=your_iex_key

# Finnhub (1 key for real-time WebSocket)
FINNHUB_API_KEY=your_finnhub_key

# Alpha Vantage (10 free keys for rotation)
ALPHA_VANTAGE_API_KEY_1=your_alpha_key_1
ALPHA_VANTAGE_API_KEY_2=your_alpha_key_2
ALPHA_VANTAGE_API_KEY_3=your_alpha_key_3
ALPHA_VANTAGE_API_KEY_4=your_alpha_key_4
ALPHA_VANTAGE_API_KEY_5=your_alpha_key_5
ALPHA_VANTAGE_API_KEY_6=your_alpha_key_6
ALPHA_VANTAGE_API_KEY_7=your_alpha_key_7
ALPHA_VANTAGE_API_KEY_8=your_alpha_key_8
ALPHA_VANTAGE_API_KEY_9=your_alpha_key_9
ALPHA_VANTAGE_API_KEY_10=your_alpha_key_10

# CoinGecko (3 free keys for rotation)
COINGECKO_API_KEY_1=your_coingecko_key_1
COINGECKO_API_KEY_2=your_coingecko_key_2
COINGECKO_API_KEY_3=your_coingecko_key_3

# CoinMarketCap (1 backup key)
COINMARKETCAP_API_KEY=your_coinmarketcap_key

# CryptoCompare (optional, free tier)
CRYPTOCOMPARE_API_KEY=your_cryptocompare_key

# CurrencyLayer (backup FX)
CURRENCYLAYER_API_KEY=your_currencylayer_key

# FRED (Federal Reserve - free)
FRED_API_KEY=your_fred_key

# BLS (Bureau of Labor - optional)
BLS_API_KEY=your_bls_key

# NewsAPI (free tier)
NEWSAPI_KEY=your_newsapi_key

# Reddit (PRAW)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT='FinanceHub/1.0 (your-email@domain.com)'

# StockTwits (free tier)
STOCKTWITS_ACCESS_TOKEN=your_stocktwits_token

# EIA (Energy Information Administration)
EIA_API_KEY=your_eia_key

# ===== EXISTING PROVIDERS =====

# Yahoo Finance (no key needed - already implemented)
# Binance (no key needed for public endpoints - already implemented)
# Alpha Vantage (already have one key - add 9 more)

# ===== DATABASE =====
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/financehub
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# ===== CELERY =====
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ===== WEBSOCKETS =====
WS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Registration Checklist

Use this checklist to track your progress:

### Stock Providers
- [ ] Register 6 Polygon.io accounts
- [ ] Register IEX Cloud account
- [ ] Register Finnhub account
- [ ] Register 10 Alpha Vantage accounts

### Crypto Providers
- [ ] Register 3 CoinGecko accounts
- [ ] Register CoinMarketCap account
- [ ] Register CryptoCompare account (optional)
- [ ] Verify Binance public access (no registration)

### Forex Providers
- [ ] Register CurrencyLayer account
- [ ] Register OANDA practice account (optional)

### Economic Data
- [ ] Register FRED API key
- [ ] Register BLS API key (optional)
- [ ] Register EIA API key

### News Providers
- [ ] Register NewsAPI account
- [ ] Test RSS feeds (no registration)

### Social Sentiment
- [ ] Register Reddit PRAW app
- [ ] Register StockTwits account

### Government Data
- [ ] Test SEC EDGAR (no registration)
- [ ] Configure User-Agent for SEC requests

---

## Security Best Practices

### 1. API Key Storage
- ✅ Store all API keys in Backend/.env (NOT in code)
- ✅ Add Backend/.env to .gitignore
- ✅ Never commit API keys to version control
- ✅ Use different email aliases for each provider (+1, +2, etc.)

### 2. API Key Encryption (Production)
- ✅ Use `django-fernet-fields` to encrypt API keys in database
- ✅ Generate encryption key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- ✅ Store encryption key in Backend/.env as `FERNET_KEY=your_key`

### 3. API Key Rotation Strategy
- ✅ Use multiple keys per provider to maximize free tier
- ✅ Implement automatic rotation on rate limit hits
- ✅ Monitor usage to avoid hitting limits
- ✅ Schedule high-volume calls during off-hours

### 4. Email Aliasing Strategy
Use email aliases to register multiple free accounts:

```
your-email+polygon1@domain.com
your-email+polygon2@domain.com
your-email+alpha1@domain.com
your-email+alpha2@domain.com
# ... etc
```

Most email providers (Gmail, Outlook, iCloud) support the `+` alias feature.

---

## Quick Start Commands

After registering all accounts, use these commands to verify:

```bash
# Test Polygon.io
curl "https://api.polygon.io/v1/meta/AAPL?apiKey=$POLYGON_API_KEY_1"

# Test IEX Cloud
curl "https://cloud.iexapis.com/stable/stock/AAPL/quote?token=$IEX_API_KEY"

# Test Finnhub
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=$FINNHUB_API_KEY"

# Test Alpha Vantage
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=$ALPHA_VANTAGE_API_KEY_1"

# Test FRED
curl "https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=$FRED_API_KEY&file_type=json"

# Test NewsAPI
curl "https://newsapi.org/v2/top-headlines?category=business&apiKey=$NEWSAPI_KEY"
```

---

## Support Links

- **Polygon.io Support**: https://polygon.io/support/
- **IEX Cloud Support**: https://iexcloud.io/docs/support/
- **Finnhub Support**: https://finnhub.io/support/
- **Alpha Vantage Support**: https://www.alphavantage.co/support/
- **CoinGecko Support**: https://www.coingecko.com/en/api/documentation
- **FRED Support**: https://fred.stlouisfed.org/docs/api/fred/
- **NewsAPI Support**: https://newsapi.org/docs
- **Reddit API**: https://praw.readthedocs.io/
- **StockTwits API**: https://api.stocktwits.com/developers/docs/

---

This guide provides everything you need to register all free API accounts for the cost-optimized Bloomberg Terminal implementation.
