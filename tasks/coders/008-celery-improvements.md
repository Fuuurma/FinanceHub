---
title: "Celery Background Jobs Improvements"
status: pending
priority: p1
estimate: "5 days"
created: "2026-01-30"
assigned_to: coder
depends_on:
  - c-005
---

## Summary

Fix the broken Celery background job system and ensure market data is properly fetched and saved to the database. The current implementation has critical failures that prevent data persistence.

## Background

The FinanceHub project has two background job systems:
1. **Celery** (`apps/backend/src/tasks/celery_tasks.py`) - 633 lines - supposed to save to DB but BROKEN
2. **Dramatiq** (`apps/backend/src/tasks/scheduler_tasks.py`) - 370 lines - saves to Redis cache only

The Celery tasks call methods that don't exist on Yahoo Finance and Binance scrapers, causing immediate failures. Additionally, even working scrapers don't save data to the database in the main task flow.

## Issues to Fix

### P0 - Critical (Must Fix)

#### 1. Add Missing Scraper Methods to YahooFinanceScraper
**File:** `apps/backend/src/data/data_providers/yahooFinance/scraper.py`

The YahooFinanceScraper is a simple wrapper that only inherits base fetcher methods. It needs:

- `fetch_multiple_stocks(symbols: List[str]) -> Dict[str, bool]` - Fetch multiple stocks and save to DB
- `fetch_and_save_stock(symbol: str) -> bool` - Fetch stock data and save to AssetPricesHistoric

Reference implementation:
- See `CoinGeckoScraper.fetch_multiple_cryptos()` in `coingecko/scraper.py`
- See `AlphaVantageScraper.fetch_and_save_stock()` in `alphaVantage/scraper.py`

**Steps:**
1. Import necessary models: `AssetPricesHistoric`, `Asset`
2. Import `asyncio` for concurrent fetching
3. Implement `fetch_multiple_stocks()` similar to CoinGecko pattern
4. Implement `fetch_and_save_stock()` similar to AlphaVantage pattern
5. Add proper error handling and logging
6. Add unit tests

#### 2. Add Missing Scraper Methods to BinanceScraper
**File:** `apps/backend/src/data/data_providers/binance/scraper.py`

The BinanceScraper is also a simple wrapper missing critical methods:

- `fetch_multiple_cryptos(symbols: List[str]) -> Dict[str, bool]` - Fetch multiple cryptos and save to DB
- `fetch_and_save_crypto(symbol: str) -> bool` - Fetch crypto data and save to AssetPricesHistoric

**Steps:**
1. Import necessary models: `AssetPricesHistoric`, `Asset`
2. Import `asyncio` for concurrent fetching
3. Implement `fetch_multiple_cryptos()` following CoinGecko pattern
4. Implement `fetch_and_save_crypto()` following CoinGecko pattern
5. Add proper error handling and logging
6. Add unit tests

#### 3. Fix Celery Tasks to Save Data to Database
**File:** `apps/backend/src/tasks/celery_tasks.py`

The current tasks call `fetch_multiple_*` methods but these don't save data. Options:

**Option A:** Use `fetch_and_save_*` methods (if available)
**Option B:** Modify `fetch_multiple_*` to save data

Recommended: Option A for consistency.

**Changes needed:**

```python
# fetch_yahoo_stocks_task (line 77-121)
# Current: calls yahoo_scraper.fetch_multiple_stocks(symbols)
# Should: call yahoo_scraper.fetch_multiple_stocks(symbols) which internally calls fetch_and_save

# Similarly for other tasks...
```

#### 4. Fix update_single_asset_task for Yahoo/Binance
**File:** `apps/backend/src/tasks/celery_tasks.py` lines 354-417

The `update_single_asset_task` calls `scraper.fetch_and_save_*()` which doesn't exist for Yahoo and Binance.

**Fix:**
1. Add missing methods to scrapers (see #1 and #2)
2. Or add fallback logic:
   ```python
   if source in ['binance', 'coingecko', 'coinmarketcap']:
       success = scraper.fetch_and_save_crypto(symbol)
   else:
       success = scraper.fetch_and_save_stock(symbol)
   ```

### P1 - High Priority

#### 5. Consolidate or Choose Task System
**Decision needed:** Should we keep both Celery and Dramatiq, or consolidate to one?

**Options:**

**Option A:** Keep Celery, remove Dramatiq
- Celery is more widely used and has better documentation
- Fix Celery to work properly
- Remove Dramatiq to reduce complexity

**Option B:** Keep Dramatiq, remove Celery
- Dramatiq is more modern and Python-native
- Currently working (cache-only)
- Would need to add DB persistence

**Option C:** Keep both for different purposes
- Celery for DB-persistent tasks (price history, fundamentals)
- Dramatiq for cache-warming and real-time data
- Document roles clearly

**Recommendation:** Option A - Keep Celery, remove Dramatiq
- Celery is already configured with beat scheduler
- Dramatiq adds infrastructure overhead (RabbitMQ)
- Simpler to maintain one system

**Steps if choosing Option A:**
1. Document all Dramatiq tasks
2. Create equivalent Celery tasks for cache-warming
3. Update documentation to reference Celery only
4. Remove Dramatiq code and dependencies
5. Update docker-compose.yml to remove RabbitMQ (if not needed elsewhere)

#### 6. Add Rate Limiting Per API Key
**Files:** All scrapers in `apps/backend/src/data/data_providers/`

Currently no rate limiting per API key, which can lead to:
- API key being blocked
- Inconsistent data availability
- Wasted resources on failed requests

**Implementation:**
1. Use the existing `BaseAPIFetcher.key_rotation()` infrastructure
2. Add per-key rate limiting:
   ```python
   class RateLimiter:
       def __init__(self):
           self.calls = defaultdict(list)
       
       def record_call(self, api_key):
           self.calls[api_key].append(time.time())
       
       def can_call(self, api_key, max_calls=100, window=60):
           # Check if under limit
           pass
   ```
3. Apply rate limiter in each scraper's `request()` method

#### 7. Add Dead Letter Queue for Failed Tasks
**File:** `apps/backend/src/core/celery.py` or `apps/backend/src/tasks/celery_tasks.py`

When tasks fail repeatedly, they should be moved to a dead letter queue for investigation.

**Implementation:**
```python
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_default_queue = 'default'
app.conf.task_queues = {
    'default': {'exchange': 'default', 'routing_key': 'default'},
    'dead_letter': {'exchange': 'dead_letter', 'routing_key': 'dead_letter'},
}
```

### P2 - Medium Priority

#### 8. Add Task Monitoring Dashboard
**Implementation options:**
1. **Flower** - Official Celery monitoring tool
   ```bash
   pip install flower
   celery -A financehub flower
   ```
2. **Custom dashboard** - Build using Celery events
3. **Integrate with existing** - Add to admin panel

**Recommended:** Install Flower for quick win
1. Add to requirements.txt
2. Add flower command to docker-compose
3. Add authentication (basic auth or disable in dev)

#### 9. Add Task Result Persistence
**File:** Celery config

Currently task results are discarded. For debugging and monitoring, store results.

**Implementation:**
```python
app.conf.result_backend = 'django-db'
app.conf.result_extended = True
app.conf.result_expires = 3600  # 1 hour
```

Requires:
- `django-celery-results` package
- Run migrations: `manage.py migrate django_celery_results`

#### 10. Improve health_check_task
**File:** `apps/backend/src/tasks/celery_tasks.py` lines 530-568

Current health check only verifies Redis connection. Should check:
1. Database connectivity
2. All configured data providers
3. Task queue status
4. Recent task success/failure rates

#### 11. Remove Hardcoded Asset Lists
**File:** `apps/backend/src/tasks/celery_tasks.py` lines 55-69

Currently:
```python
TOP_STOCKS = ['AAPL', 'MSFT', 'GOOGL', ...]
TOP_CRYPTOS = ['BTC', 'ETH', 'BNB', ...]
```

Should be:
1. Loaded from database
2. Configurable via settings
3. Updated based on portfolio holdings or market cap

### P3 - Low Priority

#### 12. Add Task Chaining for Dependent Tasks
Example: Fetch price → Calculate indicators → Send notifications

#### 13. Implement Task Prioritization by Asset Popularity
- More popular assets (by portfolio holdings) get higher priority
- Dynamic priority adjustment

#### 14. Add SLA Monitoring
Track task execution times and alert if SLAs breached.

## Files to Modify

1. `apps/backend/src/data/data_providers/yahooFinance/scraper.py` - Add missing methods
2. `apps/backend/src/data/data_providers/binance/scraper.py` - Add missing methods
3. `apps/backend/src/tasks/celery_tasks.py` - Fix task implementations
4. `apps/backend/src/core/celery.py` - Add DLQ and monitoring config
5. `requirements.txt` - Add django-celery-results (optional)
6. `docker-compose.yml` - Remove RabbitMQ if consolidating to Celery

## Files to Create

1. `tasks/coders/008-celery-improvements-progress.md` - Progress tracking

## Files to Delete (if consolidating)

1. `apps/backend/src/tasks/scheduler_tasks.py` - Dramatiq tasks
2. Any Dramatiq configuration files

## Testing

1. **Unit Tests** for new scraper methods
2. **Integration Tests** for Celery tasks
3. **Manual Testing:**
   ```bash
   cd apps/backend
   celery -A core worker --loglevel=info
   celery -A core beat --loglevel=info
   # Trigger tasks manually and verify DB updates
   ```

## Success Criteria

1. ✅ All market data tasks run without errors
2. ✅ Price data is saved to `AssetPricesHistoric` model
3. ✅ Fundamental data is saved to respective models
4. ✅ No duplicate task systems
5. ✅ Task monitoring available (Flower or equivalent)
6. ✅ Rate limiting prevents API key blocking
7. ✅ Failed tasks go to dead letter queue

## Estimate Breakdown

| Task | Days |
|------|------|
| Add Yahoo scraper methods | 1 |
| Add Binance scraper methods | 1 |
| Fix Celery task implementations | 1 |
| Rate limiting | 0.5 |
| Dead letter queue | 0.5 |
| Consolidate task systems | 1 |
| Testing and bug fixes | 0.5-1 |
| **Total** | **5-6 days** |

## Notes

- The `investments/tasks/alpha_vantage_tasks.py` file shows the correct pattern for async Celery tasks
- Reference CoinGeckoScraper for proper `fetch_and_save` implementation
- Consider creating a base scraper mixin with common save logic
