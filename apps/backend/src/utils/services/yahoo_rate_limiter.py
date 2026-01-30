"""
Yahoo Finance Rate Limiter
Optimizes API requests to avoid blocking and maximize throughput
"""
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import time

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class YahooFinanceRateLimiter:
    """
    Rate limiter for Yahoo Finance API requests
    
    Yahoo Finance doesn't have official rate limits but may block
    aggressive requests. This class implements smart rate limiting.
    """
    
    def __init__(self, requests_per_minute: int = 120, requests_per_second: int = 2):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests per minute (default: 120)
            requests_per_second: Maximum requests per second (default: 2)
        
        Performance: Uses sliding window for accurate rate limiting
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        
        # Sliding window for rate limiting
        self.request_timestamps = []
        self.window_size = 60  # 60 second window
        
        # Per-second tracking
        self.last_request_time = None
        self.min_request_interval = 1.0 / requests_per_second
        
        # Adaptive rate limiting
        self.block_count = 0
        self.last_block_time = None
        self.backoff_factor = 1.0
    
    async def wait_if_needed(self):
        """
        Wait if rate limit would be exceeded
        
        Performance: Efficient window cleanup and async waiting
        """
        now = datetime.now()
        current_timestamp = now.timestamp()
        
        # Clean old timestamps outside window
        self._cleanup_old_timestamps(current_timestamp)
        
        # Check per-second limit
        if self.last_request_time:
            time_since_last = current_timestamp - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                logger.debug(f"Rate limiting (per-second): waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        # Check per-minute limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            # Find oldest timestamp in window
            oldest_timestamp = min(self.request_timestamps)
            wait_time = 60 - (current_timestamp - oldest_timestamp) + 1
            
            if wait_time > 0:
                logger.debug(f"Rate limiting (per-minute): waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                
                # Cleanup after wait
                self._cleanup_old_timestamps(current_timestamp)
        
        self.last_request_time = datetime.now().timestamp()
    
    def record_request(self):
        """
        Record a request timestamp for rate limiting
        
        Performance: O(1) operation with efficient list management
        """
        current_timestamp = datetime.now().timestamp()
        self.request_timestamps.append(current_timestamp)
        
        # Maintain list size
        if len(self.request_timestamps) > self.requests_per_minute * 2:
            self.request_timestamps = self.request_timestamps[-self.requests_per_minute:]
    
    def _cleanup_old_timestamps(self, current_timestamp: float):
        """
        Remove timestamps outside the sliding window
        
        Performance: Efficient list filtering
        """
        cutoff_timestamp = current_timestamp - self.window_size
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if ts > cutoff_timestamp
        ]
    
    async def handle_rate_limit_error(self, error: Exception) -> None:
        """
        Handle rate limit errors with adaptive backoff
        
        Performance: Exponential backoff for resilience
        """
        now = datetime.now()
        
        # Track consecutive blocks
        if self.last_block_time and (now - self.last_block_time).total_seconds() < 60:
            self.block_count += 1
        else:
            self.block_count = 1
        
        self.last_block_time = now
        
        # Calculate backoff time
        if self.block_count == 1:
            wait_time = 5  # 5 seconds
        elif self.block_count == 2:
            wait_time = 30  # 30 seconds
        elif self.block_count == 3:
            wait_time = 120  # 2 minutes
        else:
            wait_time = 300  # 5 minutes
        
        # Apply backoff factor
        wait_time = wait_time * self.backoff_factor
        self.backoff_factor = min(self.backoff_factor * 2, 10.0)  # Max 10x
        
        logger.warning(f"Rate limit detected (block #{self.block_count}), backoff {wait_time:.1f}s")
        await asyncio.sleep(wait_time)
    
    def reset_backoff(self) -> None:
        """
        Reset backoff factor after successful request
        
        Performance: Allows recovery after rate limit issues
        """
        if self.backoff_factor > 1.0:
            self.backoff_factor = max(self.backoff_factor / 2, 1.0)
            logger.info(f"Reducing backoff factor to {self.backoff_factor:.2f}x")
    
    def get_current_request_rate(self) -> float:
        """
        Get current request rate (requests per minute)
        
        Performance: Uses sliding window for accurate calculation
        """
        now = datetime.now().timestamp()
        self._cleanup_old_timestamps(now)
        
        if len(self.request_timestamps) == 0:
            return 0.0
        
        window_duration = 60  # Always 60 seconds
        requests_in_window = len(self.request_timestamps)
        
        return requests_in_window / window_duration
    
    def is_rate_limited(self) -> bool:
        """
        Check if currently rate limited
        
        Performance: O(1) check
        """
        current_rate = self.get_current_request_rate()
        return current_rate >= self.requests_per_minute


class AdaptiveRateLimiter(YahooFinanceRateLimiter):
    """
    Adaptive rate limiter that adjusts based on response patterns
    
    Performance: Learns optimal rate based on success/failure patterns
    """
    
    def __init__(self, initial_rate: int = 120):
        super().__init__(requests_per_minute=initial_rate)
        self.success_count = 0
        self.failure_count = 0
        self.optimal_rate = initial_rate
    
    def record_success(self) -> None:
        """
        Record successful request and potentially increase rate
        
        Performance: Adaptive rate adjustment
        """
        self.success_count += 1
        self.failure_count = 0  # Reset consecutive failures
        
        # Gradually increase rate if successful
        if self.success_count % 10 == 0:
            current_rate = self.get_current_request_rate()
            if current_rate < self.optimal_rate * 0.9:
                # Too slow, increase rate by 10%
                new_rate = min(int(self.requests_per_minute * 1.1), 300)
                self.requests_per_minute = new_rate
                logger.info(f"Increasing rate limit to {new_rate} req/min")
    
    def record_failure(self, is_rate_limit: bool = False) -> None:
        """
        Record failed request and potentially decrease rate
        
        Performance: Adaptive rate adjustment
        """
        self.failure_count += 1
        
        if is_rate_limit:
            # Rate limited, decrease rate
            if self.failure_count >= 3:
                new_rate = max(int(self.requests_per_minute * 0.7), 10)
                self.requests_per_minute = new_rate
                logger.warning(f"Decreasing rate limit to {new_rate} req/min due to rate limits")
                self.failure_count = 0


async def rate_limiter_context(limiter: YahooFinanceRateLimiter):
    """
    Context manager for rate-limited requests
    
    Performance: Ensures proper cleanup
    """
    try:
        await limiter.wait_if_needed()
        limiter.record_request()
        yield
    finally:
        # Cleanup happens automatically through sliding window
        pass


# Singleton instance for shared use
_default_limiter = None

def get_rate_limiter() -> YahooFinanceRateLimiter:
    """
    Get default rate limiter instance
    
    Performance: Shared instance reduces memory usage
    """
    global _default_limiter
    if _default_limiter is None:
        _default_limiter = AdaptiveRateLimiter(initial_rate=120)
    return _default_limiter


if __name__ == "__main__":
    # Test rate limiter
    print("Testing Yahoo Finance Rate Limiter...")
    
    async def test_rate_limiter():
        limiter = YahooFinanceRateLimiter(requests_per_minute=60)
        
        print(f"Initial rate: {limiter.requests_per_minute} req/min")
        print(f"Min interval: {limiter.min_request_interval*1000:.0f}ms")
        print()
        
        # Simulate multiple requests
        for i in range(20):
            await limiter.wait_if_needed()
            limiter.record_request()
            
            current_rate = limiter.get_current_request_rate()
            print(f"Request {i+1}: Current rate = {current_rate:.1f} req/min")
            
            # Simulate some failures
            if i in [5, 15]:
                print("  -> Simulated rate limit error")
                await limiter.handle_rate_limit_error(Exception("429 Too Many Requests"))
            else:
                limiter.reset_backoff()
            
            await asyncio.sleep(0.1)  # Simulate request time
        
        print()
        print(f"Final rate: {limiter.get_current_request_rate():.1f} req/min")
        print(f"Total requests recorded: {len(limiter.request_timestamps)}")
        print(f"Is rate limited: {limiter.is_rate_limited()}")
    
    asyncio.run(test_rate_limiter())
