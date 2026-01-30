# API Performance Issues Runbook

## Severity
- **Level**: P1 (High)
- **Response Time**: < 15 minutes

## Symptoms
- API response times > 2 seconds (P95)
- High CPU usage on backend containers
- User complaints about slow loading
- Timeouts on API endpoints

## Diagnosis

### 1. Check System Health
```bash
# Check CPU and memory
docker stats financehub-backend

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=finance-hub-api
```

### 2. Identify Slow Endpoints
```bash
# Check application logs
docker-compose logs backend | grep "slow"

# Check Django debug toolbar (if enabled)
# Visit /__debug__/ in browser

# Run profiling
cd Backend/src
python -m cProfile -o profile.stats manage.py runserver
python -m pstats profile.stats
> sort cumulative
> stats 20
```

### 3. Check Database Performance
```bash
# Check database connections
docker-compose exec postgres psql -U financehub -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
docker-compose exec backend python manage.py debugsqlshell

# View query statistics
docker-compose exec postgres psql -U financehub -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;
"
```

### 4. Check Cache Performance
```bash
# Check Redis hit rate
docker-compose exec redis redis-cli info stats | grep keyspace

# Check memory usage
docker-compose exec redis redis-cli info memory
```

## Resolution

### 1. Immediate Actions

#### If Database is the Bottleneck
```bash
# Check for long-running transactions
docker-compose exec postgres psql -U financehub -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query
  FROM pg_stat_activity
  WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Kill long-running queries if necessary
docker-compose exec postgres psql -U financehub -c "
  SELECT pg terminate_backend(pid)
  FROM pg_stat_activity
  WHERE pid <> pg_backend_pid()
  AND query_start < now() - interval '5 minutes';
"
```

#### If Cache Hit Rate is Low
```bash
# Warm up cache
curl http://localhost:8000/api/v1/portfolios
curl http://localhost:8000/api/v1/market/overview

# Check cache configuration
docker-compose exec redis redis-cli config get maxmemory
```

#### If N+1 Query Problem
```bash
# Enable Django debug toolbar
# Add to .env: DJANGO_DEBUG_TOOLBAR=True

# Use Django Debug Server to identify N+1 queries
# Look for duplicate queries in query panel
```

### 2. Scale Backend (Temporary)
```bash
# Increase ECS tasks
aws ecs update-service \
  --cluster finance-hub-production \
  --service finance-hub-api \
  --desired-count 10

# Or scale locally
docker-compose up -d --scale backend=5
```

### 3. Optimize Slow Queries

#### Add Database Indexes
```python
# Example: Add index to frequently queried field
# In migrations
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_portfolio_user ON portfolios_portfolio(user_id);"
        ),
    ]
```

#### Use Query Optimization
```python
# Bad: N+1 query
for portfolio in portfolios:
    print(portfolio.holdings.all())  # Separate query for each

# Good: Prefetch related
portfolios = Portfolio.objects.prefetch_related('holdings').all()
for portfolio in portfolios:
    print(portfolio.holdings.all())  # Already loaded
```

### 4. Enable/Improve Caching

```python
# Add caching to views
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def market_overview(request):
    # ...

# Add cache for expensive operations
from django.core.cache import cache

def get_portfolio_value(portfolio_id):
    cache_key = f"portfolio_value_{portfolio_id}"
    value = cache.get(cache_key)
    if value is None:
        value = calculate_portfolio_value(portfolio_id)
        cache.set(cache_key, value, timeout=300)  # 5 minutes
    return value
```

## Prevention

### 1. Monitoring
- Set up CloudWatch alarms for API latency
- Monitor database query performance
- Track cache hit rates

### 2. Regular Maintenance
- Weekly review of slow query log
- Monthly database index review
- Quarterly performance testing

### 3. Code Review Checklist
- [ ] No N+1 queries
- [ ] Appropriate use of select_related/prefetch_related
- [ ] Expensive operations are cached
- [ ] Database indexes are used
- [ ] Pagination for large result sets

### 4. Performance Testing
```bash
# Run load tests with Locust
cd Backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Test with 100 users, spawn rate 10/second
# Target: < 500ms response time, 0% errors
```

## Related
- [HIGH_CPU_MEMORY.md](./HIGH_CPU_MEMORY.md)
- [DATABASE_ISSUES.md](./DATABASE_ISSUES.md)
- [CACHE_ISSUES.md](./CACHE_ISSUES.md)

## Metrics to Monitor

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| API P95 Latency | > 2s | P1 |
| API P99 Latency | > 5s | P0 |
| Database Query Time | > 100ms | P2 |
| Cache Hit Rate | < 80% | P2 |
| Backend CPU | > 80% | P1 |

## Escalation
If unresolved after 30 minutes:
1. Inform team in Slack #incidents
2. Consider posting on call
3. Prepare rollback plan
