"""
Search Functionality with Indexing and Ranking
Implements efficient search using Meilisearch for production-ready performance
"""
import orjson
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Search configuration
DEFAULT_SEARCH_LIMIT = 20
MAX_SEARCH_LIMIT = 100
SEARCH_TIMEOUT = 5  # seconds

# Search categories
CATEGORY_WEIGHTS = {
    'exact_match': 10.0,
    'symbol_match': 8.0,
    'name_match': 5.0,
    'volume_high': 3.0,
    'recent': 2.0,
}

# Relevance thresholds
MIN_RELEVANCE_SCORE = 0.5


class SearchResult:
    """Container for a single search result"""
    
    def __init__(
        self,
        asset_id: str,
        symbol: str,
        name: str,
        asset_type: str,
        relevance_score: float,
        match_type: str,
        highlighted: Dict[str, str]
    ):
        self.asset_id = asset_id
        self.symbol = symbol
        self.name = name
        self.asset_type = asset_type
        self.relevance_score = relevance_score
        self.match_type = match_type
        self.highlighted = highlighted
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.asset_id,
            'symbol': self.symbol,
            'name': self.name,
            'asset_type': self.asset_type,
            'relevance_score': round(self.relevance_score, 2),
            'match_type': self.match_type,
            'highlighted': self.highlighted,
        }


class SearchIndexer:
    """
    Search indexer with ranking algorithm
    
    Features:
    - Fuzzy search on symbols and names
    - Category-based filtering
    - Relevance scoring with multiple factors
    - Highlighting of matched terms
    - Caching for performance
    - Support for orjson parsing
    """
    
    def __init__(self):
        self.search_cache = {}
        self.cache_timeout = 60  # seconds
        
        # Predefined popular symbols for ranking
        self.popular_symbols = self._load_popular_symbols()
    
    def _load_popular_symbols(self) -> List[str]:
        """Load list of popular symbols for ranking boost"""
        popular = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE',
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VUG', 'VWO'
        ]
        return popular
    
    def search(
        self,
        query: str,
        asset_types: Optional[List[str]] = None,
        limit: int = DEFAULT_SEARCH_LIMIT,
        min_volume: Optional[float] = None
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Perform search with filters and ranking
        
        Args:
            query: Search query string
            asset_types: Filter by asset types (Stock, Crypto, etc.)
            limit: Maximum number of results
            min_volume: Filter by minimum 24h volume
            min_price: Filter by minimum price
            max_price: Filter by maximum price
        
        Returns:
            Tuple of (results, metadata)
        """
        start_time = datetime.now()
        
        try:
            # Normalize query
            query = query.strip().upper()
            
            if not query or len(query) < 2:
                return [], self._get_empty_metadata(query, limit)
            
            # Check cache
            cache_key = self._get_cache_key(query, asset_types, limit, min_volume, min_price, max_price)
            cached_results = self._get_cached_results(cache_key)
            
            if cached_results:
                logger.info(f"Returning cached results for query: {query}")
                return cached_results, self._get_search_metadata(len(cached_results), start_time, cached=True)
            
            # Perform search
            results = self._perform_search(
                query, asset_types, limit, min_volume, min_price, max_price
            )
            
            # Calculate search metadata
            metadata = self._get_search_metadata(len(results), start_time, cached=False)
            
            # Cache results
            self._cache_results(cache_key, results)
            
            # Log search
            logger.info(
                f"Search completed for '{query}': {len(results)} results, "
                f"took {metadata['elapsed_ms']}ms"
            )
            
            return results, metadata
        
        except Exception as e:
            logger.error(f"Search error for query '{query}': {str(e)}")
            return [], self._get_error_metadata(str(e), start_time)
    
    def _perform_search(
        self,
        query: str,
        asset_types: Optional[List[str]],
        limit: int,
        min_volume: Optional[float],
        min_price: Optional[float],
        max_price: Optional[float]
    ) -> List[Dict]:
        """Execute the actual search query"""
        from assets.models.asset_type import AssetType
        
        # Build queryset
        qs = Asset.objects.filter(is_active=True)
        
        # Asset type filter
        if asset_types:
            qs = qs.filter(asset_type__name__in=[at.upper() for at in asset_types])
        
        # Symbol match (exact or partial)
        symbol_matches = qs.filter(symbol__iexact=query)
        
        # Name match (case-insensitive)
        name_matches = qs.filter(name__icontains=query)
        
        # Combine results (symbol matches first)
        all_assets = list(symbol_matches.union(name_matches).distinct()[:limit * 2])
        
        # Get additional data for each asset
        results = []
        for asset in all_assets[:limit * 3]:  # Get extra for ranking
            # Get latest price
            latest_price = AssetPricesHistoric.objects.filter(
                asset=asset
            ).order_by('-timestamp').first()
            
            # Calculate relevance score
            search_result = self._calculate_relevance(
                asset, query, latest_price
            )
            
            # Apply price and volume filters
            if min_price and latest_price and float(latest_price.close) < min_price:
                continue
            
            if max_price and latest_price and float(latest_price.close) > max_price:
                continue
            
            if min_volume and latest_price and float(latest_price.volume) < min_volume:
                continue
            
            results.append(search_result.to_dict())
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:limit]
    
    def _calculate_relevance(
        self,
        asset: Asset,
        query: str,
        latest_price: Optional[AssetPricesHistoric]
    ) -> SearchResult:
        """
        Calculate relevance score for a search result
        
        Scoring factors:
        1. Exact symbol match: +10.0
        2. Partial symbol match: +8.0
        3. Name match: +5.0
        4. High volume: +3.0
        5. Recent update: +2.0
        6. Popular symbol: +1.0
        """
        score = 0.0
        match_type = 'none'
        highlighted = {}
        
        query = query.upper()
        symbol = asset.symbol.upper()
        name = asset.name.upper()
        
        # Exact symbol match
        if symbol == query:
            score += CATEGORY_WEIGHTS['exact_match']
            match_type = 'exact_symbol'
            highlighted['symbol'] = symbol
        # Partial symbol match
        elif query in symbol:
            score += CATEGORY_WEIGHTS['symbol_match']
            match_type = 'partial_symbol'
            highlighted['symbol'] = self._highlight_match(symbol, query)
        # Name match
        elif query in name:
            score += CATEGORY_WEIGHTS['name_match']
            match_type = 'name'
            highlighted['name'] = self._highlight_match(name, query)
        
        # Volume ranking
        if latest_price and float(latest_price.volume) > 1000000:
            score += CATEGORY_WEIGHTS['volume_high']
        
        # Recent update (within last hour)
        if latest_price:
            time_diff = (datetime.now() - latest_price.timestamp).total_seconds()
            if time_diff < 3600:  # 1 hour
                score += CATEGORY_WEIGHTS['recent']
        
        # Popular symbol boost
        if symbol in self.popular_symbols:
            score += 1.0
        
        # Ensure minimum score
        score = max(score, MIN_RELEVANCE_SCORE)
        
        return SearchResult(
            asset_id=str(asset.id),
            symbol=asset.symbol,
            name=asset.name,
            asset_type=asset.asset_type.name if asset.asset_type else 'Unknown',
            relevance_score=score,
            match_type=match_type,
            highlighted=highlighted
        )
    
    def _highlight_match(self, text: str, query: str) -> str:
        """Highlight matched portion of text"""
        query = query.upper()
        text = text.upper()
        
        start_idx = text.find(query)
        
        if start_idx == -1:
            return text
        
        end_idx = start_idx + len(query)
        
        # Return with markdown-style highlighting
        return (
            text[:start_idx] + 
            f'**{text[start_idx:end_idx]}**' + 
            text[end_idx:]
        )
    
    def _get_cache_key(
        self,
        query: str,
        asset_types: Optional[List[str]],
        limit: int,
        min_volume: Optional[float],
        min_price: Optional[float],
        max_price: Optional[float]
    ) -> str:
        """Generate cache key"""
        parts = [query]
        
        if asset_types:
            parts.append('_'.join(sorted(asset_types)))
        
        parts.append(str(limit))
        
        if min_volume is not None:
            parts.append(f"min_vol_{min_volume}")
        
        if min_price is not None:
            parts.append(f"min_price_{min_price}")
        
        if max_price is not None:
            parts.append(f"max_price_{max_price}")
        
        return '|'.join(parts)
    
    def _cache_results(self, cache_key: str, results: List[Dict]) -> None:
        """Cache search results with expiration"""
        self.search_cache[cache_key] = {
            'results': results,
            'timestamp': datetime.now(),
            'count': len(results)
        }
    
    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached results if valid"""
        cached = self.search_cache.get(cache_key)
        
        if not cached:
            return None
        
        # Check if cache is still valid
        cache_age = (datetime.now() - cached['timestamp']).total_seconds()
        
        if cache_age > self.cache_timeout:
            del self.search_cache[cache_key]
            return None
        
        return cached.get('results')
    
    def _get_search_metadata(
        self,
        result_count: int,
        start_time: datetime,
        cached: bool = False
    ) -> Dict[str, Any]:
        """Generate search metadata"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            'total_results': result_count,
            'query_time_ms': round(elapsed * 1000, 2),
            'cached': cached,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_empty_metadata(self, query: str, limit: int) -> Dict[str, Any]:
        """Get metadata for empty search"""
        return {
            'total_results': 0,
            'query_time_ms': 0,
            'cached': False,
            'timestamp': datetime.now().isoformat(),
            'message': f'Query too short or empty: "{query}"'
        }
    
    def _get_error_metadata(self, error: str, start_time: datetime) -> Dict[str, Any]:
        """Get metadata for error"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            'total_results': 0,
            'query_time_ms': round(elapsed * 1000, 2),
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions for autocomplete"""
        query = query.strip().upper()
        
        if len(query) < 2:
            return []
        
        # Get symbols that start with query
        from assets.models.asset import Asset
        
        symbols = Asset.objects.filter(
            is_active=True,
            symbol__istartswith=query
        ).values_list('symbol', flat=True)[:limit]
        
        return symbols
    
    def get_trending_assets(self, limit: int = 20) -> List[Dict]:
        """Get currently trending assets"""
        from assets.models.historic.prices import AssetPricesHistoric
        from datetime import timedelta
        
        # Get most traded assets in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        trending = AssetPricesHistoric.objects.filter(
            timestamp__gte=one_hour_ago
        ).order_by('-volume')[:limit]
        
        results = []
        for price in trending:
            results.append({
                'id': str(price.asset.id),
                'symbol': price.asset.symbol,
                'name': price.asset.name,
                'asset_type': price.asset.asset_type.name if price.asset.asset_type else 'Unknown',
                'current_price': float(price.close),
                'volume_24h': float(price.volume),
                'timestamp': price.timestamp.isoformat()
            })
        
        return results
    
    def clean_cache(self):
        """Clean expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, value in self.search_cache.items():
            cache_age = (now - value['timestamp']).total_seconds()
            
            if cache_age > self.cache_timeout:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.search_cache[key]
        
        logger.info(f"Cleaned {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.search_cache),
            'cache_timeout': self.cache_timeout,
            'popular_symbols_count': len(self.popular_symbols),
            'timestamp': datetime.now().isoformat()
        }


class AdvancedSearchIndexer(SearchIndexer):
    """
    Advanced search with Meilisearch integration for production
    
    This would be used when Meilisearch is deployed
    For now, it inherits the basic implementation
    """
    
    def __init__(self):
        super().__init__()
        self.meilisearch_client = None
    
    def _init_meilisearch(self):
        """Initialize Meilisearch client"""
        try:
            from meilisearch import Client
            self.meilisearch_client = Client('http://localhost:7700')
            logger.info("Meilisearch client initialized")
        except ImportError:
            logger.warning("Meilisearch not available, using basic search")
            self.meilisearch_client = None
    
    def search(self, *args, **kwargs) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Perform search using Meilisearch if available
        
        Falls back to basic search if not available
        """
        if self.meilisearch_client is None:
            self._init_meilisearch()
        
        if self.meilisearch_client is None:
            return super().search(*args, **kwargs)
        
        try:
            query = kwargs.get('query', '')
            limit = kwargs.get('limit', DEFAULT_SEARCH_LIMIT)
            
            # Search in Meilisearch
            index = self.meilisearch_client.index('assets')
            results = index.search(query, limit=limit)
            
            search_results = []
            for hit in results.hits:
                search_results.append({
                    'id': hit['id'],
                    'symbol': hit['symbol'],
                    'name': hit['name'],
                    'asset_type': hit['asset_type'],
                    'relevance_score': hit['_rankingScore'],
                    'match_type': 'meilisearch',
                    'highlighted': hit['_formatted']
                })
            
            metadata = {
                'total_results': len(search_results),
                'query_time_ms': results.processingTimeMs,
                'cached': False,
                'search_engine': 'meilisearch',
                'timestamp': datetime.now().isoformat()
            }
            
            return search_results, metadata
        
        except Exception as e:
            logger.error(f"Meilisearch error: {str(e)}, falling back to basic search")
            return super().search(*args, **kwargs)


# Global search indexer instance
search_indexer = AdvancedSearchIndexer()


def search_assets(query: str, **filters) -> Tuple[List[Dict], Dict]:
    """Search for assets"""
    return search_indexer.search(query, **filters)


def get_search_suggestions(query: str, limit: int = 10) -> List[str]:
    """Get search suggestions"""
    return search_indexer.get_suggestions(query, limit)


def get_trending_assets(limit: int = 20) -> List[Dict]:
    """Get trending assets"""
    return search_indexer.get_trending_assets(limit)


if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        """Test search functionality"""
        print("Testing search functionality...")
        
        # Test basic search
        results, metadata = search_assets("AAPL", limit=10)
        print(f"Search results: {len(results)}")
        print(f"Metadata: {metadata}")
        
        # Test suggestions
        suggestions = get_search_suggestions("AP")
        print(f"Suggestions: {suggestions}")
        
        # Test trending
        trending = get_trending_assets()
        print(f"Trending: {len(trending)}")
        
        # Test cache stats
        stats = search_indexer.get_cache_stats()
        print(f"Cache stats: {stats}")
    
    asyncio.run(test_search())
