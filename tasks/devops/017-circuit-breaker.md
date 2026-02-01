# Task D-017: Circuit Breaker Implementation

**Task ID:** D-017
**Assigned To:** Karen (DevOps)
**Priority:** 🟢 PROACTIVE
**Status:** 🔄 IN PROGRESS
**Created:** February 1, 2026
**Estimated Time:** 3 hours
**Deadline:** February 10, 2026

---

## 📋 OVERVIEW

**Objective:** Implement circuit breaker pattern for external API calls to prevent cascading failures

**Problem:**
- 18+ external data providers (IEX Cloud, Alpha Vantage, etc.)
- No protection against slow/failing external APIs
- Can cause application-wide slowdowns
- No automatic recovery mechanism

**Solution:**
- Circuit breaker for each external API
- Automatic timeout enforcement
- Fallback to cached data
- Automatic recovery after failures
- Monitoring and alerting

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Create Circuit Breaker Utility (1.5 hours)

**File:** `apps/backend/src/utils/circuit_breaker.py` (NEW)

```python
from datetime import datetime, timedelta
from enum import Enum
import logging
from functools import wraps
from typing import Callable, Any, Optional
import time

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is tripped, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker for external service calls

    Prevents cascading failures by:
    1. Tripping after threshold failures
    2. Blocking calls for timeout period
    3. Testing recovery with single request
    4. Closing again if service recovered
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: Exception = Exception,
        half_open_max_calls: int = 3
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls

        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = CircuitState.CLOSED
        self._half_open_call_count = 0

    def call(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Check if circuit should allow request
            if not self._can_allow_request():
                logger.warning(
                    f"Circuit breaker OPEN for {self.service_name}, "
                    f"blocking call to {func.__name__}"
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open for {self.service_name}"
                )

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Success - reset or close circuit
                self._on_success()

                return result

            except self.expected_exception as e:
                # Failure - increment counter
                self._on_failure()
                raise e

        return wrapper

    def _can_allow_request(self) -> bool:
        """Check if circuit should allow request"""
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            # Check if timeout has passed
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._half_open_call_count = 0
                logger.info(
                    f"Circuit breaker for {self.service_name} "
                    f"entering HALF_OPEN state"
                )
                return True
            return False

        if self._state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self._half_open_call_count < self.half_open_max_calls

        return False

    def _on_success(self):
        """Handle successful call"""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_call_count += 1

            # If successful calls in half-open, close circuit
            if self._half_open_call_count >= self.half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(
                    f"Circuit breaker for {self.service_name} "
                    f"CLOSED after successful recovery"
                )
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        logger.warning(
            f"Circuit breaker for {self.service_name} "
            f"failure count: {self._failure_count}/{self.failure_threshold}"
        )

        # Trip circuit if threshold exceeded
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker for {self.service_name} "
                f"TRIPPED after {self._failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self._last_failure_time:
            return True

        elapsed = (datetime.now() - self._last_failure_time).total_seconds()
        return elapsed >= self.timeout_seconds

    def get_state(self) -> dict:
        """Get circuit breaker state for monitoring"""
        return {
            "service": self.service_name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
        }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Circuit breaker instances for external services
CIRCUIT_BREAKERS = {
    "iex_cloud": CircuitBreaker("iex_cloud", failure_threshold=5, timeout_seconds=60),
    "alpha_vantage": CircuitBreaker("alpha_vantage", failure_threshold=5, timeout_seconds=120),
    "finnhub": CircuitBreaker("finnhub", failure_threshold=3, timeout_seconds=60),
    "polygon": CircuitBreaker("polygon", failure_threshold=5, timeout_seconds=60),
    "news_api": CircuitBreaker("news_api", failure_threshold=5, timeout_seconds=120),
    "benzinga": CircuitBreaker("benzinga", failure_threshold=5, timeout_seconds=60),
    "quandl": CircuitBreaker("quandl", failure_threshold=3, timeout_seconds=180),
    "sec_edgar": CircuitBreaker("sec_edgar", failure_threshold=3, timeout_seconds=120),
    "fred": CircuitBreaker("fred", failure_threshold=5, timeout_seconds=120),
    "twelvedata": CircuitBreaker("twelvedata", failure_threshold=5, timeout_seconds=60),
}

def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get circuit breaker for service"""
    if service_name not in CIRCUIT_BREAKERS:
        # Create new circuit breaker with defaults
        CIRCUIT_BREAKERS[service_name] = CircuitBreaker(service_name)
    return CIRCUIT_BREAKERS[service_name]
```

### Phase 2: Add Monitoring Endpoint (30 min)

**File:** `apps/backend/src/api/circuit_breaker_status.py` (NEW)

```python
from ninja import Router
from utils.circuit_breaker import CIRCUIT_BREAKERS

router = Router(tags=["Monitoring"])

@router.get("/circuit-breakers")
def circuit_breaker_status(request):
    """Get all circuit breaker states"""
    return {
        "circuit_breakers": [
            cb.get_state() for cb in CIRCUIT_BREAKERS.values()
        ],
        "total": len(CIRCUIT_BREAKERS),
        "open": sum(1 for cb in CIRCUIT_BREAKERS.values()
                    if cb.get_state()["state"] == "open"),
        "half_open": sum(1 for cb in CIRCUIT_BREAKERS.values()
                        if cb.get_state()["state"] == "half_open"),
    }
```

### Phase 3: Integration with Data Providers (1 hour)

**Example: IEX Cloud Provider**

**Before:**
```python
# apps/backend/src/data/iex_cloud.py
class IEXCloudProvider:
    def fetch_quote(self, symbol: str):
        response = requests.get(f"{self.base_url}/stock/{symbol}/quote")
        return response.json()
```

**After:**
```python
from utils.circuit_breaker import get_circuit_breaker
from requests.exceptions import RequestException

class IEXCloudProvider:
    def __init__(self):
        self.circuit_breaker = get_circuit_breaker("iex_cloud")

    @get_circuit_breaker("iex_cloud").call
    def fetch_quote(self, symbol: str):
        response = requests.get(
            f"{self.base_url}/stock/{symbol}/quote",
            timeout=10  # Add timeout
        )
        response.raise_for_status()
        return response.json()
```

### Phase 4: Prometheus Integration (30 min)

**Add to metrics.py:**
```python
CIRCUIT_BREAKER_STATE = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half_open, 2=open)',
    ['service']
)

CIRCUIT_BREAKER_FAILURES = Counter(
    'circuit_breaker_failures_total',
    'Total circuit breaker trips',
    ['service']
)

CIRCUIT_BREAKER_REQUESTS = Counter(
    'circuit_breaker_requests_total',
    'Total requests through circuit breaker',
    ['service', 'result']  # result: allowed, blocked
)
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Circuit breaker utility created
- [ ] Monitoring endpoint created
- [ ] Integrated with at least 3 major data providers
- [ ] Prometheus metrics added
- [ ] Documentation created
- [ ] Testing completed

---

## 📊 EXPECTED RESULTS

**Before:**
- No protection against external API failures
- Cascading failures possible
- No automatic recovery
- Manual intervention required

**After:**
- Automatic circuit tripping on failures
- Isolated failures (no cascading)
- Automatic recovery after timeout
- Monitoring and alerting

**Benefits:**
- ✅ Improved reliability
- ✅ Better user experience (fast fallback)
- ✅ Reduced support burden
- ✅ Proactive failure detection

---

## 🧪 TESTING

### Test Circuit Breaker Behavior
```python
# Test normal operation
cb = CircuitBreaker("test", failure_threshold=3, timeout_seconds=10)

@cb.call
def test_func():
    return "success"

# Should work
assert test_func() == "success"
assert cb.get_state()["state"] == "closed"

# Simulate failures
@cb.call
def failing_func():
    raise Exception("Service unavailable")

for _ in range(3):
    try:
        failing_func()
    except:
        pass

# Circuit should be open
assert cb.get_state()["state"] == "open"

# Should block requests
try:
    test_func()
except CircuitBreakerOpenError:
    pass  # Expected
```

---

## 📁 FILES TO CREATE

1. `apps/backend/src/utils/circuit_breaker.py` - Circuit breaker implementation
2. `apps/backend/src/api/circuit_breaker_status.py` - Monitoring endpoint

**Files to Modify:**
1. `apps/backend/src/data/iex_cloud.py` - Add circuit breaker
2. `apps/backend/src/data/alpha_vantage.py` - Add circuit breaker
3. `apps/backend/src/data/finnhub.py` - Add circuit breaker
4. `apps/backend/src/core/metrics.py` - Add circuit breaker metrics
5. `apps/backend/src/api/__init__.py` - Register circuit breaker router

---

## 🎯 PRIORITY INTEGRATION

**High Priority (Do First):**
1. IEX Cloud (primary data source)
2. Alpha Vantage (backup data source)
3. Finnhub (real-time data)

**Medium Priority:**
4. Polygon.io
5. News API
6. Benzinga

**Low Priority:**
7-18. Remaining providers

---

**Task D-017 Status:** 🔄 IN PROGRESS

**Next:** Create circuit breaker utility

**Karen - DevOps Engineer**
*Building Financial Excellence* 🎨
