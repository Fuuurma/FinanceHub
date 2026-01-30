"""
ATLAS News Adapter
Bridges ATLAS RSS feeds and crawlers with FinanceHub news system
"""

import os
import json
import glob
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ATLASNewsAdapter:
    """
    Adapter to integrate ATLAS news sources with FinanceHub.

    Supports:
    - RSS feed aggregation
    - JSON file parsing from ATLAS output
    - Web crawler data integration
    """

    # Default ATLAS RSS sources (investments, crypto, tech)
    DEFAULT_SOURCES = {
        "investments": [
            {
                "name": "Bloomberg Markets",
                "url": "https://feeds.bloomberg.com/markets/news.rss",
                "type": "rss",
            },
            {
                "name": "CNBC",
                "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                "type": "rss",
            },
            {
                "name": "Financial Times",
                "url": "https://www.ft.com/world/uk/rss",
                "type": "rss",
            },
            {
                "name": "Reuters Business",
                "url": "https://www.reuters.com/rssFeed/rss/us2.0.businessNews",
                "type": "rss",
            },
            {
                "name": "Wall Street Journal",
                "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness",
                "type": "rss",
            },
        ],
        "crypto": [
            {
                "name": "CoinDesk",
                "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "type": "rss",
            },
            {
                "name": "Cointelegraph",
                "url": "https://cointelegraph.com/rss",
                "type": "rss",
            },
            {
                "name": "CryptoCompare",
                "url": "https://www.cryptocompare.com/api/news/short",
                "type": "api",
            },
        ],
        "tech": [
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/feed/",
                "type": "rss",
            },
            {
                "name": "Ars Technica",
                "url": "https://feeds.arstechnica.com/arstechnica/index",
                "type": "rss",
            },
            {
                "name": "The Verge",
                "url": "https://www.theverge.com/rss/index.xml",
                "type": "rss",
            },
        ],
    }

    def __init__(self, atlas_base_path: str = None):
        """
        Initialize ATLAS adapter.

        Args:
            atlas_base_path: Base path for ATLAS data (defaults to clawd/ATLAS)
        """
        self.atlas_base_path = atlas_base_path or "/Users/sergi/clawd/ATLAS"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

        # Source directory paths
        self.news_data_path = f"{self.atlas_base_path}/tasks/daily/news/data"
        self.crypto_data_path = (
            f"{self.atlas_base_path}/tasks/daily/research/crypto-research/data"
        )
        self.tools_path = f"{self.atlas_base_path}/tools"

        # Ensure output directory exists for FinanceHub
        self.output_dir = (
            "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/media/news_cache"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_rss_feed(self, source: Dict) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(source["url"])

            articles = []
            for entry in feed.entries[:15]:  # Top 15 articles
                article = {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", entry.get("description", ""))[
                        :1000
                    ],
                    "source": source["name"],
                    "category": self._get_category_from_source(source),
                    "url": entry.get("link", ""),
                    "author": entry.get("author", ""),
                    "image_url": self._extract_image_from_entry(entry),
                }
                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from {source['name']}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching {source['name']}: {e}")
            return []

    def _extract_image_from_entry(self, entry) -> str:
        """Extract image URL from RSS entry"""
        # Check media:content
        if hasattr(entry, "media_content"):
            for media in entry.media_content:
                if media.get("type", "").startswith("image"):
                    return media.get("url", "")

        # Check media:thumbnail
        if hasattr(entry, "media_thumbnail"):
            if entry.media_thumbnail:
                return entry.media_thumbnail[0].get("url", "")

        # Check enclosures
        if hasattr(entry, "enclosures"):
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image"):
                    return enc.get("href", "")

        # Try to extract from content
        if hasattr(entry, "content"):
            for content in entry.content:
                if content.type.startswith("image"):
                    return content.src

        return ""

    def _get_category_from_source(self, source: Dict) -> str:
        """Determine category from source URL"""
        url = source["url"].lower()

        if "bloomberg" in url or "cnbc" in url or "ft.com" in url:
            return "investments"
        if "coindesk" in url or "cointelegraph" in url or "crypto" in url:
            return "crypto"
        if "techcrunch" in url or "arstechnica" in url or "theverge" in url:
            return "tech"
        if "reuters" in url:
            return "investments"

        return "general"

    def fetch_all_rss_feeds(
        self, categories: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Fetch all RSS feeds from configured sources.

        Args:
            categories: List of categories to fetch (default: investments, crypto, tech)

        Returns:
            Dict mapping category to list of articles
        """
        if categories is None:
            categories = ["investments", "crypto", "tech"]

        results = {}

        for category in categories:
            if category not in self.DEFAULT_SOURCES:
                logger.warning(f"Unknown category: {category}")
                continue

            category_articles = []
            sources = self.DEFAULT_SOURCES[category]

            for source in sources:
                articles = self.fetch_rss_feed(source)
                category_articles.extend(articles)

            results[category] = category_articles
            logger.info(
                f"Fetched {len(category_articles)} total articles for {category}"
            )

        return results

    def parse_atlas_json_output(self, file_path: str = None) -> List[Dict]:
        """
        Parse existing ATLAS JSON output files.

        Args:
            file_path: Specific file path or None to use latest

        Returns:
            List of articles from ATLAS JSON
        """
        if file_path is None:
            # Use latest file
            pattern = f"{self.news_data_path}/aggregated_news_*.json"
            files = glob.glob(pattern)
            if not files:
                logger.warning(f"No ATLAS JSON files found in {self.news_data_path}")
                return []
            file_path = max(files, key=os.path.getmtime)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            articles = []

            # Handle different ATLAS output formats
            if "categories" in data:
                for category, category_data in data["categories"].items():
                    for article in category_data.get("articles", []):
                        article["category"] = category
                        articles.append(article)

            elif isinstance(data, list):
                articles = data

            elif "articles" in data:
                articles = data["articles"]

            logger.info(f"Parsed {len(articles)} articles from {file_path}")
            return articles

        except Exception as e:
            logger.error(f"Error parsing ATLAS JSON: {e}")
            return []

    def parse_crypto_news_file(self, file_path: str = None) -> List[Dict]:
        """
        Parse ATLAS crypto news JSON files.

        Args:
            file_path: Specific file path or None to use latest

        Returns:
            List of crypto news articles
        """
        if file_path is None:
            pattern = f"{self.crypto_data_path}/crypto_news_*.json"
            files = glob.glob(pattern)
            if not files:
                logger.warning(f"No crypto news files found in {self.crypto_data_path}")
                return []
            file_path = max(files, key=os.path.getmtime)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Handle different formats
            if isinstance(data, list):
                articles = data
            elif "Data" in data:
                articles = data["Data"]
            else:
                articles = []

            # Normalize to common format
            normalized = []
            for item in articles:
                normalized.append(
                    {
                        "title": item.get("title", "No title"),
                        "link": item.get("link", item.get("url", "")),
                        "published": item.get("timestamp", item.get("publishedAt", "")),
                        "source": item.get("source", "ATLAS Crypto"),
                        "summary": item.get("summary", ""),
                        "category": "crypto",
                    }
                )

            logger.info(f"Parsed {len(normalized)} crypto articles from {file_path}")
            return normalized

        except Exception as e:
            logger.error(f"Error parsing crypto news file: {e}")
            return []

    def fetch_cryptocompare_api(self) -> List[Dict]:
        """Fetch crypto news from CryptoCompare API"""
        url = "https://www.cryptocompare.com/api/news/short"

        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = []

                if "Data" in data:
                    for item in data["Data"][:20]:
                        articles.append(
                            {
                                "title": item.get("Title", "No title"),
                                "link": item.get("Url", ""),
                                "published": datetime.now().isoformat(),
                                "source": "CryptoCompare",
                                "summary": item.get("body", "")[:500],
                                "category": "crypto",
                                "image_url": item.get("imageurl", ""),
                                "url": item.get("Url", ""),
                            }
                        )

                logger.info(f"Fetched {len(articles)} articles from CryptoCompare")
                return articles

            return []

        except Exception as e:
            logger.error(f"Error fetching CryptoCompare: {e}")
            return []

    def get_all_articles(self, categories: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Get all articles from all configured sources.

        Combines:
        - RSS feeds from DEFAULT_SOURCES
        - Existing ATLAS JSON files
        - CryptoCompare API

        Args:
            categories: Categories to include

        Returns:
            Dict mapping category to articles
        """
        if categories is None:
            categories = ["investments", "crypto", "tech"]

        all_articles = {cat: [] for cat in categories}
        all_articles["general"] = []

        # 1. Fetch RSS feeds
        rss_articles = self.fetch_all_rss_feeds(categories)
        for cat, articles in rss_articles.items():
            all_articles[cat].extend(articles)

        # 2. Parse ATLAS JSON files
        atlas_articles = self.parse_atlas_json_output()
        for article in atlas_articles:
            cat = article.get("category", "general")
            if cat not in all_articles:
                all_articles[cat] = []
            all_articles[cat].append(article)

        # 3. Fetch CryptoCompare (crypto specific)
        if "crypto" in categories:
            cc_articles = self.fetch_cryptocompare_api()
            all_articles["crypto"].extend(cc_articles)

        # 4. Parse crypto news files
        crypto_file_articles = self.parse_crypto_news_file()
        all_articles["crypto"].extend(crypto_file_articles)

        # Log summary
        total = sum(len(articles) for articles in all_articles.values())
        logger.info(
            f"Total articles from ATLAS: {total} across {len(categories)} categories"
        )

        return all_articles

    def save_to_json(
        self, articles: Dict[str, List[Dict]], timestamp: datetime = None
    ) -> str:
        """
        Save articles to JSON file for pickle processing.

        Args:
            articles: Dict of {category: articles}
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Path to saved file
        """
        ts = timestamp or datetime.now()
        filename = f"atlas_news_{ts.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)

        data = {
            "timestamp": ts.isoformat(),
            "source": "ATLAS",
            "categories": {},
            "total_articles": 0,
        }

        for category, category_articles in articles.items():
            if category_articles:
                data["categories"][category] = {
                    "articles": category_articles,
                    "count": len(category_articles),
                }
                data["total_articles"] += len(category_articles)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {data['total_articles']} articles to {filepath}")
        return filepath

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about ATLAS news data"""
        stats = {
            "sources_configured": len(self.DEFAULT_SOURCES),
            "categories": list(self.DEFAULT_SOURCES.keys()),
            "articles_by_category": {},
            "files_in_news_dir": 0,
            "files_in_crypto_dir": 0,
        }

        # Count articles by category
        articles = self.get_all_articles()
        for cat, arts in articles.items():
            if arts:
                stats["articles_by_category"][cat] = len(arts)

        # Count files
        stats["files_in_news_dir"] = len(glob.glob(f"{self.news_data_path}/*.json"))
        stats["files_in_crypto_dir"] = len(glob.glob(f"{self.crypto_data_path}/*.json"))

        return stats


class ATLASNewsCrawler:
    """
    Web crawler for ATLAS-compatible news sources.
    Handles dynamic pages that can't be fetched via RSS.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    def crawl_coindesk(self, limit: int = 10) -> List[Dict]:
        """Crawl CoinDesk for latest news"""
        url = "https://www.coindesk.com/news/"

        try:
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                articles = []

                # Find article cards
                cards = soup.find_all(
                    "div", class_=lambda x: x and "article-card" in x
                )[:limit]

                for card in cards:
                    try:
                        title_tag = card.find("h3") or card.find("h2")
                        link_tag = card.find("a")

                        if title_tag and link_tag:
                            articles.append(
                                {
                                    "title": title_tag.get_text().strip(),
                                    "link": "https://www.coindesk.com"
                                    + link_tag["href"]
                                    if link_tag["href"].startswith("/")
                                    else link_tag["href"],
                                    "source": "CoinDesk",
                                    "category": "crypto",
                                    "published": datetime.now().isoformat(),
                                }
                            )
                    except Exception:
                        continue

                logger.info(f"Crawled {len(articles)} articles from CoinDesk")
                return articles

            return []

        except Exception as e:
            logger.error(f"Error crawling CoinDesk: {e}")
            return []

    def crawl_theblock(self, limit: int = 10) -> List[Dict]:
        """Crawl The Block for latest news"""
        url = "https://www.theblock.co/"

        try:
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                articles = []

                # Find article elements
                cards = soup.find_all("article")[:limit]

                for card in cards:
                    try:
                        title_tag = card.find("h2") or card.find("h3")
                        link_tag = card.find("a")

                        if title_tag and link_tag:
                            articles.append(
                                {
                                    "title": title_tag.get_text().strip(),
                                    "link": link_tag["href"],
                                    "source": "The Block",
                                    "category": "crypto",
                                    "published": datetime.now().isoformat(),
                                }
                            )
                    except Exception:
                        continue

                logger.info(f"Crawled {len(articles)} articles from The Block")
                return articles

            return []

        except Exception as e:
            logger.error(f"Error crawling The Block: {e}")
            return []

    def crawl_all(self) -> Dict[str, List[Dict]]:
        """Crawl all web sources"""
        results = {}

        # CoinDesk
        results["coindesk"] = self.crawl_coindesk()

        # The Block
        results["theblock"] = self.crawl_theblock()

        total = sum(len(arts) for arts in results.values())
        logger.info(f"Crawled {total} articles from web sources")

        return results


def get_atlas_adapter(atlas_base_path: str = None) -> ATLASNewsAdapter:
    """Factory function to get ATLAS adapter"""
    return ATLASNewsAdapter(atlas_base_path)
