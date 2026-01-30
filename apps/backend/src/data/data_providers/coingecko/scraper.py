"""
CoinGecko Crypto Scraper using BaseAPIFetcher for key rotation
Performance optimized with orjson and async operations
"""
import aiohttp
from typing import Dict, Optional, List, Any
import orjson

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class CoinGeckoScraper(BaseAPIFetcher):
    """
    CoinGecko API implementation with key rotation
    
    Free tier: 10-50 requests/minute per key
    Strategy: Rotate between multiple free accounts
    """
    
    def __init__(self):
        super().__init__(provider_name="coingecko")
    
    def get_base_url(self) -> str:
        return "https://api.coingecko.com/api/v3"
    
    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from CoinGecko response"""
        if 'error' in response:
            error = response['error']
            if any(keyword in error.lower() for keyword in ['rate limit', 'too many requests', '429']):
                return error
        if 'status' in response and response.get('status', {}).get('error_code') == 429:
            return "Rate limit exceeded"
        return None
    
    async def _make_request(self, endpoint: str, params: Optional[Dict], method: str, api_key) -> Dict:
        """Make request with async HTTP client"""
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)
        
        async with self.session.request(method, url, params=params, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()
            # Use orjson for fast parsing
            return orjson.loads(content)
    
    def _get_headers(self, api_key) -> Dict:
        """CoinGecko uses API key in header for Pro tier"""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'FinanceHub/1.0'
        }
        if api_key.key_value:
            headers['X-CMC_PRO_API_KEY'] = api_key.key_value
        return headers
    
    async def get_coin_list(self, vs_currency: str = "usd", per_page: int = 250, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of coins with price, market cap and 24h change
        
        Performance: Uses async request with orjson parsing
        """
        params = {
            'vs_currency': vs_currency,
            'per_page': per_page,
            'page': page,
            'order': 'market_cap_desc',
            'sparkline': False,
            'price_change_percentage': '24h',
            'locale': 'en'
        }
        
        data = await self.request("coins/markets", params=params)
        
        if data and isinstance(data, list):
            return data
        return None
    
    async def get_top_coins_by_market_cap(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get top coins by market cap"""
        return await self.get_coin_list(per_page=limit, page=1)
    
    async def get_coin_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 365
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get coin market chart data
        
        Performance: Uses async request with orjson parsing
        """
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        
        data = await self.request(f"coins/{coin_id}/market_chart", params=params)
        
        if data and isinstance(data, dict):
            return data.get('prices', [])
        return None
    
    async def get_coin(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get coin data by ID with full details"""
        return await self.request(f"coins/{coin_id}")
    
    async def search_coins(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for coins by name, symbol or ID"""
        params = {
            'query': query,
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1
        }
        
        data = await self.request("search", params=params)
        
        if data and 'coins' in data:
            return data['coins']
        return None
    
    async def get_trending(self, limit: int = 7) -> Optional[List[Dict[str, Any]]]:
        """Get trending cryptocurrencies"""
        data = await self.request("search/trending")
        
        if data and 'coins' in data:
            return data['coins'][:limit]
        return None
    
    async def get_all_coins_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of all supported coins
        
        Performance: Large operation, use with caution
        """
        data = await self.request("coins/list")
        
        if data and isinstance(data, list):
            return data
        return None
    
    async def fetch_multiple_cryptos(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Fetch multiple cryptocurrencies with async operations
        
        Performance: Processes requests concurrently for better throughput
        """
        results = {}
        async with self:
            tasks = [self.fetch_and_save_crypto(symbol) for symbol in symbols]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, result in zip(symbols, task_results):
                if isinstance(result, Exception):
                    results[symbol] = False
                    logger.error(f"Error fetching {symbol}: {str(result)}")
                else:
                    results[symbol] = result
        return results
    
    async def fetch_and_save_crypto(self, symbol: str) -> bool:
        """
        Fetch and save a single cryptocurrency
        
        Performance: Uses async operations and orjson
        """
        try:
            coin_id = symbol.lower()
            
            # Get coin data
            coin_data = await self.get_coin(coin_id)
            if not coin_data:
                logger.warning(f"Could not get coin data for {symbol}")
                return False
            
            # Get market chart data (last 365 days)
            chart_data = await self.get_coin_market_chart(coin_id, days=365)
            
            # Save to database
            await self._save_asset_to_db(coin_data, chart_data, symbol)
            
            logger.info(f"Successfully fetched and saved data for crypto {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching/saving crypto {symbol}: {str(e)}")
            return False
    
    async def _save_asset_to_db(
        self,
        coin_data: Dict[str, Any],
        chart_data: Optional[List] = None,
        symbol: str = ""
    ):
        """Save crypto asset data to database"""
        from assets.models.asset import Asset, AssetType
        from assets.models.historic.prices import AssetPricesHistoric
        from datetime import datetime
        
        try:
            # Get or create asset type for crypto
            crypto_type, _ = await asyncio.to_thread(
                AssetType.objects.get_or_create,
                name='Crypto',
                defaults={'name': 'Crypto'}
            )
            
            # Get or create asset
            asset, created = await asyncio.to_thread(
                Asset.objects.update_or_create,
                symbol__iexact=symbol,
                defaults={
                    'symbol': symbol,
                    'name': coin_data.get('name', symbol),
                    'asset_type': crypto_type,
                }
            )
            
            # Update asset details
            asset.name = coin_data.get('name', symbol)
            asset.description = coin_data.get('description', '').get('en', '')
            asset.country = coin_data.get('country')
            asset.website = coin_data.get('links', {}).get('homepage', '')
            
            # Save image URL
            if 'image' in coin_data and 'large' in coin_data['image']:
                asset.logo_url = coin_data['image']['large']
            
            asset.is_active = True
            
            # Save asset synchronously within async context
            await asyncio.to_thread(asset.save)
            
            # Save current price if available
            market_data = coin_data.get('market_data', {})
            if 'current_price' in market_data:
                current_price = float(market_data.get('current_price', 0))
                
                await asyncio.to_thread(
                    AssetPricesHistoric.objects.create,
                    asset=asset,
                    timestamp=datetime.now(),
                    open=current_price,
                    high=float(market_data.get('ath', 0)),
                    low=float(market_data.get('atl', 0)),
                    close=current_price,
                    volume=float(market_data.get('total_volume', 0))
                )
                logger.info(f"Saved current price for {symbol}: {current_price}")
            
            # Save historical prices efficiently
            if chart_data:
                count = 0
                for price_point in chart_data[:300]:  # Save last 300 days
                    try:
                        timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                        
                        await asyncio.to_thread(
                            AssetPricesHistoric.objects.create,
                            asset=asset,
                            timestamp=timestamp,
                            open=float(price_point[1]),
                            high=float(price_point[1]),
                            low=float(price_point[1]),
                            close=float(price_point[1]),
                            volume=0
                        )
                        count += 1
                    except Exception as e:
                        logger.debug(f"Error saving price point for {symbol}: {str(e)}")
                        continue
                
                logger.info(f"Saved {count} historical prices for {symbol}")
            
            logger.info(f"Saved data for crypto asset {symbol} (created: {created})")
            
        except Exception as e:
            logger.error(f"Error saving crypto asset {symbol} to DB: {str(e)}")
    
    async def get_popular_cryptos(self, limit: int = 100) -> List[str]:
        """Get list of popular cryptocurrencies to track"""
        coins = await self.get_top_coins_by_market_cap(limit)
        
        if coins:
            return [coin['id'].upper() for coin in coins]
        return []
    
    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings
        scraper = cls()
        return scraper


async def get_popular_cryptos(limit: int = 100) -> List[str]:
    """Get list of popular cryptocurrencies to track"""
    scraper = CoinGeckoScraper()
    popular_cryptos = await scraper.get_popular_cryptos(limit)
    
    logger.info(f"Retrieved {len(popular_cryptos)} popular cryptos from CoinGecko")
    return popular_cryptos


async def get_trending_cryptos(limit: int = 7) -> List[str]:
    """Get trending cryptocurrencies"""
    scraper = CoinGeckoScraper()
    trending = await scraper.get_trending(limit)
    
    if trending:
        return [item['item']['id'].upper() for item in trending]
    return []


if __name__ == "__main__":
    import asyncio
    
    async def main():
        scraper = CoinGeckoScraper()
        
        # Test with BTC
        print("Testing CoinGecko scraper with BTC...")
        result = await scraper.fetch_and_save_crypto('BTC')
        print(f"BTC Result: {result}")
        
        # Test with ETH
        print("\nTesting CoinGecko scraper with ETH...")
        result = await scraper.fetch_and_save_crypto('ETH')
        print(f"ETH Result: {result}")
        
        # Test with multiple cryptos
        print("\nTesting CoinGecko scraper with popular cryptos...")
        popular = await get_popular_cryptos(10)
        results = await scraper.fetch_multiple_cryptos(popular)
        print(f"Results: {results}")
        
        # Get trending
        print("\nGetting trending cryptos...")
        trending = await get_trending_cryptos(7)
        print(f"Trending: {trending}")
    
    asyncio.run(main())
