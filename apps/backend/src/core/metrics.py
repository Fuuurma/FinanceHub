from prometheus_client import Counter, Histogram, Gauge, generate_latest, Summary
from django.http import HttpResponse
from django.db import connection
import os
import time

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Enhanced per-endpoint metrics
API_REQUEST_DURATION = Histogram(
    "api_endpoint_duration_seconds",
    "API endpoint duration in seconds",
    ["method", "endpoint"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

API_REQUEST_ERRORS = Counter(
    "api_endpoint_errors_total",
    "Total API errors by endpoint",
    ["method", "endpoint", "error_type", "status_code"],
)

API_SLOW_REQUESTS = Counter(
    "api_slow_requests_total",
    "Total slow API requests (>1s)",
    ["method", "endpoint", "threshold"],
)

API_ACTIVE_REQUESTS = Gauge(
    "api_active_requests", "Currently active API requests", ["endpoint"]
)

# System metrics
ACTIVE_USERS = Gauge("active_users", "Number of active users")

DB_CONNECTIONS = Gauge("db_connections", "Database connections")

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["query_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

# Cache metrics
CACHE_HITS = Counter("cache_hits_total", "Cache hits", ["backend"])
CACHE_MISSES = Counter("cache_misses_total", "Cache misses", ["backend"])

CACHE_HIT_RATE = Gauge("cache_hit_rate", "Cache hit rate", ["backend"])

# Task metrics
TASK_COUNT = Counter("tasks_total", "Total tasks processed", ["task_type", "status"])
TASK_DURATION = Histogram("task_duration_seconds", "Task duration", ["task_type"])

TASK_QUEUE_SIZE = Gauge("task_queue_size", "Current task queue size", ["queue_name"])

# Background worker metrics
WORKER_ACTIVE = Gauge("worker_active", "Active background workers", ["worker_type"])

WORKER_TASKS_PROCESSED = Counter(
    "worker_tasks_processed_total",
    "Total tasks processed by worker",
    ["worker_type", "status"],
)


def metrics_view(request):
    """Prometheus metrics endpoint"""
    # Update DB connections metric
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            db_conn = cursor.fetchone()[0]
            DB_CONNECTIONS.set(db_conn)
    except Exception:
        pass

    return HttpResponse(generate_latest(), content_type="text/plain")


class MetricsMiddleware:
    """Enhanced middleware to track request metrics with latency"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Track active requests
        endpoint = self._normalize_endpoint(request.path)
        API_ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()

        response = self.get_response(request)

        # Calculate duration
        duration = time.time() - start_time

        # Track request count
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.path, status=response.status_code
        ).inc()

        # Track API latency with normalized endpoint
        API_REQUEST_DURATION.labels(method=request.method, endpoint=endpoint).observe(
            duration
        )

        # Track errors
        if response.status_code >= 400:
            error_type = (
                "client_error" if response.status_code < 500 else "server_error"
            )
            API_REQUEST_ERRORS.labels(
                method=request.method,
                endpoint=endpoint,
                error_type=error_type,
                status_code=str(response.status_code),
            ).inc()

        # Track slow requests
        if duration > 1.0:
            API_SLOW_REQUESTS.labels(
                method=request.method, endpoint=endpoint, threshold="1s"
            ).inc()

        # Decrement active requests
        API_ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()

        return response

    def _normalize_endpoint(self, path):
        """Normalize endpoint path for metrics grouping"""
        parts = path.strip("/").split("/")
        normalized_parts = []

        for part in parts:
            # Replace numeric IDs
            if part.isdigit():
                normalized_parts.append(":id")
            # Replace UUIDs
            elif len(part) == 36 and part.count("-") == 4:
                normalized_parts.append(":uuid")
            # Replace date patterns
            elif part.count("-") == 2 and len(part) <= 10:
                normalized_parts.append(":date")
            else:
                normalized_parts.append(part)

        return "/" + "/".join(normalized_parts)
