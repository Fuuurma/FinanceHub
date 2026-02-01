"""
WebSocket Message Manager
Handles broadcasting price updates to subscribed clients
"""

import orjson
import asyncio
import logging
from channels.layers import get_channel_layer
from channels.exceptions import ChannelFull
from datetime import datetime, timedelta

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from data.data_providers.binance.scraper import BinanceScraper
from data.data_providers.yahooFinance.scraper import YahooFinanceScraper
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

channel_layer = get_channel_layer()


# Initialize scrapers for real-time data
binance_scraper = BinanceScraper()
yahoo_scraper = YahooFinanceScraper()


class PriceBroadcaster:
    """
    Manages broadcasting price updates to WebSocket clients

    Features:
    - Tracks active symbol subscriptions
    - Fetches real-time prices from multiple sources
    - Broadcasts updates to subscribed users
    - Handles connection errors gracefully
    """

    def __init__(self):
        self.active_symbols = set()
        self.symbol_prices = {}
        self.last_update = {}
        self.update_intervals = {
            "crypto": 5,  # seconds
            "stock": 60,  # seconds (Yahoo doesn't have real-time)
        }
        self._running = False

    async def start(self):
        """Start the price broadcaster"""
        if self._running:
            logger.warning("Price broadcaster already running")
            return

        self._running = True
        logger.info("Starting price broadcaster")

        # Start update tasks
        await asyncio.gather(
            [self._update_crypto_prices(), self._update_stock_prices()]
        )

    async def stop(self):
        """Stop the price broadcaster"""
        self._running = False
        logger.info("Stopping price broadcaster")

    async def _update_crypto_prices(self):
        """Update crypto prices from Binance"""
        while self._running:
            try:
                # Get all active crypto symbols
                if not self.active_symbols:
                    await asyncio.sleep(self.update_intervals["crypto"])
                    continue

                # Fetch prices from Binance
                from assets.models.asset_type import AssetType

                crypto_type = AssetType.objects.filter(name__iexact="Crypto").first()

                if crypto_type:
                    assets = Asset.objects.filter(
                        asset_type=crypto_type, is_active=True
                    ).values_list("symbol", flat=True)

                    # Convert to Binance format (add USDT)
                    binance_symbols = [f"{symbol}USDT" for symbol in assets if symbol]

                    # Fetch ticker data
                    all_tickers = binance_scraper.get_all_tickers()

                    if all_tickers:
                        updates = []
                        for ticker in all_tickers:
                            if (
                                ticker["symbol"].replace("USDT", "")
                                in self.active_symbols
                            ):
                                updates.append(
                                    {
                                        "symbol": ticker["symbol"],
                                        "price": ticker["price"],
                                        "change": ticker.get("change", 0),
                                        "change_percent": ticker.get(
                                            "change_percent", 0
                                        ),
                                        "high": ticker["high"],
                                        "low": ticker["low"],
                                        "open": ticker["open"],
                                        "volume": ticker["volume"],
                                    }
                                )

                        # Broadcast updates
                        await self._broadcast_price_updates(updates)

                        # Store prices
                        for update in updates:
                            self.symbol_prices[update["symbol"]] = update
                            self.last_update[update["symbol"]] = datetime.now()

                # Wait before next update
                await asyncio.sleep(self.update_intervals["crypto"])

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Error updating crypto prices: {str(e)}")
                await asyncio.sleep(10)

    async def _update_stock_prices(self):
        """Update stock prices from Yahoo Finance"""
        while self._running:
            try:
                # Get all active stock symbols
                from assets.models.asset_type import AssetType

                stock_type = AssetType.objects.filter(name__iexact="Stock").first()

                if not stock_type or not self.active_symbols:
                    await asyncio.sleep(self.update_intervals["stock"])
                    continue

                assets = Asset.objects.filter(
                    asset_type=stock_type,
                    is_active=True,
                    symbol__in=self.active_symbols,
                )

                updates = []

                for asset in assets:
                    # Fetch latest price from database
                    latest_price = (
                        AssetPricesHistoric.objects.filter(asset=asset)
                        .order_by("-timestamp")
                        .first()
                    )

                    if latest_price:
                        updates.append(
                            {
                                "symbol": asset.symbol,
                                "price": float(latest_price.close),
                                "change": 0,  # Would be calculated
                                "change_percent": 0,
                                "high": float(latest_price.high),
                                "low": float(latest_price.low),
                                "open": float(latest_price.open),
                                "volume": float(latest_price.volume),
                            }
                        )

                if updates:
                    await self._broadcast_price_updates(updates)

                # Wait before next update
                await asyncio.sleep(self.update_intervals["stock"])

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Error updating stock prices: {str(e)}")
                await asyncio.sleep(10)

    async def _broadcast_price_updates(self, updates: list):
        """Broadcast price updates to all subscribed clients"""
        if not updates:
            return

        for update in updates:
            symbol = update["symbol"]

            # Broadcast to symbol's channel
            channel_name = f"asset_{symbol}_prices"

            message = {
                "type": "price_update",
                "symbol": symbol,
                "data": update,
                "timestamp": datetime.now().isoformat(),
            }

            try:
                await channel_layer.group_send(channel_name, message)
                logger.debug(
                    f"Broadcasted price update for {symbol}: {update.get('price')}"
                )

            except ChannelFull:
                logger.warning(f"Channel full for {symbol}, skipping update")
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Error broadcasting to {symbol}: {str(e)}")

    def subscribe_symbol(self, symbol: str):
        """Add symbol to active subscriptions"""
        self.active_symbols.add(symbol.upper())
        logger.info(f"Added symbol to subscriptions: {symbol}")

    def unsubscribe_symbol(self, symbol: str):
        """Remove symbol from active subscriptions"""
        self.active_symbols.discard(symbol.upper())
        logger.info(f"Removed symbol from subscriptions: {symbol}")

    def get_symbol_price(self, symbol: str) -> dict:
        """Get current cached price for a symbol"""
        return self.symbol_prices.get(symbol.upper(), {})


# Global broadcaster instance
price_broadcaster = PriceBroadcaster()


async def start_price_broadcaster():
    """Start the global price broadcaster"""
    await price_broadcaster.start()


async def stop_price_broadcaster():
    """Stop the global price broadcaster"""
    await price_broadcaster.stop()


if __name__ == "__main__":
    import asyncio

    async def test():
        """Test the price broadcaster"""
        logger.info("Starting price broadcaster test...")

        # Subscribe to some symbols
        price_broadcaster.subscribe_symbol("BTC")
        price_broadcaster.subscribe_symbol("ETH")
        price_broadcaster.subscribe_symbol("AAPL")

        # Start broadcaster
        await start_price_broadcaster()

        # Run for 30 seconds
        await asyncio.sleep(30)

        # Stop broadcaster
        await stop_price_broadcaster()

        logger.info("Final prices: %s", price_broadcaster.symbol_prices)

    asyncio.run(test())
