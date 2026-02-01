# Unified Task Queue Migration Guide

## Overview
Consolidated duplicate Dramatiq + Celery task systems into a single Celery-based unified task queue.

## Changes Made

### 1. New Files Created
| File | Purpose |
|------|---------|
| `tasks/unified_tasks.py` | Unified Celery tasks (replaces both celery_tasks.py + scheduler_tasks.py) |
| `tasks/models.py` | TaskFailure model for dead letter queue |

### 2. Files to Remove (After Migration)
- `tasks/celery_tasks.py` (632 lines) - **DEPRECATED**
- `tasks/scheduler_tasks.py` (369 lines) - **DEPRECATED**

### 3. Key Improvements

#### A. Lazy Scraper Initialization
```python
# BEFORE: Module-level initialization (fails if API keys not ready)
yahoo_scraper = YahooFinanceScraper()

# AFTER: Lazy initialization
def get_yahoo_scraper():
    if 'yahoo' not in _scraper_cache:
        from data.data_providers.yahooFinance.scraper import YahooFinanceScraper
        _scraper_cache['yahoo'] = YahooFinanceScraper()
    return _scraper_cache['yahoo']
```

#### B. Exponential Backoff Retry Logic
```python
# BEFORE: Fixed 60s countdown
raise self.retry(exc=e, countdown=60)

# AFTER: Exponential backoff (60s, 120s, 240s, 480s, 960s)
raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

#### C. Fixed Hardcoded Symbol Bug
```python
# BEFORE: Only calculates for AAPL
kwargs = {'symbol': 'AAPL'}

# AFTER: Calculates for all active assets
if symbols is None:
    symbols = get_active_symbols('stock', 50)
```

#### D. Dead Letter Queue
```python
def send_to_dead_letter(task_name, args, kwargs, exception):
    TaskFailure.objects.create(
        task_name=task_name,
        args=str(args),
        kwargs=str(kwargs),
        exception=str(exception),
        traceback=traceback.format_exc()
    )
```

#### E. Unified Task Names
| Old (Celery) | Old (Dramatiq) | New (Unified) |
|--------------|----------------|---------------|
| fetch_yahoo_stocks_task | - | tasks.fetch_yahoo_stocks |
| fetch_alpha_stocks_task | - | tasks.fetch_alpha_stocks |
| fetch_binance_cryptos_task | fetch_crypto_prices_task | tasks.fetch_binance_cryptos |
| - | fetch_stock_prices_task | tasks.fetch_stock_prices |
| - | fetch_news_task | tasks.fetch_news |
| calculate_indicators_task | fetch_technical_indicators_task | tasks.calculate_indicators |
| health_check_task | health_check_task | tasks.health_check |

## Migration Steps

### 1. Stop Old Workers
```bash
pkill -f dramatiq
pkill -f celery
```

### 2. Run Migrations
```bash
cd apps/backend/src
python3 manage.py makemigrations tasks
python3 manage.py migrate
```

### 3. Start New Worker
```bash
cd apps/backend/src
python3 -m celery -A tasks worker --loglevel=info
```

### 4. Start Beat Scheduler (for periodic tasks)
```bash
python3 -m celery -A tasks beat --loglevel=info
```

### 5. Remove Old Files
```bash
rm apps/backend/src/tasks/celery_tasks.py
rm apps/backend/src/tasks/scheduler_tasks.py
```

## Configuration

### Celery Settings (settings.py)
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_BEAT_SCHEDULE = {
    'fetch-stocks-every-5-min': {
        'task': 'tasks.fetch_yahoo_stocks',
        'schedule': crontab(minute='*/5'),
        'kwargs': {'limit': 50}
    },
    'fetch-crypto-every-5-min': {
        'task': 'tasks.fetch_binance_cryptos',
        'schedule': crontab(minute='*/5'),
        'kwargs': {'limit': 30}
    },
    'calculate-indicators-hourly': {
        'task': 'tasks.calculate_indicators',
        'schedule': crontab(minute=0, hour='*'),
        'kwargs': {'period': 200}
    },
}
```

## Task List (14 Unified Tasks)

| Task | Priority | Retry | Description |
|------|----------|-------|-------------|
| fetch_yahoo_stocks | HIGH | 5x | Yahoo Finance stock data |
| fetch_alpha_stocks | HIGH | 5x | Alpha Vantage stock data |
| fetch_binance_cryptos | HIGH | 5x | Binance crypto data |
| fetch_coingecko_cryptos | MEDIUM | 3x | CoinGecko crypto data |
| fetch_unified_crypto | HIGH | 5x | Unified crypto provider |
| fetch_stock_prices | MEDIUM | 3x | Finnhub stock prices |
| fetch_news | MEDIUM | 3x | News aggregation |
| calculate_indicators | MEDIUM | 3x | Technical indicators |
| cleanup_old_data | LOW | 1x | Database cleanup |
| update_single_asset | HIGH | 3x | On-demand updates |
| cache_warming | MEDIUM | 3x | Cache warming |
| health_check | - | - | System health |
| fetch_all_markets | MEDIUM | 3x | Batch fetch |
| batch_update_popular | - | - | Scheduled batch |

## Monitoring

### Check Active Tasks
```bash
celery -A tasks inspect active
```

### Check Worker Stats
```bash
celery -A tasks inspect stats
```

### View Dead Letter Queue
```python
from tasks.models import TaskFailure
failures = TaskFailure.objects.all()[:100]
```

## Performance Improvements

| Metric | Before | After |
|--------|--------|-------|
| Task systems | 2 (Dramatiq + Celery) | 1 (Celery) |
| Scraper init | Module-level | Lazy |
| Retry logic | Fixed (60s) | Exponential |
| Dead letter queue | None | Database-backed |
| Hardcoded symbols | 1 bug | Fixed |

## Rollback Plan
If issues arise, restore from git:
```bash
git checkout HEAD~1 -- apps/backend/src/tasks/celery_tasks.py
git checkout HEAD~1 -- apps/backend/src/tasks/scheduler_tasks.py
rm apps/backend/src/tasks/unified_tasks.py
rm apps/backend/src/tasks/models.py
```
