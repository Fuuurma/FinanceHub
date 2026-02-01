"""
NewsAPI News Scraper using BaseAPIFetcher for key rotation
Best for news aggregation from 150,000+ sources
"""

import aiohttp
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class NewsAPIScraper(BaseAPIFetcher):
    """
    NewsAPI API implementation with key rotation

    Free tier (Developer): 100 requests/day
    Strategy: Use for comprehensive news aggregation from 150,000+ sources

    Data Available:
    - News aggregation from multiple sources
    - Headline and full articles
    - Search by keyword, category, source
    - 24-hour delay on full articles
    """

    def __init__(self):
        super().__init__(provider_name="newsapi")

    def get_base_url(self) -> str:
        return "https://newsapi.org/v2"

    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from NewsAPI response"""
        if response and isinstance(response, dict):
            if "status" in response and response.get("status") == "error":
                error = response.get("message", "")
                if any(
                    keyword in error.lower()
                    for keyword in ["rate limit", "too many requests", "429"]
                ):
                    return error
        return None

    async def _make_request(
        self, endpoint: str, params: Optional[Dict], method: str, api_key
    ) -> Dict:
        """Make request with async HTTP client"""
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)

        async with self.session.request(
            method, url, params=params, headers=headers
        ) as response:
            response.raise_for_status()
            content = await response.read()
            # Use orjson for fast parsing
            import orjson

            return orjson.loads(content)

    def _get_headers(self, api_key) -> Dict:
        """NewsAPI uses API key in query string (not header)"""
        return {"Accept": "application/json", "User-Agent": "FinanceHub/1.0"}

    async def get_everything(
        self,
        q: Optional[str] = None,
        sources: Optional[str] = None,
        domains: Optional[str] = None,
        exclude_domains: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page: int = 1,
        page_size: int = 100,
        search_in: Optional[str] = "title,description",
    ) -> Optional[Dict]:
        """
        Get all news matching parameters

        Args:
            q: Keywords or phrases to search for
            sources: A comma-seperated string of identifiers for the news sources or blogs
            domains: A comma-seperated string of domains to restrict the search to
            exclude_domains: A comma-seperated string of domains to remove from the results
            from: A date and optional time for the oldest article allowed
            to: A date and optional time for the newest article allowed
            language: The 2-letter ISO-639-1 language code
            sort_by: Order to sort by
            page: Use this to page through results
            page_size: The number of results to return per page (max 100)
            search_in: Fields to search in
        """
        params = {
            "language": language,
            "sortBy": sort_by,
            "page": page,
            "pageSize": min(page_size, 100),
        }

        if q:
            params["q"] = q
        if sources:
            params["sources"] = sources
        if domains:
            params["domains"] = domains
        if exclude_domains:
            params["excludeDomains"] = exclude_domains
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if search_in:
            params["searchIn"] = search_in

        return await self.request("everything", params)

    async def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 20,
        page: int = 1,
    ) -> Optional[Dict]:
        """
        Get top headlines

        Args:
            country: The 2-letter ISO 3166-1 country code
            category: Category to filter by (business, entertainment, general, health, science, sports, technology)
            page_size: Number of results to return
            page: Page number
        """
        params = {"country": country, "pageSize": min(page_size, 100), "page": page}

        if category:
            params["category"] = category

        return await self.request(f"top-headlines/{country}", params)

    async def get_sources(self) -> Optional[List]:
        """Get list of all available sources"""
        return await self.request("sources", {})

    async def get_headlines_by_source(
        self, sources: str, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        """
        Get headlines from specific sources

        Args:
            sources: Comma-separated list of source IDs or domains
            page: Page number
            page_size: Number of results (max 100)
        """
        params = {"sources": sources, "pageSize": min(page_size, 100), "page": page}

        return await self.request("top-headlines/sources", params)

    async def get_headlines_by_category(
        self, category: str, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        """
        Get headlines by category

        Categories: business, entertainment, general, health, science, sports, technology
        """
        params = {"category": category, "pageSize": min(page_size, 100), "page": page}

        return await self.request(f"top-headlines/category/{category}", params)

    async def search_by_keyword(
        self,
        keyword: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        page_size: int = 20,
        page: int = 1,
    ) -> Optional[Dict]:
        """
        Search for articles by keyword

        Args:
            keyword: Search keyword or phrase
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            language: Language code
            page_size: Number of results (max 100)
        """
        params = {
            "q": keyword,
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": min(page_size, 100),
            "page": page,
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        return await self.request("everything", params)

    async def get_business_news(
        self, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        """Get business news"""
        return await self.get_headlines_by_category("business", page, page_size)

    async def get_technology_news(
        self, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        """Get technology news"""
        return await self.get_headlines_by_category("technology", page, page_size)

    async def get_science_news(
        self, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        """Get science news"""
        return await self.get_headlines_by_category("science", page, page_size)

    async def fetch_and_save_news(
        self, query: str = "business", category: Optional[str] = None, limit: int = 20
    ) -> bool:
        """
        Fetch and save news to database

        Args:
            query: Search query or category name
            category: Category filter (optional)
            limit: Number of articles to fetch

        Returns:
            True if successful, False otherwise
        """
        try:
            from assets.models.news import NewsArticle
            from datetime import timedelta
            import asyncio

            logger.info(f"Fetching news for query: {query} (category: {category})")

            if category:
                # Use category-based headlines
                data = await self.get_headlines_by_category(
                    category, page=1, page_size=limit
                )
            else:
                # Use keyword search
                data = await self.search_by_keyword(query, page=1, page_size=limit)

            if not data or "articles" not in data:
                logger.warning(f"No news found for query: {query}")
                return False

            # Save articles
            count = 0
            for article in data["articles"]:
                try:
                    # Check for duplicates
                    existing = await asyncio.to_thread(
                        NewsArticle.objects.filter(url=article.get("url")).afirst
                    )

                    if existing:
                        logger.debug(f"Article already exists: {article.get('title')}")
                        continue

                    # Create news article
                    await asyncio.to_thread(
                        NewsArticle.objects.create,
                        title=article.get("title", ""),
                        url=article.get("url", ""),
                        source=article.get("source", {}).get(
                            "name", article.get("source", {}).get("id", "")
                        ),
                        author=article.get("author", article.get("content", "")[:500]),
                        content=article.get("content", ""),
                        published_at=datetime.fromisoformat(article.get("publishedAt"))
                        if article.get("publishedAt")
                        else None,
                        category=category or query,
                        description=article.get("description", "")[:500],
                        image_url=article.get("urlToImage"),
                        is_active=True,
                    )
                    count += 1

                except Exception as e:
                    logger.debug(f"Error saving article: {str(e)}")
                    continue

            logger.info(f"Saved {count} news articles for query: {query}")
            return True

        except Exception as e:
            logger.error(f"Error fetching/saving news: {str(e)}")
            return False

    async def fetch_multiple_queries(
        self,
        queries: List[str],
        category: Optional[str] = None,
        limit_per_query: int = 20,
    ) -> Dict[str, List[Dict]]:
        """
        Fetch news for multiple queries

        Args:
            queries: List of search queries or categories
            category: Common category for all (optional)
            limit_per_query: Number of articles per query

        Returns:
            Dict mapping queries to article lists
        """
        logger.info(f"Fetching news for {len(queries)} queries...")

        results = {}

        async with self:
            tasks = [
                self.fetch_and_save_news(query, category, limit_per_query)
                for query in queries
            ]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for query, result in zip(queries, task_results):
                if isinstance(result, Exception):
                    results[query] = []
                    logger.error(f"Error fetching {query}: {str(result)}")
                else:
                    # Fetch articles from database
                    if category:
                        articles_data = await self.search_by_keyword(
                            query, page=1, page_size=limit_per_query
                        )
                    else:
                        articles_data = await self.search_by_keyword(
                            query, page=1, page_size=limit_per_query
                        )

                    articles = []
                    if articles_data and "articles" in articles_data:
                        for article in articles_data["articles"]:
                            articles.append(
                                {
                                    "title": article.get("title"),
                                    "url": article.get("url"),
                                    "source": article.get("source", {}).get("name"),
                                    "published_at": article.get("publishedAt"),
                                    "description": article.get("description", "")[:200],
                                    "image_url": article.get("urlToImage"),
                                }
                            )

                    results[query] = articles

        total_articles = sum(len(articles) for articles in results.values())
        logger.info(
            f"Fetched {total_articles} total articles across {len(queries)} queries"
        )

        return results

    async def get_popular_categories(self) -> Optional[Dict]:
        """Get popular news categories"""
        return await self.request("top-headlines/sources", {"pageSize": 10})

    async def get_all_sources(self) -> Optional[List[Dict]]:
        """Get all available sources"""
        data = await self.get_sources()

        if data:
            return data.get("sources", [])
        return []

    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings

        scraper = cls()
        return scraper


# Common query terms for financial news
FINANCIAL_SEARCH_TERMS = {
    "market": ["market", "stock", "economy", "trading"],
    "business": ["finance", "company", "corporate", "earnings"],
    "crypto": ["cryptocurrency", "bitcoin", "ethereum", "blockchain"],
    "economy": ["inflation", "gdp", "federal reserve", "interest rates"],
}


async def fetch_financial_news(limit_per_query: int = 20) -> Dict[str, List]:
    """Fetch financial news from multiple categories"""
    scraper = NewsAPIScraper()

    all_articles = {}

    # Get business news
    business_data = await scraper.get_business_news(page=1, page_size=limit_per_query)
    if business_data and "articles" in business_data:
        all_articles["business"] = business_data["articles"]

    # Get technology news
    tech_data = await scraper.get_technology_news(page=1, page_size=limit_per_query)
    if tech_data and "articles" in tech_data:
        all_articles["technology"] = tech_data["articles"]

    # Search for specific terms
    for category, terms in FINANCIAL_SEARCH_TERMS.items():
        for term in terms[:2]:  # Top 2 terms per category
            data = await scraper.search_by_keyword(term, page=1, page_size=10)
            if data and "articles" in data:
                if term not in all_articles:
                    all_articles[term] = data["articles"][:10]

    logger.info(
        f"Fetched {sum(len(v) for v in all_articles.values())} total financial news articles"
    )
    return all_articles


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = NewsAPIScraper()

        # Test with business category
        logger.info("Testing NewsAPI scraper with business news...")
        result = await scraper.fetch_and_save_news(
            "business", category="business", limit=5
        )
        logger.info("Business news Result: %s", result)

        # Test with technology category
        logger.info("Testing NewsAPI scraper with technology news...")
        result = await scraper.fetch_and_save_news(
            "technology", category="technology", limit=5
        )
        logger.info("Technology news Result: %s", result)

        # Test with keyword search
        logger.info("Testing NewsAPI scraper with keyword search...")
        result = await scraper.fetch_and_save_news("AAPL stock", limit=5)
        logger.info("AAPL news Result: %s", result)

        # Get top headlines
        logger.info("Getting top headlines...")
        headlines = await scraper.get_top_headlines(country="us", page_size=10)
        logger.info("Top headlines: %s", headlines)

        # Get sources
        logger.info("Getting available sources...")
        sources = await scraper.get_all_sources()
        logger.info("Found %d sources", len(sources))

    asyncio.run(main())
