"""
Finnhub API Scraper with WebSocket support for real-time data
Best for real-time prices, WebSocket streaming, and news with sentiment
"""
import aiohttp
import asyncio
import websockets
from typing import Dict, Optional, List, Any, Callable
from datetime import datetime, timedelta
import logging
import json

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class FinnhubScraper(BaseAPIFetcher):
    """
    Finnhub API implementation with WebSocket support
    
    Free tier: 60 requests/minute
    Strategy: Use WebSocket for real-time data, REST for everything else
    
    Data Available:
    - Real-time stock prices (WebSocket)
    - WebSocket streaming for top stocks
    - News with sentiment analysis
    - Company fundamentals
    - Stock splits and dividends
    - Pattern recognition
    - Technical indicators (SMA, EMA, RSI, MACD, Bollinger)
    - 1 year of historical data
    """
    
    # WebSocket URL
    WS_BASE_URL = "wss://ws.finnhub.io"
    
    def __init__(self):
        super().__init__(provider_name="finnhub")
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.subscribed_symbols: Set[str] = set()
        self.callbacks: Dict[str, Callable] = {}
        self.is_connected = False
    
    def get_base_url(self) -> str:
        return "https://api.finnhub.io/api/v1"
    
    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from Finnhub response"""
        if isinstance(response, dict):
            if 'error' in response:
                error = response['error']
                if any(keyword in error.lower() for keyword in ['rate limit', 'too many', '429']):
                    return str(error)
            if response.get('statusCode') == 429:
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
            import orjson
            return orjson.loads(content)
    
    def _get_headers(self, api_key) -> Dict:
        """Finnhub uses API key in query string (not header)"""
        return {
            'Accept': 'application/json',
            'User-Agent': 'FinanceHub/1.0'
        }
    
    async def connect_websocket(self, api_key: str) -> bool:
        """Connect to Finnhub WebSocket"""
        try:
            logger.info("Connecting to Finnhub WebSocket...")
            
            self.websocket = await websockets.connect(
                f"{self.WS_BASE_URL}?token={api_key.key_value}",
                ping_interval=20,
                ping_timeout=60,
                close_timeout=10
            )
            
            self.is_connected = True
            logger.info("Successfully connected to Finnhub WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Finnhub WebSocket: {str(e)}")
            return False
    
    async def disconnect_websocket(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from Finnhub WebSocket")
    
    async def subscribe_trades(self, symbol: str, callback: Optional[Callable] = None) -> bool:
        """
        Subscribe to real-time trades via WebSocket
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            callback: Callback for trade updates
        """
        try:
            if not self.is_connected:
                logger.warning("WebSocket not connected, cannot subscribe")
                return False
            
            channel = f'{"type":"subscribe","symbol":"{symbol}"}'
            await self.websocket.send(channel)
            
            self.subscribed_symbols.add(symbol)
            
            if callback:
                self.callbacks[f'trades_{symbol}'] = callback
            
            logger.info(f"Subscribed to trades for {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Error subscribing to trades for {symbol}: {str(e)}")
            return False
    
    async def subscribe_quote(self, symbol: str, callback: Optional[Callable] = None) -> bool:
        """
        Subscribe to real-time quotes via WebSocket
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            callback: Callback for quote updates
        """
        try:
            if not self.is_connected:
                logger.warning("WebSocket not connected, cannot subscribe")
                return False
            
            channel = f'{"type":"subscribe","symbol":"{symbol}"}'
            await self.websocket.send(channel)
            
            self.subscribed_symbols.add(symbol)
            
            if callback:
                self.callbacks[f'quote_{symbol}'] = callback
            
            logger.info(f"Subscribed to quote for {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Error subscribing to quote for {symbol}: {str(e)}")
            return False
    
    async def subscribe_candles(
        self,
        symbol: str,
        resolution: str = "D",
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Subscribe to candlestick data via WebSocket
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            resolution: Candle resolution (1, 5, 15, 60, D, W, M)
            callback: Callback for candle updates
        """
        try:
            if not self.is_connected:
                logger.warning("WebSocket not connected, cannot subscribe")
                return False
            
            channel = f'{"type":"subscribe","symbol":"{symbol}","resolution":"{resolution}"}'
            await self.websocket.send(channel)
            
            if callback:
                self.callbacks[f'candles_{symbol}_{resolution}'] = callback
            
            logger.info(f"Subscribed to candles ({resolution}) for {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Error subscribing to candles for {symbol}: {str(e)}")
            return False
    
    async def unsubscribe_trades(self, symbol: str) -> bool:
        """Unsubscribe from trades"""
        try:
            channel = f'{"type":"unsubscribe","symbol":"{symbol}"}'
            await self.websocket.send(channel)
            self.subscribed_symbols.discard(symbol)
            logger.info(f"Unsubscribed from trades for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing trades for {symbol}: {str(e)}")
            return False
    
    async def listen_websocket(self):
        """
        Listen for WebSocket messages and dispatch to callbacks
        This is a blocking call, should be run in a task
        """
        if not self.websocket:
            logger.error("WebSocket not connected")
            return
        
        try:
            logger.info("Listening for Finnhub WebSocket messages...")
            
            async for message in self.websocket:
                self._process_websocket_message(message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Finnhub WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in listen loop: {str(e)}")
    
    async def _process_websocket_message(self, message):
        """Process WebSocket message and dispatch to callbacks"""
        try:
            if isinstance(message, str):
                data = json.loads(message)
            else:
                data = message
            
            # Handle different message types
            if data.get('type') == 'trade':
                symbol = data.get('data', {}).get('s', '')
                callback = self.callbacks.get(f'trades_{symbol}')
                if callback:
                    await self._run_callback(callback, data['data'])
            
            elif data.get('type') == 'quote':
                symbol = data.get('data', {}).get('s', '')
                callback = self.callbacks.get(f'quote_{symbol}')
                if callback:
                    await self._run_callback(callback, data['data'])
            
            elif data.get('type') == 'candle':
                symbol = data.get('data', {}).get('s', '')
                resolution = data.get('data', {}).get('i', 'D')
                callback = self.callbacks.get(f'candles_{symbol}_{resolution}')
                if callback:
                    await self._run_callback(callback, data['data'])
            
            logger.debug(f"Processed WebSocket message: {data.get('type')}")
        
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
    
    async def _run_callback(self, callback: Callable, data: dict):
        """Run callback function"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote for a symbol"""
        params = {'symbol': symbol}
        return await self.request("quote", params)
    
    async def get_quotes(self, symbols: List[str]) -> Optional[Dict]:
        """Get quotes for multiple symbols"""
        params = {'symbol': ','.join(symbols)}
        return await self.request("quote", params)
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile"""
        params = {'symbol': symbol}
        return await self.request("stock/profile2", params)
    
    async def get_company_basic_financials(self, symbol: str) -> Optional[Dict]:
        """Get company basic financials"""
        params = {'symbol': symbol, 'metric': 'all'}
        return await self.request("stock/metric", params)
    
    async def get_financials(
        self,
        symbol: str,
        metric: str = 'all'
    ) -> Optional[Dict]:
        """Get financial metrics"""
        params = {'symbol': symbol, 'metric': metric}
        return await self.request("stock/metric", request="stock/metric", params=params)
    
    async def get_peers(self, symbol: str) -> Optional[Dict]:
        """Get peer comparison"""
        params = {'symbol': symbol}
        return await self.request("stock/peers", params)
    
    async def get_news(
        self,
        symbol: Optional[str] = None,
        min_id: Optional[int] = None
        limit: int = 20
    ) -> Optional[Dict]:
        """
        Get news with sentiment analysis
        
        Args:
            symbol: Stock ticker (optional)
            min_id: Only fetch news with ID greater than this
            limit: Number of articles
        """
        params = {}
        
        if symbol:
            params['symbol'] = symbol
        if min_id:
            params['minId'] = min_id
        if limit:
            params['limit'] = limit
        
        return await self.request("news", params)
    
    async def get_company_news(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """Get company-specific news"""
        params = {'symbol': symbol, 'id': 0}
        return await self.request("company/news", params)
    
    async def get_stock_splits(self, symbol: str, from_date: Optional[str] = None) -> Optional[Dict]:
        """Get stock splits"""
        params = {'symbol': symbol}
        if from_date:
            params['from'] = from_date
        return await self.request("stock/split", params)
    
    async def get_dividends(self, symbol: str, from_date: Optional[str] = None) -> Optional[Dict]:
        """Get dividends"""
        params = {'symbol': symbol}
        if from_date:
            params['from'] = from_date
        return await self.request("stock/dividend", params)
    
    async def get_symbol_recommendation(
        self,
        symbol: str
    ) -> Optional[Dict]:
        """Get symbol recommendation (buy/sell/hold)"""
        params = {'symbol': symbol}
        return await self.request("stock/recommendation", params)
    
    async def get_price_target(self, symbol: str) -> Optional[Dict]:
        """Get analyst price targets"""
        params = {'symbol': symbol}
        return await self.request("stock/price-target", params)
    
    async def get_estimates(
        self,
        symbol: str
    ) -> Optional[Dict]:
        """Get earnings estimates"""
        params = {'symbol': symbol}
        return await self.request("stock/earnings", params)
    
    async def get_technical_indicators(
        self,
        symbol: str,
        indicator: str,
        resolution: str = "D",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get technical indicators
        
        Args:
            symbol: Stock ticker
            indicator: Indicator type (sma, ema, rsi, macd, bbands)
            resolution: Time resolution (1, 5, 15, 60, D, W, M)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        """
        params = {'symbol': symbol, 'indicator': indicator, 'resolution': resolution}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        return await self.request(f"indicator/{indicator}", params)
    
    async def get_pattern_recognition(
        self,
        symbol: str,
        pattern: str = "candlestick"
    ) -> Optional[Dict]:
        """
        Get pattern recognition
        
        Args:
            symbol: Stock ticker
            pattern: Pattern type (candlestick)
        """
        params = {'symbol': symbol, 'pattern': pattern}
        return await self.request("scan/pattern", params)
    
    async def fetch_and_save_stock(
        self,
        symbol: str,
        historical_days: int = 365
        use_websocket: bool = False
    ) -> bool:
        """
        Fetch and save stock data to database
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            historical_days: Number of days of historical data
            use_websocket: Whether to use WebSocket for real-time data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from assets.models.asset import Asset, AssetType
            from assets.models.historic.prices import AssetPricesHistoric
            from datetime import timedelta
            import asyncio
            
            # Get or create asset type for stock
            stock_type, _ = await asyncio.to_thread(
                AssetType.objects.get_or_create,
                name='Stock',
                defaults={'name': 'Stock'}
            )
            
            # Get or create asset
            asset, created = await asyncio.to_thread(
                Asset.objects.update_or_create,
                symbol__iexact=symbol,
                defaults={
                    'symbol': symbol,
                    'name': symbol,
                    'asset_type': stock_type,
                }
            )
            
            # Get company profile
            profile = await self.get_company_profile(symbol)
            
            if profile and isinstance(profile, dict):
                asset.name = profile.get('name', symbol)
                asset.description = profile.get('description', '')
                asset.website = profile.get('weburl', '')
                asset.logo_url = profile.get('logo', '')
                asset.industry = profile.get('gics', {}).get('sector', '')
                asset.country = profile.get('country', '')
                asset.is_active = True
                
                await asyncio.to_thread(asset.save)
                
                logger.info(f"Saved company profile for {symbol}")
            
            # Get current quote
            quote = await self.get_quote(symbol)
            
            if quote and isinstance(quote, dict):
                price_data = quote.get('c', {})
                
                await asyncio.to_thread(
                    AssetPricesHistoric.objects.create,
                    asset=asset,
                    timestamp=datetime.now(),
                    open=float(price_data.get('o', 0)),
                    high=float(price_data.get('h', 0)),
                    low=float(price_data.get('l', 0)),
                    close=float(price_data.get('c', 0)),
                    volume=float(price_data.get('v', 0))
                )
                
                logger.info(f"Saved current price for {symbol}: {price_data.get('c')}")
            
            # Get historical data
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=historical_days)
                
                candles = await self.get_technical_indicators(
                    symbol,
                    indicator='candle',
                    resolution='D',
                    from_date=start_date.strftime('%Y-%m-%d'),
                    to_date=end_date.strftime('%Y-%m-%d')
                )
                
                if candles and isinstance(candles, dict) and 'data' in candles:
                    count = 0
                    for candle in candles['data']:
                        try:
                            await asyncio.to_thread(
                                AssetPricesHistoric.objects.create,
                                asset=asset,
                                timestamp=datetime.strptime(candle['t'][:10], '%Y-%m-%d'),
                                open=float(candle['o'], 0)),
                                high=float(candle['h'], 0)),
                                low=float(candle['l'], 0)),
                                close=float(candle['c'], 0)),
                                volume=float(candle['v'], 0))
                            )
                            count += 1
                        except Exception as e:
                            logger.debug(f"Error saving candle for {symbol}: {str(e)}")
                            continue
                    
                    logger.info(f"Saved {count} historical prices for {symbol}")
            
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            
            # Get news
            try:
                news = await self.get_company_news(symbol, limit=5)
                
                if news and isinstance(news, dict) and 'data' in news:
                    logger.info(f"Fetched {len(news['data'])} news articles for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {str(e)}")
            
            logger.info(f"Successfully fetched and saved data for stock {symbol} (created: {created})")
            return True
        
        except Exception as e:
            logger.error(f"Error fetching/saving stock {symbol}: {str(e)}")
            return False
    
    async def fetch_multiple_stocks(
        self,
        symbols: List[str],
        historical_days: int = 365
    ) -> Dict[str, bool]:
        """
        Fetch multiple stocks with batch operations
        
        Args:
            symbols: List of stock tickers
            historical_days: Number of days of historical data
        
        Returns:
            Dict mapping symbols to success/failure
        """
        logger.info(f"Fetching {len(symbols)} stocks from Finnhub...")
        
        results = {}
        async with self:
            tasks = [self.fetch_and_save_stock(symbol, historical_days) for symbol in symbols]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, result in zip(symbols, task_results):
                if isinstance(result, Exception):
                    results[symbol] = False
                    logger.error(f"Error fetching {symbol}: {str(result)}")
                else:
                    results[symbol] = result
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Finnhub: {success_count}/{len(symbols)} stocks fetched successfully")
        
        return results
    
    async def get_popular_stocks(self, limit: int = 20) -> List[str]:
        """Get list of popular stocks to track"""
        from tasks.data_fetcher import POPULAR_STOCKS
        return POPULAR_STOCKS[:limit]
    
    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings
        scraper = cls()
        return scraper


async def get_popular_stocks(limit: int = 20) -> List[str]:
    """Get list of popular stocks to track"""
    scraper = FinnhubScraper()
    popular_stocks = await scraper.get_popular_stocks(limit)
    
    logger.info(f"Retrieved {len(popular_stocks)} popular stocks from Finnhub")
    return popular_stocks


if __name__ == "__main__":
    import asyncio
    
    async def main():
        scraper = FinnhubScraper()
        
        # Test with AAPL
        print("Testing Finnhub scraper with AAPL...")
        result = await scraper.fetch_and_save_stock('AAPL')
        print(f"AAPL Result: {result}")
        
        # Test with MSFT
        print("\nTesting Finnhub scraper with MSFT...")
        result = await scraper.fetch_and_save_stock('MSFT')
        print(f"MSFT Result: {result}")
        
        # Get quote
        print("\nGetting quote for AAPL...")
        quote = await scraper.get_quote('AAPL')
        print(f"Quote: {quote}")
        
        # Get news
        print("\nGetting news for AAPL...")
        news = await scraper.get_company_news('AAPL')
        print(f"News: {news}")
        
        # Get financials
        print("\nGetting financials for AAPL...")
        financials = await scraper.get_financials('AAPL')
        print(f"Financials: {financials}")
    
    asyncio.run(main())