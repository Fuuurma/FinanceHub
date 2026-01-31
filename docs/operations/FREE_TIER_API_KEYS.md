# Free Tier API Keys Setup Guide

**Date:** 2026-01-30
**Author:** Charo (Security Engineer)
**Purpose:** Document free tier API keys needed for FinanceHub

---

## Overview

FinanceHub can operate with **100% free API tiers** for most data sources. This document lists which APIs are needed, how to get free keys, and what data they provide.

---

## API Keys Status

### ✅ Already Configured (Working)

| API | Status | Key |
|-----|--------|-----|
| **CoinGecko** | ✅ WORKING | `CG-UjB2TuiQdT31Yrc5qNwjYP6Y` |

### ⚠️ Need Setup (Free Tier Available)

| API | Environment Variable | Free Tier | Data Provided |
|-----|---------------------|-----------|---------------|
| **FRED** | `FRED_API_KEY` | ✅ Unlimited | Economic data, interest rates, GDP |
| **Alpha Vantage** | `ALPHA_VANTAGE_API_KEY` | 25 calls/day | Stock fundamentals, global quotes |
| **Finnhub** | `FINNHUB_API_KEY` | 60 calls/min | Real-time quotes, news |
| **NewsAPI** | `NEWS_API_KEY` | 100 req/day | Financial news |

### ❌ Placeholder Keys (Not Working)

| API | Environment Variable | Status |
|-----|---------------------|--------|
| CoinMarketCap | `COINMARKETCAP_API_KEY` | Placeholder (1234) |
| Binance | `BINANCE_API_KEY` | Placeholder (1234) |
| Massive | `MASSIVE_API_KEY` | Placeholder (1234) |

---

## How to Get Free API Keys

### 1. FRED API Key (RECOMMENDED - Unlimited Free)

**What it provides:**
- Economic indicators (GDP, inflation, unemployment)
- Interest rates (Fed funds, treasury yields)
- Consumer sentiment data
- International economic data

**Get your free key:**
1. Go to: https://fred.stlouisfed.org/docs/api/api_key.html
2. Enter your email
3. Click "Get API Key"
4. Check your email for the key

**Free tier:** Unlimited requests

**Setup:**
```bash
# Add to apps/backend/.env
FRED_API_KEY=your_fred_api_key_here
```

---

### 2. Alpha Vantage API Key (RECOMMENDED - 25 calls/day)

**What it provides:**
- Company overviews and fundamentals
- Global real-time quotes
- Daily time series
- Technical indicators
- Cryptocurrency data

**Get your free key:**
1. Go to: https://www.alphavantage.co/support/#api-key
2. Fill out the form
3. Click "Get Free API Key"
4. API key displayed immediately

**Free tier:** 25 requests per day

**Setup:**
```bash
# Add to apps/backend/.env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

---

### 3. Finnhub API Key (OPTIONAL - 60 calls/min)

**What it provides:**
- Real-time stock quotes
- Market news
- Company fundamentals
- Economic calendar
- Insider transactions

**Get your free key:**
1. Go to: https://finnhub.io/register
2. Create free account
3. API key shown in dashboard

**Free tier:** 60 calls per minute

**Setup:**
```bash
# Add to apps/backend/.env
FINNHUB_API_KEY=your_finnhub_api_key_here
```

---

### 4. NewsAPI Key (OPTIONAL - 100 req/day)

**What it provides:**
- Financial news headlines
- Business news
- Technology news
- Market news

**Get your free key:**
1. Go to: https://newsapi.org/register
2. Create free account
3. API key shown in dashboard

**Free tier:** 100 requests per day

**Setup:**
```bash
# Add to apps/backend/.env
NEWS_API_KEY=your_newsapi_key_here
```

---

## Current .env Configuration

```bash
# Database
DB_NAME=finance_hub_dev
DB_USER=root
DB_PASSWORD=240699sfb
DB_HOST=127.0.0.1
DB_PORT=3306

# Security
DJANGO_SECRET_KEY=django-insecure-change-this-in-production-min-50-chars-at-least
DEBUG=True
ENVIRONMENT=development

# API Keys (Free Tiers)
COINGECKO_API_KEY=CG-UjB2TuiQdT31Yrc5qNwjYP6Y  # ✅ Working - Crypto data
FRED_API_KEY=your_fred_api_key_here              # ⚠️ NEEDS SETUP - Economic data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key     # ⚠️ NEEDS SETUP - Stock fundamentals
FINNHUB_API_KEY=your_finnhub_api_key             # ⚠️ NEEDS SETUP - Real-time quotes
NEWS_API_KEY=your_newsapi_key                    # ⚠️ NEEDS SETUP - News (optional)

# Placeholders (Not working)
COINMARKETCAP_API_KEY=1234  # ❌ Not configured
BINANCE_API_KEY=1234        # ❌ Not configured
MASSIVE_API_KEY=1234        # ❌ Not configured
```

---

## Priority Order

### Priority 1 (Set up this week)
1. **FRED_API_KEY** - Unlimited free, economic data
2. **ALPHA_VANTAGE_API_KEY** - 25 calls/day, stock fundamentals

### Priority 2 (Set up when needed)
3. **FINNHUB_API_KEY** - Real-time quotes (optional)
4. **NEWS_API_KEY** - News (optional)

---

## What Works Without API Keys

FinanceHub is designed to work **without paid API keys**:

| Feature | Status | Data Source |
|---------|--------|-------------|
| **Crypto Prices** | ✅ Working | CoinGecko (free, unlimited) |
| **Economic Data** | ⚠️ Limited | FRED (needs key) |
| **Stock Prices** | ⚠️ Limited | Yahoo Finance scraper |
| **Stock Fundamentals** | ⚠️ Limited | Alpha Vantage (needs key) |
| **News** | ⚠️ Limited | NewsAPI (needs key) |

---

## Security Notes

### ✅ Current Security
- All API keys stored in `.env` (not committed to git)
- `.env` in `.gitignore`
- No keys in code or documentation

### ⚠️ To Improve
- Consider using secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Add API key rotation for production
- Monitor API key usage for anomalies

---

## Testing API Keys

### Test FRED API
```bash
cd apps/backend
python -c "
import os
from data.data_fetcher.fred import FredFetcher
fred = FredFetcher()
print('FRED API:', 'Connected' if fred.test_connection() else 'Failed')
"
```

### Test Alpha Vantage
```bash
cd apps/backend
python -c "
from data.data_fetcher.alpha_vantage import AlphaVantageJobs
av = AlphaVantageJobs(api_key='your_key')
print('Alpha Vantage:', 'Connected' if av.test_connection() else 'Failed')
"
```

---

## References

| Resource | URL |
|----------|-----|
| FRED API | https://fred.stlouisfed.org/docs/api/api_key.html |
| Alpha Vantage | https://www.alphavantage.co/support/#api-key |
| Finnhub | https://finnhub.io/ |
| NewsAPI | https://newsapi.org/ |
| CoinGecko | https://www.coingecko.com/en/api |

---

## Next Steps

1. ⏳ Get FRED API key (5 minutes)
2. ⏳ Get Alpha Vantage API key (5 minutes)
3. ⏳ Update `apps/backend/.env` with new keys
4. ⏳ Test API connections
5. ⏳ Document successful setup

---

**Document Version:** 1.0
**Created:** 2026-01-30
**Author:** Charo (Security Engineer)
