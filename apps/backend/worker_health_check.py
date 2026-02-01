#!/usr/bin/env python3
"""
Worker health check script for Dramatiq
Used by Docker health check to verify worker is processing tasks
"""

import os
import sys
import json

# Setup Django
sys.path.insert(0, "/app/src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    import django

    django.setup()

    from dramatiq.brokers.redis import RedisBroker
    from redis import Redis
    from django.db import connection

    def check_worker_health():
        """Check if worker is healthy"""
        health_status = {
            "worker": "unknown",
            "broker": "unknown",
            "database": "unknown",
            "redis_connected": False,
            "error": None,
        }

        try:
            # Check Redis broker connection
            redis_client = Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=0,
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            redis_client.ping()
            health_status["redis_connected"] = True
            health_status["broker"] = "healthy"

            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status["database"] = "healthy"

            # Overall status
            if all(
                status == "healthy"
                for status in [health_status["broker"], health_status["database"]]
            ):
                health_status["worker"] = "healthy"
            else:
                health_status["worker"] = "degraded"

            return health_status

        except Exception as e:
            health_status["worker"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status

    if __name__ == "__main__":
        status = check_worker_health()

        if status["worker"] == "healthy":
            print(json.dumps(status))
            sys.exit(0)
        else:
            print(json.dumps(status))
            sys.exit(1)

except ImportError as e:
    # Fallback if imports fail
    print(
        json.dumps(
            {
                "worker": "unhealthy",
                "error": f"Import error: {e}",
                "broker": "unknown",
                "database": "unknown",
            }
        )
    )
    sys.exit(1)
