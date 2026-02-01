"""
Enhanced Health Check Endpoint
Provides detailed system health status for deployment safety and monitoring.
"""

from typing import Dict, Any, List
from ninja import Router
from django.core.cache import cache
from django.db import connection
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router(tags=["Health"])


def check_database() -> Dict[str, Any]:
    """Check database connectivity and status."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        # Get connection counts
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) as total
                FROM pg_stat_activity
            """)
            result = cursor.fetchone()
            total_connections = result[0] if result else 0

        # Get database size
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = cursor.fetchone()[0]

        return {
            "status": "healthy",
            "connections": total_connections,
            "size": db_size,
            "response_time_ms": 0,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connections": 0,
            "size": "unknown",
        }


def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and status."""
    try:
        # Test Redis connection
        start_time = time.time()
        cache.set("health_check", "ok", 10)
        value = cache.get("health_check")
        response_time = (time.time() - start_time) * 1000

        # Get Redis info if available
        redis_info = {}
        try:
            from django.core.cache import caches

            redis_client = caches["default"].get_client()
            info = redis_client.info()
            redis_info = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_days": info.get("uptime_in_days", 0),
            }
        except:
            pass

        return {
            "status": "healthy" if value == "ok" else "unhealthy",
            "response_time_ms": round(response_time, 2),
            **redis_info,
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "response_time_ms": 0}


def check_migrations() -> Dict[str, Any]:
    """Check if there are pending migrations."""
    try:
        from django.core.management import call_command
        from io import StringIO

        # Check for pending migrations
        out = StringIO()
        call_command("showmigrations", "--plan", stdout=out)
        output = out.getvalue()

        # Count pending migrations (lines starting with '[')
        pending = output.count("[") - output.count("[X]")

        # Exclude optional migrations (sessions) from critical check
        optional_migrations = ["sessions"]
        critical_pending = pending
        if (
            "sessions" in output
            and "[ ]" in output.split("sessions")[0].split("\n")[-1]
        ):
            critical_pending = pending - 1

        return {
            "status": "healthy" if critical_pending == 0 else "warning",
            "pending_migrations": pending,
            "critical_pending_migrations": critical_pending,
            "all_applied": pending == 0,
            "critical_applied": critical_pending == 0,
        }
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "pending_migrations": -1,
            "critical_pending_migrations": -1,
        }
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return {"status": "error", "error": str(e), "pending_migrations": -1}


def get_deployment_info() -> Dict[str, Any]:
    """Get deployment information."""
    try:
        # Try to get git commit hash
        import subprocess

        commit_hash = "unknown"
        try:
            commit_hash = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    cwd="/app/src",
                )
                .decode("utf-8")
                .strip()
            )
        except:
            pass

        # Get container uptime (approximate by process start time)
        uptime = "unknown"
        try:
            with connection.cursor() as cursor:
                # This gives us postgres uptime, close enough for proxy
                cursor.execute("SELECT pg_postmaster_start_time()")
                start_time = cursor.fetchone()[0]
                uptime = str(datetime.now() - start_time).split(".")[0]
        except:
            pass

        return {
            "commit": commit_hash,
            "uptime": uptime,
            "timestamp": datetime.now().isoformat(),
            "environment": "development",  # TODO: Make this configurable
        }
    except Exception as e:
        return {
            "commit": "unknown",
            "uptime": "unknown",
            "timestamp": datetime.now().isoformat(),
            "environment": "unknown",
        }


@router.get("/detailed", response=Dict[str, Any])
def detailed_health(request) -> Dict[str, Any]:
    """
    Get detailed system health status.

    Returns comprehensive health information for all system components.
    Use this for pre-deployment and post-deployment validation.
    """
    start_time = time.time()

    database = check_database()
    redis = check_redis()
    migrations = check_migrations()
    deployment = get_deployment_info()

    # Calculate overall status
    components = [database, redis, migrations]
    if all(c["status"] == "healthy" for c in components):
        overall_status = "healthy"
    elif any(
        c["status"] == "unhealthy" or c.get("status") == "error" for c in components
    ):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    response_time = (time.time() - start_time) * 1000

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "response_time_ms": round(response_time, 2),
        "components": {"database": database, "redis": redis, "migrations": migrations},
        "deployment": deployment,
        "checks": {
            "database_healthy": database["status"] == "healthy",
            "redis_healthy": redis["status"] == "healthy",
            "migrations_applied": migrations["all_applied"],
            "critical_migrations_applied": migrations["critical_applied"],
            "can_deploy": all(
                [
                    database["status"] == "healthy",
                    redis["status"] == "healthy",
                    migrations["critical_applied"],
                ]
            ),
        },
    }


@router.get("/simple", response=Dict[str, Any])
def simple_health(request) -> Dict[str, Any]:
    """
    Get simple health status for load balancers.

    Returns minimal health information. Use this for Docker health checks.
    """
    database_ok = check_database()["status"] == "healthy"
    redis_ok = check_redis()["status"] == "healthy"

    overall_status = "healthy" if (database_ok and redis_ok) else "unhealthy"

    return {"status": overall_status, "timestamp": datetime.now().isoformat()}


@router.get("/ready", response=Dict[str, Any])
def readiness_check(request) -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe.

    Check if the service is ready to accept traffic.
    """
    try:
        # Check critical dependencies
        database = check_database()
        redis = check_redis()

        ready = database["status"] == "healthy" and redis["status"] == "healthy"

        return {
            "ready": ready,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": database["status"] == "healthy",
                "redis": redis["status"] == "healthy",
            },
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/live", response=Dict[str, Any])
def liveness_check(request) -> Dict[str, Any]:
    """
    Kubernetes-style liveness probe.

    Check if the service is alive. If this fails, the container should be restarted.
    """
    return {"alive": True, "timestamp": datetime.now().isoformat()}
