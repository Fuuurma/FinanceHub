"""
Django management command to test Finnhub integration
Fetches sample news and technical indicators
"""

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from data.data_providers.finnHub.scraper import FinnhubScraper
from assets.models.asset import Asset
from investments.models.news import NewsArticle
from investments.models.technical_indicators import TechnicalIndicator
from investments.models.data_provider import DataProvider


class Command(BaseCommand):
    help = "Test Finnhub integration by fetching news and technical indicators"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="AAPL",
            help="Symbol to fetch data for (default: AAPL)",
        )
        parser.add_argument("--news", action="store_true", help="Fetch news articles")
        parser.add_argument(
            "--indicators", action="store_true", help="Fetch technical indicators"
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        self.stdout.write(f"Testing Finnhub integration for {symbol}...\n")

        # Check API key
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key or api_key == "1234":
            self.stdout.write(
                "ERROR: FINNHUB_API_KEY not set or invalid. Please set in .env file.\n"
            )
            return

        # Get or create data provider
        provider, _ = DataProvider.objects.get_or_create(
            name="finnhub",
            defaults={
                "display_name": "Finnhub",
                "api_key": api_key,
                "is_active": True,
            },
        )

        # Get asset
        asset = Asset.objects.filter(ticker__iexact=symbol).first()
        if not asset:
            self.stdout.write(f"ERROR: Asset {symbol} not found in database\n")
            return

        scraper = FinnhubScraper()

        # Fetch news if requested
        if options["news"]:
            self.stdout.write(f"\n=== Fetching news for {symbol} ===\n")
            self.fetch_news(scraper, asset, provider)

        # Fetch technical indicators if requested
        if options["indicators"]:
            self.stdout.write(f"\n=== Fetching technical indicators for {symbol} ===\n")
            self.fetch_indicators(scraper, asset, provider)

        self.stdout.write("\n✅ Finnhub integration test complete!\n")

    def fetch_news(self, scraper, asset, provider):
        """Fetch and save news articles"""
        try:
            # Get news from the past day
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)

            news_data = scraper.get_company_news(
                symbol=asset.ticker,
                start=start_time.strftime("%Y-%m-%d"),
                end=end_time.strftime("%Y-%m-%d"),
            )

            if not news_data:
                self.stdout.write("  No news found\n")
                return

            count = 0
            for article in news_data[:10]:
                # Simple sentiment analysis
                headline = article.get("headline", "")
                sentiment = "neutral"
                sentiment_score = Decimal("0")

                positive_words = ["gain", "rise", "growth", "profit", "bull", "upgrade"]
                negative_words = [
                    "loss",
                    "fall",
                    "drop",
                    "decline",
                    "bear",
                    "downgrade",
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

                # Create news article
                NewsArticle.objects.update_or_create(
                    url=article.get("url", ""),
                    defaults={
                        "title": headline,
                        "description": article.get("summary", "")[:5000],
                        "source": article.get("source", "Finnhub"),
                        "author": article.get("author", ""),
                        "published_at": datetime.fromtimestamp(
                            article.get("datetime", 0)
                        ),
                        "sentiment": sentiment,
                        "sentiment_score": sentiment_score,
                        "related_symbols": [asset.ticker],
                        "category": "company",
                    },
                )
                count += 1

            self.stdout.write(f"  ✓ Saved {count} news articles\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error fetching news: {e}\n")

    def fetch_indicators(self, scraper, asset, provider):
        """Fetch and save technical indicators"""
        try:
            # Fetch SMA
            self.stdout.write("  Fetching SMA...\n")
            sma_data = scraper.get_technical_indicators(
                symbol=asset.ticker, indicator="sma", resolution="1d", period=20
            )

            if sma_data and "sma" in sma_data:
                for item in sma_data["sma"][:5]:
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    value = Decimal(str(item.get("v", 0)))

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="sma",
                        timeframe="1d",
                        timestamp=timestamp,
                        defaults={
                            "value": value,
                            "signal": self.calculate_sma_signal(asset, value),
                            "source": provider,
                        },
                    )
                self.stdout.write(f"    ✓ Saved 5 SMA values\n")

            # Fetch RSI
            self.stdout.write("  Fetching RSI...\n")
            rsi_data = scraper.get_technical_indicators(
                symbol=asset.ticker, indicator="rsi", resolution="1d", period=14
            )

            if rsi_data and "rsi" in rsi_data:
                for item in rsi_data["rsi"][:5]:
                    timestamp = datetime.fromtimestamp(item.get("t", 0))
                    value = Decimal(str(item.get("v", 0)))

                    signal = "neutral"
                    if value > 70:
                        signal = "sell"
                    elif value < 30:
                        signal = "buy"

                    TechnicalIndicator.objects.update_or_create(
                        asset=asset,
                        indicator_type="rsi",
                        timeframe="1d",
                        timestamp=timestamp,
                        defaults={
                            "value": value,
                            "signal": signal,
                            "source": provider,
                        },
                    )
                self.stdout.write(f"    ✓ Saved 5 RSI values\n")

            self.stdout.write("  ✓ Technical indicators saved\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error fetching indicators: {e}\n")

    def calculate_sma_signal(self, asset, current_sma: Decimal) -> str:
        """Calculate trading signal based on SMA"""
        if asset.last_price and current_sma:
            if asset.last_price > current_sma:
                return "buy"
            else:
                return "sell"
        return "neutral"
