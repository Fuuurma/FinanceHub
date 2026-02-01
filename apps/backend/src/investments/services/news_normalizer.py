"""
News Article Normalizer Service
Normalizes articles from multiple sources, deduplicates, and prepares for storage
"""

import re
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Set, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass, asdict
from multiprocessing import cpu_count

logger = logging.getLogger(__name__)


def _hash_url(url: str) -> str:
    """Generate consistent hash for URL deduplication"""
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def _normalize_title(title: str) -> str:
    """Normalize title for similarity comparison"""
    if not title:
        return ""

    # Lowercase, remove special chars, normalize whitespace
    normalized = re.sub(r"[^\w\s]", "", title.lower())
    normalized = " ".join(normalized.split())
    return normalized


@dataclass
class NormalizedArticle:
    """Standardized article format for all sources"""

    title: str
    description: str
    url: str
    source: str
    author: str
    published_at: datetime
    category: str
    image_url: str
    content: str
    raw_data: Dict[str, Any]

    # Extracted fields
    symbols: List[str]
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

    # Metadata
    url_hash: str = ""
    normalized_title: str = ""
    word_count: int = 0

    def __post_init__(self):
        self.url_hash = _hash_url(self.url)
        self.normalized_title = _normalize_title(self.title)
        self.word_count = len(self.title.split())


class NewsNormalizer:
    """
    Normalize articles from different sources into a standard format.

    Performance: Uses multiprocessing for parallel normalization.
    Deduplication: URL hash + title similarity checks.
    """

    # Common news sources and their field mappings
    SOURCE_MAPPINGS = {
        "reuters": {"source": "Reuters", "author_field": "author"},
        "bloomberg": {"source": "Bloomberg", "author_field": "author"},
        "cnbc": {"source": "CNBC", "author_field": "author"},
        "wsj": {"source": "Wall Street Journal", "author_field": "author"},
        "financial times": {"source": "Financial Times", "author_field": "author"},
        "coindesk": {"source": "CoinDesk", "author_field": "author"},
        "cointelegraph": {"source": "Cointelegraph", "author_field": "author"},
        "techcrunch": {"source": "TechCrunch", "author_field": "author"},
        "the block": {"source": "The Block", "author_field": "author"},
    }

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: Minimum similarity for duplicate detection (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.seen_urls: Set[str] = set()
        self.seen_titles: List[str] = []

    @staticmethod
    def _hash_url(url: str) -> str:
        """Generate consistent hash for URL deduplication"""
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title for similarity comparison"""
        if not title:
            return ""

        # Lowercase, remove special chars, normalize whitespace
        normalized = re.sub(r"[^\w\s]", "", title.lower())
        normalized = " ".join(normalized.split())
        return normalized

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats from different sources"""
        if not date_str:
            return None

        date_formats = [
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601
            "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone
            "%Y-%m-%d %H:%M:%S",  # MySQL format
            "%Y-%m-%d",  # Date only
            "%b %d, %Y %H:%M",  # "Jan 29, 2026 12:00"
            "%b %d, %Y",  # "Jan 29, 2026"
            "%d %b %Y",  # "29 Jan 2026"
            "%B %d, %Y",  # "January 29, 2026"
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.replace(" +0000", ""), fmt)
            except ValueError:
                continue

        logger.debug(f"Could not parse date: {date_str}")
        return None

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags and clean content"""
        if not html:
            return ""

        # Simple HTML stripping (use BeautifulSoup for complex cases)
        text = re.sub(r"<[^>]+>", "", html)
        text = " ".join(text.split())
        return text.strip()

    def _is_duplicate(self, article: Dict) -> bool:
        """Check if article is duplicate based on URL or title"""
        url = article.get("url", "")
        url_hash = self._hash_url(url)

        # URL-based deduplication (fastest)
        if url_hash in self.seen_urls:
            return True

        # Title-based similarity check
        title = article.get("title", "")
        if title:
            normalized_title = self._normalize_title(title)
            for seen_title in self.seen_titles[-100:]:  # Check last 100
                similarity = SequenceMatcher(None, normalized_title, seen_title).ratio()
                if similarity >= self.similarity_threshold:
                    return True
            self.seen_titles.append(normalized_title)

        self.seen_urls.add(url_hash)
        return False

    def normalize_newsapi_article(
        self, article: Dict, category: str = "general"
    ) -> Optional[NormalizedArticle]:
        """Normalize article from NewsAPI format"""
        if not article:
            return None

        try:
            source = article.get("source", {})
            if isinstance(source, dict):
                source_name = source.get("name", "Unknown")
            else:
                source_name = str(source)

            # Parse published date
            published_at = self._parse_date(article.get("publishedAt", ""))

            return NormalizedArticle(
                title=article.get("title", "")[:500],
                description=self._clean_html(article.get("description", ""))[:2000],
                url=article.get("url", ""),
                source=source_name,
                author=article.get("author", "")[:200] or "",
                published_at=published_at or datetime.now(),
                category=category,
                image_url=article.get("urlToImage", "") or "",
                content=self._clean_html(article.get("content", "")),
                raw_data=article,
                symbols=[],  # Will be extracted separately
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error normalizing NewsAPI article: {e}")
            return None

    def normalize_finnhub_article(
        self, article: Dict, category: str = "business"
    ) -> Optional[NormalizedArticle]:
        """Normalize article from Finnhub format"""
        if not article:
            return None

        try:
            published_at = self._parse_date(article.get("datetime", ""))

            return NormalizedArticle(
                title=article.get("headline", "")[:500],
                description=self._clean_html(article.get("summary", ""))[:2000],
                url=article.get("url", ""),
                source=article.get("source", "Finnhub"),
                author="",
                published_at=published_at or datetime.now(),
                category=category,
                image_url="",
                content=self._clean_html(article.get("summary", "")),
                raw_data=article,
                symbols=article.get("relatedSymbols", []),
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error normalizing Finnhub article: {e}")
            return None

    def normalize_atlas_article(
        self, article: Dict, category: str = "general"
    ) -> Optional[NormalizedArticle]:
        """Normalize article from ATLAS RSS format"""
        if not article:
            return None

        try:
            published_at = self._parse_date(article.get("published", ""))

            return NormalizedArticle(
                title=article.get("title", "")[:500],
                description=article.get("summary", "")[:2000],
                url=article.get("link", ""),
                source=article.get("source", "ATLAS"),
                author="",
                published_at=published_at or datetime.now(),
                category=category,
                image_url="",
                content=article.get("summary", ""),
                raw_data=article,
                symbols=[],
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error normalizing ATLAS article: {e}")
            return None

    def normalize_article(
        self, article: Dict, source_type: str = "generic", category: str = "general"
    ) -> Optional[NormalizedArticle]:
        """Generic article normalizer that dispatches to specific handlers"""

        # Check for duplicates before processing
        if self._is_duplicate(article):
            logger.debug(
                f"Skipping duplicate article: {article.get('title', '')[:50]}..."
            )
            return None

        handlers = {
            "newsapi": lambda: self.normalize_newsapi_article(article, category),
            "finnhub": lambda: self.normalize_finnhub_article(article, category),
            "atlas": lambda: self.normalize_atlas_article(article, category),
            "rss": lambda: self.normalize_atlas_article(article, category),
            "generic": lambda: self._normalize_generic_article(article, category),
        }

        handler = handlers.get(source_type, handlers["generic"])
        return handler()

    def _normalize_generic_article(
        self, article: Dict, category: str
    ) -> Optional[NormalizedArticle]:
        """Generic fallback normalizer"""
        try:
            published_at = self._parse_date(
                article.get("published_at", "")
                or article.get("published", "")
                or article.get("date", "")
            )

            source = article.get("source", {})
            if isinstance(source, dict):
                source_name = source.get("name", "Unknown")
            else:
                source_name = str(source)

            return NormalizedArticle(
                title=article.get("title", "")[:500],
                description=self._clean_html(
                    article.get("description", "") or article.get("summary", "") or ""
                )[:2000],
                url=article.get("url", "") or article.get("link", ""),
                source=source_name,
                author=article.get("author", "")[:200] or "",
                published_at=published_at or datetime.now(),
                category=category,
                image_url=article.get("image_url", "")
                or article.get("urlToImage", "")
                or "",
                content=self._clean_html(
                    article.get("content", "") or article.get("body", "")
                ),
                raw_data=article,
                symbols=[],
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error normalizing generic article: {e}")
            return None

    def normalize_batch(
        self,
        articles: List[Dict],
        source_type: str = "generic",
        category: str = "general",
    ) -> List[NormalizedArticle]:
        """
        Normalize a batch of articles with deduplication.

        Performance: Uses multiprocessing for parallel processing.
        """
        from multiprocessing import Pool, cpu_count
        import asyncio

        # Reset deduplication sets for each batch
        self.seen_urls = set()
        self.seen_titles = []

        # Filter out None and duplicates in parallel
        normalized = []

        for article in articles:
            result = self.normalize_article(article, source_type, category)
            if result:
                normalized.append(result)

        logger.info(
            f"Normalized {len(normalized)} articles (from {len(articles)} input)"
        )
        return normalized

    def to_dict(self, article: NormalizedArticle) -> Dict[str, Any]:
        """Convert normalized article to dict for database/storage"""
        return {
            "title": article.title,
            "description": article.description,
            "url": article.url,
            "source": article.source,
            "author": article.author,
            "published_at": article.published_at.isoformat()
            if article.published_at
            else None,
            "category": article.category,
            "image_url": article.image_url,
            "content": article.content,
            "symbols": article.symbols,
            "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "url_hash": article.url_hash,
            "normalized_title": article.normalized_title,
            "word_count": article.word_count,
            "raw_data": str(article.raw_data) if article.raw_data else "",
        }


class BatchNormalizer:
    """
    Batch processing with parallelization for high throughput.
    """

    def __init__(self, normalizer: NewsNormalizer, num_workers: int = None):
        self.normalizer = normalizer
        self.num_workers = num_workers or cpu_count()

    def process_source(
        self, articles: List[Dict], source_type: str, category: str
    ) -> List[NormalizedArticle]:
        """Process articles from a single source"""
        return self.normalizer.normalize_batch(articles, source_type, category)

    async def process_sources_async(
        self, sources: Dict[str, Tuple[List[Dict], str]]
    ) -> Dict[str, List[NormalizedArticle]]:
        """
        Process multiple sources concurrently.

        Args:
            sources: Dict of {source_name: (articles, source_type, category)}
        """
        results = {}

        for source_name, (articles, source_type, category) in sources.items():
            try:
                normalized = self.process_source(articles, source_type, category)
                results[source_name] = normalized
                logger.info(f"Processed {len(normalized)} articles from {source_name}")
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Error processing {source_name}: {e}")
                results[source_name] = []

        return results


def similarity_score(title1: str, title2: str) -> float:
    """Calculate similarity score between two titles"""
    if not title1 or not title2:
        return 0.0

    norm1 = re.sub(r"[^\w\s]", "", title1.lower())
    norm2 = re.sub(r"[^\w\s]", "", title2.lower())
    norm1 = " ".join(norm1.split())
    norm2 = " ".join(norm2.split())

    return SequenceMatcher(None, norm1, norm2).ratio()


def cluster_articles(
    articles: List[NormalizedArticle], threshold: float = 0.7
) -> List[List[NormalizedArticle]]:
    """
    Cluster similar articles together.

    Used to identify:
    - Duplicate stories across sources
    - Related coverage of same event
    - Trending topics
    """
    if not articles:
        return []

    clusters = []
    used_indices = set()

    for i, article in enumerate(articles):
        if i in used_indices:
            continue

        cluster = [article]
        used_indices.add(i)

        for j, other in enumerate(articles):
            if j in used_indices or i == j:
                continue

            sim = similarity_score(article.title, other.title)
            if sim >= threshold:
                cluster.append(other)
                used_indices.add(j)

        clusters.append(cluster)

    return clusters


def extract_topics_from_cluster(cluster: List[NormalizedArticle]) -> Dict[str, Any]:
    """
    Extract common topics from a cluster of related articles.
    """
    if not cluster:
        return {}

    # Count symbols mentioned
    symbol_counts = {}
    for article in cluster:
        for symbol in article.symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

    # Extract keywords from titles
    all_words = []
    for article in cluster:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", article.title.lower())
        all_words.extend(words)

    word_counts = {}
    for word in all_words:
        # Filter common words
        if word not in {
            "this",
            "that",
            "with",
            "from",
            "have",
            "will",
            "what",
            "when",
            "they",
            "been",
            "more",
            "than",
            "just",
            "over",
            "your",
            "year",
            "years",
            "after",
            "first",
            "last",
        }:  # Add stopwords
            word_counts[word] = word_counts.get(word, 0) + 1

    return {
        "article_count": len(cluster),
        "sources": list(set(a.source for a in cluster)),
        "top_symbols": sorted(symbol_counts.items(), key=lambda x: -x[1])[:5],
        "top_keywords": sorted(word_counts.items(), key=lambda x: -x[1])[:10],
        "published_range": {
            "earliest": min(a.published_at for a in cluster).isoformat(),
            "latest": max(a.published_at for a in cluster).isoformat(),
        },
    }
