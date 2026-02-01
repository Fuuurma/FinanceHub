"""
CoinMarketCap Crypto Scraper using BaseAPIFetcher for key rotation
Performance optimized with orjson and async operations
"""

import aiohttp
from typing import Dict, Optional, List, Any
import orjson

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class CoinMarketCapScraper(BaseAPIFetcher):
    """
    CoinMarketCap API implementation with key rotation

    Free tier: 10,000 requests/day, 10 requests/minute per key
    Strategy: Rotate between multiple free accounts
    """

    def __init__(self):
        super().__init__(provider_name="coinmarketcap")

    def get_base_url(self) -> str:
        return "https://pro-api.coinmarketcap.com/v1"

    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from CoinMarketCap response"""
        if "status" in response:
            status = response.get("status", {})
            error_code = status.get("error_code")
            if (
                error_code == 429
                or "rate limit" in str(status.get("error_message", "")).lower()
            ):
                return status.get("error_message", "Rate limit exceeded")
        if "error" in response:
            error = response["error"]
            if "rate" in str(error).lower() or "limit" in str(error).lower():
                return str(error)
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
            return orjson.loads(content)

    def _get_headers(self, api_key) -> Dict:
        """CoinMarketCap uses API key in header"""
        return {
            "Accept": "application/json",
            "User-Agent": "FinanceHub/1.0",
            "X-CMC_PRO_API_KEY": str(api_key.key_value),
        }

    async def get_cryptocurrency_map(self) -> Optional[Dict[str, Any]]:
        """
        Get ID map for all cryptocurrencies

        Performance: Uses async request with orjson parsing
        """
        data = await self.request("cryptocurrency/map")
        if data and isinstance(data, dict):
            return data.get("data", {})
        return None

    async def get_listings(
        self,
        start: int = 1,
        limit: int = 100,
        vs_currency: str = "usd",
        sort: str = "market_cap",
        cryptocurrency_type: str = "all",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get latest cryptocurrency listings

        Performance: Uses async request with orjson parsing
        """
        params = {
            "start": start,
            "limit": limit,
            "vs_currency": vs_currency,
            "sort": sort,
            "cryptocurrency_type": cryptocurrency_type,
        }

        data = await self.request("cryptocurrency/listings/latest", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_cryptocurrency_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cryptocurrency info by symbol

        Performance: Uses async request with orjson parsing
        """
        params = {
            "symbol": symbol,
            "aux": "cmc_rank,total_supply,max_supply,circulating_supply,logo,description,tags,platform,date_added",
        }

        data = await self.request("cryptocurrency/info", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_quotes_latest(
        self, symbol: str = None, id: str = None, convert: str = "usd"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get latest quotes for cryptocurrency

        Performance: Uses async request with orjson parsing
        """
        params = {"convert": convert}

        if symbol:
            params["symbol"] = symbol
        if id:
            params["id"] = id

        data = await self.request("cryptocurrency/quotes/latest", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return list(data["data"].values())
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
            # Get crypto info
            crypto_info = await self.get_cryptocurrency_info(symbol)
            if not crypto_info:
                logger.warning(f"Could not get crypto info for {symbol}")
                return False

            # Get latest quote
            quotes = await self.get_quotes_latest(symbol=symbol)

            # Save to database
            await self._save_asset_to_db(crypto_info, quotes, symbol)

            logger.info(f"Successfully fetched and saved data for crypto {symbol}")
            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching/saving crypto {symbol}: {str(e)}")
            return False

    async def _save_asset_to_db(
        self,
        crypto_info: Dict[str, Any],
        quotes: Optional[List[Dict[str, Any]]] = None,
        symbol: str = "",
    ):
        """Save crypto asset data to database"""
        from assets.models.asset import Asset, AssetType
        from assets.models.historic.prices import AssetPricesHistoric
        from datetime import datetime

        try:
            # Get or create asset type for crypto
            crypto_type, _ = await asyncio.to_thread(
                AssetType.objects.get_or_create,
                name="Crypto",
                defaults={"name": "Crypto"},
            )

            # Extract data from response
            if symbol in crypto_info:
                data = crypto_info[symbol]
            elif crypto_info:
                # Get first available symbol
                data = list(crypto_info.values())[0]
                symbol = data.get("symbol", symbol)
            else:
                logger.error(f"No data found in crypto_info")
                return

            # Get or create asset
            asset, created = await asyncio.to_thread(
                Asset.objects.update_or_create,
                symbol__iexact=symbol,
                defaults={
                    "symbol": symbol,
                    "name": data.get("name", symbol),
                    "asset_type": crypto_type,
                },
            )

            # Update asset details
            asset.name = data.get("name", symbol)
            asset.description = data.get("description", "")
            asset.website = (
                data.get("urls", {}).get("website", [""])[0]
                if data.get("urls", {}).get("website")
                else ""
            )

            # Save logo URL
            if "logo" in data and data["logo"]:
                asset.logo_url = data["logo"]

            asset.is_active = True

            # Save asset synchronously within async context
            await asyncio.to_thread(asset.save)

            # Save current price if available
            if quotes and len(quotes) > 0:
                quote = quotes[0]
                quote_data = quote.get("quote", {}).get("USD", {})

                if "price" in quote_data:
                    price = float(quote_data["price"])

                    await asyncio.to_thread(
                        AssetPricesHistoric.objects.create,
                        asset=asset,
                        timestamp=datetime.now(),
                        open=price,
                        high=float(quote_data.get("high_24h", price)),
                        low=float(quote_data.get("low_24h", price)),
                        close=price,
                        volume=float(quote_data.get("volume_24h", 0)),
                    )
                    logger.info(f"Saved current price for {symbol}: {price}")

            logger.info(f"Saved data for crypto asset {symbol} (created: {created})")

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error saving crypto asset {symbol} to DB: {str(e)}")

    async def get_popular_cryptos(self, limit: int = 100) -> List[str]:
        """Get list of popular cryptocurrencies to track"""
        listings = await self.get_listings(limit=limit)

        if listings:
            return [item["symbol"] for item in listings]
        return []

    async def get_cryptocurrencyhistorical_data(
        self, id: str, start: int = 1, count: int = 100, interval: str = "day"
    ) -> Optional[List[Dict]]:
        """
        Get historical market cap and price data

        Args:
            id: Cryptocurrency ID
            start: Starting position
            count: Number of data points
            interval: 'day' or 'hour'
        """
        params = {"id": id, "start": start, "count": count, "interval": interval}

        data = await self.request("cryptocurrency OHLCV", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"].get("points", [])
        return None

    async def get_market_pairs(
        self, id: str, start: int = 1, limit: int = 100
    ) -> Optional[List[Dict]]:
        """
        Get market pairs for a cryptocurrency

        Args:
            id: Cryptocurrency ID
            start: Starting position
            limit: Number of pairs
        """
        params = {
            "id": id,
            "start": start,
            "limit": limit,
            "aux": "num_market_pairs,cmc_rank,volume,price,tx_count,trade_url",
        }

        data = await self.request("cryptocurrency/market-pairs", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"].get("markets", [])
        return None

    async def get_global_metrics(self) -> Optional[Dict]:
        """
        Get global cryptocurrency market metrics
        """
        data = await self.request("global-metrics/quotes/latest")

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_trending_gainers_losers(
        self, sort: str = "percent_change_24h", sort_dir: str = "desc", limit: int = 100
    ) -> Optional[Dict]:
        """
        Get trending cryptocurrencies (gainers/losers)

        Args:
            sort: Sort field
            sort_dir: asc or desc
            limit: Number of results
        """
        params = {"sort": sort, "sort_dir": sort_dir, "limit": limit}

        data = await self.request("cryptocurrency/trending", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_trending_most_visited(self, limit: int = 100) -> Optional[List[Dict]]:
        """
        Get most visited/shilled cryptocurrencies
        """
        params = {"limit": limit}

        data = await self.request("cryptocurrency/trending/most-visited", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_exchange_map(self) -> Optional[List[Dict]]:
        """
        Get exchange ID map
        """
        data = await self.request("exchange/map")

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_exchange_listings(
        self, start: int = 1, limit: int = 100
    ) -> Optional[List[Dict]]:
        """
        Get exchange listings
        """
        params = {"start": start, "limit": limit}

        data = await self.request("exchange/listings/latest", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_exchange_info(self, slug: str) -> Optional[Dict]:
        """
        Get exchange info by slug
        """
        params = {"slug": slug, "aux": "num_market_pairs,volume,trade_url,website,logo"}

        data = await self.request("exchange/info", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_fiat_map(self) -> Optional[List[Dict]]:
        """
        Get supported fiat currencies
        """
        data = await self.request("fiat/map")

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_price_snapshot(self, id: str, convert: str = "usd") -> Optional[Dict]:
        """
        Get price and volume over time (last 24h)

        Args:
            id: Cryptocurrency ID
            convert: Convert currency
        """
        params = {"id": id, "convert": convert}

        data = await self.request(
            "cryptocurrency/price-performance-stats", params=params
        )

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    async def get_tokenomics(self, id: str) -> Optional[Dict]:
        """
        Get tokenomics and supply data

        Args:
            id: Cryptocurrency ID
        """
        params = {
            "id": id,
            "aux": "total_supply,circulating_supply,max_supply,cmc_rank,date_launched",
        }

        data = await self.request("cryptocurrency/info", params=params)

        if data and isinstance(data, dict) and "data" in data:
            return data["data"]
        return None

    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings

        scraper = cls()
        return scraper


async def get_popular_cryptos(limit: int = 100) -> List[str]:
    """Get list of popular cryptocurrencies to track"""
    scraper = CoinMarketCapScraper()
    popular_cryptos = await scraper.get_popular_cryptos(limit)

    logger.info(f"Retrieved {len(popular_cryptos)} popular cryptos from CoinMarketCap")
    return popular_cryptos


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = CoinMarketCapScraper()

        # Test with BTC
        print("Testing CoinMarketCap scraper with BTC...")
        result = await scraper.fetch_and_save_crypto("BTC")
        print(f"BTC Result: {result}")

        # Test with ETH
        print("\nTesting CoinMarketCap scraper with ETH...")
        result = await scraper.fetch_and_save_crypto("ETH")
        print(f"ETH Result: {result}")

        # Test with multiple cryptos
        print("\nTesting CoinMarketCap scraper with popular cryptos...")
        popular = await get_popular_cryptos(10)
        results = await scraper.fetch_multiple_cryptos(popular)
        print(f"Results: {results}")

        # Get crypto map
        print("\nGetting cryptocurrency map...")
        crypto_map = await scraper.get_cryptocurrency_map()
        print(f"Found {len(crypto_map)} cryptocurrencies in map")

    asyncio.run(main())
