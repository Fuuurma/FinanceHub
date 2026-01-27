"""
CoinMarketCap Crypto Data Scraper
Fetches cryptocurrency data from CoinMarketCap API
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


class CoinMarketCapScraper:
    """CoinMarketCap API scraper using requests and orjson"""
    
    def __init__(self):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.timeout = 30
        self.session = requests.Session()
        
        # Free tier: 10,000 requests per day, 10 requests per minute
        # Rate limiting: 6 seconds between requests
        self.rate_limit_delay = 6
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a request to CoinMarketCap API with rate limiting"""
        try:
            import time
            time.sleep(self.rate_limit_delay)
            
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={'X-CMC_PRO_API_KEY': ''}  # Empty for free tier
            )
            
            # Parse JSON with orjson for faster performance
            data = orjson.loads(response.content)
            
            # Check for API errors
            if 'status' in data and data['status']['error_code'] != 0:
                logger.error(f"CoinMarketCap API error: {data['status']['error_message']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinMarketCap request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing CoinMarketCap response: {str(e)}")
            return None
    
    def get_cryptocurrency_map(self) -> Optional[Dict[str, Any]]:
        """
        Get ID map for all cryptocurrencies
        Documentation: https://coinmarketcap.com/api/documentation/v1/
        """
        data = self._make_request("cryptocurrency/map")
        return data.get('data', {})
    
    def get_listings(
        self,
        start: int = 1,
        limit: int = 100,
        vs_currency: str = "usd",
        sort: str = "market_cap",
        cryptocurrency_type: str = "all"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get latest cryptocurrency listings
        start: Start offset (for pagination, min 1)
        limit: Number of records to return (max 5000)
        vs_currency: Target currency (default: usd)
        sort: Sort order (id, market_cap, symbol, name, circulating_supply, total_volume)
        cryptocurrency_type: all, coins, tokens
        """
        data = self._make_request("cryptocurrency/listings/latest", {
            'start': start,
            'limit': limit,
            'vs_currency': vs_currency,
            'sort': sort,
            'cryptocurrency_type': cryptocurrency_type
        })
        
        if data and 'data' in data:
            return data['data']
        return None
    
    def get_cryptocurrency_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cryptocurrency info by symbol (identifier)
        Returns data for a single cryptocurrency
        """
        # Get ID map first
        coin_map = self.get_cryptocurrency_map()
        if not coin_map:
            return None
        
        # Find coin by symbol
        coin_id = next((cid, coin) for cid, coin in coin_map.items() 
                      if coin.get('symbol', '').lower() == symbol.lower())
        
        if not coin_id:
            logger.warning(f"Coin {symbol} not found in CoinMarketCap")
            return None
        
        # Get coin info
        data = self._make_request(f"cryptocurrency/info", {
            'id': coin_id
        })
        
        if data and 'data' in data and len(data['data']) > 0:
            return data['data'][0]
        return None
    
    def get_ohlcv_historical(
        self,
        symbol: str,
        interval: str = "daily",
        time_start: Optional[str] = None,
        time_end: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get OHLCV historical prices
        interval: hourly, daily
        """
        # Get coin info to get ID
        coin_info = self.get_cryptocurrency_info(symbol)
        if not coin_info:
            return None
        
        coin_id = coin_info.get('id')
        
        params = {
            'id': coin_id,
            'interval': interval
        }
        
        if time_start:
            params['time_start'] = time_start
        if time_end:
            params['time_end'] = time_end
        
        data = self._make_request(f"cryptocurrency/ohlcv/historical", params)
        
        if data and 'data' in data:
            return data['data']
        return None
    
    def get_trending(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get trending cryptocurrencies (gainers and losers)
        Documentation: https://coinmarketcap.com/api/documentation/v1/
        """
        data = self._make_request("cryptocurrency/trending", {
            'limit': limit
        })
        
        if data and 'data' in data:
            return data['data']
        return None
    
    def fetch_and_save_crypto(self, symbol: str) -> bool:
        """
        Complete workflow: fetch crypto data and save to database
        Returns True if successful
        """
        try:
            # Get coin info
            coin_info = self.get_cryptocurrency_info(symbol)
            if not coin_info:
                logger.warning(f"Could not get coin info for {symbol}")
                return False
            
            # Get historical prices (last 365 days)
            historical_data = self.get_ohlcv_historical(symbol, interval='daily')
            if not historical_data:
                logger.warning(f"Could not get historical data for {symbol}")
                # Save with just coin info
                self._save_asset_to_db(coin_info, None)
                return True
            
            # Save to database
            self._save_asset_to_db(coin_info, historical_data)
            
            logger.info(f"Successfully fetched and saved data for crypto {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching/saving crypto {symbol}: {str(e)}")
            return False
    
    def _save_asset_to_db(
        self,
        coin_info: Dict[str, Any],
        historical_data: Optional[List] = None
    ):
        """Save crypto asset data to database"""
        symbol = coin_info.get('symbol', '').upper()
        name = coin_info.get('name', '')
        
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
                    'name': name,
                    'asset_type': crypto_type,
                }
            )
            
            # Update asset details
            asset.name = name
            asset.description = coin_info.get('description', '')
            asset.website = coin_info.get('urls', {}).get('website')
            asset.logo_url = coin_info.get('image', {}).get('large', '')
            asset.is_active = True
            asset.save()
            
            # Save current price if available
            quote = coin_info.get('quote', {})
            if quote and 'USD' in quote:
                usd_quote = quote['USD']
                AssetPricesHistoric.objects.create(
                    asset=asset,
                    timestamp=datetime.now(),
                    open=float(usd_quote.get('open', 0)),
                    high=float(usd_quote.get('high', 0)),
                    low=float(usd_quote.get('low', 0)),
                    close=float(usd_quote.get('price', 0)),
                    volume=float(usd_quote.get('volume', 0))
                )
                logger.info(f"Saved current price for {symbol}: {usd_quote.get('price')}")
            
            # Save historical prices
            if historical_data:
                count = 0
                for price_point in historical_data[:300]:  # Save last 300 days
                    try:
                        timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                        AssetPricesHistoric.objects.create(
                            asset=asset,
                            timestamp=timestamp,
                            open=float(price_point[1]) if len(price_point) > 1 else float(price_point[1]),
                            high=float(price_point[2]) if len(price_point) > 2 else float(price_point[2]),
                            low=float(price_point[3]) if len(price_point) > 3 else float(price_point[3]) if len(price_point) > 3 else float(price_point[1]),
                            close=float(price_point[4]),
                            volume=float(price_point.get('volume', 0))
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
        logger.info(f"CoinMarketCap: Fetched data for {success_count}/{len(symbols)} cryptos")
        
        return results
    
    def get_top_cryptos_by_volume(self, limit: int = 100) -> List[str]:
        """Get top cryptocurrencies by 24h volume"""
        listings = self.get_listings(limit=limit, sort='volume_24h')
        
        if listings:
            return [coin.get('symbol', '') for coin in listings]
        return []
    
    def get_trending_cryptos(self, limit: int = 10) -> List[str]:
        """Get trending cryptocurrencies"""
        trending_data = self.get_trending(limit=limit)
        
        if trending_data:
            return [coin.get('symbol', '') for coin in trending_data]
        return []


def get_popular_cryptos() -> List[str]:
    """Get list of popular cryptocurrencies to track"""
    scraper = CoinMarketCapScraper()
    popular = scraper.get_top_cryptos_by_volume(100)
    
    logger.info(f"Retrieved {len(popular)} popular cryptos from CoinMarketCap")
    return popular


def get_trending_cryptos() -> List[str]:
    """Get trending cryptocurrencies"""
    scraper = CoinMarketCapScraper()
    trending = scraper.get_trending_cryptos(7)
    
    logger.info(f"Retrieved {len(trending)} trending cryptos from CoinMarketCap")
    return trending


if __name__ == "__main__":
    scraper = CoinMarketCapScraper()
    
    # Test with BTC
    print("Testing CoinMarketCap scraper with BTC...")
    scraper.fetch_and_save_crypto('BTC')
    
    # Test with ETH
    print("\nTesting CoinMarketCap scraper with ETH...")
    scraper.fetch_and_save_crypto('ETH')
    
    # Test with multiple cryptos
    print("\nTesting CoinMarketCap scraper with popular cryptos...")
    popular = get_popular_cryptos()[:10]
    results = scraper.fetch_multiple_cryptos(popular)
    print(f"Results: {results}")
    
    # Get trending
    print("\nGetting trending cryptos...")
    trending = get_trending_cryptos()
    print(f"Trending: {trending}")
