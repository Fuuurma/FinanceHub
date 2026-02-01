"""
Django management command to test NewsAPI + ATLAS integration
Fetches news from multiple sources and tests the normalization pipeline
"""

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from investments.services.news_normalizer import NewsNormalizer, BatchNormalizer
from investments.services.atlas_news_adapter import ATLASNewsAdapter, get_atlas_adapter
from investments.services.symbol_extractor import SymbolExtractor, SentimentAnalyzer
from investments.models.news import NewsArticle
from investments.models.data_provider import DataProvider
from utils.pickle_cache import get_pickle_cache


class Command(BaseCommand):
    help = "Test NewsAPI + ATLAS integration with full pipeline"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="AAPL",
            help="Symbol to fetch news for (default: AAPL)",
        )
        parser.add_argument("--all", action="store_true", help="Test all news sources")
        parser.add_argument(
            "--newsapi", action="store_true", help="Test NewsAPI source"
        )
        parser.add_argument(
            "--finnhub", action="store_true", help="Test Finnhub source"
        )
        parser.add_argument(
            "--atlas", action="store_true", help="Test ATLAS RSS adapter"
        )
        parser.add_argument(
            "--normalize",
            action="store_true",
            help="Test normalization pipeline",
        )
        parser.add_argument(
            "--sentiment",
            action="store_true",
            help="Test sentiment analysis",
        )
        parser.add_argument(
            "--symbols",
            action="store_true",
            help="Test symbol extraction",
        )
        parser.add_argument("--cache", action="store_true", help="Test pickle cache")
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of articles to fetch (default: 10)",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]
        count = options["count"]

        self.stdout.write(f"Testing NewsAPI + ATLAS integration for {symbol}...\n")

        # Check API keys
        newsapi_key = os.getenv("NEWSAPI_API_KEY")
        finnhub_key = os.getenv("FINNHUB_API_KEY")

        # Get or create data provider
        provider, _ = DataProvider.objects.get_or_create(
            name="newsapi",
            defaults={
                "display_name": "NewsAPI",
                "api_key": newsapi_key or "",
                "is_active": True,
            },
        )

        # Run tests based on flags
        if options["all"] or not any(
            [
                options["newsapi"],
                options["finnhub"],
                options["atlas"],
                options["normalize"],
                options["sentiment"],
                options["symbols"],
                options["cache"],
            ]
        ):
            # Run all tests by default
            self.test_newsapi(symbol, count, newsapi_key)
            self.test_finnhub(symbol, count, finnhub_key)
            self.test_atlas_adapter(symbol, count)
            self.test_normalization(symbol, count)
            self.test_sentiment_analysis()
            self.test_symbol_extraction()
            self.test_pickle_cache()
        else:
            if options["newsapi"]:
                self.test_newsapi(symbol, count, newsapi_key)
            if options["finnhub"]:
                self.test_finnhub(symbol, count, finnhub_key)
            if options["atlas"]:
                self.test_atlas_adapter(symbol, count)
            if options["normalize"]:
                self.test_normalization(symbol, count)
            if options["sentiment"]:
                self.test_sentiment_analysis()
            if options["symbols"]:
                self.test_symbol_extraction()
            if options["cache"]:
                self.test_pickle_cache()

        self.stdout.write("\n✅ NewsAPI + ATLAS integration test complete!\n")

    def test_newsapi(self, symbol, count, api_key):
        """Test NewsAPI integration"""
        self.stdout.write(f"\n=== Testing NewsAPI for {symbol} ===\n")

        if not api_key or api_key == "1234":
            self.stdout.write("  ⚠ SKIP: NEWSAPI_API_KEY not set or invalid\n")
            return

        try:
            from data.data_providers.newsapi.scraper import NewsAPIScraper

            scraper = NewsAPIScraper()

            # Fetch business and technology news
            news_data = scraper.get_everything(
                query=symbol,
                from_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                language="en",
                sort_by="publishedAt",
            )

            if not news_data or "articles" not in news_data:
                self.stdout.write("  ⚠ No articles found\n")
                return

            articles = news_data["articles"][:count]
            self.stdout.write(f"  ✓ Fetched {len(articles)} articles\n")

            # Process first few articles
            for i, article in enumerate(articles[:3]):
                title = article.get("title", "No title")
                self.stdout.write(f"    {i + 1}. {title[:50]}...")
                self.stdout.write(
                    f"       Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                )

            self.stdout.write(f"  ✓ NewsAPI test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_finnhub(self, symbol, count, api_key):
        """Test Finnhub news integration"""
        self.stdout.write(f"\n=== Testing Finnhub News for {symbol} ===\n")

        if not api_key or api_key == "1234":
            self.stdout.write("  ⚠ SKIP: FINNHUB_API_KEY not set or invalid\n")
            return

        try:
            from data.data_providers.finnHub.scraper import FinnhubScraper

            scraper = FinnhubScraper()

            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)

            news_data = scraper.get_company_news(
                symbol=symbol,
                start=start_time.strftime("%Y-%m-%d"),
                end=end_time.strftime("%Y-%m-%d"),
            )

            if not news_data:
                self.stdout.write("  ⚠ No articles found\n")
                return

            articles = news_data[:count]
            self.stdout.write(f"  ✓ Fetched {len(articles)} articles\n")

            for i, article in enumerate(articles[:3]):
                title = article.get("headline", "No title")
                self.stdout.write(f"    {i + 1}. {title[:50]}...")
                self.stdout.write(
                    f"       Source: {article.get('source', 'Unknown')}\n"
                )

            self.stdout.write(f"  ✓ Finnhub news test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_atlas_adapter(self, symbol, count):
        """Test ATLAS RSS adapter"""
        self.stdout.write(f"\n=== Testing ATLAS RSS Adapter ===\n")

        try:
            adapter = get_atlas_adapter()

            # Fetch RSS feeds
            feeds = adapter.fetch_all_rss_feeds()
            self.stdout.write(f"  ✓ Fetched {len(feeds)} RSS feeds\n")

            if feeds:
                # Show first article
                first_feed = list(feeds.keys())[0]
                first_article = feeds[first_feed][0] if feeds[first_feed] else None
                if first_article:
                    self.stdout.write(
                        f"    Sample: {first_article.get('title', 'No title')[:50]}\n"
                    )

            # Test crypto crawler
            crypto_news = adapter.fetch_crypto_crawler_news()
            self.stdout.write(f"  ✓ Fetched {len(crypto_news)} crypto articles\n")

            self.stdout.write(f"  ✓ ATLAS adapter test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_normalization(self, symbol, count):
        """Test news normalization pipeline"""
        self.stdout.write(f"\n=== Testing Normalization Pipeline ===\n")

        try:
            normalizer = NewsNormalizer()
            batch_normalizer = BatchNormalizer(normalizer)

            # Create sample articles from different sources
            sample_articles = [
                {
                    "title": f"{symbol} stock jumps 5% after earnings report",
                    "description": "The tech giant reported better than expected quarterly results",
                    "url": "https://example.com/article1",
                    "source": "NewsAPI",
                    "published_at": datetime.now().isoformat(),
                    "author": "John Doe",
                },
                {
                    "headline": f"{symbol} announces new product line",
                    "summary": "The company unveiled innovative solutions today",
                    "url": "https://example.com/article2",
                    "source": "Finnhub",
                    "datetime": datetime.now().timestamp(),
                },
                {
                    "title": f"{symbol} price analysis and market trends",
                    "content": "Detailed analysis of recent market movements",
                    "link": "https://example.com/article3",
                    "pubDate": datetime.now().isoformat(),
                    "source": {"name": "ATLAS RSS"},
                },
            ]

            normalized = normalizer.normalize_batch(sample_articles, "mixed", "general")
            self.stdout.write(
                f"  ✓ Normalized {len(normalized)} articles from {len(sample_articles)} sources\n"
            )

            for i, article in enumerate(normalized[:2]):
                self.stdout.write(
                    f"    {i + 1}. {article.title[:40]}... (source: {article.source})\n"
                )

            self.stdout.write(f"  ✓ Normalization test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        self.stdout.write(f"\n=== Testing Sentiment Analysis ===\n")

        try:
            analyzer = SentimentAnalyzer()

            test_headlines = [
                f"AAPL stock surges 10% on record earnings",
                f"Market crashes as fears grow over recession",
                f"Company announces quarterly results",
            ]

            for headline in test_headlines:
                sentiment, score = analyzer.analyze_text(headline)
                self.stdout.write(f'  • "{headline[:40]}..."\n')
                self.stdout.write(f"    Score: {score:.3f}, Sentiment: {sentiment}\n")

            self.stdout.write(f"  ✓ Sentiment analysis test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_symbol_extraction(self):
        """Test symbol extraction"""
        self.stdout.write(f"\n=== Testing Symbol Extraction ===\n")

        try:
            extractor = SymbolExtractor()

            test_texts = [
                "$AAPL and $GOOGL lead market gains today",
                "Tesla stock rises on new vehicle announcements",
                "Bitcoin and Ethereum surge in early trading",
                "Microsoft (MSFT) reports strong Q4 results",
            ]

            for text in test_texts:
                symbols = extractor.extract_all(text)
                self.stdout.write(f'  • "{text[:50]}..."\n')
                self.stdout.write(
                    f"    Found symbols: {', '.join(symbols) if symbols else 'None'}\n"
                )

            self.stdout.write(f"  ✓ Symbol extraction test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_pickle_cache(self):
        """Test pickle cache functionality"""
        self.stdout.write(f"\n=== Testing Pickle Cache ===\n")

        try:
            cache = get_pickle_cache()

            # Create test data
            test_articles = [
                {
                    "title": "Test Article 1",
                    "source": "NewsAPI",
                    "sentiment": "positive",
                    "category": "technology",
                    "related_symbols": ["AAPL"],
                },
                {
                    "title": "Test Article 2",
                    "source": "Finnhub",
                    "sentiment": "negative",
                    "category": "finance",
                    "related_symbols": ["GOOGL"],
                },
            ]

            # Save to cache (without timestamp parameter)
            filepath = cache.save_articles(test_articles)
            self.stdout.write(f"  ✓ Saved {len(test_articles)} articles to cache\n")

            # Load from cache (uses latest file)
            loaded = cache.load_articles()
            self.stdout.write(f"  ✓ Loaded {len(loaded)} articles from cache\n")

            # Get stats
            stats = cache.get_cache_stats()
            self.stdout.write(f"  ✓ Cache stats: {stats}\n")

            # Export to JSON
            json_path = cache.export_to_json()
            self.stdout.write(f"  ✓ Exported to JSON: {json_path}\n")

            # Clean up test data
            cache.cleanup_expired()
            self.stdout.write(f"  ✓ Cleaned up test data\n")

            self.stdout.write(f"  ✓ Pickle cache test passed\n")

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(f"  ✗ Error: {e}\n")
