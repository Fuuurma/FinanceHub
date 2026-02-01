# Data Providers Skill

## Overview
Data providers are external APIs and services that supply financial market data, including real-time quotes, historical prices, news, social sentiment, and economic indicators.

## Key Concepts
- **Market Data APIs**: Real-time and historical price data
- **WebSocket Streams**: Real-time data feeds
- **Rate Limiting**: API request limits and quotas
- **Authentication**: API keys, OAuth, tokens
- **Data Normalization**: Standardizing formats across providers
- **Fallback Providers**: Multiple sources for redundancy
- **Caching**: Reducing API calls with local cache
- **Error Handling**: Timeouts, failures, partial data

## Popular Financial Data Providers

### Free/Cheap Tier
- **Alpha Vantage**: Free tier (500 requests/day)
- **IEX Cloud**: Free tier (100k requests/month)
- **Polygon.io**: Free tier (5 requests/minute)
- **Yahoo Finance** (yfinance): Unofficial, free
- **Finnhub**: Free tier (60 requests/minute)

### Paid/Enterprise
- **Bloomberg Terminal**: Enterprise, expensive
- **Reuters Refinitiv**: Enterprise, expensive
- **Interactive Brokers**: For trading execution
- **TD Ameritrade**: For trading execution
- **Alpaca Markets**: Free tier for paper trading

### Specialized Data
- **News**: NewsAPI, Google News, Bing News
- **Social Sentiment**: Twitter API, Reddit API (PRAW), StockTwits
- **Economic Data**: FRED (Federal Reserve), Bureau of Labor Statistics
- **Fundamental Data**: Financial Modeling Prep, IEX Cloud
- **Options Data**: CBOE, Intrinio

## Learning Resources
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [Polygon.io Docs](https://polygon.io/docs/)
- [IEX Cloud Docs](https://iexcloud.io/docs/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)

## Best Practices
- **Rate Limiting**: Respect API limits, use backoff
- **Caching**: Cache expensive API calls
- **Error Handling**: Retry with exponential backoff
- **Fallback**: Multiple providers for critical data
- **Authentication**: Secure API key storage (environment variables)
- **Data Validation**: Validate API responses
- **Logging**: Log API calls for debugging
- **Cost Monitoring**: Track API usage to avoid overages

## Integration Patterns

### REST API (Historical Data)
```python
import requests
from django.conf import settings
from django.core.cache import cache

class MarketDataAPI:
    BASE_URL = "https://www.alphavantage.co/query"

    def get_historical_prices(self, symbol: str, days: int = 30):
        # Check cache first
        cache_key = f"prices:{symbol}:{days}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Fetch from API
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact"
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Normalize and cache
            normalized = self._normalize_data(data)
            cache.set(cache_key, normalized, timeout=3600)  # 1 hour
            return normalized

        except requests.exceptions.RequestException as e:
            # Log error, return fallback data
            logger.error(f"API error: {e}")
            return self._get_fallback_data(symbol)

    def _normalize_data(self, raw_data):
        # Convert API format to internal format
        # "Time Series (Daily)": {"2024-01-01": {"open": "100.00", ...}}
        # → [{"date": "2024-01-01", "open": 100.00, ...}, ...]
        pass
```

### WebSocket Stream (Real-Time Data)
```python
import websockets
import json
from typing import AsyncIterator

class RealTimeDataStream:
    POLYGON_WS_URL = "wss://stream.polygon.io/stocks"

    async def stream_quotes(self, symbols: list[str]) -> AsyncIterator[dict]:
        """Stream real-time quotes for symbols."""
        uri = f"{self.POLYGON_WS_URL}?apiKey={settings.POLYGON_API_KEY}"

        async with websockets.connect(uri) as websocket:
            # Subscribe to symbols
            await websocket.send(json.dumps({
                "action": "subscribe",
                "params": f"T.{','.join(symbols)}"
            }))

            # Stream messages
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                # Yield only relevant events
                if data.get("ev") == "T":  # Trade event
                    yield {
                        "symbol": data["sym"],
                        "price": data["p"],
                        "volume": data["v"],
                        "timestamp": data["t"]
                    }
```

### Background Tasks (Periodic Updates)
```python
from dramatiq import actor
import requests

@actor
def update_market_data(symbols: list[str]):
    """Background task to update market data."""
    for symbol in symbols:
        # Fetch latest data
        data = MarketDataAPI().get_quote(symbol)

        # Update database
        update_quote_in_db(symbol, data)

        # Cache for UI
        cache.set(f"quote:{symbol}", data, timeout=60)
```

## Django Integration

### Settings Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ...
    "data_providers",
]

# API Keys (from environment)
ALPHA_VANTAGE_API_KEY = env("ALPHA_VANTAGE_API_KEY")
POLYGON_API_KEY = env("POLYGON_API_KEY")
TWITTER_BEARER_TOKEN = env("TWITTER_BEARER_TOKEN")
REDDIT_CLIENT_ID = env("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = env("REDDIT_CLIENT_SECRET")

# Rate Limits
DATA_PROVIDER_RATE_LIMIT = "100/minute"
```

### Management Commands
```python
# management/commands/fetch_market_data.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Fetch latest market data from API"

    def handle(self, *args, **options):
        symbols = ["AAPL", "MSFT", "GOOGL"]
        api = MarketDataAPI()

        for symbol in symbols:
            data = api.get_quote(symbol)
            self.stdout.write(f"{symbol}: ${data['price']}")
```

## Testing Data Providers

### Mock API Responses
```python
import pytest
from unittest.mock import patch, Mock
from data_providers.apis import MarketDataAPI

@pytest.fixture
def mock_api_response():
    return {
        "Global Quote": {
            "01. symbol": "AAPL",
            "05. price": "150.25",
            "09. change": "2.50"
        }
    }

@patch('requests.get')
def test_get_quote(mock_get, mock_api_response):
    # Mock API response
    mock_get.return_value.json.return_value = mock_api_response

    # Test
    api = MarketDataAPI()
    quote = api.get_quote("AAPL")

    assert quote["symbol"] == "AAPL"
    assert quote["price"] == 150.25
```

### Integration Tests
```python
@pytest.mark.integration
def test_real_api_call():
    """Test real API (only run when API key available)."""
    if not settings.ALPHA_VANTAGE_API_KEY:
        pytest.skip("No API key configured")

    api = MarketDataAPI()
    data = api.get_quote("AAPL")

    assert "symbol" in data
    assert "price" in data
```

## Error Handling

### Retry with Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(symbol: str):
    """Fetch with exponential backoff retry."""
    try:
        return MarketDataAPI().get_quote(symbol)
    except requests.exceptions.RequestException as e:
        logger.error(f"Fetch failed for {symbol}: {e}")
        raise
```

### Fallback Providers
```python
class FallbackMarketDataAPI:
    """Try multiple providers until one works."""

    def __init__(self):
        self.providers = [
            AlphaVantageAPI(),
            PolygonAPI(),
            YahooFinanceAPI()
        ]

    def get_quote(self, symbol: str):
        for provider in self.providers:
            try:
                data = provider.get_quote(symbol)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"{provider.__class__} failed: {e}")
                continue

        # All failed
        raise DataProviderError("All providers failed")
```

## Cost Optimization

### Caching Strategy
```python
from django.core.cache import cache
from datetime import timedelta

class CachedMarketDataAPI:
    """Wrap API with aggressive caching."""

    def get_quote(self, symbol: str):
        cache_key = f"quote:{symbol}"

        # Check cache (30 seconds for real-time)
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Fetch from API
        data = self._fetch_from_api(symbol)

        # Cache with short TTL
        cache.set(cache_key, data, timeout=30)
        return data

    def get_historical(self, symbol: str, days: int):
        cache_key = f"historical:{symbol}:{days}"

        # Check cache (1 hour for historical)
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Fetch from API
        data = self._fetch_historical(symbol, days)

        # Cache with longer TTL
        cache.set(cache_key, data, timeout=3600)
        return data
```

### Request Batching
```python
def batch_fetch_quotes(symbols: list[str]) -> dict[str, dict]:
    """Fetch multiple quotes efficiently."""
    results = {}

    # Use bulk API if available
    if len(symbols) > 10:
        results = AlphaVantageAPI().get_batch_quotes(symbols)
    else:
        # Parallel requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(api.get_quote, symbol): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    logger.error(f"Failed to fetch {symbol}: {e}")

    return results
```

## Context for FinanceHub
**Relevance:** High - Core platform functionality depends on market data

**Integration Points:**
- **Trading Engine**: Real-time quotes for order execution
- **Portfolio Tracking**: Current prices for P&L calculation
- **Charts**: Historical price data for visualization
- **Screeners**: Market data for stock screening
- **News Feed**: News API for sentiment analysis
- **Social Sentiment**: Twitter/Reddit APIs for sentiment

**Current Implementation:**
- Alpha Vantage for historical data
- Polygon.io for real-time WebSocket streams
- NewsAPI for news sentiment
- Twitter API (tweepy) for social sentiment
- Reddit API (praw) for social sentiment

**Usage:**
- Linus: Backend API integration
- Turing: WebSocket client in frontend
- Charo: API key security review
- Karen: API monitoring, rate limiting

**Security:**
- Never commit API keys to git
- Use environment variables for secrets
- Rotate API keys regularly
- Monitor API usage for anomalies
- Implement rate limiting to prevent overages

**Updates:**
- WebSocket subscriptions for real-time data
- Webhook support for price alerts
- Batch API calls for efficiency
- Fallback providers for redundancy

**Notes:**
- Free tiers have strict rate limits
- Real-time data requires paid subscriptions
- Cache aggressively to reduce costs
- Monitor usage to avoid bill shocks
- Test with paper trading before live data
