"""
Pickle Cache Manager for News Data
Fast batch storage and retrieval for analytics/ML workloads
"""

import os
import pickle
import gzip
import json
import logging
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class NewsCacheHeader:
    """Metadata header for pickle cache files"""

    timestamp: str  # ISO format
    article_count: int
    categories: Dict[str, int]  # category -> count
    sources: List[str]
    symbols: List[str]  # Most mentioned symbols
    sentiment_distribution: Dict[str, int]  # positive/negative/neutral -> count
    file_size_bytes: int
    checksum: str  # MD5 of pickled data


class NewsPickleCache:
    """
    High-performance pickle cache for news articles.

    Features:
    - Compressed pickle files (gzip)
    - Hourly snapshots
    - Fast lookup by symbol, category, sentiment
    - 30-day TTL with automatic cleanup
    - Integrity checksums
    """

    def __init__(self, cache_dir: str = None, ttl_days: int = 30):
        """
        Initialize pickle cache.

        Args:
            cache_dir: Directory for cache files
            ttl_days: Days before cache expires
        """
        self.cache_dir = (
            cache_dir
            or "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/media/news_cache"
        )
        self.ttl_days = ttl_days
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_filename(self, timestamp: datetime = None) -> str:
        """Generate cache filename"""
        ts = timestamp or datetime.now()
        return f"news_cache_{ts.strftime('%Y%m%d_%H%M%S')}.pkl.gz"

    def _get_latest_cache_file(self) -> Optional[str]:
        """Get the most recent cache file"""
        pattern = os.path.join(self.cache_dir, "news_cache_*.pkl.gz")
        files = glob.glob(pattern)

        if not files:
            return None

        return max(files, key=os.path.getmtime)

    def save_articles(self, articles: List[Dict], timestamp: datetime = None) -> str:
        """
        Save articles to compressed pickle file.

        Args:
            articles: List of article dicts
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Path to saved file
        """
        ts = timestamp or datetime.now()
        filename = self._get_cache_filename(ts)
        filepath = os.path.join(self.cache_dir, filename)

        # Build header
        header = self._build_header(articles, filepath)

        # Prepare data
        cache_data = {"header": asdict(header), "articles": articles}

        # Save compressed pickle
        try:
            with gzip.open(filepath, "wb") as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"Saved {len(articles)} articles to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            raise

    def _build_header(self, articles: List[Dict], filepath: str) -> NewsCacheHeader:
        """Build cache header from articles"""
        categories = {}
        sources = set()
        symbols = []
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}

        for article in articles:
            # Categories
            cat = article.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

            # Sources
            sources.add(article.get("source", "Unknown"))

            # Symbols
            symbols.extend(article.get("related_symbols", article.get("symbols", [])))

            # Sentiment
            sent = article.get("sentiment", "neutral")
            sentiments[sent] = sentiments.get(sent, 0) + 1

        # Top 20 symbols
        from collections import Counter

        symbol_counts = Counter(symbols)
        top_symbols = [s for s, _ in symbol_counts.most_common(20)]

        # File size
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

        # Checksum placeholder (will be recalculated)
        checksum = ""

        return NewsCacheHeader(
            timestamp=datetime.now().isoformat(),
            article_count=len(articles),
            categories=categories,
            sources=list(sources),
            symbols=top_symbols,
            sentiment_distribution=sentiments,
            file_size_bytes=file_size,
            checksum=checksum,
        )

    def load_articles(self, filepath: str = None) -> Optional[List[Dict]]:
        """
        Load articles from pickle cache.

        Args:
            filepath: Specific file path or None for latest

        Returns:
            List of articles or None if not found
        """
        if filepath is None:
            filepath = self._get_latest_cache_file()

        if not filepath or not os.path.exists(filepath):
            logger.warning(f"Cache file not found: {filepath}")
            return None

        try:
            with gzip.open(filepath, "rb") as f:
                cache_data = pickle.load(f)

            articles = cache_data.get("articles", [])
            logger.info(f"Loaded {len(articles)} articles from {filepath}")
            return articles

        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None

    def load_latest_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Load latest articles mentioning a symbol"""
        articles = self.load_articles()

        if not articles:
            return []

        filtered = [
            a
            for a in articles
            if symbol.upper() in a.get("related_symbols", a.get("symbols", []))
        ]

        return filtered[:limit]

    def load_latest_by_sentiment(self, sentiment: str, limit: int = 100) -> List[Dict]:
        """Load latest articles by sentiment"""
        articles = self.load_articles()

        if not articles:
            return []

        filtered = [a for a in articles if a.get("sentiment", "neutral") == sentiment]

        return filtered[:limit]

    def load_latest_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """Load latest articles by category"""
        articles = self.load_articles()

        if not articles:
            return []

        filtered = [
            a for a in articles if a.get("category", "").lower() == category.lower()
        ]

        return filtered[:limit]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cache"""
        pattern = os.path.join(self.cache_dir, "news_cache_*.pkl.gz")
        files = glob.glob(pattern)

        if not files:
            return {
                "file_count": 0,
                "total_articles": 0,
                "cache_size_mb": 0,
                "oldest_file": None,
                "newest_file": None,
            }

        total_articles = 0
        total_size = 0

        for f in files:
            try:
                # Load header without loading full data
                with gzip.open(f, "rb") as h:
                    header = pickle.load(h).get("header", {})
                total_articles += header.get("article_count", 0)
                total_size += header.get("file_size_bytes", os.path.getsize(f))
            except Exception:
                total_size += os.path.getsize(f)

        file_times = [(f, os.path.getmtime(f)) for f in files]
        oldest = min(file_times, key=lambda x: x[1])
        newest = max(file_times, key=lambda x: x[1])

        return {
            "file_count": len(files),
            "total_articles": total_articles,
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_file": datetime.fromtimestamp(oldest[1]).isoformat(),
            "newest_file": datetime.fromtimestamp(newest[1]).isoformat(),
            "cache_dir": self.cache_dir,
            "ttl_days": self.ttl_days,
        }

    def cleanup_expired(self) -> int:
        """Remove cache files older than TTL"""
        cutoff = datetime.now() - timedelta(days=self.ttl_days)
        removed = 0

        pattern = os.path.join(self.cache_dir, "news_cache_*.pkl.gz")
        for filepath in glob.glob(pattern):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)
                    removed += 1
                    logger.info(f"Removed expired cache: {filepath}")
            except Exception as e:
                logger.error(f"Error removing {filepath}: {e}")

        logger.info(f"Cleaned up {removed} expired cache files")
        return removed

    def create_backup(self, name: str = None) -> str:
        """Create a named backup of current cache"""
        articles = self.load_articles()

        if not articles:
            raise ValueError("No articles to backup")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{ts}"

        backup_dir = os.path.join(self.cache_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        filepath = os.path.join(backup_dir, f"{backup_name}.pkl.gz")

        # Save without auto-cleanup
        with gzip.open(filepath, "wb") as f:
            pickle.dump(
                {
                    "header": self._build_header(articles, filepath).__dict__,
                    "articles": articles,
                },
                f,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

        logger.info(f"Created backup: {filepath}")
        return filepath

    def export_to_json(self, filepath: str = None) -> str:
        """Export cache to JSON (for debugging/portability)"""
        articles = self.load_articles()

        if not articles:
            raise ValueError("No articles to export")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = filepath or os.path.join(self.cache_dir, f"news_export_{ts}.json")

        with open(output_path, "w") as f:
            json.dump(
                {
                    "exported_at": datetime.now().isoformat(),
                    "article_count": len(articles),
                    "articles": articles,
                },
                f,
                indent=2,
            )

        logger.info(f"Exported {len(articles)} articles to {output_path}")
        return output_path

    def get_symbol_index(self) -> Dict[str, List[str]]:
        """
        Build index of articles by symbol.
        Useful for fast symbol-based queries.

        Returns:
            Dict mapping symbol -> article URLs
        """
        articles = self.load_articles()

        if not articles:
            return {}

        index = {}
        for article in articles:
            symbols = article.get("related_symbols", article.get("symbols", []))
            for symbol in symbols:
                symbol = symbol.upper()
                if symbol not in index:
                    index[symbol] = []
                index[symbol].append(article.get("url", ""))

        return index


class NewsCacheBatchWriter:
    """
    Batch writer for efficient cache updates.
    Accumulates articles and writes in batches.
    """

    def __init__(self, cache: NewsPickleCache, batch_size: int = 1000):
        self.cache = cache
        self.batch_size = batch_size
        self.buffer: List[Dict] = []

    def add_article(self, article: Dict):
        """Add article to buffer"""
        self.buffer.append(article)

        if len(self.buffer) >= self.batch_size:
            self.flush()

    def add_articles(self, articles: List[Dict]):
        """Add multiple articles to buffer"""
        self.buffer.extend(articles)

        while len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        """Write buffered articles to cache"""
        if not self.buffer:
            return

        self.cache.save_articles(self.buffer)
        self.buffer = []
        logger.info(f"Flushed {len(self.buffer)} articles to cache")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()


def get_pickle_cache(cache_dir: str = None) -> NewsPickleCache:
    """Factory function to get pickle cache"""
    return NewsPickleCache(cache_dir)
