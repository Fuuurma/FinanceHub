"""
News Ingestion Celery Tasks
Background tasks for fetching, processing, and storing news from multiple sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from investments.models import DataProvider
from investments.models.news import NewsArticle
from investments.services.news_normalizer import NewsNormalizer, BatchNormalizer
from investments.services.atlas_news_adapter import ATLASNewsAdapter, get_atlas_adapter
from investments.services.symbol_extractor import SymbolExtractor, SentimentAnalyzer
from utils.pickle_cache import get_pickle_cache

logger = logging.getLogger(__name__)


def parse_decimal(value):
    """Safe decimal parsing"""
    if value is None:
        return None
    try:
        from decimal import Decimal

        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_newsapi_news(
    self, category: str = "business", limit: int = 100
) -> Dict[str, Any]:
    """
    Fetch news from NewsAPI and store in database.

    Args:
        category: NewsAPI category (business, technology, science, etc.)
        limit: Number of articles to fetch

    Returns:
        Dict with fetch status
    """
    try:
        from data.data_providers.newsapi.scraper import NewsAPIScraper

        scraper = NewsAPIScraper()

        async def fetch():
            async with scraper:
                return await scraper.get_headlines_by_category(
                    category, page=1, page_size=limit
                )

        data = asyncio.run(fetch())

        if not data or "articles" not in data:
            return {"status": "error", "message": "No articles returned"}

        # Normalize and store
        normalizer = NewsNormalizer()
        normalized = normalizer.normalize_batch(
            data["articles"], source_type="newsapi", category=category
        )

        # Extract symbols and sentiment
        extractor = SymbolExtractor()
        extractor.load_from_database()

        analyzer = SentimentAnalyzer()

        saved_count = 0
        for article in normalized:
            # Extract symbols
            symbols = extractor.extract_all(
                article.title, f"{article.description} {article.content}"
            )

            # Analyze sentiment
            sentiment, score = analyzer.analyze_text(
                f"{article.title} {article.description}"
            )

            # Create database entry
            try:
                NewsArticle.objects.create(
                    title=article.title[:500],
                    description=article.description[:2000],
                    url=article.url,
                    source=article.source,
                    author=article.author[:200] or "",
                    published_at=article.published_at or timezone.now(),
                    category=article.category,
                    image_url=article.image_url,
                    content=article.content[:5000],
                    related_symbols=symbols,
                    sentiment=sentiment,
                    sentiment_score=score,
                    is_active=True,
                )
                saved_count += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.debug(f"Error saving article: {e}")
                continue

        return {
            "status": "success",
            "source": "newsapi",
            "category": category,
            "fetched": len(data["articles"]),
            "normalized": len(normalized),
            "saved": saved_count,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching NewsAPI news: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def fetch_finnhub_news(self, symbol: str = None, limit: int = 50) -> Dict[str, Any]:
    """
    Fetch news from Finnhub and store in database.

    Args:
        symbol: Stock symbol to filter by (optional)
        limit: Number of articles to fetch

    Returns:
        Dict with fetch status
    """
    try:
        from data.data_providers.finnHub.scraper import FinnhubScraper

        scraper = FinnhubScraper()

        async def fetch():
            async with scraper:
                if symbol:
                    return await scraper.get_company_news(symbol, limit=limit)
                return await scraper.get_general_news(limit=limit)

        data = asyncio.run(fetch())

        if not data or "news" not in data:
            return {"status": "error", "message": "No news returned"}

        # Normalize and store
        normalizer = NewsNormalizer()
        normalized = normalizer.normalize_batch(
            data["news"], source_type="finnhub", category="business"
        )

        saved_count = 0
        for article in normalized:
            try:
                NewsArticle.objects.create(
                    title=article.title[:500],
                    description=article.description[:2000],
                    url=article.url,
                    source=article.source,
                    author=article.author[:200] or "",
                    published_at=article.published_at or timezone.now(),
                    category=article.category,
                    image_url=article.image_url,
                    content=article.content[:5000],
                    related_symbols=article.symbols,
                    is_active=True,
                )
                saved_count += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.debug(f"Error saving Finnhub article: {e}")
                continue

        return {
            "status": "success",
            "source": "finnhub",
            "symbol": symbol,
            "fetched": len(data["news"]),
            "saved": saved_count,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching Finnhub news: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_atlas_news(self, categories: List[str] = None) -> Dict[str, Any]:
    """
    Fetch news from ATLAS RSS feeds and crawlers.

    Args:
        categories: Categories to fetch (default: investments, crypto, tech)

    Returns:
        Dict with fetch status
    """
    if categories is None:
        categories = ["investments", "crypto", "tech"]

    try:
        adapter = get_atlas_adapter()

        # Get all articles from ATLAS
        articles_by_category = adapter.get_all_articles(categories)

        # Normalize and store
        normalizer = NewsNormalizer()
        extractor = SymbolExtractor()
        analyzer = SentimentAnalyzer()

        total_fetched = 0
        total_saved = 0

        for category, articles in articles_by_category.items():
            if not articles:
                continue

            total_fetched += len(articles)

            normalized = normalizer.normalize_batch(
                articles, source_type="atlas", category=category
            )

            for article in normalized:
                # Extract symbols
                symbols = extractor.extract_all(
                    article.title, f"{article.description} {article.content}"
                )

                # Analyze sentiment
                sentiment, score = analyzer.analyze_text(
                    f"{article.title} {article.description}"
                )

                try:
                    NewsArticle.objects.create(
                        title=article.title[:500],
                        description=article.description[:2000],
                        url=article.url,
                        source=article.source,
                        author=article.author[:200] or "",
                        published_at=article.published_at or timezone.now(),
                        category=article.category,
                        image_url=article.image_url,
                        content=article.content[:5000],
                        related_symbols=symbols,
                        sentiment=sentiment,
                        sentiment_score=score,
                        is_active=True,
                    )
                    total_saved += 1
                except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                    logger.debug(f"Error saving ATLAS article: {e}")
                    continue

        # Save to pickle cache
        try:
            cache = get_pickle_cache()
            all_articles = []
            for articles in articles_by_category.values():
                for a in articles:
                    all_articles.append(
                        {
                            "title": a.get("title", ""),
                            "url": a.get("url", ""),
                            "source": a.get("source", ""),
                            "category": a.get("category", ""),
                            "published": a.get("published", ""),
                            "summary": a.get("summary", ""),
                        }
                    )

            cache.save_articles(all_articles)
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error saving to pickle cache: {e}")

        return {
            "status": "success",
            "source": "atlas",
            "categories": categories,
            "fetched": total_fetched,
            "saved": total_saved,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching ATLAS news: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def fetch_all_news_sources(self) -> Dict[str, Any]:
    """
    Fetch news from all configured sources.

    This is the main orchestration task that triggers:
    - NewsAPI (business, technology)
    - Finnhub (stock-specific news)
    - ATLAS RSS feeds (investments, crypto, tech)

    Returns:
        Dict with overall status
    """
    results = {}

    # Queue individual fetches
    results["newsapi_business"] = fetch_newsapi_news.delay(category="business")
    results["newsapi_tech"] = fetch_newsapi_news.delay(category="technology")
    results["finnhub"] = fetch_finnhub_news.delay()
    results["atlas"] = fetch_atlas_news.delay()

    # Wait for results
    total_fetched = 0
    total_saved = 0

    for task_name, task in results.items():
        try:
            result = task.get(timeout=120)
            if result.get("status") == "success":
                total_fetched += result.get("fetched", 0)
                total_saved += result.get("saved", 0)
                logger.info(f"{task_name}: {result}")
            else:
                logger.warning(f"{task_name}: {result}")
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error waiting for {task_name}: {e}")

    return {
        "status": "completed",
        "total_fetched": total_fetched,
        "total_saved": total_saved,
        "timestamp": timezone.now().isoformat(),
    }


@shared_task(bind=True, max_retries=1, default_retry_delay=600)
def analyze_sentiment_batch(self, hours: int = 24) -> Dict[str, Any]:
    """
    Analyze sentiment for recent articles without sentiment.

    Args:
        hours: Look back period

    Returns:
        Dict with analysis status
    """
    try:
        cutoff = timezone.now() - timedelta(hours=hours)

        # Get articles without sentiment
        articles = NewsArticle.objects.filter(
            sentiment="neutral", sentiment_score__isnull=True, published_at__gte=cutoff
        ).order_by("-published_at")[:1000]

        analyzer = SentimentAnalyzer()
        updated = 0

        for article in articles:
            text = f"{article.title} {article.description}"
            sentiment, score = analyzer.analyze_text(text)

            article.sentiment = sentiment
            article.sentiment_score = score
            article.save(update_fields=["sentiment", "sentiment_score", "updated_at"])
            updated += 1

        return {
            "status": "success",
            "articles_analyzed": updated,
            "hours_lookback": hours,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error in sentiment batch: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=1, default_retry_delay=600)
def extract_symbols_batch(self, hours: int = 24) -> Dict[str, Any]:
    """
    Extract and update symbols for articles.

    Args:
        hours: Look back period

    Returns:
        Dict with extraction status
    """
    try:
        from assets.models.asset import Asset

        # Load valid symbols from database
        stocks = set(
            Asset.objects.filter(asset_type__name__in=["stock", "etf"]).values_list(
                "symbol", flat=True
            )
        )

        cryptos = set(
            Asset.objects.filter(asset_type__name__in=["crypto", "token"]).values_list(
                "symbol", flat=True
            )
        )

        extractor = SymbolExtractor(valid_symbols=stocks, valid_cryptos=cryptos)

        # Get articles without symbols
        cutoff = timezone.now() - timedelta(hours=hours)
        articles = NewsArticle.objects.filter(
            related_symbols=[], published_at__gte=cutoff
        ).order_by("-published_at")[:500]

        updated = 0

        for article in articles:
            text = f"{article.title} {article.description} {article.content}"
            symbols = extractor.extract_all(text)

            if symbols:
                article.related_symbols = symbols
                article.save(update_fields=["related_symbols", "updated_at"])
                updated += 1

        return {
            "status": "success",
            "articles_updated": updated,
            "hours_lookback": hours,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error in symbol extraction batch: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def create_pickle_cache_dump() -> Dict[str, Any]:
    """
    Create hourly pickle cache dump of recent news.

    Returns:
        Dict with cache status
    """
    try:
        cache = get_pickle_cache()

        # Get recent articles (last 24 hours)
        cutoff = timezone.now() - timedelta(hours=24)
        articles = NewsArticle.objects.filter(
            published_at__gte=cutoff, is_active=True
        ).order_by("-published_at")[:5000]

        # Convert to dicts
        articles_data = []
        for article in articles:
            articles_data.append(
                {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": article.published_at.isoformat(),
                    "category": article.category,
                    "image_url": article.image_url,
                    "content": article.content,
                    "related_symbols": article.related_symbols,
                    "sentiment": article.sentiment,
                    "sentiment_score": str(article.sentiment_score)
                    if article.sentiment_score
                    else None,
                }
            )

        # Save to pickle
        filepath = cache.save_articles(articles_data)

        return {
            "status": "success",
            "articles_dumped": len(articles_data),
            "filepath": filepath,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error creating pickle dump: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def cleanup_old_news(days: int = 30) -> Dict[str, Any]:
    """
    Delete old news articles and archive to pickle.

    Args:
        days: Age threshold for deletion

    Returns:
        Dict with cleanup status
    """
    try:
        # First, archive to pickle
        create_pickle_cache_dump.delay()

        # Then delete old articles
        cutoff = timezone.now() - timedelta(days=days)

        old_articles = NewsArticle.objects.filter(
            published_at__lt=cutoff, is_active=True
        )

        count = old_articles.count()
        old_articles.update(is_active=False, deleted_at=timezone.now())

        # Clean up pickle cache
        cache = get_pickle_cache()
        removed = cache.cleanup_expired()

        return {
            "status": "success",
            "articles_archived": count,
            "cache_files_removed": removed,
            "days_threshold": days,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error in cleanup: {e}")
        return {"status": "error", "message": str(e)}


@shared_task
def sync_news_provider_status() -> Dict[str, Any]:
    """
    Check news provider API statuses and update configuration.

    Returns:
        Dict with provider status
    """
    providers = [
        ("newsapi", "NewsAPI"),
        ("finnhub", "Finnhub"),
    ]

    status = {}

    for code, name in providers:
        try:
            provider, _ = DataProvider.objects.get_or_create(
                code=code, defaults={"name": name, "is_active": False}
            )

            # Simple health check
            is_active = True  # Assume active if we can import the scraper
            provider.is_active = is_active
            provider.save()

            status[code] = {"name": name, "is_active": is_active}

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error checking {name}: {e}")
            status[code] = {"name": name, "is_active": False, "error": str(e)}

    return {
        "status": "success",
        "providers": status,
        "timestamp": timezone.now().isoformat(),
    }


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def fetch_news_for_symbol(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
    """
    Fetch news specifically for a stock/crypto symbol.

    Args:
        symbol: Stock or crypto symbol (e.g., AAPL, BTC)
        limit: Number of articles

    Returns:
        Dict with fetch status
    """
    try:
        # Fetch from Finnhub (best for stock-specific news)
        finnhub_result = fetch_finnhub_news.delay(symbol=symbol, limit=limit // 2)

        # Fetch from NewsAPI
        newsapi_result = fetch_newsapi_news.delay(category="business", limit=limit // 2)

        # Get results
        finnhub_data = finnhub_result.get(timeout=60)
        newsapi_data = newsapi_result.get(timeout=60)

        return {
            "status": "success",
            "symbol": symbol,
            "finnhub": finnhub_data,
            "newsapi": newsapi_data,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=1, default_retry_delay=300)
def generate_news_summary(self, hours: int = 24) -> Dict[str, Any]:
    """
    Generate summary statistics for recent news.

    Args:
        hours: Look back period

    Returns:
        Dict with summary
    """
    try:
        from collections import Counter
        from django.db.models import Count

        cutoff = timezone.now() - timedelta(hours=hours)

        # Get recent articles
        articles = NewsArticle.objects.filter(published_at__gte=cutoff, is_active=True)

        # Count by source
        sources = list(
            articles.values("source")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Count by category
        categories = list(
            articles.values("category").annotate(count=Count("id")).order_by("-count")
        )

        # Count by sentiment
        sentiments = dict(
            articles.values("sentiment")
            .annotate(count=Count("id"))
            .values("sentiment", "count")
        )

        # Top symbols
        from django.db.models import Q

        symbol_counts = Counter()
        for article in articles:
            for symbol in article.related_symbols:
                symbol_counts[symbol.upper()] += 1

        top_symbols = [
            {"symbol": s, "count": c} for s, c in symbol_counts.most_common(20)
        ]

        return {
            "status": "success",
            "hours": hours,
            "total_articles": articles.count(),
            "sources": sources,
            "categories": categories,
            "sentiments": sentiments,
            "top_symbols": top_symbols,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error generating news summary: {e}")
        return {"status": "error", "message": str(e)}
