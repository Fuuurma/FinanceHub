"""
Task Monitor - Track task execution, failures, and performance metrics
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging
import redis

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class TaskStats:
    running: int = 0
    succeeded: int = 0
    failed: int = 0
    avg_runtime_ms: float = 0
    last_success: datetime = None
    last_failure: datetime = None


class TaskMonitor:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.stats: Dict[str, TaskStats] = {}
        self.start_times: Dict[str, float] = {}

    def start_operation(self, operation_id: str):
        self.start_times[operation_id] = datetime.now().timestamp()
        key = f"task:running:{operation_id}"
        self.redis_client.set(key, datetime.now().isoformat(), ex=3600)

    def end_operation(self, operation_id: str, success: bool = True):
        if operation_id not in self.start_times:
            logger.warning(f"Operation {operation_id} not started")
            return

        elapsed_ms = (
            datetime.now().timestamp() - self.start_times[operation_id]
        ) * 1000
        del self.start_times[operation_id]

        self.redis_client.delete(f"task:running:{operation_id}")

        operation_type = operation_id.split(":")[0]
        if success:
            self.redis_client.incr(f"task:succeeded:{operation_type}")
            self.redis_client.set(
                f"task:last_success:{operation_type}", datetime.now().isoformat()
            )
        else:
            self.redis_client.incr(f"task:failed:{operation_type}")
            self.redis_client.set(
                f"task:last_failure:{operation_type}", datetime.now().isoformat()
            )

        self._update_stats(operation_type, success, elapsed_ms)

    def _update_stats(self, operation_type: str, success: bool, elapsed_ms: float):
        if operation_type not in self.stats:
            self.stats[operation_type] = TaskStats()

        stats = self.stats[operation_type]
        stats.total_processed = getattr(stats, "total_processed", 0) + 1

        if success:
            stats.succeeded += 1
        else:
            stats.failed += 1

        current_avg = stats.avg_runtime_ms
        total = stats.succeeded + stats.failed
        if total > 0:
            stats.avg_runtime_ms = ((current_avg * (total - 1)) + elapsed_ms) / total

    def get_stats(self, task_name: str) -> Dict[str, Any]:
        succeeded = self.redis_client.get(f"task:succeeded:{task_name}") or 0
        failed = self.redis_client.get(f"task:failed:{task_name}") or 0
        last_success = self.redis_client.get(f"task:last_success:{task_name}")
        last_failure = self.redis_client.get(f"task:last_failure:{task_name}")

        return {
            "task": task_name,
            "succeeded": int(succeeded),
            "failed": int(failed),
            "last_success": last_success,
            "last_failure": last_failure,
            "error_rate": (int(failed) / (int(succeeded) + int(failed)) * 100)
            if (int(succeeded) + int(failed)) > 0
            else 0,
        }

    def get_all_stats(self) -> Dict[str, Dict]:
        return {
            task: self.get_stats(task)
            for task in ["crypto", "stock", "news", "indicators", "cleanup", "health"]
        }

    def cleanup_old_records(self, max_age_hours: int = 24) -> int:
        cleaned = 0
        pattern = "task:*"
        keys = self.redis_client.keys(pattern)
        for key in keys:
            try:
                ttl = self.redis_client.ttl(key)
                if ttl == -1:
                    self.redis_client.delete(key)
                    cleaned += 1
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError):
                pass
        return cleaned


_task_monitor = None


def get_task_monitor() -> TaskMonitor:
    global _task_monitor
    if _task_monitor is None:
        _task_monitor = TaskMonitor()
    return _task_monitor
