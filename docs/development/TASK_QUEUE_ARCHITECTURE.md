# Task Queue Architecture

## Overview

FinanceHub uses **Dramatiq** as the single, unified task queue system (as of January 30, 2026).

**Architecture Decision:** Dramatiq was chosen over Celery because:
- Native async/await support (Django 5 compatible)
- Cleaner, simpler API
- Better performance
- Built-in Prometheus monitoring
- Smaller dependency footprint

## Task Types

### High Priority Queue
- `fetch_crypto_prices_task` - Crypto prices every 2 minutes
- `fetch_stock_prices_task` - Stock prices every 5 minutes

### Medium Priority Queue
- `fetch_news_task` - News aggregation every 30 minutes
- `calculate_indicators_task` - Technical indicators for all active assets every hour

### Low Priority Queue
- `cleanup_old_cache_task` - Cache cleanup daily
- `health_check_task` - Health checks every minute
- `cleanup_failed_tasks_task` - Clean up old task records

## Key Features

### 1. Lazy Scraper Initialization
```python
def get_yahoo_scraper():
    from data.data_providers.yahooFinance.scraper import YahooFinanceScraper
    return YahooFinanceScraper()
```
Scrapers are initialized when needed, not at module import time.

### 2. Retry Logic with Exponential Backoff
Built into Dramatiq middleware with 5 retries:
```python
redis_broker.add_middleware(Retries(max_retries=5))
```

### 3. Task Monitoring
All tasks track:
- Success/failure counts
- Average runtime
- Last success/failure timestamps

### 4. Circuit Breaker Pattern
Prevents cascading failures when external APIs are down.

## Configuration

```python
# Dramatiq Configuration
DRAMATIQ_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
DRAMATIQ_TASK_TIMEOUT = 300000  # 5 minutes
DRAMATIQ_MAX_RETRIES = 5
DRAMATIQ_RETRY_BACKOFF = True
```

## Running Tasks

```bash
# Start worker
dramatiq tasks.unified_tasks -p 1 -t 4

# Start scheduler
dramatiq-scheduler --broker redis://localhost:6379/0
```

## Migration from Celery

### Files Removed
- `tasks/celery_tasks.py` (633 lines - DUPLICATE)
- `tasks/scheduler_tasks.py` (368 lines - replaced by unified_tasks.py)

### Files Added
- `tasks/unified_tasks.py` (400+ lines - single source of truth)
- `utils/services/task_monitor.py` (monitoring)

### Bug Fixes
1. ✅ `fetch_stock_prices_task` now correctly filters by `stock` type (was `crypto`)
2. ✅ `calculate_indicators_task` now processes ALL active assets (was hardcoded to AAPL)
3. ✅ Lazy scraper initialization (was at module level)

## Monitoring

### Check Task Stats
```python
from utils.services.task_monitor import get_task_monitor
monitor = get_task_monitor()
stats = monitor.get_all_stats()
```

### Health Check
```bash
curl http://localhost:8000/api/health/
```

## Performance Improvements

- **Code reduction**: 1000+ lines removed (duplicate systems eliminated)
- **Maintenance**: One system to maintain
- **Reliability**: Proper retry logic with exponential backoff
- **Monitoring**: Built-in Prometheus metrics

## Known Issues Fixed

1. ❌ Hardcoded AAPL in schedule → ✅ All active assets
2. ❌ Wrong asset type filter → ✅ Correct filter (stock, not crypto)
3. ❌ No retry logic → ✅ Exponential backoff (5 retries)
4. ❌ Duplicate systems → ✅ Single unified system
5. ❌ Eager scraper init → ✅ Lazy initialization
