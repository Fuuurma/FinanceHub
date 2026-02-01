"""Binance Order Book Depth Analysis Service"""

import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from collections import defaultdict, deque
from datetime import datetime
import logging

import polars as pl

from utils.helpers.logger.logger import get_logger
from .websocket_client import get_binance_ws_client
from .base import BinanceFetcher

logger = get_logger(__name__)


class OrderBookDepth:
    """
    Order book depth data structure
    
    L2 (Level 2): Top N bids/asks
    L3 (Level 3): Full order book with price level aggregation
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: Dict[Decimal, Decimal] = {}
        self.asks: Dict[Decimal, Decimal] = {}
        self.last_update_id: Optional[int] = None
        self.last_update_time: Optional[datetime] = None
        self.best_bid: Optional[Tuple[Decimal, Decimal]] = None
        self.best_ask: Optional[Tuple[Decimal, Decimal]] = None
        self.spread: Optional[Decimal] = None
    
    def update_bids(self, bids: List[Tuple[Decimal, Decimal]]):
        """Update bid side"""
        for price, quantity in bids:
            if quantity == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = quantity
        
        self._update_best_bid()
    
    def update_asks(self, asks: List[Tuple[Decimal, Decimal]]):
        """Update ask side"""
        for price, quantity in asks:
            if quantity == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = quantity
        
        self._update_best_ask()
    
    def _update_best_bid(self):
        """Update best bid (highest buy price)"""
        if self.bids:
            best_price = max(self.bids.keys())
            self.best_bid = (best_price, self.bids[best_price])
        else:
            self.best_bid = None
        
        self._update_spread()
    
    def _update_best_ask(self):
        """Update best ask (lowest sell price)"""
        if self.asks:
            best_price = min(self.asks.keys())
            self.best_ask = (best_price, self.asks[best_price])
        else:
            self.best_ask = None
        
        self._update_spread()
    
    def _update_spread(self):
        """Update spread"""
        if self.best_bid and self.best_ask:
            bid_price, _ = self.best_bid
            ask_price, _ = self.best_ask
            self.spread = ask_price - bid_price
    
    def get_top_bids(self, n: int = 10) -> List[Tuple[Decimal, Decimal]]:
        """Get top N bids (sorted by price descending)"""
        sorted_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)
        return sorted_bids[:n]
    
    def get_top_asks(self, n: int = 10) -> List[Tuple[Decimal, Decimal]]:
        """Get top N asks (sorted by price ascending)"""
        sorted_asks = sorted(self.asks.items(), key=lambda x: x[0])
        return sorted_asks[:n]
    
    def get_depth_at_price(self, price: Decimal, side: str, levels: int = 100) -> Decimal:
        """
        Get total volume depth at or near price level
        
        Args:
            price: Target price
            side: 'bid' or 'ask'
            levels: Number of price levels to aggregate
        """
        orders = self.bids if side == 'bid' else self.asks
        
        if side == 'bid':
            relevant = [(p, q) for p, q in orders.items() if p <= price]
            relevant = sorted(relevant, key=lambda x: x[0], reverse=True)[:levels]
        else:
            relevant = [(p, q) for p, q in orders.items() if p >= price]
            relevant = sorted(relevant, key=lambda x: x[0])[:levels]
        
        return sum(q for _, q in relevant)
    
    def get_imbalance(self, levels: int = 10) -> Decimal:
        """
        Calculate order book imbalance
        
        Returns:
            Ratio > 1: More buy pressure
            Ratio < 1: More sell pressure
            Ratio = 1: Balanced
        """
        top_bids = self.get_top_bids(levels)
        top_asks = self.get_top_asks(levels)
        
        bid_volume = sum(q for _, q in top_bids)
        ask_volume = sum(q for _, q in top_asks)
        
        if ask_volume == 0:
            return Decimal('inf')
        
        return bid_volume / ask_volume
    
    def get_price_impact(self, quantity: Decimal, side: str) -> Optional[Decimal]:
        """
        Calculate price impact for a trade of given size
        
        Args:
            quantity: Trade size
            side: 'buy' or 'sell'
        
        Returns:
            Average slippage as percentage
        """
        orders = self.asks if side == 'buy' else self.bids
        
        if side == 'buy':
            sorted_orders = sorted(orders.items(), key=lambda x: x[0])
        else:
            sorted_orders = sorted(orders.items(), key=lambda x: x[0], reverse=True)
        
        remaining = quantity
        total_value = Decimal(0)
        
        for price, qty in sorted_orders:
            if remaining <= 0:
                break
            
            fill_qty = min(remaining, qty)
            total_value += price * fill_qty
            remaining -= fill_qty
        
        if remaining > 0:
            return None
        
        avg_price = total_value / quantity
        
        if side == 'buy' and self.best_ask:
            best_price, _ = self.best_ask
            return ((avg_price - best_price) / best_price) * Decimal(100)
        elif side == 'sell' and self.best_bid:
            best_price, _ = self.best_bid
            return ((best_price - avg_price) / best_price) * Decimal(100)
        
        return None
    
    def to_dict(self, levels: int = 10) -> dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'last_update_id': self.last_update_id,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'best_bid': {
                'price': float(self.best_bid[0]) if self.best_bid else None,
                'quantity': float(self.best_bid[1]) if self.best_bid else None
            },
            'best_ask': {
                'price': float(self.best_ask[0]) if self.best_ask else None,
                'quantity': float(self.best_ask[1]) if self.best_ask else None
            },
            'spread': float(self.spread) if self.spread else None,
            'spread_percent': float((self.spread / self.best_bid[0]) * 100) if self.spread and self.best_bid else None,
            'imbalance': float(self.get_imbalance(levels)) if self.best_bid and self.best_ask else None,
            'bids': [
                {'price': float(p), 'quantity': float(q)}
                for p, q in self.get_top_bids(levels)
            ],
            'asks': [
                {'price': float(p), 'quantity': float(q)}
                for p, q in self.get_top_asks(levels)
            ]
        }


class BinanceOrderBookService:
    """
    Binance Order Book Depth Analysis Service
    
    Features:
    - Real-time order book updates via WebSocket
    - L2 depth (top N levels)
    - L3 depth (full order book with diff updates)
    - Order imbalance analysis
    - Price impact calculation
    - Liquidity assessment
    """
    
    def __init__(self):
        self.order_books: Dict[str, OrderBookDepth] = {}
        self.ws_client = get_binance_ws_client()
        self.rest_client = BinanceFetcher()
        
        # History for trend analysis
        self.bid_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.ask_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.imbalance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    async def initialize_depth(self, symbol: str, level: int = 20):
        """
        Initialize order book for symbol with snapshot
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            level: Number of depth levels (5, 10, 20, 50, 100, 500, 1000, 5000)
        """
        try:
            logger.info(f"Initializing order book for {symbol} (level {level})...")
            
            # Get snapshot via REST API
            async with self.rest_client:
                snapshot = await self.rest_client.get_order_book(symbol, limit=level)
            
            # Create order book
            order_book = OrderBookDepth(symbol)
            
            # Parse bids
            bids = []
            for price_str, qty_str in snapshot.get('bids', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                bids.append((price, qty))
            
            # Parse asks
            asks = []
            for price_str, qty_str in snapshot.get('asks', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                asks.append((price, qty))
            
            # Update order book
            order_book.update_bids(bids)
            order_book.update_asks(asks)
            order_book.last_update_id = snapshot.get('lastUpdateId')
            order_book.last_update_time = datetime.now()
            
            self.order_books[symbol] = order_book
            
            logger.info(f"Order book initialized for {symbol}: {len(bids)} bids, {len(asks)} asks")
            
            # Subscribe to real-time updates
            await self._subscribe_depth_updates(symbol, level)
            
            return order_book
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error initializing order book for {symbol}: {str(e)}")
            raise
    
    async def _subscribe_depth_updates(self, symbol: str, level: int = 20):
        """Subscribe to real-time order book updates"""
        try:
            # Define callback for depth updates
            async def on_depth_update(data: dict):
                await self._process_depth_update(symbol, data)
            
            # Subscribe to depth updates
            await self.ws_client.subscribe_depth(symbol, level, on_depth_update)
            
            logger.info(f"Subscribed to depth updates for {symbol}")
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error subscribing to depth updates for {symbol}: {str(e)}")
    
    async def _subscribe_depth_diff_updates(self, symbol: str, update_speed: str = '100ms'):
        """
        Subscribe to L3 order book diff updates
        
        Args:
            symbol: Trading pair
            update_speed: Update speed (100ms, 250ms, 500ms, 1000ms)
        """
        try:
            # Define callback for diff updates
            async def on_depth_diff(data: dict):
                await self._process_depth_diff(symbol, data)
            
            # Subscribe to depth diff updates
            await self.ws_client.subscribe_depth_diff(symbol, update_speed, on_depth_diff)
            
            logger.info(f"Subscribed to depth diff updates for {symbol}")
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error subscribing to depth diff for {symbol}: {str(e)}")
    
    async def _process_depth_update(self, symbol: str, data: dict):
        """
        Process depth snapshot update
        
        Args:
            symbol: Trading pair
            data: Depth data from WebSocket
        """
        try:
            order_book = self.order_books.get(symbol)
            if not order_book:
                logger.warning(f"Order book not found for {symbol}")
                return
            
            # Parse bids
            bids = []
            for price_str, qty_str in data.get('bids', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                bids.append((price, qty))
            
            # Parse asks
            asks = []
            for price_str, qty_str in data.get('asks', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                asks.append((price, qty))
            
            # Update order book
            order_book.update_bids(bids)
            order_book.update_asks(asks)
            order_book.last_update_id = data.get('lastUpdateId')
            order_book.last_update_time = datetime.now()
            
            # Update history
            self._update_history(symbol, order_book)
            
            logger.debug(f"Updated order book for {symbol}: {len(bids)} bids, {len(asks)} asks")
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error processing depth update for {symbol}: {str(e)}")
    
    async def _process_depth_diff(self, symbol: str, data: dict):
        """
        Process depth diff update (L3 level)
        
        Args:
            symbol: Trading pair
            data: Depth diff data from WebSocket
        """
        try:
            order_book = self.order_books.get(symbol)
            if not order_book:
                logger.warning(f"Order book not found for {symbol}")
                return
            
            # Parse bids (format: [price, quantity])
            bids = []
            for price_str, qty_str in data.get('b', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                bids.append((price, qty))
            
            # Parse asks
            asks = []
            for price_str, qty_str in data.get('a', []):
                price = Decimal(str(price_str))
                qty = Decimal(str(qty_str))
                asks.append((price, qty))
            
            # Update order book
            order_book.update_bids(bids)
            order_book.update_asks(asks)
            order_book.last_update_id = data.get('lastUpdateId')
            order_book.last_update_time = datetime.now()
            
            # Update history
            self._update_history(symbol, order_book)
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error processing depth diff for {symbol}: {str(e)}")
    
    def _update_history(self, symbol: str, order_book: OrderBookDepth):
        """Update order book history for trend analysis"""
        if order_book.best_bid:
            self.bid_history[symbol].append(order_book.best_bid)
        
        if order_book.best_ask:
            self.ask_history[symbol].append(order_book.best_ask)
        
        imbalance = order_book.get_imbalance(10)
        if imbalance:
            self.imbalance_history[symbol].append(imbalance)
    
    async def get_order_book(self, symbol: str, levels: int = 10) -> Optional[dict]:
        """Get current order book for symbol"""
        order_book = self.order_books.get(symbol)
        if not order_book:
            logger.warning(f"Order book not found for {symbol}")
            return None
        
        return order_book.to_dict(levels)
    
    async def get_depth_summary(self, symbol: str) -> Optional[dict]:
        """Get depth summary statistics"""
        order_book = self.order_books.get(symbol)
        if not order_book:
            return None
        
        return {
            'symbol': symbol,
            'best_bid': float(order_book.best_bid[0]) if order_book.best_bid else None,
            'best_ask': float(order_book.best_ask[0]) if order_book.best_ask else None,
            'spread': float(order_book.spread) if order_book.spread else None,
            'imbalance': float(order_book.get_imbalance(10)) if order_book.best_bid else None,
            'total_bids': len(order_book.bids),
            'total_asks': len(order_book.asks),
            'bid_volume': float(sum(order_book.bids.values())),
            'ask_volume': float(sum(order_book.asks.values())),
            'liquidity_score': self._calculate_liquidity_score(order_book)
        }
    
    def _calculate_liquidity_score(self, order_book: OrderBookDepth) -> float:
        """
        Calculate liquidity score based on order book depth
        
        Returns score between 0-100
        """
        if not order_book.best_bid or not order_book.best_ask:
            return 0.0
        
        # Factors:
        # 1. Total volume (40%)
        # 2. Spread tightness (30%)
        # 3. Order book balance (30%)
        
        total_volume = sum(order_book.bids.values()) + sum(order_book.asks.values())
        spread = order_book.spread
        mid_price = (order_book.best_bid[0] + order_book.best_ask[0]) / 2
        imbalance = order_book.get_imbalance(10)
        
        # Volume score (logarithmic scale)
        volume_score = min(100, 20 * (float(total_volume) ** 0.3))
        
        # Spread score (lower is better)
        spread_pct = (spread / mid_price) * 100
        spread_score = max(0, 100 - spread_pct * 100)
        
        # Balance score (closer to 1 is better)
        balance_score = 100 * (1 - abs(imbalance - 1) / 2)
        
        # Weighted average
        liquidity_score = (volume_score * 0.4 + spread_score * 0.3 + balance_score * 0.3)
        
        return min(100, max(0, liquidity_score))
    
    async def get_price_impact_analysis(self, symbol: str, trade_sizes: List[float]) -> Optional[dict]:
        """
        Analyze price impact for various trade sizes
        
        Args:
            symbol: Trading pair
            trade_sizes: List of trade sizes to analyze
        
        Returns:
            Dict with price impact for each size
        """
        order_book = self.order_books.get(symbol)
        if not order_book:
            return None
        
        results = {}
        
        for size in trade_sizes:
            quantity = Decimal(str(size))
            
            buy_impact = order_book.get_price_impact(quantity, 'buy')
            sell_impact = order_book.get_price_impact(quantity, 'sell')
            
            results[float(size)] = {
                'buy_impact_percent': float(buy_impact) if buy_impact else None,
                'sell_impact_percent': float(sell_impact) if sell_impact else None,
                'avg_impact_percent': float((buy_impact + sell_impact) / 2) if buy_impact and sell_impact else None
            }
        
        return results
    
    async def get_depth_distribution(self, symbol: str, bins: int = 20) -> Optional[dict]:
        """
        Analyze depth distribution across price levels
        
        Args:
            symbol: Trading pair
            bins: Number of price bins
        
        Returns:
            Depth distribution analysis
        """
        order_book = self.order_books.get(symbol)
        if not order_book or not order_book.best_bid or not order_book.best_ask:
            return None
        
        mid_price = (order_book.best_bid[0] + order_book.best_ask[0]) / 2
        price_range = mid_price * Decimal(0.01)  # 1% around mid price
        
        # Build dataframe for analysis
        bid_data = []
        for price, qty in order_book.bids.items():
            if mid_price - price_range <= price <= mid_price:
                bid_data.append({
                    'price': float(price),
                    'quantity': float(qty),
                    'side': 'bid'
                })
        
        ask_data = []
        for price, qty in order_book.asks.items():
            if mid_price <= price <= mid_price + price_range:
                ask_data.append({
                    'price': float(price),
                    'quantity': float(qty),
                    'side': 'ask'
                })
        
        if not bid_data and not ask_data:
            return None
        
        df = pl.DataFrame(bid_data + ask_data)
        
        # Bin by price
        min_price = float(mid_price - price_range)
        max_price = float(mid_price + price_range)
        bin_width = (max_price - min_price) / bins
        
        df_binned = df.with_columns([
            ((pl.col('price') - min_price) / bin_width).floor().alias('bin').cast(pl.Int32)
        ])
        
        # Aggregate by bin
        depth_dist = (
            df_binned
            .group_by('bin', 'side')
            .agg([
                pl.col('quantity').sum().alias('total_quantity'),
                pl.col('price').mean().alias('avg_price')
            ])
            .sort('bin', 'side')
        )
        
        return {
            'symbol': symbol,
            'mid_price': float(mid_price),
            'price_range': float(price_range),
            'bin_count': bins,
            'distribution': depth_dist.to_dict(as_series=False)
        }
    
    async def start(self, symbols: List[str], level: int = 20):
        """Start order book service for multiple symbols"""
        tasks = []
        
        for symbol in symbols:
            task = self.initialize_depth(symbol, level)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        logger.info(f"Order book service started for {len(symbols)} symbols")
    
    async def stop(self):
        """Stop order book service"""
        self.order_books.clear()
        logger.info("Order book service stopped")


# Singleton instance
_binance_order_book_service: Optional[BinanceOrderBookService] = None


def get_binance_order_book_service() -> BinanceOrderBookService:
    """Get singleton order book service instance"""
    global _binance_order_book_service
    
    if _binance_order_book_service is None:
        _binance_order_book_service = BinanceOrderBookService()
    
    return _binance_order_book_service