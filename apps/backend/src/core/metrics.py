from prometheus_client import Counter, Histogram, Gauge, generate_latest
from django.http import HttpResponse
from django.db import connection
import os

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_USERS = Gauge('active_users', 'Number of active users')

DB_CONNECTIONS = Gauge('db_connections', 'Database connections')

CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['backend'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['backend'])

TASK_COUNT = Counter('tasks_total', 'Total tasks processed', ['task_type', 'status'])
TASK_DURATION = Histogram('task_duration_seconds', 'Task duration', ['task_type'])


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
    
    return HttpResponse(generate_latest(), content_type='text/plain')


class MetricsMiddleware:
    """Middleware to track request metrics"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track request count
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        
        return response
