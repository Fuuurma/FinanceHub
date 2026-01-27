# Bloomberg Terminal - Phase 0-1 Implementation Plan

## Overview

This plan covers **Phase 0: API Key Management Foundation** and **Phase 1: Scraping Infrastructure**, which are the prerequisites for all subsequent development.

**Timeline**: 14 days
**Cost**: $0 (all free tiers)
**API Keys Required**: 25+ keys (registration guide provided)

---

## Phase 0: API Key Management Foundation (Days 1-3)

### Objective

Build the infrastructure for managing multiple API keys per provider with automatic rotation, rate limiting, and health monitoring.

### Deliverables

1. **Database Models** (Day 1)
2. **APIKeyManager Service** (Day 2)
3. **BaseAPIFetcher Class** (Day 2)
4. **Background Tasks** (Day 3)
5. **Admin Dashboard** (Day 3)
6. **API Keys Template File** (Day 0 - Now)

---

## Implementation Plan

### Day 0: Create API Keys Template

**Action**: Create `.opencode/plans/API_KEYS_TEMPLATE.md`

**Purpose**: Template file for user to populate with registered API keys

**Structure**:
```markdown
# API Keys Template
# Register all accounts using FREE_API_REGISTRATION_GUIDE.md
# Then populate this file with your actual keys

# ========================================
# STOCK DATA PROVIDERS
# ========================================

## Polygon.io (6 free accounts)
POLYGON_API_KEY_1=register_1_get_key
POLYGON_API_KEY_2=register_2_get_key
POLYGON_API_KEY_3=register_3_get_key
POLYGON_API_KEY_4=register_4_get_key
POLYGON_API_KEY_5=register_5_get_key
POLYGON_API_KEY_6=register_6_get_key

## IEX Cloud (1 account)
IEX_API_KEY=register_get_key

## Finnhub (1 account)
FINNHUB_API_KEY=register_get_key

## Alpha Vantage (10 accounts)
ALPHA_VANTAGE_API_KEY_1=register_1_get_key
ALPHA_VANTAGE_API_KEY_2=register_2_get_key
# ... through 10

# ... [rest of template]
```

---

### Day 1: Database Models

**Files to Create**:

#### 1. Backend/src/investments/models/api_key.py

**Purpose**: Model for storing multiple API keys per provider

**Schema**:
```python
class APIKey(UUIDModel, TimestampedModel):
    """
    API Key for a data provider
    Supports multiple keys per provider with automatic rotation
    """
    
    # Provider relation
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE, related_name="api_keys")
    
    # Key details
    name = models.CharField(max_length=100, help_text="Descriptive name for this key")
    key_value = models.CharField(max_length=500, help_text="Encrypted API key value")
    
    # Key metadata
    key_type = models.CharField(max_length=50, choices=[("free", "Free"), ("basic", "Basic"), ("pro", "Pro")], default="free")
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("rate_limited", "Rate Limited"), ("disabled", "Disabled")], default="active")
    
    # Rate limits
    rate_limit_per_minute = models.PositiveIntegerField(null=True, blank=True)
    rate_limit_daily = models.PositiveIntegerField(null=True, blank=True)
    
    # Priority (lower = higher priority)
    priority = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    # Usage tracking
    usage_today = models.PositiveIntegerField(default=0)
    usage_today_reset = models.DateTimeField(auto_now_add=True)
    usage_this_hour = models.PositiveIntegerField(default=0)
    usage_this_hour_reset = models.DateTimeField(auto_now_add=True)
    total_usage_lifetime = models.PositiveBigIntegerField(default=0)
    
    # Health tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.PositiveSmallIntegerField(default=0)
    
    # Auto-recovery
    auto_recover_after_minutes = models.PositiveSmallIntegerField(default=60)
    max_consecutive_failures = models.PositiveSmallIntegerField(default=5)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    # Indexes
    class Meta:
        db_table = "api_keys"
        unique_together = ("provider", "name")
        ordering = ["provider", "priority", "id"]
        indexes = [
            models.Index(fields=["provider", "status", "priority"]),
            models.Index(fields=["status", "last_used_at"]),
            models.Index(fields=["provider", "last_used_at"]),
        ]
    
    # Methods
    def is_available(self) -> bool:
        """Check if key is available for use"""
        return self.status == "active"
    
    def increment_usage(self) -> None:
        """Increment usage counters with automatic reset"""
        now = timezone.now()
        
        # Reset daily if needed
        if (now - self.usage_today_reset).days >= 1:
            self.usage_today = 0
            self.usage_today_reset = now
        
        # Reset hourly if needed
        if (now - self.usage_this_hour_reset).seconds >= 3600:
            self.usage_this_hour = 0
            self.usage_this_hour_reset = now
        
        self.usage_today += 1
        self.usage_this_hour += 1
        self.total_usage_lifetime += 1
        self.last_used_at = now
        self.save(update_fields=["usage_today", "usage_today_reset", "usage_this_hour", "usage_this_hour_reset", "total_usage_lifetime", "last_used_at"])
    
    def record_success(self) -> None:
        """Record a successful API call"""
        now = timezone.now()
        self.last_success_at = now
        self.consecutive_failures = 0
        self.save(update_fields=["last_success_at", "consecutive_failures"])
    
    def record_failure(self, error_type: str = "unknown") -> None:
        """Record a failed API call"""
        now = timezone.now()
        self.last_failure_at = now
        self.consecutive_failures += 1
        
        # Auto-disable if too many failures
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.status = "disabled"
        
        self.save(update_fields=["last_failure_at", "consecutive_failures", "status"])
    
    def mark_rate_limited(self) -> None:
        """Mark key as rate limited"""
        self.status = "rate_limited"
        self.save(update_fields=["status"])
```

**Fields**:
- **Provider**: FK to DataProvider
- **Key Details**: name, key_value, key_type, status
- **Rate Limits**: rate_limit_per_minute, rate_limit_daily
- **Priority**: Lower number = higher priority (1-100)
- **Usage Tracking**: today, this_hour, lifetime counters
- **Health Tracking**: last_success_at, last_failure_at, consecutive_failures
- **Auto-Recovery**: auto_recover_after_minutes, max_consecutive_failures

**Methods**:
- `is_available()`: Check if key can be used
- `increment_usage()`: Track usage with automatic reset
- `record_success()`: Log successful call
- `record_failure()`: Log failed call, auto-disable if threshold exceeded
- `mark_rate_limited()`: Mark as rate limited

---

#### 2. Backend/src/investments/models/api_call_log.py

**Purpose**: Log every API call for monitoring and analytics

**Schema**:
```python
class APIKeyUsageLog(UUIDModel, TimestampedModel):
    """
    Log of API calls for monitoring and analytics
    """
    
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name="usage_logs")
    
    # Request details
    endpoint = models.CharField(max_length=200, help_text="API endpoint called")
    method = models.CharField(max_length=10, default="GET")
    
    # Response details
    status_code = models.PositiveIntegerField()
    success = models.BooleanField()
    response_time_ms = models.PositiveIntegerField()
    
    # Error details
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # Additional details
    request_params = models.JSONField(default=dict, blank=True)
    response_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = "api_key_usage_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["api_key", "-created_at"]),
            models.Index(fields=["api_key", "success"]),
            models.Index(fields=["-created_at"]),
        ]
```

**Fields**:
- **API Key**: FK to APIKey
- **Request**: endpoint, method, params
- **Response**: status_code, success, response_time_ms, response_size_bytes
- **Error**: error_type, error_message

---

#### 3. Backend/src/investments/models/__init__.py (Update)

**Action**: Export new models

```python
from .api_key import APIKey
from .api_call_log import APIKeyUsageLog
from .data_provider import DataProvider

__all__ = ['APIKey', 'APIKeyUsageLog', 'DataProvider']
```

---

### Migration (Day 1)

**Action**: Create and run Django migrations

**Commands**:
```bash
cd Backend/src
python manage.py makemigrations investments
python manage.py migrate
```

**Expected Output**:
- Create APIKey model
- Create APIKeyUsageLog model
- Add indexes

---

### Day 2: Core Services

#### 1. Backend/src/investments/services/api_key_manager.py

**Purpose**: Manage API key selection and rotation

**Class Structure**:
```python
class APIKeyManager:
    """
    Manages API key rotation and health monitoring
    """
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.cache_timeout = 60  # 1 minute cache
    
    def get_best_key(self, exclude_ids: List[int] = None) -> Optional[APIKey]:
        """
        Get best available API key using weighted selection
        Algorithm: priority_score - usage_penalty - recent_use_penalty
        """
        # Check cache first
        cache_key = f"api_keys:best:{self.provider_name}"
        cached_key_id = cache.get(cache_key)
        
        if cached_key_id:
            try:
                key = APIKey.objects.get(id=cached_key_id)
                if key.is_available():
                    return key
            except APIKey.DoesNotExist:
                cache.delete(cache_key)
        
        # Get available keys
        available_keys = self._get_available_keys(exclude_ids)
        
        if not available_keys:
            return None
        
        # Select best key using weighted algorithm
        selected_key = self._select_weighted_key(available_keys)
        
        # Cache selection
        cache.set(cache_key, selected_key.id, self.cache_timeout)
        
        return selected_key
    
    def _get_available_keys(self, exclude_ids: List[int] = None) -> List[APIKey]:
        """Get available keys, excluding specified ones"""
        queryset = APIKey.objects.filter(
            provider__name=self.provider_name,
            status="active"
        ).select_related("provider")
        
        if exclude_ids:
            queryset = queryset.exclude(id__in=exclude_ids)
        
        return list(queryset)
    
    def _select_weighted_key(self, keys: List[APIKey]) -> APIKey:
        """
        Select key based on weighted scoring
        Score = (priority_score) - (usage_penalty) - (recent_use_penalty)
        """
        now = timezone.now()
        best_key = None
        best_score = float("-inf")
        
        for key in keys:
            # Priority: lower number = higher priority (1-100)
            priority_score = (100 - key.priority) * 10
            
            # Usage penalty: discourage keys with high usage
            usage_penalty = key.usage_this_hour * 2
            
            # Recent use penalty: discourage recently used keys
            recent_use_penalty = 0
            if key.last_used_at:
                minutes_since_use = (now - key.last_used_at).total_seconds() / 60
                recent_use_penalty = max(0, 10 - minutes_since_use) * 5
            
            # Total score
            total_score = priority_score - usage_penalty - recent_use_penalty
            
            if total_score > best_score:
                best_score = total_score
                best_key = key
        
        return best_key
    
    def rotate_on_rate_limit(self, failed_key: APIKey) -> Optional[APIKey]:
        """
        Handle rate limit by rotating to next available key
        """
        # Mark key as rate limited
        failed_key.mark_rate_limited()
        
        # Get next available key
        next_key = self.get_best_key(exclude_ids=[failed_key.id])
        
        return next_key
    
    def recover_rate_limited_keys(self) -> int:
        """
        Recover rate-limited keys that have cooled down
        """
        now = timezone.now()
        keys_to_recover = []
        
        rate_limited_keys = APIKey.objects.filter(
            provider__name=self.provider_name,
            status="rate_limited"
        )
        
        for key in rate_limited_keys:
            if key.last_failure_at:
                minutes_since_failure = (now - key.last_failure_at).total_seconds() / 60
                
                if minutes_since_failure >= key.auto_recover_after_minutes:
                    keys_to_recover.append(key)
        
        # Recover keys
        for key in keys_to_recover:
            key.status = "active"
            key.consecutive_failures = 0
            key.save(update_fields=["status", "consecutive_failures"])
        
        # Clear cache
        cache.delete(f"api_keys:best:{self.provider_name}")
        
        return len(keys_to_recover)
    
    def get_key_health_report(self) -> dict:
        """Get health report for all provider keys"""
        keys = APIKey.objects.filter(provider__name=self.provider_name)
        
        report = {
            "provider": self.provider_name,
            "total_keys": keys.count(),
            "active_keys": keys.filter(status="active").count(),
            "rate_limited_keys": keys.filter(status="rate_limited").count(),
            "disabled_keys": keys.filter(status="disabled").count(),
            "keys": []
        }
        
        for key in keys:
            report["keys"].append({
                "name": key.name,
                "status": key.status,
                "priority": key.priority,
                "usage_today": key.usage_today,
                "usage_this_hour": key.usage_this_hour,
                "consecutive_failures": key.consecutive_failures,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            })
        
        return report
```

**Key Methods**:
- `get_best_key()`: Weighted selection with caching
- `_select_weighted_key()`: Priority-based algorithm
- `rotate_on_rate_limit()`: Automatic failover
- `recover_rate_limited_keys()`: Auto-recovery
- `get_key_health_report()`: Health monitoring

**Weighted Selection Algorithm**:
```
Score = Priority_Score - Usage_Penalty - Recent_Use_Penalty

Where:
- Priority_Score = (100 - priority) * 10
- Usage_Penalty = usage_this_hour * 2
- Recent_Use_Penalty = max(0, 10 - minutes_since_use) * 5
```

---

#### 2. Backend/src/data/data_providers/base_fetcher.py

**Purpose**: Base class for all API fetchers with automatic key rotation

**Class Structure**:
```python
class BaseAPIFetcher(ABC):
    """
    Base class for all API fetchers with key rotation support
    """
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.key_manager = APIKeyManager(provider_name)
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_key: Optional[APIKey] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Get base URL for API"""
        pass
    
    @abstractmethod
    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from response if present"""
        pass
    
    async def request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API request with automatic key rotation
        """
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            # Get best API key
            api_key = self.key_manager.get_best_key()
            
            if not api_key:
                raise Exception(f"No available API keys for {self.provider_name}")
            
            self.current_key = api_key
            start_time = timezone.now()
            
            try:
                # Increment usage before request
                api_key.increment_usage()
                
                # Make request
                response_data = await self._make_request(endpoint, params, method, api_key)
                
                # Calculate response time
                response_time = (timezone.now() - start_time).total_seconds() * 1000
                
                # Check for rate limit
                rate_limit_error = self.extract_rate_limit_error(response_data)
                if rate_limit_error:
                    # Log attempt
                    await self._log_api_call(api_key, endpoint, method, success=False, status_code=429, response_time_ms=int(response_time), error_type="rate_limit", error_message=rate_limit_error, request_params=params)
                    
                    # Rotate to next key
                    self.current_key = self.key_manager.rotate_on_rate_limit(api_key)
                    retry_count += 1
                    continue
                
                # Success - record and return
                await self._log_api_call(api_key, endpoint, method, success=True, status_code=200, response_time_ms=int(response_time), request_params=params)
                api_key.record_success()
                return response_data
                
            except Exception as e:
                response_time = (timezone.now() - start_time).total_seconds() * 1000
                last_error = e
                
                # Log error
                await self._log_api_call(api_key, endpoint, method, success=False, status_code=500, response_time_ms=int(response_time), error_type=str(type(e).__name__), error_message=str(e), request_params=params)
                api_key.record_failure(str(type(e).__name__))
                
                # Don't retry on certain errors
                if isinstance(e, (ValueError, KeyError)):
                    raise
                
                retry_count += 1
                await asyncio.sleep(1 * retry_count)  # Exponential backoff
        
        raise Exception(f"Max retries exceeded. Last error: {last_error}")
    
    async def _make_request(self, endpoint: str, params: Optional[Dict], method: str, api_key: APIKey) -> Dict:
        """Make the actual HTTP request"""
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)
        
        async with self.session.request(method, url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    def _get_headers(self, api_key: APIKey) -> Dict:
        """Get headers for request"""
        # Override in subclasses for provider-specific auth
        return {}
    
    async def _log_api_call(self, api_key: APIKey, endpoint: str, method: str, success: bool, status_code: int, response_time_ms: int, error_type: str = "", error_message: str = "", request_params: Dict = None):
        """Log API call for monitoring"""
        try:
            APIKeyUsageLog.objects.create(
                api_key=api_key,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                success=success,
                response_time_ms=response_time_ms,
                error_type=error_type,
                error_message=error_message[:1000],
                request_params=request_params or {}
            )
        except Exception as e:
            logger.error(f"Failed to log API call: {str(e)}")
```

**Key Features**:
- Automatic retry with exponential backoff
- Rate limit detection and handling
- Automatic key rotation on rate limit
- Request logging for monitoring
- Abstract methods for provider-specific implementations

---

### Day 3: Background Tasks & Admin

#### 1. Backend/src/tasks/api_key_management.py

**Purpose**: Background tasks for API key health and recovery

**Tasks**:
```python
@dramatiq.actor
def recover_rate_limited_keys():
    """Recover rate-limited keys (runs every 5 minutes)"""
    providers = ["polygon", "iex_cloud", "finnhub", "alpha_vantage", "coingecko", "news_api"]
    
    total_recovered = 0
    for provider in providers:
        try:
            manager = APIKeyManager(provider)
            recovered = manager.recover_rate_limited_keys()
            total_recovered += recovered
        except Exception as e:
            logger.error(f"Error recovering keys for {provider}: {str(e)}")
    
    logger.info(f"Recovered {total_recovered} rate-limited keys")


@dramatiq.actor
def reset_daily_usage_counters():
    """Reset daily usage counters (runs daily at midnight)"""
    from investments.models.api_key import APIKey
    from django.utils import timezone
    
    updated = APIKey.objects.filter(usage_today__gt=0).update(
        usage_today=0,
        usage_today_reset=timezone.now()
    )
    
    logger.info(f"Reset daily usage for {updated} keys")


@dramatiq.actor
def generate_health_report():
    """Generate health report for all providers (runs hourly)"""
    providers = ["polygon", "iex_cloud", "finnhub", "alpha_vantage", "coingecko", "news_api"]
    
    for provider in providers:
        try:
            manager = APIKeyManager(provider)
            report = manager.get_key_health_report()
            logger.info(f"Health report for {provider}: {report}")
            
            # Store in cache for dashboard
            cache.set(f"api_health:{provider}", report, 3600)
            
        except Exception as e:
            logger.error(f"Error generating health report for {provider}: {str(e)}")
```

**Tasks**:
- `recover_rate_limited_keys()`: Every 5 minutes
- `reset_daily_usage_counters()`: Daily at midnight
- `generate_health_report()`: Hourly

---

#### 2. Backend/src/investments/admin.py

**Purpose**: Admin interface for managing API keys

**Code**:
```python
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'status', 'priority', 'usage_today', 'usage_this_hour', 'last_used_at', 'consecutive_failures']
    list_filter = ['status', 'key_type', 'provider']
    search_fields = ['name', 'provider__name']
    readonly_fields = ['total_usage_lifetime', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Key Details', {
            'fields': ('provider', 'name', 'key_value', 'key_type', 'status')
        }),
        ('Rate Limits', {
            'fields': ('rate_limit_per_minute', 'rate_limit_daily', 'priority')
        }),
        ('Usage Tracking', {
            'fields': ('usage_today', 'usage_this_hour', 'total_usage_lifetime', 'last_used_at')
        }),
        ('Health', {
            'fields': ('last_success_at', 'last_failure_at', 'consecutive_failures', 'auto_recover_after_minutes', 'max_consecutive_failures')
        }),
        ('Metadata', {
            'fields': ('metadata', 'notes')
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_rate_limited', 'reset_usage_counters']
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} keys marked as active")
    
    def reset_usage_counters(self, request, queryset):
        now = timezone.now()
        queryset.update(
            usage_today=0,
            usage_this_hour=0,
            usage_today_reset=now,
            usage_this_hour_reset=now
        )
        self.message_user(request, f"Reset usage counters for {queryset.count()} keys")


@admin.register(APIKeyUsageLog)
class APIKeyUsageLogAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'endpoint', 'method', 'status_code', 'success', 'response_time_ms', 'error_type', 'created_at']
    list_filter = ['success', 'status_code', 'error_type', 'api_key']
    search_fields = ['endpoint', 'api_key__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # Logs are read-only
```

---

## Phase 1: Scraping Infrastructure (Days 4-7)

### Objective

Build scrapers for free data sources: SEC EDGAR, RSS feeds, FRED, Reddit, StockTwits

### Deliverables

1. **SEC EDGAR Scraper** (Day 4)
2. **RSS News Aggregator** (Day 4-5)
3. **FRED API Integration** (Day 5)
4. **Reddit Sentiment Scraper** (Day 6)
5. **StockTwits API Integration** (Day 7)

---

### Day 4-5: SEC EDGAR & RSS Scrapers

#### 1. Backend/src/data/data_providers/sec_edgar/scraper.py

**Features**:
- Company CIK lookup
- 10-K/10-Q/8-K filings download
- Insider trading (Form 4) tracking
- Rate limiting (10 req/sec)

**Key Methods**:
```python
class SECEDGARScraper:
    async def get_company_filings(self, ticker: str, filing_type: str = '10-K') -> List[Dict]:
        """Get recent filings for a company"""
        pass
    
    async def get_filing_document(self, url: str) -> str:
        """Download and return filing document"""
        pass
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Get SEC CIK from ticker symbol"""
        pass
```

---

#### 2. Backend/src/data/data_providers/rss_news/scraper.py

**Features**:
- Multi-source aggregation (CNBC, Reuters, MarketWatch, etc.)
- Deduplication across sources
- Headline extraction

**Key Methods**:
```python
class RSSNewsScraper:
    SOURCES = {
        'CNBC': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
        'Reuters': 'https://www.reutersagency.com/feed/',
        # ... etc
    }
    
    def get_news(self, source: str = 'CNBC', limit: int = 20) -> List[Dict]:
        """Get news from RSS feed"""
        pass
    
    def get_all_news(self, limit_per_source: int = 10) -> List[Dict]:
        """Get news from all sources"""
        pass
```

---

### Day 5: FRED API Integration

**File**: Backend/src/data/data_providers/fred/scraper.py

**Features**:
- Treasury yields (2y, 5y, 10y, 30y)
- Economic indicators (GDP, CPI, unemployment)
- Historical data back to 1940s

**Key Methods**:
```python
class FREDScraper:
    SERIES = {
        'treasury_10y': 'DGS10',
        'treasury_2y': 'DGS2',
        'fed_funds': 'DFF',
        'gdp': 'GDP',
        'cpi': 'CPIAUCSL',
        'unemployment': 'UNRATE'
    }
    
    def get_series_data(self, series_id: str, start_date: Optional[str] = None) -> Dict:
        """Get data for an economic series"""
        pass
    
    def get_treasury_yields(self) -> Dict:
        """Get current treasury yields"""
        pass
```

---

### Day 6: Reddit Sentiment Scraper

**File**: Backend/src/data/data_providers/reddit/scraper.py

**Features**:
- PRAW integration
- Multiple subreddit monitoring
- TextBlob sentiment analysis
- Symbol extraction from posts

**Key Methods**:
```python
class RedditSentimentScraper:
    SUBREDDITS = [
        'wallstreetbets',
        'stocks',
        'investing',
        'options',
        'CryptoCurrency'
    ]
    
    def get_stock_sentiment(self, ticker: str) -> Dict:
        """Get sentiment for a stock ticker"""
        pass
    
    def calculate_sentiment(self, text: str) -> Dict:
        """Calculate sentiment using TextBlob"""
        pass
```

---

### Day 7: StockTwits API Integration

**File**: Backend/src/data/data_providers/stocktwits/scraper.py

**Features**:
- Symbol sentiment stream
- Bullish/bearish ratio calculation
- Trending symbols

**Key Methods**:
```python
class StockTwitsAPI:
    def get_symbol_sentiment(self, symbol: str) -> Dict:
        """Get bullish/bearish sentiment for symbol"""
        pass
    
    def get_trending(self) -> List[Dict]:
        """Get trending symbols"""
        pass
```

---

## Testing Strategy

### Unit Tests

**Files to Create**:
- `Backend/tests/test_api_key_manager.py`
- `Backend/tests/test_base_fetcher.py`
- `Backend/tests/test_sec_edgar_scraper.py`
- `Backend/tests/test_rss_scraper.py`
- `Backend/tests/test_fred_scraper.py`

**Test Coverage**:
- API key selection algorithm
- Rate limit handling
- Key rotation
- Data parsing
- Error handling

---

## Configuration Files

### 1. Backend/.env.example

Create example environment file:
```bash
# ===== API KEYS =====
# Register accounts using FREE_API_REGISTRATION_GUIDE.md
# Then add your actual keys below

# Polygon.io (6 free keys)
POLYGON_API_KEY_1=your_key_here
# ... add others

# IEX Cloud
IEX_API_KEY=your_key_here

# Finnhub
FINNHUB_API_KEY=your_key_here

# Alpha Vantage (10 free keys)
ALPHA_VANTAGE_API_KEY_1=your_key_here
# ... add others

# ... [rest of providers]

# ===== DATABASE =====
DATABASE_URL=postgresql://user:password@localhost:5432/financehub
REDIS_URL=redis://localhost:6379/0

# ===== CELERY =====
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Dependencies to Install

### Backend Requirements

Add to `Backend/requirements.txt`:
```txt
# API Key Management
django-fernet-fields==1.1.0  # For API key encryption

# Scraping
feedparser==6.0.10          # RSS feeds
praw==7.7.1                # Reddit API
textblob==0.17.1             # Sentiment analysis

# Existing
dramatiq==1.15.0
aiohttp==3.9.0
requests==2.31.0
```

---

## Summary of Deliverables

### Files to Create (14 files total)

**Day 0**:
- `.opencode/plans/API_KEYS_TEMPLATE.md`

**Day 1** (Database):
- `Backend/src/investments/models/api_key.py`
- `Backend/src/investments/models/api_call_log.py`
- `Backend/src/investments/models/__init__.py` (update)

**Day 2** (Services):
- `Backend/src/investments/services/api_key_manager.py`
- `Backend/src/data/data_providers/base_fetcher.py`

**Day 3** (Background & Admin):
- `Backend/src/tasks/api_key_management.py`
- `Backend/src/investments/admin.py`

**Day 4** (SEC EDGAR):
- `Backend/src/data/data_providers/sec_edgar/base.py`
- `Backend/src/data/data_providers/sec_edgar/scraper.py`

**Day 5** (RSS & FRED):
- `Backend/src/data/data_providers/rss_news/base.py`
- `Backend/src/data/data_providers/rss_news/scraper.py`
- `Backend/src/data/data_providers/fred/base.py`
- `Backend/src/data/data_providers/fred/scraper.py`

**Day 6** (Reddit):
- `Backend/src/data/data_providers/reddit/base.py`
- `Backend/src/data/data_providers/reddit/scraper.py`

**Day 7** (StockTwits):
- `Backend/src/data/data_providers/stocktwits/base.py`
- `Backend/src/data/data_providers/stocktwits/scraper.py`

---

## Next Steps After Phase 0-1

1. **User Action**: Register 25+ free API accounts using guide
2. **User Action**: Populate API_KEYS_TEMPLATE.md with actual keys
3. **Developer Action**: Create all Phase 0-1 files
4. **Developer Action**: Run migrations
5. **Developer Action**: Install new dependencies
6. **Developer Action**: Write unit tests
7. **Developer Action**: Test all scrapers
8. **Proceed to Phase 2**: Free Tier API Additions

---

## Questions for Implementation

1. Should I include example API key values in the template (e.g., "register_at_polygon_and_replace_this")?
2. Do you want unit tests created alongside implementation files?
3. Should I add logging configuration for the API key manager?
4. Do you want me to create a Django management command to initialize API keys from .env file?
5. Should I add database indexes for the usage logs to improve query performance?

---

This plan provides a complete roadmap for Phase 0-1 with all necessary files, models, services, and background tasks defined.
