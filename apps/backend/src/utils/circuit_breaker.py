"""
Circuit Breaker Implementation

Prevents cascading failures from external API calls.
"""

from datetime import datetime, timedelta
from enum import Enum
import logging
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""

    pass


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
        half_open_max_calls: int = 3,
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
            if not self._can_allow_request():
                logger.warning(f"Circuit breaker OPEN for {self.service_name}")
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open for {self.service_name}"
                )

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _can_allow_request(self) -> bool:
        """Check if circuit should allow request"""
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._half_open_call_count = 0
                logger.info(f"Circuit breaker {self.service_name} -> HALF_OPEN")
                return True
            return False

        if self._state == CircuitState.HALF_OPEN:
            return self._half_open_call_count < self.half_open_max_calls

        return False

    def _on_success(self):
        """Handle successful call"""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_call_count += 1
            if self._half_open_call_count >= self.half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"Circuit breaker {self.service_name} -> CLOSED")
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        logger.warning(
            f"Circuit breaker {self.service_name} "
            f"failures: {self._failure_count}/{self.failure_threshold}"
        )

        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(f"Circuit breaker {self.service_name} TRIPPED")

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
            "last_failure_time": self._last_failure_time.isoformat()
            if self._last_failure_time
            else None,
        }


# Circuit breaker instances for external services
CIRCUIT_BREAKERS = {}


def get_circuit_breaker(service_name: str, **kwargs) -> CircuitBreaker:
    """Get or create circuit breaker for service"""
    if service_name not in CIRCUIT_BREAKERS:
        CIRCUIT_BREAKERS[service_name] = CircuitBreaker(service_name, **kwargs)
    return CIRCUIT_BREAKERS[service_name]
