# API Keys Template
# ========================================
# INSTRUCTIONS
# ========================================
# 
# 1. Register ALL free API accounts using this guide:
#    .opencode/plans/FREE_API_REGISTRATION_GUIDE.md
# 
# 2. Copy API keys from each provider's dashboard
# 
# 3. Paste keys below in place of the placeholder text
# 
# 4. Save this file
# 
# 5. Update Backend/.env with your actual keys
# 
# ========================================

# ========================================
# STOCK DATA PROVIDERS
# ========================================

## Polygon.io (6 free accounts)
# Register at: https://polygon.io/
# Get keys from: Dashboard → API Keys
# Strategy: 6 keys = 30 requests/minute

POLYGON_API_KEY_1=REGISTER_AND_REPLACE_WITH_KEY_1
POLYGON_API_KEY_2=REGISTER_AND_REPLACE_WITH_KEY_2
POLYGON_API_KEY_3=REGISTER_AND_REPLACE_WITH_KEY_3
POLYGON_API_KEY_4=REGISTER_AND_REPLACE_WITH_KEY_4
POLYGON_API_KEY_5=REGISTER_AND_REPLACE_WITH_KEY_5
POLYGON_API_KEY_6=REGISTER_AND_REPLACE_WITH_KEY_6

## IEX Cloud (1 account)
# Register at: https://iexcloud.io/pricing/
# Get key from: Console → API Tokens
# Strategy: 1 account sufficient for fundamentals (sandbox)

IEX_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

## Finnhub (1 account)
# Register at: https://finnhub.io/
# Get key from: Dashboard → API Key
# Strategy: 1 account sufficient for real-time WebSocket

FINNHUB_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

## Alpha Vantage (10 free accounts)
# Register at: https://www.alphavantage.co/support/#api-key
# Get keys from: Email confirmation (10 separate emails)
# Strategy: 10 keys = 250 requests/day

ALPHA_VANTAGE_API_KEY_1=REGISTER_AND_REPLACE_WITH_KEY_1
ALPHA_VANTAGE_API_KEY_2=REGISTER_AND_REPLACE_WITH_KEY_2
ALPHA_VANTAGE_API_KEY_3=REGISTER_AND_REPLACE_WITH_KEY_3
ALPHA_VANTAGE_API_KEY_4=REGISTER_AND_REPLACE_WITH_KEY_4
ALPHA_VANTAGE_API_KEY_5=REGISTER_AND_REPLACE_WITH_KEY_5
ALPHA_VANTAGE_API_KEY_6=REGISTER_AND_REPLACE_WITH_KEY_6
ALPHA_VANTAGE_API_KEY_7=REGISTER_AND_REPLACE_WITH_KEY_7
ALPHA_VANTAGE_API_KEY_8=REGISTER_AND_REPLACE_WITH_KEY_8
ALPHA_VANTAGE_API_KEY_9=REGISTER_AND_REPLACE_WITH_KEY_9
ALPHA_VANTAGE_API_KEY_10=REGISTER_AND_REPLACE_WITH_KEY_10

# ========================================
# CRYPTO DATA PROVIDERS
# ========================================

## Binance (no key needed)
# Public endpoints: No API key required
# WebSocket: wss://stream.binance.com:9443/ws

BINANCE_API_KEY=NOT_REQUIRED_FOR_PUBLIC_ENDPOINTS

## CoinGecko (3 free accounts)
# Register at: https://www.coingecko.com/en/api
# Get keys from: API Keys page (3 separate accounts)
# Strategy: 3 keys = 150 requests/minute

COINGECKO_API_KEY_1=REGISTER_AND_REPLACE_WITH_KEY_1
COINGECKO_API_KEY_2=REGISTER_AND_REPLACE_WITH_KEY_2
COINGECKO_API_KEY_3=REGISTER_AND_REPLACE_WITH_KEY_3

## CoinMarketCap (1 backup account)
# Register at: https://coinmarketcap.com/api/
# Get key from: Dashboard → API Keys
# Strategy: Use as backup to CoinGecko

COINMARKETCAP_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

## CryptoCompare (free tier - optional)
# Register at: https://min-api.cryptocompare.com/
# Get key from: Dashboard → API Keys
# Strategy: Start with free, upgrade to Pro ($79/mo) if needed

CRYPTOCOMPARE_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

# ========================================
# FOREX DATA PROVIDERS
# ========================================

## CurrencyLayer (backup FX)
# Register at: https://currencylayer.com/
# Get key from: Dashboard → API Access Key
# Strategy: Use as backup to Alpha Vantage

CURRENCYLAYER_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

## OANDA (optional practice account)
# Register at: https://www.oanda.com/
# Get key from: Developer portal
# Strategy: Only use if real FX data critical

OANDA_API_KEY=REGISTER_AND_REPLACE_WITH_KEY_IF_NEEDED

# ========================================
# ECONOMIC DATA PROVIDERS
# ========================================

## FRED (Federal Reserve - free)
# Register at: https://fred.stlouisfed.org/docs/api/api_key.html
# Get key from: Email confirmation (instant)
# Strategy: Excellent source, 1 account sufficient

FRED_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

## BLS (Bureau of Labor - optional)
# Register at: https://www.bls.gov/developers/
# Get key from: Registration confirmation
# Strategy: Optional, FRED is better

BLS_API_KEY=REGISTER_AND_REPLACE_WITH_KEY_IF_NEEDED

## EIA (Energy Information)
# Register at: https://www.eia.gov/opendata/
# Get key from: Dashboard → API Keys
# Strategy: Good for commodities (oil, gas)

EIA_API_KEY=REGISTER_AND_REPLACE_WITH_KEY

# ========================================
# NEWS DATA PROVIDERS
# ========================================

## NewsAPI (developer tier - free)
# Register at: https://newsapi.org/
# Get key from: Dashboard → API Key
# Strategy: 100 req/day, schedule every 6 hours

NEWSAPI_KEY=REGISTER_AND_REPLACE_WITH_KEY

# RSS Feeds (no API keys required)
# Sources: CNBC, Reuters, MarketWatch, Seeking Alpha, Benzinga
# No registration needed - just parse feeds

# CNBC
RSS_CNBC=https://www.cnbc.com/id/10000664/device/rss/rss.html

# Reuters
RSS_REUTERS=https://www.reutersagency.com/feed/

# MarketWatch
RSS_MARKETWATCH=https://www.marketwatch.com/rss/topstories

# Seeking Alpha
RSS_SEEKINGALPHA=https://seekingalpha.com/feed.xml

# Benzinga
RSS_BENZINGA=https://www.benzinga.com/feed

# Bloomberg
RSS_BLOOMBERG=https://feeds.bloomberg.com/markets/news.rss

# ========================================
# SOCIAL SENTIMENT DATA PROVIDERS
# ========================================

## Reddit (PRAW - free)
# Register at: https://www.reddit.com/prefs/apps
# Get keys from: "create another app" form
# Strategy: 60 req/minute

REDDIT_CLIENT_ID=REGISTER_AND_REPLACE_WITH_CLIENT_ID
REDDIT_CLIENT_SECRET=REGISTER_AND_REPLACE_WITH_CLIENT_SECRET
REDDIT_USER_AGENT='FinanceHub/1.0 (your-email@domain.com)'

## StockTwits (free tier)
# Register at: https://api.stocktwits.com/developers
# Get key from: Dashboard → Access Tokens
# Strategy: 200 req/hour

STOCKTWITS_ACCESS_TOKEN=REGISTER_AND_REPLACE_WITH_TOKEN

# ========================================
# EXISTING PROVIDERS (ALREADY HAVE KEYS)
# ========================================

## Yahoo Finance (no key needed)
# Already implemented via yfinance
# No API key required

YAHOO_FINANCE_API_KEY=NOT_NEEDED

## Alpha Vantage (existing)
# Already have 1 key from current implementation
# Add 9 more keys above

ALPHA_VANTAGE_API_KEY_EXISTING=YOUR_EXISTING_KEY_HERE

## CoinGecko (existing)
# Already have 1 key from current implementation
# Add 2 more keys above

COINGECKO_API_KEY_EXISTING=YOUR_EXISTING_KEY_HERE

# ========================================
# DATABASE (KEEP YOURS)
# ========================================

DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/financehub
REDIS_URL=redis://localhost:6379/0

# ========================================
# CELERY (KEEP YOURS)
# ========================================

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ========================================
# WEBSOCKETS (KEEP YOURS)
# ========================================

WS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# ========================================
# NEXT STEPS AFTER REGISTERING
# ========================================
#
# 1. Replace all "REGISTER_AND_REPLACE_WITH_KEY" placeholders above
# 2. Save this file
# 3. Update Backend/.env with the values from this template
# 4. Run: cd Backend/src && python manage.py makemigrations
# 5. Run: cd Backend/src && python manage.py migrate
# 6. Run: cd Backend/src && python manage.py createsuperuser
# 7. Run: cd Backend/src && python manage.py runserver
# 8. Test API keys by running commands from FREE_API_REGISTRATION_GUIDE.md
#
# ========================================
