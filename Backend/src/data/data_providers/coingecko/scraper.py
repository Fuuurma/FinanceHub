"""
CoinGecko Crypto Data Scraper
Fetches cryptocurrency data from CoinGecko API
"""
import requests
import orjson
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset_type import AssetType
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class CoinGeckoScraper:
    """CoinGecko API scraper using requests and orjson"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 30
        self.session = requests.Session()
        
        # Free tier: 10-50 requests/minute
        # Rate limiting: 1 request per second
        self.rate_limit_delay = 1.2  # seconds between requests
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a request to CoinGecko API with rate limiting"""
        try:
            import time
            time.sleep(self.rate_limit_delay)
            
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            
            # Parse JSON with orjson for faster performance
            data = orjson.loads(response.content)
            
            # Check for API errors
            if 'error' in data:
                logger.error(f"CoinGecko API error: {data['error']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing CoinGecko response: {str(e)}")
            return None
    
    def get_coin(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get coin data by ID
        Documentation: https://www.coingecko.com/en/api/v3/#get_coin_data_by_id
        """
        data = self._make_request(f"coins/{coin_id}")
        return data
    
    def get_coin_list(self, vs_currency: str = "usd", per_page: int = 250, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of coins with price, market cap, and 24h change
        Documentation: https://www.coingecko.com/en/api/v3/#get_coins_markets
        """
        data = self._make_request("coins/markets", {
            'vs_currency': vs_currency,
            'per_page': per_page,
            'page': page,
            'order': 'market_cap_desc',
            'sparkline': False,
            'price_change_percentage': '24h',
            'locale': 'en'
        })
        
        if data and 'data' in data:
            return data['data']
        return None
    
    def get_top_coins_by_market_cap(self, limit: int = 100) -> Optional[List[Dict[str, Any]]):
        """Get top coins by market cap"""
        return self.get_coin_list(per_page=limit, page=1)
    
    def get_coin_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 365
    ) -> Optional[List[Dict[str, Any]]):
        """
        Get coin market chart data
        Days: 1, 7, 14, 30, 90, 180, 365, max
        Documentation: https://www.coingecko.com/en/api/v3/#get_coin_market_chart
        """
        data = self._make_request(f"coins/{coin_id}/market_chart", {
            'vs_currency': vs_currency,
            'days': days
        })
        
        if data:
            return data.get('prices', [])
        return None
    
    def get_all_coins_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of all supported coins
        Note: This is a large operation, use with caution
        Documentation: https://www.coingecko.com/en/api/v3#/coins/list
        """
        data = self._make_request("coins/list")
        
        if data:
            return data
        return None
    
    def search_coins(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Search for coins by name, symbol or ID
        Documentation: https://www.coingecko.com/en/api/v3#/search_coins
        """
        data = self._make_request("search", {
            'query': query,
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1
        })
        
        if data and 'coins' in data:
            return data['coins']
        return None
    
    def fetch_and_save_crypto(self, symbol: str) -> bool:
        """
        Complete workflow: fetch crypto data and save to database
        Returns True if successful
        """
        try:
            # Get coin data
            coin_data = self.get_coin(symbol.lower())
            if not coin_data:
                logger.warning(f"Could not get coin data for {symbol}")
                return False
            
            # Get market chart data (last 365 days)
            chart_data = self.get_coin_market_chart(symbol.lower(), days=365)
            if not chart_data:
                logger.warning(f"Could not get market chart for {symbol}")
            
            # Save to database
            self._save_asset_to_db(coin_data, chart_data)
            
            logger.info(f"Successfully fetched and saved data for crypto {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching/saving crypto {symbol}: {str(e)}")
            return False
    
    def _save_asset_to_db(
        self,
        coin_data: Dict[str, Any],
        chart_data: Optional[List] = None
    ):
        """Save crypto asset data to database"""
        symbol = coin_data.get('id', '').upper()
        
        try:
            # Get or create asset type for crypto
            crypto_type, _ = AssetType.objects.get_or_create(
                name='Crypto',
                defaults={'name': 'Crypto'}
            )
            
            # Get or create asset
            asset, created = Asset.objects.update_or_create(
                symbol__iexact=symbol,
                defaults={
                    'symbol': symbol,
                    'name': coin_data.get('name', symbol),
                    'asset_type': crypto_type,
                }
            )
            
            # Update asset details
            asset.name = coin_data.get('name', symbol)
            asset.description = coin_data.get('description', coin_data.get('description', '').get('en', ''))
            asset.country = coin_data.get('country')
            asset.website = coin_data.get('links', {}).get('homepage')
            
            # Save image URL
            if 'image' in coin_data and coin_data['image']:
                asset.logo_url = coin_data['image']
            
            asset.is_active = True
            asset.save()
            
            # Save current price if available
            market_data = coin_data.get('market_data', {})
            if 'current_price' in market_data:
                AssetPricesHistoric.objects.create(
                    asset=asset,
                    timestamp=datetime.now(),
                    open=float(market_data.get('current_price', market_data.get('current_price', 0))),
                    high=float(market_data.get('ath', 0)),
                    low=float(market_data.get('atl', 0)),
                    close=float(market_data.get('current_price', market_data.get('current_price', 0))),
                    volume=float(market_data.get('total_volume', 0))
                )
                logger.info(f"Saved current price for {symbol}: {market_data.get('current_price')}")
            
            # Save historical prices
            if chart_data:
                count = 0
                for price_point in chart_data[:300]:  # Save last 300 days
                    try:
                        timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                        AssetPricesHistoric.objects.create(
                            asset=asset,
                            timestamp=timestamp,
                            open=float(price_point[1]) if len(price_point) > 1 else float(price_point[1]) if len(price_point) > 1 else float(price_point[1]),
                            high=float(price_point[2]) if len(price_point) > 2 else float(price_point[2]) if len(price_point) > 2 else float(price_point[1]),
                            low=float(price_point[3]) if len(price_point) > 3 else float(price_point[3]) if len(price_point) > 3 else float(price_point[1]),
                            close=float(price_point[1]),
                            volume=0
                        )
                        count += 1
                    except Exception as e:
                        continue
                
                logger.info(f"Saved {count} historical prices for {symbol}")
            
            logger.info(f"Saved data for crypto asset {symbol} (created: {created})")
            
        except Exception as e:
            logger.error(f"Error saving crypto asset {symbol} to DB: {str(e)}")
    
    def fetch_multiple_cryptos(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Fetch data for multiple cryptocurrencies with rate limiting
        Returns dictionary mapping symbol to success status
        """
        results = {}
        
        for symbol in symbols:
            results[symbol] = self.fetch_and_save_crypto(symbol)
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"CoinGecko: Fetched data for {success_count}/{len(symbols)} cryptos")
        
        return results
    
    def get_popular_cryptos(self, limit: int = 100) -> List[str]:
        """Get list of popular cryptocurrencies to track"""
        coins = self.get_top_coins_by_market_cap(limit)
        
        if coins:
            return [coin['id'].upper() for coin in coins]
        return []
    
    def get_trending_cryptos(self, limit: int = 7) -> List[str]:
        """
        Get trending cryptocurrencies
        Documentation: https://www.coingecko.com/en/api/v3#/get_trending
        """
        data = self._make_request("search/trending")
        
        if data and 'coins' in data:
            trending = []
            for item in data['coins'][:limit]:
                trending.append(item['item']['id'].upper())
            return trending
        
        return []


def get_popular_cryptos() -> List[str]:
    """Get list of popular cryptocurrencies to track"""
    scraper = CoinGeckoScraper()
    popular_cryptos = scraper.get_popular_cryptos(100)
    
    logger.info(f"Retrieved {len(popular_cryptos)} popular cryptos from CoinGecko")
    return popular_cryptos


def get_trending_cryptos() -> List[str]:
    """Get trending cryptocurrencies"""
    scraper = CoinGeckoScraper()
    trending = scraper.get_trending_cryptos(7)
    
    logger.info(f"Retrieved {len(trending)} trending cryptos from CoinGecko")
    return trending


if __name__ == "__main__":
    scraper = CoinGeckoScraper()
    
    # Test with BTC
    print("Testing CoinGecko scraper with BTC...")
    scraper.fetch_and_save_crypto('BTC')
    
    # Test with ETH
    print("\nTesting CoinGecko scraper with ETH...")
    scraper.fetch_and_save_crypto('ETH')
    
    # Test with multiple cryptos
    print("\nTesting CoinGecko scraper with popular cryptos...")
    popular = get_popular_cryptos()[:10]
    results = scraper.fetch_multiple_cryptos(popular)
    print(f"Results: {results}")
    
    # Get trending
    print("\nGetting trending cryptos...")
    trending = get_trending_cryptos()
    print(f"Trending: {trending}")
