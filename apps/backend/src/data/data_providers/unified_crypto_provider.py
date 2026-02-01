"""
Unified Crypto Data Provider
Integrates CoinGecko and CoinMarketCap with intelligent provider switching
"""
import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
import logging

import polars as pl
from django.core.cache import cache

from data.data_providers.coingecko.scraper import CoinGeckoScraper
from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper
from data.data_providers.crypto_cross_validator import get_crypto_cross_validator
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class UnifiedCryptoProvider:
    """
    Unified crypto data provider with intelligent provider selection
    
    Features:
    - Automatic provider switching based on rate limits
    - Cross-validation for data quality
    - Enhanced caching with tiered TTL
    - Batch operations with polars optimization
    - Provider health monitoring
    """
    
    def __init__(self):
        self.coingecko = CoinGeckoScraper()
        self.coinmarketcap = CoinMarketCapScraper()
        self.cross_validator = get_crypto_cross_validator()
        
        # Provider health tracking
        self.provider_health = {
            'coingecko': {
                'last_success': None,
                'last_failure': None,
                'consecutive_failures': 0,
                'is_healthy': True,
                'rate_limited_until': None
            },
            'coinmarketcap': {
                'last_success': None,
                'last_failure': None,
                'consecutive_failures': 0,
                'is_healthy': True,
                'rate_limited_until': None
            }
        }
        
        # Provider preferences
        self.primary_provider = 'coingecko'  # Default primary
        self.secondary_provider = 'coinmarketcap'
        
        # Caching configuration
        self.cache_ttl = {
            'quotes': 60,  # 1 minute
            'market_data': 300,  # 5 minutes
            'historical': 3600,  # 1 hour
            'validation': 300  # 5 minutes
        }
        
        # Batch configuration
        self.batch_size = 50  # Symbols per batch
        self.max_concurrent = 10  # Concurrent requests
    
    async def get_provider_health(self, provider: str) -> dict:
        """Get health status of a provider"""
        if provider not in self.provider_health:
            return {'is_healthy': False, 'error': 'Unknown provider'}
        
        health = self.provider_health[provider].copy()
        
        # Check if rate limit has expired
        if health['rate_limited_until']:
            if datetime.now() >= health['rate_limited_until']:
                health['rate_limited_until'] = None
                health['consecutive_failures'] = 0
                health['is_healthy'] = True
        
        # Check consecutive failures
        if health['consecutive_failures'] >= 3:
            health['is_healthy'] = False
        
        return health
    
    def _update_provider_health(self, provider: str, success: bool):
        """Update provider health status"""
        if provider not in self.provider_health:
            return
        
        health = self.provider_health[provider]
        
        if success:
            health['last_success'] = datetime.now()
            health['consecutive_failures'] = 0
            health['is_healthy'] = True
            health['rate_limited_until'] = None
        else:
            health['last_failure'] = datetime.now()
            health['consecutive_failures'] += 1
            
            # If many consecutive failures, mark as unhealthy for 5 minutes
            if health['consecutive_failures'] >= 3:
                health['is_healthy'] = False
                health['rate_limited_until'] = datetime.now() + timedelta(minutes=5)
    
    def _select_provider(self) -> str:
        """Select best available provider"""
        primary_health = asyncio.run(self.get_provider_health(self.primary_provider))
        secondary_health = asyncio.run(self.get_provider_health(self.secondary_provider))
        
        # Prefer primary if healthy
        if primary_health['is_healthy']:
            logger.debug(f"Using primary provider: {self.primary_provider}")
            return self.primary_provider
        
        # Fall back to secondary if healthy
        if secondary_health['is_healthy']:
            logger.warning(f"Primary unhealthy, using secondary: {self.secondary_provider}")
            return self.secondary_provider
        
        # Both unhealthy - use primary anyway and let it fail
        logger.error(f"Both providers unhealthy, using primary: {self.primary_provider}")
        return self.primary_provider
    
    async def fetch_crypto_data(
        self,
        symbol: str,
        use_validation: bool = True,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch crypto data with intelligent provider selection
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            use_validation: Use cross-validation
            force_refresh: Ignore cache
        
        Returns:
            Unified crypto data or None
        """
        # Check cache
        cache_key = f"crypto_data_{symbol}"
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {symbol}")
                return cached
        
        # Cross-validation if requested
        if use_validation:
            validation_result = await self.cross_validator.validate_symbol(symbol, force_refresh)
            
            # Use recommended source
            if validation_result.recommended_source == 'coingecko' and validation_result.coingecko_data:
                data = self._normalize_coingecko_data(validation_result.coingecko_data)
                self._update_provider_health('coingecko', True)
            elif validation_result.recommended_source == 'coinmarketcap' and validation_result.coinmarketcap_data:
                data = self._normalize_coinmarketcap_data(validation_result.coinmarketcap_data)
                self._update_provider_health('coinmarketcap', True)
            else:
                # Fallback to provider selection
                provider = self._select_provider()
                data = await self._fetch_from_provider(symbol, provider)
            
            # Add validation metadata
            if data:
                data['validation'] = {
                    'confidence': validation_result.overall_confidence,
                    'source': validation_result.recommended_source,
                    'price_difference_percent': float(validation_result.price_difference_percent) if validation_result.price_difference_percent else None
                }
        else:
            # Simple fetch without validation
            provider = self._select_provider()
            data = await self._fetch_from_provider(symbol, provider)
        
        # Cache and return
        if data:
            cache.set(cache_key, data, self.cache_ttl['quotes'])
        
        return data
    
    async def _fetch_from_provider(self, symbol: str, provider: str) -> Optional[Dict]:
        """Fetch data from specific provider"""
        try:
            if provider == 'coingecko':
                raw_data = await self._fetch_coingecko_raw(symbol)
                if raw_data:
                    data = self._normalize_coingecko_data(raw_data)
                    self._update_provider_health('coingecko', True)
                    return data
            elif provider == 'coinmarketcap':
                raw_data = await self._fetch_coinmarketcap_raw(symbol)
                if raw_data:
                    data = self._normalize_coinmarketcap_data(raw_data)
                    self._update_provider_health('coinmarketcap', True)
                    return data
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching {symbol} from {provider}: {str(e)}")
            self._update_provider_health(provider, False)
        
        return None
    
    async def _fetch_coingecko_raw(self, symbol: str) -> Optional[Dict]:
        """Fetch raw data from CoinGecko"""
        try:
            coin_data = await self.coingecko.get_coin(symbol.lower())
            if not coin_data:
                return None
            
            market_data = coin_data.get('market_data', {})
            
            return {
                'provider': 'coingecko',
                'price': Decimal(str(market_data.get('current_price', 0))),
                'market_cap': Decimal(str(market_data.get('market_cap', {}).get('usd', 0))),
                'volume_24h': Decimal(str(market_data.get('total_volume', {}).get('usd', 0))),
                'change_24h': Decimal(str(market_data.get('price_change_percentage_24h', 0))),
                'high_24h': Decimal(str(market_data.get('ath', 0))),
                'low_24h': Decimal(str(market_data.get('atl', 0))),
                'name': coin_data.get('name'),
                'symbol': coin_data.get('symbol', '').upper(),
                'logo': coin_data.get('image', {}).get('large'),
                'description': coin_data.get('description', {}).get('en', '')
            }
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"CoinGecko fetch error: {str(e)}")
            return None
    
    async def _fetch_coinmarketcap_raw(self, symbol: str) -> Optional[Dict]:
        """Fetch raw data from CoinMarketCap"""
        try:
            quotes = await self.coinmarketcap.get_quotes_latest(symbol=symbol)
            if not quotes or len(quotes) == 0:
                return None
            
            quote = quotes[0]
            quote_data = quote.get('quote', {}).get('USD', {})
            
            return {
                'provider': 'coinmarketcap',
                'price': Decimal(str(quote_data.get('price', 0))),
                'market_cap': Decimal(str(quote_data.get('market_cap', 0))),
                'volume_24h': Decimal(str(quote_data.get('volume_24h', 0))),
                'change_24h': Decimal(str(quote_data.get('percent_change_24h', 0))),
                'high_24h': Decimal(str(quote_data.get('high_24h', 0))),
                'low_24h': Decimal(str(quote_data.get('low_24h', 0))),
                'name': quote.get('name'),
                'symbol': quote.get('symbol'),
                'logo': quote.get('logo'),
                'description': quote.get('description', '')
            }
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"CoinMarketCap fetch error: {str(e)}")
            return None
    
    def _normalize_coingecko_data(self, data: Dict) -> Dict:
        """Normalize CoinGecko data to standard format"""
        return {
            'price': float(data.get('price', 0)),
            'market_cap': float(data.get('market_cap', 0)),
            'volume_24h': float(data.get('volume_24h', 0)),
            'change_24h': float(data.get('change_24h', 0)),
            'high_24h': float(data.get('high_24h', 0)),
            'low_24h': float(data.get('low_24h', 0)),
            'name': data.get('name'),
            'symbol': data.get('symbol'),
            'logo': data.get('logo'),
            'description': data.get('description'),
            'source': 'coingecko'
        }
    
    def _normalize_coinmarketcap_data(self, data: Dict) -> Dict:
        """Normalize CoinMarketCap data to standard format"""
        return {
            'price': float(data.get('price', 0)),
            'market_cap': float(data.get('market_cap', 0)),
            'volume_24h': float(data.get('volume_24h', 0)),
            'change_24h': float(data.get('change_24h', 0)),
            'high_24h': float(data.get('high_24h', 0)),
            'low_24h': float(data.get('low_24h', 0)),
            'name': data.get('name'),
            'symbol': data.get('symbol'),
            'logo': data.get('logo'),
            'description': data.get('description'),
            'source': 'coinmarketcap'
        }
    
    async def fetch_batch_cryptos(
        self,
        symbols: List[str],
        use_validation: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Optional[Dict]]:
        """
        Fetch multiple cryptos in batch with polars optimization
        
        Args:
            symbols: List of crypto symbols
            use_validation: Use cross-validation (slower)
            force_refresh: Ignore cache
        
        Returns:
            Dict mapping symbols to their data
        """
        logger.info(f"Batch fetching {len(symbols)} cryptos...")
        
        results = {}
        
        # Process in batches to avoid overwhelming providers
        for i in range(0, len(symbols), self.batch_size):
            batch = symbols[i:i + self.batch_size]
            logger.debug(f"Processing batch {i//self.batch_size + 1}: {len(batch)} symbols")
            
            # Fetch concurrently
            tasks = [
                self.fetch_crypto_data(symbol, use_validation, force_refresh)
                for symbol in batch
            ]
            
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for symbol, result in zip(batch, task_results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {symbol}: {str(result)}")
                    results[symbol] = None
                else:
                    results[symbol] = result
        
        # Convert to polars dataframe for processing
        valid_data = [(k, v) for k, v in results.items() if v is not None]
        
        if valid_data:
            df = pl.DataFrame([
                {
                    'symbol': v['symbol'],
                    'price': v['price'],
                    'market_cap': v['market_cap'],
                    'volume_24h': v['volume_24h'],
                    'change_24h': v['change_24h'],
                    'source': v['source'],
                    'confidence': v.get('validation', {}).get('confidence', None)
                }
                for _, v in valid_data
            ])
            
            # Calculate aggregate statistics
            stats = {
                'total_volume': df['volume_24h'].sum(),
                'total_market_cap': df['market_cap'].sum(),
                'avg_confidence': df['confidence'].mean() if 'confidence' in df.columns else None,
                'source_distribution': df.group_by('source').agg(pl.len()).to_dict(as_series=False)
            }
            
            logger.info(
                f"Batch fetch complete: {len(valid_data)}/{len(symbols)} successful, "
                f"total_volume=${stats['total_volume']:,.0f}"
            )
        
        return results
    
    async def get_trending_cryptos(self, limit: int = 10) -> List[Dict]:
        """Get trending cryptocurrencies"""
        trending_coins = await self.coingecko.get_trending(limit)
        
        if not trending_coins:
            return []
        
        # Fetch detailed data for trending coins
        symbols = [item['item'].get('id', '').upper() for item in trending_coins]
        results = await self.fetch_batch_cryptos(symbols[:limit])
        
        return [results.get(symbol) for symbol in symbols[:limit] if results.get(symbol)]
    
    async def get_top_cryptos(
        self,
        limit: int = 100,
        sort_by: str = 'market_cap'
    ) -> List[Dict]:
        """
        Get top cryptocurrencies by ranking
        
        Args:
            limit: Number of results
            sort_by: Sort field (market_cap, volume, change_24h)
        """
        # Fetch top coins from CoinGecko
        top_coins = await self.coingecko.get_top_coins_by_market_cap(limit)
        
        if not top_coins:
            return []
        
        # Extract symbols
        symbols = [coin.get('id', '').upper() for coin in top_coins]
        
        # Batch fetch detailed data
        results = await self.fetch_batch_cryptos(symbols)
        
        # Convert to list and sort
        cryptos = [results.get(symbol) for symbol in symbols if results.get(symbol)]
        
        if sort_by != 'market_cap':
            cryptos.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        return cryptos[:limit]
    
    def get_provider_summary(self) -> dict:
        """Get summary of provider health and statistics"""
        return {
            'primary_provider': self.primary_provider,
            'secondary_provider': self.secondary_provider,
            'provider_health': {
                'coingecko': self.provider_health['coingecko'],
                'coinmarketcap': self.provider_health['coinmarketcap']
            },
            'cache_config': self.cache_ttl,
            'batch_config': {
                'size': self.batch_size,
                'max_concurrent': self.max_concurrent
            }
        }


# Singleton instance
_unified_crypto_provider: Optional[UnifiedCryptoProvider] = None


def get_unified_crypto_provider() -> UnifiedCryptoProvider:
    """Get singleton unified crypto provider instance"""
    global _unified_crypto_provider
    
    if _unified_crypto_provider is None:
        _unified_crypto_provider = UnifiedCryptoProvider()
    
    return _unified_crypto_provider