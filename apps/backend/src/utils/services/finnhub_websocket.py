"""
Finnhub WebSocket Client
Manages real-time WebSocket connections for live stock prices
"""

import asyncio
import websockets
import json
import logging
from typing import Set, Dict, Callable, Optional
from datetime import datetime

from django.utils import timezone
from assets.models.asset import Asset
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class FinnhubWebSocketClient:
    """
    Finnhub WebSocket client for real-time stock data

    Features:
    - Real-time quote streaming
    - Trade streaming
    - Aggregated candle streaming
    - News updates
    """

    WS_URL = "wss://ws.finnhub.io?token={token}"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.subscriptions: Set[str] = set()
        self.is_connected = False
        self.listeners: Dict[str, Callable] = {}

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            url = self.WS_URL.format(token=self.api_key)
            logger.info(f"Connecting to Finnhub WebSocket...")
            self.websocket = await websockets.connect(url)
            self.is_connected = True

            # Start message listener
            asyncio.create_task(self._listen_messages())
            logger.info("Finnhub WebSocket connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Finnhub WebSocket: {e}")
            raise

    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            self.subscriptions.clear()
            logger.info("Finnhub WebSocket disconnected")

    async def subscribe_quote(self, symbol: str):
        """Subscribe to real-time quotes for a symbol"""
        if not self.is_connected:
            raise ConnectionError("WebSocket not connected")

        # Convert symbol to format expected by Finnhub
        # Finnhub expects uppercase symbols without suffixes
        symbol_upper = symbol.replace("-USD", "").upper()

        message = {"type": "subscribe", "symbol": symbol_upper}

        await self.websocket.send(json.dumps(message))
        self.subscriptions.add(symbol_upper)
        logger.info(f"Subscribed to quotes for {symbol_upper}")

    async def unsubscribe_quote(self, symbol: str):
        """Unsubscribe from quotes for a symbol"""
        if not self.is_connected:
            return

        symbol_upper = symbol.replace("-USD", "").upper()

        message = {"type": "unsubscribe", "symbol": symbol_upper}

        await self.websocket.send(json.dumps(message))
        self.subscriptions.discard(symbol_upper)
        logger.info(f"Unsubscribed from quotes for {symbol_upper}")

    async def subscribe_news(self, symbols: list[str]):
        """Subscribe to news for symbols"""
        if not self.is_connected:
            raise ConnectionError("WebSocket not connected")

        # Finnhub supports news subscriptions
        for symbol in symbols:
            symbol_upper = symbol.replace("-USD", "").upper()
            message = {"type": "subscribe", "symbol": symbol_upper}
            await self.websocket.send(json.dumps(message))
            logger.info(f"Subscribed to news for {symbol_upper}")

    def add_listener(self, event_type: str, callback: Callable):
        """Add a callback listener for specific event types"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.info(f"Added listener for {event_type}")

    async def _listen_messages(self):
        """Listen for WebSocket messages and process them"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode message: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            self.is_connected = False

    async def _handle_message(self, data: dict):
        """Handle incoming WebSocket message"""
        msg_type = data.get("type")

        if msg_type == "quote":
            await self._handle_quote_update(data)
        elif msg_type == "news":
            await self._handle_news_update(data)
        elif msg_type == "ping":
            # Respond to ping
            await self.websocket.send(json.dumps({"type": "pong"}))
        elif msg_type == "error":
            logger.error(f"WebSocket error: {data}")
        else:
            logger.debug(f"Unhandled message type: {msg_type}")

    async def _handle_quote_update(self, data: dict):
        """Handle real-time quote update"""
        try:
            symbol = data.get("s", "").upper()
            current_price = data.get("c")  # Current price
            change = data.get("d")  # Change
            percent_change = data.get("dp")  # Percent change
            high = data.get("h")  # High price of the day
            low = data.get("l")  # Low price of the day
            open_price = data.get("o")  # Open price
            prev_close = data.get("pc")  # Previous close
            volume = data.get("v")  # Volume

            # Update Asset model
            asset = Asset.objects.filter(ticker=symbol).first()
            if asset and current_price:
                from decimal import Decimal

                asset.last_price = Decimal(str(current_price))
                asset.last_price_updated_at = timezone.now()

                # Update metadata with intraday info
                asset.metadata.update(
                    {
                        "intraday_high": high,
                        "intraday_low": low,
                        "open_price": open_price,
                        "prev_close": prev_close,
                        "change": change,
                        "percent_change": percent_change,
                        "volume_24h": volume,
                    }
                )
                asset.save()

                logger.debug(f"Updated {symbol} price: {current_price}")

            # Call registered listeners
            if "quote" in self.listeners:
                for callback in self.listeners["quote"]:
                    await callback(data)

        except Exception as e:
            logger.error(f"Error handling quote update: {e}")

    async def _handle_news_update(self, data: dict):
        """Handle news update from WebSocket"""
        try:
            # Save news article to database
            from investments.models.news import NewsArticle
            from decimal import Decimal

            # Parse news data from Finnhub format
            headline = data.get("headline", "")
            summary = data.get("summary", "")
            url = data.get("url", "")
            source = data.get("source", "Finnhub")
            timestamp = datetime.fromtimestamp(data.get("datetime", 0))
            related = data.get("related", [])

            # Sentiment analysis (Finnhub provides sentiment)
            sentiment = "neutral"
            sentiment_score = 0

            if "positive" in headline.lower():
                sentiment = "positive"
                sentiment_score = 0.5
            elif "negative" in headline.lower():
                sentiment = "negative"
                sentiment_score = -0.5

            # Create or update news article
            article, created = NewsArticle.objects.update_or_create(
                url=url,
                defaults={
                    "title": headline,
                    "description": summary,
                    "source": source,
                    "published_at": timestamp,
                    "sentiment": sentiment,
                    "sentiment_score": Decimal(str(sentiment_score)),
                    "related_symbols": related,
                },
            )

            if created:
                logger.info(f"Saved news article: {headline[:50]}...")

            # Call registered listeners
            if "news" in self.listeners:
                for callback in self.listeners["news"]:
                    await callback(data)

        except Exception as e:
            logger.error(f"Error handling news update: {e}")

    async def get_connection_status(self) -> dict:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "subscriptions": list(self.subscriptions),
            "listener_count": sum(
                len(callbacks) for callbacks in self.listeners.values()
            ),
        }
