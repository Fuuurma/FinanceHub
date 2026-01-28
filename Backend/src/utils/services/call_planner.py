import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict, deque

from django.utils import timezone
from django.core.cache import cache
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class Priority(Enum):
    URGENT = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BATCH = 4


@dataclass(order=True)
class CallRequest:
    priority: Priority
    endpoint: str = field(compare=False)
    timestamp: datetime = field(default_factory=timezone.now, compare=False)
    params: dict = field(default_factory=dict, compare=False)
    callback: callable = field(default=None, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    request_id: str = field(default="", compare=False)
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"{self.endpoint}_{self.timestamp.timestamp()}"


class RateLimitTracker:
    def __init__(self, provider_name: str, limits: dict):
        self.provider_name = provider_name
        self.limits = limits
        self.call_history: deque = deque()
        self.call_count: int = 0
        self.reset_time: Optional[datetime] = None
        
    def can_make_call(self) -> bool:
        now = timezone.now()
        
        if self.reset_time and now >= self.reset_time:
            self.call_history.clear()
            self.call_count = 0
            self.reset_time = None
        
        if self.call_count >= self.limits.get('max_calls', 1000):
            return False
        
        window = self.limits.get('window_seconds', 60)
        cutoff = now - timedelta(seconds=window)
        self.call_history = deque([
            call_time for call_time in self.call_history if call_time > cutoff
        ])
        
        return len(self.call_history) < self.limits.get('calls_per_window', 10)
    
    def record_call(self):
        now = timezone.now()
        self.call_history.append(now)
        self.call_count += 1
        
        if not self.reset_time:
            reset_period = self.limits.get('reset_period_seconds', 3600)
            self.reset_time = now + timedelta(seconds=reset_period)
    
    def get_time_until_next_call(self) -> float:
        if self.can_make_call():
            return 0
        
        now = timezone.now()
        if self.call_history:
            oldest_in_window = self.call_history[0]
            window = self.limits.get('window_seconds', 60)
            return (oldest_in_window + timedelta(seconds=window) - now).total_seconds()
        
        if self.reset_time:
            return (self.reset_time - now).total_seconds()
        
        return 60


class CallPlanner:
    def __init__(self):
        self.request_queue: List[CallRequest] = []
        self.active_requests: Dict[str, CallRequest] = {}
        self.processing: Set[str] = set()
        self.rate_limiters: Dict[str, RateLimitTracker] = {}
        self.provider_limits: Dict[str, dict] = {}
        self.batch_buffer: Dict[str, List[CallRequest]] = defaultdict(list)
        self.batch_timeout: Dict[str, datetime] = {}
        self.running = False
        self.workers: List[asyncio.Task] = []
        
    def configure_provider(self, provider_name: str, limits: dict):
        self.provider_limits[provider_name] = limits
        self.rate_limiters[provider_name] = RateLimitTracker(provider_name, limits)
        logger.info(f"Configured provider '{provider_name}' with limits: {limits}")
    
    def add_request(
        self,
        provider_name: str,
        endpoint: str,
        params: dict,
        priority: Priority = Priority.MEDIUM,
        callback: callable = None,
        batch_key: Optional[str] = None
    ) -> str:
        request = CallRequest(
            priority=priority,
            endpoint=endpoint,
            params=params,
            callback=callback
        )
        
        if batch_key and priority == Priority.BATCH:
            self.batch_buffer[batch_key].append(request)
            
            if batch_key not in self.batch_timeout:
                batch_delay = self.provider_limits.get(provider_name, {}).get('batch_delay_seconds', 5)
                self.batch_timeout[batch_key] = timezone.now() + timedelta(seconds=batch_delay)
            
            logger.debug(f"Added batch request for '{batch_key}': {endpoint}")
        else:
            heapq.heappush(self.request_queue, request)
            logger.debug(f"Added request: {endpoint} (priority: {priority.name})")
        
        return request.request_id
    
    def cancel_request(self, request_id: str) -> bool:
        if request_id in self.active_requests:
            self.active_requests[request_id].priority = Priority.LOW
            return True
        return False
    
    def get_queue_status(self) -> dict:
        priority_counts = defaultdict(int)
        for req in self.request_queue:
            priority_counts[req.priority.name] += 1
        
        return {
            'pending': len(self.request_queue),
            'processing': len(self.processing),
            'active': len(self.active_requests),
            'by_priority': dict(priority_counts),
            'batches': len(self.batch_buffer),
            'rate_limited': {
                provider: not limiter.can_make_call()
                for provider, limiter in self.rate_limiters.items()
            }
        }
    
    async def _process_batch(self, batch_key: str) -> bool:
        if batch_key not in self.batch_buffer:
            return False
        
        requests = self.batch_buffer[batch_key]
        
        if timezone.now() < self.batch_timeout[batch_key]:
            return False
        
        if not requests:
            del self.batch_buffer[batch_key]
            del self.batch_timeout[batch_key]
            return True
        
        provider_name = requests[0].params.get('provider', 'unknown')
        limiter = self.rate_limiters.get(provider_name)
        
        if not limiter or not limiter.can_make_call():
            return False
        
        aggregated_params = {}
        all_endpoints = set()
        
        for req in requests:
            all_endpoints.add(req.endpoint)
            aggregated_params.update(req.params)
        
        batch_request = CallRequest(
            priority=Priority.BATCH,
            endpoint=f"batch_{'_'.join(sorted(all_endpoints))}",
            params=aggregated_params
        )
        
        heapq.heappush(self.request_queue, batch_request)
        del self.batch_buffer[batch_key]
        del self.batch_timeout[batch_key]
        
        logger.info(f"Processed batch '{batch_key}' with {len(requests)} requests")
        return True
    
    async def _execute_request(self, request: CallRequest) -> bool:
        provider_name = request.params.get('provider', 'unknown')
        limiter = self.rate_limiters.get(provider_name)
        
        if limiter and not limiter.can_make_call():
            wait_time = limiter.get_time_until_next_call()
            
            if wait_time > 60:
                logger.warning(f"Rate limited for provider '{provider_name}', waiting {wait_time:.1f}s")
                await asyncio.sleep(min(wait_time, 30))
                return False
            
            await asyncio.sleep(wait_time + 0.1)
        
        if limiter:
            limiter.record_call()
        
        self.processing.add(request.request_id)
        self.active_requests[request.request_id] = request
        
        try:
            if request.callback:
                try:
                    result = await request.callback(**request.params)
                    logger.debug(f"Request completed: {request.endpoint}")
                except Exception as e:
                    logger.error(f"Callback failed for {request.endpoint}: {str(e)}")
                    if request.retry_count < request.max_retries:
                        request.retry_count += 1
                        heapq.heappush(self.request_queue, request)
                        logger.info(f"Retrying request {request.request_id} (attempt {request.retry_count})")
                        return False
                    else:
                        logger.error(f"Max retries exceeded for {request.endpoint}")
                        return False
            else:
                logger.debug(f"No callback for request: {request.endpoint}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing request {request.request_id}: {str(e)}")
            if request.retry_count < request.max_retries:
                request.retry_count += 1
                heapq.heappush(self.request_queue, request)
                logger.info(f"Retrying request {request.request_id} (attempt {request.retry_count})")
            return False
            
        finally:
            self.processing.discard(request.request_id)
            self.active_requests.pop(request.request_id, None)
    
    async def _worker(self, worker_id: int):
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                await self._process_batches()
                
                if not self.request_queue:
                    await asyncio.sleep(0.1)
                    continue
                
                request = heapq.heappop(self.request_queue)
                
                if request.request_id in self.processing:
                    continue
                
                await self._execute_request(request)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_batches(self):
        for batch_key in list(self.batch_buffer.keys()):
            await self._process_batch(batch_key)
    
    async def start(self, num_workers: int = 3):
        if self.running:
            logger.warning("Call planner already running")
            return
        
        self.running = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
        
        logger.info(f"Call planner started with {num_workers} workers")
    
    async def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Call planner stopped")
    
    def get_statistics(self) -> dict:
        total_calls = sum(
            limiter.call_count 
            for limiter in self.rate_limiters.values()
        )
        
        provider_stats = {}
        for provider, limiter in self.rate_limiters.items():
            provider_stats[provider] = {
                'calls_total': limiter.call_count,
                'calls_in_window': len(limiter.call_history),
                'can_make_call': limiter.can_make_call(),
                'reset_time': limiter.reset_time.isoformat() if limiter.reset_time else None,
                'limits': self.provider_limits.get(provider, {})
            }
        
        return {
            'queue_status': self.get_queue_status(),
            'total_calls': total_calls,
            'provider_stats': provider_stats,
            'active_workers': len(self.workers),
            'running': self.running
        }


_call_planner_instance: Optional[CallPlanner] = None


def get_call_planner() -> CallPlanner:
    global _call_planner_instance
    if _call_planner_instance is None:
        _call_planner_instance = CallPlanner()
        
        defaults = {
            'alpha_vantage': {
                'max_calls': 250,
                'window_seconds': 86400,
                'calls_per_window': 5,
                'reset_period_seconds': 86400,
                'batch_delay_seconds': 10
            },
            'coingecko': {
                'max_calls': 50000,
                'window_seconds': 60,
                'calls_per_window': 30,
                'reset_period_seconds': 60,
                'batch_delay_seconds': 2
            },
            'coinmarketcap': {
                'max_calls': 10000,
                'window_seconds': 86400,
                'calls_per_window': 10,
                'reset_period_seconds': 86400,
                'batch_delay_seconds': 5
            },
            'polygon_io': {
                'max_calls': 5,
                'window_seconds': 60,
                'calls_per_window': 5,
                'reset_period_seconds': 60,
                'batch_delay_seconds': 12
            },
            'iex_cloud': {
                'max_calls': 500000,
                'window_seconds': 86400,
                'calls_per_window': 100,
                'reset_period_seconds': 86400,
                'batch_delay_seconds': 1
            },
            'finnhub': {
                'max_calls': 60,
                'window_seconds': 60,
                'calls_per_window': 60,
                'reset_period_seconds': 60,
                'batch_delay_seconds': 1
            },
            'newsapi': {
                'max_calls': 100,
                'window_seconds': 86400,
                'calls_per_window': 100,
                'reset_period_seconds': 86400,
                'batch_delay_seconds': 60
            },
            'binance': {
                'max_calls': 1200,
                'window_seconds': 60,
                'calls_per_window': 1200,
                'reset_period_seconds': 60,
                'batch_delay_seconds': 0.1
            }
        }
        
        for provider, limits in defaults.items():
            _call_planner_instance.configure_provider(provider, limits)
    
    return _call_planner_instance
