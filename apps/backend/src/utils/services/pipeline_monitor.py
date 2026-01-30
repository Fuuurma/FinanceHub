import time
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PipelineMetrics:
    def __init__(self):
        self._total_processed = 0
        self._successful = 0
        self._failed = 0
        self._total_time_ms = 0.0
        self._processing_times = []
        self._last_updated = datetime.now()

    def record(self, success: bool, elapsed_ms: float):
        self._total_processed += 1
        self._processing_times.append(elapsed_ms)
        self._total_time_ms += elapsed_ms

        if success:
            self._successful += 1
        else:
            self._failed += 1

        self._last_updated = datetime.now()

    def get_metrics(self) -> Dict[str, Any]:
        times = self._processing_times
        return {
            "total_processed": self._total_processed,
            "successful": self._successful,
            "failed": self._failed,
            "avg_time_ms": self._total_time_ms / max(self._total_processed, 1),
            "min_time_ms": min(times) if times else 0,
            "max_time_ms": max(times) if times else 0,
            "error_rate": (self._failed / max(self._total_processed, 1)) * 100,
            "success_rate": (self._successful / max(self._total_processed, 1)) * 100,
            "last_updated": self._last_updated.isoformat(),
        }

    def reset(self):
        self._total_processed = 0
        self._successful = 0
        self._failed = 0
        self._total_time_ms = 0.0
        self._processing_times = []
        self._last_updated = datetime.now()


_metrics_instance = None


def get_metrics() -> PipelineMetrics:
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PipelineMetrics()
    return _metrics_instance


def reset_metrics():
    global _metrics_instance
    _metrics_instance = None
