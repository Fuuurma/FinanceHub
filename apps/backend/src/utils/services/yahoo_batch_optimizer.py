"""
Yahoo Finance Batch Optimizer
Optimizes batch requests to maximize throughput and minimize API calls
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import polars as pl
import orjson
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.services.yahoo_rate_limiter import get_rate_limiter
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class YahooFinanceBatchOptimizer:
    """
    Optimizes Yahoo Finance API calls through batching and caching
    
    Performance: Uses polars for data processing, async operations
    """
    
    def __init__(self, max_workers: int = 10):
        """
        Initialize batch optimizer
        
        Args:
            max_workers: Maximum concurrent workers
        """
        self.max_workers = max_workers
        self.rate_limiter = get_rate_limiter()
        self.cache = {}  # In-memory cache for recent data
        
        # Cache TTL (time-to-live) in seconds
        self.cache_ttl = {
            'quotes': 60,  # 1 minute
            'historical': 300,  # 5 minutes
            'fundamentals': 3600  # 1 hour
        }
    
    async def fetch_multiple_quotes(
        self,
        symbols: List[str],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch multiple quotes efficiently with caching
        
        Performance: Batch download with yfinance, polars for processing
        """
        try:
            # Check cache first
            if use_cache:
                cached_data, missed_symbols = self._check_cache(symbols, 'quotes')
                if cached_data:
                    logger.info(f"Cache hit: {len(cached_data)}/{len(symbols)} symbols")
                
                symbols_to_fetch = list(set(symbols) - set(missed_symbols))
            else:
                cached_data = {}
                symbols_to_fetch = symbols
            
            if not symbols_to_fetch:
                return cached_data
            
            # Batch download using yfinance
            logger.info(f"Fetching {len(symbols_to_fetch)} quotes from Yahoo Finance")
            
            # Use rate limiter context
            async with self.rate_limiter as limiter:
                await limiter.wait_if_needed()
                
                # Download in current thread (yfinance is blocking)
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    self._download_quotes_blocking,
                    symbols_to_fetch
                )
            
            # Process results with polars for performance
            processed_data = self._process_quotes(results)
            
            # Record success for rate limiter
            if isinstance(limiter, type(self.rate_limiter)):
                limiter.record_success()
            
            # Update cache
            new_data = {**cached_data, **processed_data}
            self._update_cache(new_data, 'quotes')
            
            return new_data
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error fetching multiple quotes: {str(e)}")
            # Record failure for rate limiter
            if isinstance(limiter, type(self.rate_limiter)):
                limiter.record_failure(is_rate_limit=True)
            return {}
    
    def _download_quotes_blocking(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Download quotes blocking (runs in thread pool)
        
        Performance: Uses yfinance batch download
        """
        try:
            # Use yfinance to download multiple tickers at once
            tickers = yf.Tickers(symbols)
            
            # Batch download is more efficient than individual requests
            data = tickers.history(period="1d", interval="1d")
            
            # Convert to dictionary
            results = {}
            for symbol in symbols:
                if symbol in data.index.get_level_values('Ticker'):
                    symbol_data = data.xs(symbol, level='Ticker')
                    
                    # Extract latest price data
                    if not symbol_data.empty:
                        latest = symbol_data.iloc[-1]
                        results[symbol] = {
                            'symbol': symbol,
                            'price': float(latest['Close']) if 'Close' in latest else None,
                            'open': float(latest['Open']) if 'Open' in latest else None,
                            'high': float(latest['High']) if 'High' in latest else None,
                            'low': float(latest['Low']) if 'Low' in latest else None,
                            'volume': int(latest['Volume']) if 'Volume' in latest else None,
                            'timestamp': latest.name.isoformat() if hasattr(latest, 'name') else None
                        }
            
            return results
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error downloading quotes: {str(e)}")
            return {s: {} for s in symbols}
    
    def _process_quotes(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process quote data with polars for performance
        
        Performance: Vectorized operations for better throughput
        """
        try:
            # Convert to polars DataFrame for efficient processing
            valid_data = {s: d for s, d in raw_data.items() if d}
            
            if not valid_data:
                return valid_data
            
            # Create DataFrame
            df = pl.DataFrame([
                {
                    'symbol': data['symbol'],
                    'price': data['price'],
                    'open': data['open'],
                    'high': data['high'],
                    'low': data['low'],
                    'volume': data['volume'],
                    'timestamp': data['timestamp']
                }
                for data in valid_data.values()
            ])
            
            # Calculate additional metrics efficiently
            df = df.with_columns([
                (pl.col('high') - pl.col('low')).alias('range'),
                (pl.col('price') - pl.col('open')).alias('change'),
                ((pl.col('price') - pl.col('open')) / pl.col('open') * 100).alias('change_percent')
            ])
            
            # Convert back to dictionary
            results = {}
            for row in df.iter_rows(named=True):
                results[row['symbol']] = dict(row)
            
            return results
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error processing quotes: {str(e)}")
            return raw_data
    
    async def fetch_historical_data(
        self,
        symbols: List[str],
        period: str = "1mo",
        interval: str = "1d",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch historical data efficiently with caching
        
        Performance: Batch download, polars processing, async operations
        """
        try:
            # Check cache
            cache_key = f"historical_{period}_{interval}"
            if use_cache:
                cached_data, missed_symbols = self._check_cache(symbols, cache_key)
                if cached_data:
                    logger.info(f"Cache hit: {len(cached_data)}/{len(symbols)} symbols")
                
                symbols_to_fetch = list(set(symbols) - set(missed_symbols))
            else:
                cached_data = {}
                symbols_to_fetch = symbols
            
            if not symbols_to_fetch:
                return cached_data
            
            logger.info(f"Fetching historical data for {len(symbols_to_fetch)} symbols")
            
            # Use rate limiter
            async with self.rate_limiter as limiter:
                await limiter.wait_if_needed()
                
                # Download in thread pool
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    self._download_historical_blocking,
                    symbols_to_fetch,
                    period,
                    interval
                )
                
                # Record success
                if isinstance(limiter, type(self.rate_limiter)):
                    limiter.record_success()
            
            # Update cache
            new_data = {**cached_data, **results}
            self._update_cache(new_data, cache_key)
            
            return new_data
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            # Record failure
            if isinstance(limiter, type(self.rate_limiter)):
                limiter.record_failure()
            return {}
    
    def _download_historical_blocking(
        self,
        symbols: List[str],
        period: str,
        interval: str
    ) -> Dict[str, Any]:
        """
        Download historical data blocking (thread pool)
        
        Performance: Batch download with yfinance
        """
        try:
            # Batch download all symbols at once
            tickers = yf.Tickers(symbols)
            data = tickers.history(period=period, interval=interval)
            
            # Convert to dictionary
            results = {}
            for symbol in symbols:
                if symbol in data.index.get_level_values('Ticker'):
                    symbol_data = data.xs(symbol, level='Ticker')
                    results[symbol] = {
                        'symbol': symbol,
                        'data': symbol_data.to_dict('records'),
                        'count': len(symbol_data)
                    }
            
            return results
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error downloading historical data: {str(e)}")
            return {s: {} for s in symbols}
    
    def _check_cache(self, symbols: List[str], cache_type: str) -> tuple[Dict[str, Any], List[str]]:
        """
        Check cache for data
        
        Performance: O(1) lookup with TTL
        """
        cache_data = {}
        missed_symbols = []
        now = datetime.now()
        
        if cache_type not in self.cache:
            return {}, symbols
        
        for symbol in symbols:
            if symbol in self.cache[cache_type]:
                cached_item = self.cache[cache_type][symbol]
                
                # Check TTL
                cache_time = cached_item.get('timestamp')
                ttl = self.cache_ttl[cache_type]
                
                if cache_time and (now - cache_time).total_seconds() < ttl:
                    cache_data[symbol] = cached_item['data']
                else:
                    missed_symbols.append(symbol)
            else:
                missed_symbols.append(symbol)
        
        return cache_data, missed_symbols
    
    def _update_cache(self, data: Dict[str, Any], cache_type: str) -> None:
        """
        Update cache with new data
        
        Performance: Efficient cache updates
        """
        if cache_type not in self.cache:
            self.cache[cache_type] = {}
        
        now = datetime.now()
        
        for symbol, item in data.items():
            self.cache[cache_type][symbol] = {
                'data': item,
                'timestamp': now
            }
    
    def clear_cache(self, cache_type: Optional[str] = None) -> None:
        """
        Clear cache (all or specific type)
        
        Performance: Instant cache invalidation
        """
        if cache_type:
            if cache_type in self.cache:
                del self.cache[cache_type]
                logger.info(f"Cleared cache: {cache_type}")
        else:
            self.cache.clear()
            logger.info("Cleared all caches")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Performance: O(n) operation
        """
        stats = {}
        now = datetime.now()
        
        for cache_type, cache_data in self.cache.items():
            valid_count = 0
            expired_count = 0
            
            ttl = self.cache_ttl.get(cache_type, 0)
            
            for symbol, item in cache_data.items():
                cache_time = item.get('timestamp')
                
                if cache_time and (now - cache_time).total_seconds() < ttl:
                    valid_count += 1
                else:
                    expired_count += 1
            
            stats[cache_type] = {
                'total_items': len(cache_data),
                'valid_items': valid_count,
                'expired_items': expired_count,
                'ttl_seconds': ttl
            }
        
        return stats


# Singleton instance
_default_optimizer = None

def get_batch_optimizer() -> YahooFinanceBatchOptimizer:
    """
    Get default batch optimizer instance
    
    Performance: Shared instance reduces memory usage
    """
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = YahooFinanceBatchOptimizer()
    return _default_optimizer


if __name__ == "__main__":
    # Test batch optimizer
    print("Testing Yahoo Finance Batch Optimizer...")
    
    optimizer = YahooFinanceBatchOptimizer()
    
    # Test multiple quotes
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    
    async def test_batch():
        print(f"\nFetching quotes for {len(symbols)} symbols...")
        quotes = await optimizer.fetch_multiple_quotes(symbols)
        
        for symbol, data in quotes.items():
            print(f"\n{symbol}:")
            if 'price' in data:
                print(f"  Price: ${data['price']:.2f}")
            if 'range' in data:
                print(f"  Range: ${data['range']:.2f}")
            if 'change_percent' in data:
                print(f"  Change: {data['change_percent']:+.2f}%")
        
        # Get cache stats
        stats = optimizer.get_cache_stats()
        print(f"\nCache Statistics:")
        for cache_type, type_stats in stats.items():
            print(f"  {cache_type}:")
            print(f"    Valid: {type_stats['valid_items']}/{type_stats['total_items']}")
            print(f"    Expired: {type_stats['expired_items']}")
    
    asyncio.run(test_batch())
