from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: Type[Exception] = Exception,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(
                    f"Circuit breaker {self.name}: HALF_OPEN - attempting reset"
                )
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN - calls blocked")

        try:
            result = func(*args, **kwargs)

            if self.state == CircuitState.HALF_OPEN:
                self._reset()
                logger.info(f"Circuit breaker {self.name}: CLOSED - recovered")

            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time >= self.timeout

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker {self.name}: OPEN - "
                f"{self.failure_count} failures exceeded threshold"
            )
        else:
            logger.warning(
                f"Circuit breaker {self.name}: "
                f"{self.failure_count}/{self.failure_threshold} failures"
            )

    def _reset(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info(f"Circuit breaker {self.name}: CLOSED - reset")


_circuit_breakers = {}


def get_circuit_breaker(
    name: str, failure_threshold: int = 5, timeout_seconds: int = 60
) -> CircuitBreaker:
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds,
        )
    return _circuit_breakers[name]
