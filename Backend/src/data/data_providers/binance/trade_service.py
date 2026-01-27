"""Binance Trade Execution Data Integration Service"""

import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

import polars as pl

from utils.helpers.logger.logger import get_logger
from .websocket_client import get_binance_ws_client
from .base import BinanceFetcher

logger = get_logger(__name__)


class Trade:
    """Trade execution data"""
    
    def __init__(self, data: dict):
        self.id = int(data.get('a', 0))  # Aggregate trade ID
        self.price = Decimal(str(data.get('p', 0)))  # Price
        self.quantity = Decimal(str(data.get('q', 0)))  # Quantity
        self.time = datetime.fromtimestamp(data.get('T', 0) / 1000)  # Trade time
        self.is_buyer_maker = data.get('m', False)  # Is buyer the maker?
        self.is_ignore = data.get('f', False)  # Was trade ignored?
    
    @property
    def value(self) -> Decimal:
        """Trade value (price * quantity)"""
        return self.price * self.quantity
    
    @property
    def side(self) -> str:
        """Trade side ('buy' or 'sell')"""
        return 'sell' if self.is_buyer_maker else 'buy'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'price': float(self.price),
            'quantity': float(self.quantity),
            'value': float(self.value),
            'time': self.time.isoformat(),
            'timestamp_ms': int(self.time.timestamp() * 1000),
            'side': self.side,
            'is_buyer_maker': self.is_buyer_maker
        }


class AggTrade(Trade):
    """Aggregated trade (trades at same time/price are combined)"""
    
    def __init__(self, data: dict):
        super().__init__(data)
        self.first_trade_id = int(data.get('f', 0))  # First trade ID
        self.last_trade_id = int(data.get('l', 0))  # Last trade ID
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            'first_trade_id': self.first_trade_id,
            'last_trade_id': self.last_trade_id,
            'trade_count': self.last_trade_id - self.first_trade_id + 1
        })
        return result


class TradeStats:
    """Trade statistics for a time period"""
    
    def __init__(self):
        self.total_trades: int = 0
        self.buy_trades: int = 0
        self.sell_trades: int = 0
        self.buy_volume: Decimal = Decimal(0)
        self.sell_volume: Decimal = Decimal(0)
        self.buy_value: Decimal = Decimal(0)
        self.sell_value: Decimal = Decimal(0)
        self.vwap_buy: Optional[Decimal] = None
        self.vwap_sell: Optional[Decimal] = None
        self.vwap_all: Optional[Decimal] = None
        self.price_high: Optional[Decimal] = None
        self.price_low: Optional[Decimal] = None
        self.avg_trade_size: Optional[Decimal] = None
    
    def add_trade(self, trade: Trade):
        """Add a trade to statistics"""
        self.total_trades += 1
        
        if trade.side == 'buy':
            self.buy_trades += 1
            self.buy_volume += trade.quantity
            self.buy_value += trade.value
        else:
            self.sell_trades += 1
            self.sell_volume += trade.quantity
            self.sell_value += trade.value
        
        if self.price_high is None or trade.price > self.price_high:
            self.price_high = trade.price
        
        if self.price_low is None or trade.price < self.price_low:
            self.price_low = trade.price
    
    def calculate_vwap(self):
        """Calculate volume-weighted average price"""
        total_volume = self.buy_volume + self.sell_volume
        total_value = self.buy_value + self.sell_value
        
        if total_volume > 0:
            self.vwap_all = total_value / total_volume
        
        if self.buy_volume > 0:
            self.vwap_buy = self.buy_value / self.buy_volume
        
        if self.sell_volume > 0:
            self.vwap_sell = self.sell_value / self.sell_volume
        
        if self.total_trades > 0:
            self.avg_trade_size = total_volume / self.total_trades
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        self.calculate_vwap()
        
        return {
            'total_trades': self.total_trades,
            'buy_trades': self.buy_trades,
            'sell_trades': self.sell_trades,
            'buy_volume': float(self.buy_volume),
            'sell_volume': float(self.sell_volume),
            'total_volume': float(self.buy_volume + self.sell_volume),
            'buy_value': float(self.buy_value),
            'sell_value': float(self.sell_value),
            'total_value': float(self.buy_value + self.sell_value),
            'vwap_all': float(self.vwap_all) if self.vwap_all else None,
            'vwap_buy': float(self.vwap_buy) if self.vwap_buy else None,
            'vwap_sell': float(self.vwap_sell) if self.vwap_sell else None,
            'price_high': float(self.price_high) if self.price_high else None,
            'price_low': float(self.price_low) if self.price_low else None,
            'avg_trade_size': float(self.avg_trade_size) if self.avg_trade_size else None,
            'buy_ratio': float(self.buy_volume / (self.buy_volume + self.sell_volume)) if (self.buy_volume + self.sell_volume) > 0 else None
        }


class BinanceTradeService:
    """
    Binance Trade Execution Data Service
    
    Features:
    - Real-time trade execution via WebSocket
    - Individual trades (@trade stream)
    - Aggregated trades (@aggTrade stream)
    - Trade statistics and analysis
    - Volume profile calculation
    - Trade direction analysis
    """
    
    def __init__(self, history_size: int = 1000):
        self.ws_client = get_binance_ws_client()
        self.rest_client = BinanceFetcher()
        
        # Trade history
        self.trades: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.agg_trades: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        
        # Statistics
        self.trade_stats: Dict[str, TradeStats] = defaultdict(TradeStats)
        
        # Time & sales (recent trades)
        self.time_and_sales: Dict[str, List[dict]] = defaultdict(list)
    
    async def subscribe_trades(self, symbol: str, callback: Optional[callable] = None):
        """
        Subscribe to real-time individual trades
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for trade updates
        """
        try:
            async def on_trade(data: dict):
                await self._process_trade(symbol, data)
                if callback:
                    await self._run_callback(callback, Trade(data).to_dict())
            
            await self.ws_client.subscribe_trade(symbol, on_trade)
            logger.info(f"Subscribed to individual trades for {symbol}")
        
        except Exception as e:
            logger.error(f"Error subscribing to trades for {symbol}: {str(e)}")
    
    async def subscribe_agg_trades(self, symbol: str, callback: Optional[callable] = None):
        """
        Subscribe to aggregated trades
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for aggregated trade updates
        """
        try:
            async def on_agg_trade(data: dict):
                await self._process_agg_trade(symbol, data)
                if callback:
                    await self._run_callback(callback, AggTrade(data).to_dict())
            
            await self.ws_client.subscribe_agg_trade(symbol, on_agg_trade)
            logger.info(f"Subscribed to aggregated trades for {symbol}")
        
        except Exception as e:
            logger.error(f"Error subscribing to agg trades for {symbol}: {str(e)}")
    
    async def _process_trade(self, symbol: str, data: dict):
        """Process individual trade"""
        try:
            trade = Trade(data)
            
            # Add to history
            self.trades[symbol].append(trade)
            
            # Update time & sales
            self.time_and_sales[symbol].append(trade.to_dict())
            if len(self.time_and_sales[symbol]) > 100:
                self.time_and_sales[symbol] = self.time_and_sales[symbol][-100:]
            
            # Update statistics
            self.trade_stats[symbol].add_trade(trade)
            
            logger.debug(f"Processed trade for {symbol}: {trade.side} {trade.quantity} @ {trade.price}")
        
        except Exception as e:
            logger.error(f"Error processing trade for {symbol}: {str(e)}")
    
    async def _process_agg_trade(self, symbol: str, data: dict):
        """Process aggregated trade"""
        try:
            agg_trade = AggTrade(data)
            
            # Add to history
            self.agg_trades[symbol].append(agg_trade)
            
            # Add to regular trades (for statistics)
            self.trades[symbol].append(agg_trade)
            
            # Update statistics
            self.trade_stats[symbol].add_trade(agg_trade)
            
            logger.debug(f"Processed agg trade for {symbol}: {agg_trade.side} {agg_trade.quantity} @ {agg_trade.price}")
        
        except Exception as e:
            logger.error(f"Error processing agg trade for {symbol}: {str(e)}")
    
    async def _run_callback(self, callback: callable, data: dict):
        """Run callback function"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[dict]:
        """Get recent trades for symbol"""
        trades = list(self.trades[symbol])[-limit:]
        return [trade.to_dict() for trade in trades]
    
    async def get_time_and_sales(self, symbol: str, limit: int = 50) -> List[dict]:
        """Get time & sales (recent trades formatted for display)"""
        return self.time_and_sales[symbol][-limit:]
    
    async def get_trade_stats(self, symbol: str) -> Optional[dict]:
        """Get trade statistics for symbol"""
        if symbol not in self.trade_stats:
            return None
        
        return self.trade_stats[symbol].to_dict()
    
    async def get_volume_profile(
        self,
        symbol: str,
        interval: str = '1h',
        bins: int = 50
    ) -> Optional[dict]:
        """
        Calculate volume profile for symbol
        
        Args:
            symbol: Trading pair
            interval: Time interval for aggregation ('1m', '5m', '15m', '1h', '4h', '1d')
            bins: Number of price bins
        
        Returns:
            Volume profile with price levels and volumes
        """
        try:
            trades = list(self.trades[symbol])
            if not trades:
                return None
            
            # Get price range
            prices = [trade.price for trade in trades]
            min_price = min(prices)
            max_price = max(prices)
            
            if min_price == max_price:
                return None
            
            # Create bins
            bin_width = (max_price - min_price) / bins
            bins_data = defaultdict(lambda: {'buy_volume': Decimal(0), 'sell_volume': Decimal(0)})
            
            for trade in trades:
                bin_idx = int((trade.price - min_price) / bin_width)
                bin_idx = min(bin_idx, bins - 1)
                
                if trade.side == 'buy':
                    bins_data[bin_idx]['buy_volume'] += trade.quantity
                else:
                    bins_data[bin_idx]['sell_volume'] += trade.quantity
            
            # Build volume profile
            volume_profile = []
            for i in range(bins):
                bin_price = min_price + (i * bin_width) + (bin_width / 2)
                buy_vol = bins_data[i]['buy_volume']
                sell_vol = bins_data[i]['sell_volume']
                total_vol = buy_vol + sell_vol
                
                volume_profile.append({
                    'price_level': float(bin_price),
                    'buy_volume': float(buy_vol),
                    'sell_volume': float(sell_vol),
                    'total_volume': float(total_vol),
                    'buy_ratio': float(buy_vol / total_vol) if total_vol > 0 else None
                })
            
            return {
                'symbol': symbol,
                'interval': interval,
                'min_price': float(min_price),
                'max_price': float(max_price),
                'bin_count': bins,
                'total_trades': len(trades),
                'volume_profile': volume_profile
            }
        
        except Exception as e:
            logger.error(f"Error calculating volume profile for {symbol}: {str(e)}")
            return None
    
    async def get_trade_flow(
        self,
        symbol: str,
        window: int = 100
    ) -> Optional[dict]:
        """
        Analyze trade flow direction
        
        Args:
            symbol: Trading pair
            window: Number of recent trades to analyze
        
        Returns:
            Trade flow analysis
        """
        try:
            trades = list(self.trades[symbol])[-window:]
            if len(trades) < 10:
                return None
            
            # Calculate moving average of buy/sell ratio
            buy_count = 0
            sell_count = 0
            buy_volume = Decimal(0)
            sell_volume = Decimal(0)
            
            for trade in trades:
                if trade.side == 'buy':
                    buy_count += 1
                    buy_volume += trade.quantity
                else:
                    sell_count += 1
                    sell_volume += trade.quantity
            
            total_count = buy_count + sell_count
            total_volume = buy_volume + sell_volume
            
            # Calculate indicators
            buy_ratio_count = buy_count / total_count if total_count > 0 else 0
            buy_ratio_volume = float(buy_volume / total_volume) if total_volume > 0 else 0
            
            # Determine flow direction
            if buy_ratio_volume > 0.6:
                direction = 'strong_buy'
            elif buy_ratio_volume > 0.52:
                direction = 'buy'
            elif buy_ratio_volume < 0.4:
                direction = 'strong_sell'
            elif buy_ratio_volume < 0.48:
                direction = 'sell'
            else:
                direction = 'neutral'
            
            return {
                'symbol': symbol,
                'window': window,
                'trade_count': total_count,
                'buy_count': buy_count,
                'sell_count': sell_count,
                'buy_ratio_count': float(buy_ratio_count),
                'buy_ratio_volume': buy_ratio_volume,
                'direction': direction,
                'total_volume': float(total_volume)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing trade flow for {symbol}: {str(e)}")
            return None
    
    async def get_large_trades(
        self,
        symbol: str,
        threshold_multiplier: float = 5.0,
        limit: int = 20
    ) -> List[dict]:
        """
        Find unusually large trades (whales)
        
        Args:
            symbol: Trading pair
            threshold_multiplier: Multiple of average trade size
            limit: Maximum number of trades to return
        
        Returns:
            List of large trades
        """
        try:
            trades = list(self.trades[symbol])
            if len(trades) < 50:
                return []
            
            # Calculate average trade size
            avg_size = sum(t.quantity for t in trades) / len(trades)
            threshold = avg_size * threshold_multiplier
            
            # Filter large trades
            large_trades = [
                trade for trade in trades
                if trade.quantity >= threshold
            ]
            
            # Sort by size (descending)
            large_trades.sort(key=lambda t: t.quantity, reverse=True)
            
            return [trade.to_dict() for trade in large_trades[:limit]]
        
        except Exception as e:
            logger.error(f"Error finding large trades for {symbol}: {str(e)}")
            return []
    
    async def get_historical_trades(
        self,
        symbol: str,
        limit: int = 500,
        from_id: Optional[int] = None
    ) -> List[dict]:
        """
        Fetch historical trades from REST API
        
        Args:
            symbol: Trading pair
            limit: Number of trades (max 1000)
            from_id: Trade ID to fetch from
        """
        try:
            async with self.rest_client:
                trades_data = await self.rest_client.get_historical_trades(
                    symbol,
                    limit=limit,
                    from_id=from_id
                )
            
            trades = []
            for trade_data in trades_data:
                trade = Trade({
                    'a': trade_data.get('id'),
                    'p': trade_data.get('price'),
                    'q': trade_data.get('qty'),
                    'T': trade_data.get('time'),
                    'm': trade_data.get('isBuyerMaker', False)
                })
                trades.append(trade.to_dict())
            
            return trades
        
        except Exception as e:
            logger.error(f"Error fetching historical trades for {symbol}: {str(e)}")
            return []
    
    async def get_agg_trades_history(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> List[dict]:
        """
        Fetch historical aggregated trades
        
        Args:
            symbol: Trading pair
            start_time: Start time in ms
            end_time: End time in ms
            limit: Number of results (max 1000)
        """
        try:
            async with self.rest_client:
                agg_trades_data = await self.rest_client.get_agg_trades(
                    symbol,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
            
            agg_trades = []
            for trade_data in agg_trades_data:
                agg_trade = AggTrade(trade_data)
                agg_trades.append(agg_trade.to_dict())
            
            return agg_trades
        
        except Exception as e:
            logger.error(f"Error fetching agg trades for {symbol}: {str(e)}")
            return []
    
    async def start(self, symbols: List[str], use_agg: bool = True):
        """
        Start trade service for multiple symbols
        
        Args:
            symbols: List of trading pairs
            use_agg: Use aggregated trades (more efficient)
        """
        tasks = []
        
        for symbol in symbols:
            if use_agg:
                task = self.subscribe_agg_trades(symbol)
            else:
                task = self.subscribe_trades(symbol)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        logger.info(f"Trade service started for {len(symbols)} symbols (agg={use_agg})")
    
    async def stop(self):
        """Stop trade service"""
        self.trades.clear()
        self.agg_trades.clear()
        self.trade_stats.clear()
        self.time_and_sales.clear()
        logger.info("Trade service stopped")


# Singleton instance
_binance_trade_service: Optional[BinanceTradeService] = None


def get_binance_trade_service(history_size: int = 1000) -> BinanceTradeService:
    """Get singleton trade service instance"""
    global _binance_trade_service
    
    if _binance_trade_service is None or _binance_trade_service.trades.default_factory().maxlen != history_size:
        _binance_trade_service = BinanceTradeService(history_size=history_size)
    
    return _binance_trade_service