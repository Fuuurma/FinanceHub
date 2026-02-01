"""
Finnhub Data Fetch Tasks
Celery tasks for fetching news, technical indicators, and real-time data from Finnhub
"""

from celery import shared_task
from datetime import datetime, timedelta
from decimal import Decimal
import os

from data.data_providers.finnHub.scraper import FinnhubScraper
from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from investments.models.news import NewsArticle
from investments.models.technical_indicators import TechnicalIndicator
from investments.models.data_provider import DataProvider
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


@shared_task(name="finnhub.fetch_technical_indicators")
def fetch_technical_indicators(
    symbol: str, indicator: str = "sma", timeframe: str = "1d", time_period: int = 20
):
    """
    Fetch and save technical indicators from Finnhub

    Args:
        symbol: Stock symbol (e.g., "AAPL")
        indicator: Indicator type (sma, ema, rsi, macd, bb, etc.)
        timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
        time_period: Period for indicators (e.g., 20 for SMA20, 14 for RSI)
    """
    try:
        scraper = FinnhubScraper()

        # Get asset
        asset = Asset.objects.filter(ticker__iexact=symbol).first()
        if not asset:
            logger.warning(f"Asset {symbol} not found")
            return

        # Get data provider
        provider = DataProvider.objects.filter(name="finnhub").first()

        # Fetch indicator data
        if indicator == "sma":
            data = scraper.get_technical_indicators(
                symbol=symbol, indicator="sma", resolution=timeframe, period=time_period
            )

            # Save SMA values
            if data and "sma" in data:
                for item in data["sma"][:20]:  # Save last 20 values
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    value = Decimal(str(item.get("v", 0)))

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="sma",
                        timeframe=timeframe,
                        timestamp=timestamp,
                        defaults={
                            "value": value,
                            "signal": _calculate_sma_signal(asset, value),
                            "source": provider,
                        },
                    )
                    logger.info(f"Saved SMA for {symbol} at {timestamp}")

        elif indicator == "rsi":
            data = scraper.get_technical_indicators(
                symbol=symbol,
                indicator="rsi",
                resolution=timeframe,
                time_period=time_period,
            )

            # Save RSI values
            if data and "rsi" in data:
                for item in data["rsi"][:20]:
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    value = Decimal(str(item.get("v", 0)))

                    # Determine RSI signal
                    signal = "neutral"
                    if value > 70:
                        signal = "sell"
                    elif value > 50:
                        signal = "neutral"
                    else:
                        signal = "buy"

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="rsi",
                        timeframe=timeframe,
                        timestamp=timestamp,
                        defaults={
                            "value": value,
                            "signal": signal,
                            "source": provider,
                        },
                    )
                    logger.info(f"Saved RSI for {symbol} at {timestamp}")

        elif indicator == "macd":
            data = scraper.get_technical_indicators(
                symbol=symbol,
                indicator="macd",
                resolution=timeframe,
                fast_period=12,
                slow_period=26,
                signal_period=9,
            )

            # Save MACD values
            if data and "macd" in data:
                for i, item in enumerate(data["macd"][:20]):
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    macd_value = Decimal(str(item.get("v", 0)))
                    signal_value = (
                        Decimal(str(data.get("signal", [{}])[i].get("v", 0)))
                        if "signal" in data
                        else None
                    )

                    from utils.financial import to_decimal

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="macd",
                        timeframe=timeframe,
                        timestamp=timestamp,
                        defaults={
                            "value": macd_value,
                            "signal": "buy"
                            if signal_value and macd_value > signal_value
                            else "sell",
                            "metadata": {
                                "signal": str(to_decimal(signal_value))
                                if signal_value
                                else None,
                                "histogram": str(to_decimal(macd_value - signal_value))
                                if signal_value
                                else None,
                            },
                            "source": provider,
                        },
                    )
                    logger.info(f"Saved MACD for {symbol} at {timestamp}")

        elif indicator == "bb":
            data = scraper.get_technical_indicators(
                symbol=symbol, indicator="bb", resolution=time_period, period=20
            )

            # Save Bollinger Bands
            if data and "bb" in data:
                for i, item in enumerate(data["bb"][:20]):
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    lower_band = Decimal(str(item.get("l", 0)))
                    upper_band = Decimal(str(item.get("u", 0)))
                    middle_band = (upper_band + lower_band) / 2

                    from utils.financial import to_decimal

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="bb",
                        timeframe=timeframe,
                        timestamp=timestamp,
                        defaults={
                            "value": middle_band,
                            "metadata": {
                                "upper": str(to_decimal(upper_band)),
                                "lower": str(to_decimal(lower_band)),
                                "middle": str(to_decimal(middle_band)),
                                "bandwidth": str(to_decimal(upper_band - lower_band)),
                            },
                            "source": provider,
                        },
                    )
                    logger.info(f"Saved Bollinger Bands for {symbol} at {timestamp}")

        logger.info(f"Completed fetching {indicator} for {symbol}")
        return {"status": "success", "symbol": symbol, "indicator": indicator}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching technical indicators for {symbol}: {e}")
        return {"status": "error", "symbol": symbol, "error": str(e)}


@shared_task(name="finnhub.fetch_news_with_sentiment")
def fetch_news_with_sentiment(symbols: list = None, category: str = "general"):
    """
    Fetch news articles with sentiment analysis from Finnhub

    Args:
        symbols: List of symbols to fetch news for
        category: News category (general, forex, crypto, merger)
    """
    try:
        scraper = FinnhubScraper()

        # Default symbols if none provided
        if not symbols:
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

        # Get data provider
        provider = DataProvider.objects.filter(name="finnhub").first()

        articles_fetched = 0

        for symbol in symbols:
            try:
                # Fetch company news
                news_data = scraper.get_company_news(
                    symbol=symbol,
                    start=datetime.now() - timedelta(days=1),
                    end=datetime.now(),
                )

                for article in news_data[:10]:  # Limit to 10 most recent
                    # Parse sentiment from Finnhub data
                    sentiment = "neutral"
                    sentiment_score = Decimal("0")

                    headline = article.get("headline", "")
                    summary = article.get("summary", "")

                    # Simple sentiment analysis
                    positive_words = [
                        "gain",
                        "rise",
                        "growth",
                        "profit",
                        "bull",
                        "upgrade",
                        "beat",
                    ]
                    negative_words = [
                        "loss",
                        "fall",
                        "drop",
                        "decline",
                        "bear",
                        "downgrade",
                        "miss",
                    ]

                    positive_count = sum(
                        1 for word in positive_words if word in headline.lower()
                    )
                    negative_count = sum(
                        1 for word in negative_words if word in headline.lower()
                    )

                    if positive_count > negative_count:
                        sentiment = "positive"
                        sentiment_score = Decimal("0.5")
                    elif negative_count > positive_count:
                        sentiment = "negative"
                        sentiment_score = Decimal("-0.5")

                    # Extract related symbols
                    related_symbols = article.get("symbols", [symbol])

                    # Create news article
                    NewsArticle.objects.update_or_create(
                        url=article.get("url"),
                        defaults={
                            "title": headline,
                            "description": summary,
                            "source": article.get("source", "Finnhub"),
                            "author": article.get("author", ""),
                            "published_at": datetime.fromtimestamp(
                                article.get("datetime", 0)
                            ),
                            "sentiment": sentiment,
                            "sentiment_score": sentiment_score,
                            "related_symbols": related_symbols,
                            "category": category,
                            "image_url": article.get("image", ""),
                            "thumbnail_url": article.get("thumbnail", ""),
                        },
                    )

                    articles_fetched += 1
                    logger.info(f"Saved news: {headline[:50]}...")

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
                continue

        logger.info(f"Completed fetching news. Total articles: {articles_fetched}")
        return {"status": "success", "articles_fetched": articles_fetched}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching news: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(name="finnhub.fetch_pattern_recognition")
def fetch_pattern_recognition(symbol: str):
    """
    Fetch candlestick pattern recognition from Finnhub

    Args:
        symbol: Stock symbol (e.g., "AAPL")
    """
    try:
        scraper = FinnhubScraper()

        asset = Asset.objects.filter(ticker__iexact=symbol).first()
        if not asset:
            logger.warning(f"Asset {symbol} not found")
            return

        provider = DataProvider.objects.filter(name="finnhub").first()

        # Fetch pattern recognition data
        patterns = scraper.get_pattern_recognition(symbol=symbol)

        if patterns and "patterns" in patterns:
            for pattern in patterns["patterns"]:
                pattern_type = pattern.get("pattern", "unknown")
                timestamp = datetime.fromtimestamp(
                    pattern.get(
                        "lastTime",
                    )
                )
                signal = pattern.get("bullishbearish", "neutral")

                # Save as technical indicator
                TechnicalIndicator.objects.update_or_create(
                    asset=asset,
                    indicator_type=f"pattern_{pattern_type.lower()}",
                    timeframe="1d",
                    timestamp=timestamp,
                    defaults={
                        "value": Decimal("1"),
                        "signal": "buy"
                        if signal == "bullish"
                        else "sell"
                        if signal == "bearish"
                        else "neutral",
                        "metadata": {
                            "pattern": pattern_type,
                            "bullishbearish": signal,
                        },
                        "source": provider,
                    },
                )
                logger.info(f"Saved pattern {pattern_type} for {symbol}")

        return {"status": "success", "symbol": symbol}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching pattern recognition for {symbol}: {e}")
        return {"status": "error", "symbol": symbol, "error": str(e)}


@shared_task(name="finnhub.update_technical_indicators_batch")
def update_technical_indicators_batch(symbols: list = None, indicators: list = None):
    """
    Update technical indicators for multiple symbols

    Args:
        symbols: List of symbols to update (defaults to popular stocks)
        indicators: List of indicators to fetch (defaults to sma, rsi, macd)
    """
    if not symbols:
        symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "JPM",
            "V",
            "JNJ",
        ]

    if not indicators:
        indicators = ["sma", "rsi"]

    results = []
    for symbol in symbols:
        for indicator in indicators:
            result = fetch_technical_indicators.delay(symbol, indicator)
            results.append(result)

    return {"status": "success", "tasks_queued": len(results)}


def _calculate_sma_signal(asset: Asset, current_sma: Decimal) -> str:
    """Calculate trading signal based on SMA"""
    if asset.last_price and current_sma:
        if asset.last_price > current_sma:
            return "buy"
        else:
            return "sell"
    return "neutral"


@shared_task(name="finnhub.start_websocket_for_symbols")
def start_websocket_for_symbols(symbols: list = None):
    """
    Start WebSocket connection for real-time price updates

    This is meant to be run as a long-running Celery task
    """
    from utils.services.finnhub_websocket import FinnhubWebSocketClient
    import os

    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        logger.error("FINNHUB_API_KEY not set in environment")
        return

    # Create async event loop for WebSocket
    import asyncio

    async def run_websocket():
        client = FinnhubWebSocketClient(api_key)
        await client.connect()

        for symbol in symbols:
            await client.subscribe_quote(symbol)

        # Keep connection alive
        while client.is_connected:
            await asyncio.sleep(30)
            # Send heartbeat
            pass

    # Run in new event loop
    asyncio.run(run_websocket())

    return {"status": "success", "symbols": symbols}
