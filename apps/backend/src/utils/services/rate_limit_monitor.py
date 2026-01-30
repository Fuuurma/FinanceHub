"""
Rate Limit Monitor

Monitor and track rate limit violations and API abuse.
"""

from django.core.cache import cache
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitViolation:
    identifier: str
    violation_count: int
    first_violation: datetime
    last_violation: datetime
    endpoint: str = None


class RateLimitMonitor:
    """Monitor and track rate limit violations"""

    BAN_THRESHOLD = 10
    BAN_DURATION = 7200  # 2 hours

    def __init__(self):
        self.redis = cache

    def record_violation(self, identifier: str, endpoint: str = None):
        """Record a rate limit violation"""
        cache_key = f"rl_violation:{identifier}"

        violation_data = self.redis.get(cache_key)

        if violation_data:
            violation_data["violation_count"] += 1
            violation_data["last_violation"] = datetime.now().isoformat()
            violation_data["endpoint"] = endpoint
            self.redis.set(cache_key, violation_data, 86400)
        else:
            violation_data = {
                "identifier": identifier,
                "violation_count": 1,
                "first_violation": datetime.now().isoformat(),
                "last_violation": datetime.now().isoformat(),
                "endpoint": endpoint,
            }
            self.redis.set(cache_key, violation_data, 86400)

        logger.warning(
            f"Rate limit violation: {identifier} "
            f"(count: {violation_data['violation_count']}, endpoint: {endpoint})"
        )

        if violation_data["violation_count"] >= self.BAN_THRESHOLD:
            self._ban_abuser(identifier)

    def _ban_abuser(self, identifier: str):
        """Temporarily ban repeat offenders"""
        ban_key = f"rl_banned:{identifier}"
        self.redis.set(ban_key, True, self.BAN_DURATION)
        logger.error(f"Rate limit ban: {identifier} ({self.BAN_DURATION}s)")

    def is_banned(self, identifier: str) -> bool:
        """Check if identifier is currently banned"""
        ban_key = f"rl_banned:{identifier}"
        return self.redis.get(ban_key, False)

    def get_violations(self, limit: int = 100) -> List[Dict]:
        """Get recent rate limit violations"""
        violations = []
        try:
            keys = self.redis.keys("rl_violation:*")
            for key in keys[:limit]:
                data = self.redis.get(key)
                if data:
                    violations.append(
                        {
                            "identifier": data["identifier"],
                            "count": data["violation_count"],
                            "first": data["first_violation"],
                            "last": data["last_violation"],
                            "endpoint": data.get("endpoint"),
                        }
                    )
        except Exception as e:
            logger.error(f"Error fetching violations: {e}")

        return sorted(violations, key=lambda x: x["count"], reverse=True)

    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        try:
            keys = self.redis.keys("rl_violation:*")
            total_violations = 0
            for key in keys:
                data = self.redis.get(key)
                if data:
                    total_violations += data["violation_count"]

            banned_keys = self.redis.keys("rl_banned:*")
            active_bans = len(banned_keys)

            return {
                "total_violations": total_violations,
                "unique_abusers": len(keys),
                "active_bans": active_bans,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    def cleanup_old_violations(self, max_age_hours: int = 168):
        """Clean up old violation records (older than 1 week)"""
        try:
            keys = self.redis.keys("rl_violation:*")
            cleaned = 0
            cutoff = datetime.now() - timedelta(hours=max_age_hours)

            for key in keys:
                data = self.redis.get(key)
                if data:
                    first_violation = datetime.fromisoformat(data["first_violation"])
                    if first_violation < cutoff:
                        self.redis.delete(key)
                        cleaned += 1

            logger.info(f"Cleaned {cleaned} old violation records")
            return cleaned
        except Exception as e:
            logger.error(f"Error cleaning violations: {e}")
            return 0


_rate_limit_monitor = None


def get_rate_limit_monitor() -> RateLimitMonitor:
    """Get global rate limit monitor instance"""
    global _rate_limit_monitor
    if _rate_limit_monitor is None:
        _rate_limit_monitor = RateLimitMonitor()
    return _rate_limit_monitor
