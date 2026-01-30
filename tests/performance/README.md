# FinanceHub Performance Testing Guide

**Author:** KAREN (DevOps Engineer)
**Date:** 2026-01-30
**Status:** Production Ready

---

## 📊 Overview

This guide covers performance testing for FinanceHub using Locust, a scalable load testing tool.

### Goals

- Identify performance bottlenecks before production
- Ensure system can handle expected traffic
- Test system behavior under load
- Establish performance baselines
- Validate auto-scaling configurations

---

## 🚀 Quick Start

### Installation

```bash
# Install Locust
pip install locust

# Or with requirements
echo "locust>=2.15.0" >> requirements-testing.txt
pip install -r requirements-testing.txt
```

### Basic Usage

**Web UI Mode (Recommended for First Time):**
```bash
locust -f tests/performance/locustfile.py --host=https://staging-api.financehub.com
```

This starts a web UI at http://localhost:8089 where you can:
- Set number of users
- Set spawn rate
- Start/stop tests
- View real-time statistics

**Headless Mode (Automated Testing):**
```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --host=https://staging-api.financehub.com
```

---

## 📋 Test Scenarios

### 1. Smoke Test (Quick Validation)

**Purpose:** Verify system is functioning normally

```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 10 \
  --spawn-rate 1 \
  --run-time 1m \
  --host=https://staging-api.financehub.com
```

**Expected:**
- 0% failures
- Response time < 500ms (p95)
- No errors in logs

### 2. Normal Load Test

**Purpose:** Simulate normal daily traffic

```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --host=https://staging-api.financehub.com
```

**Expected:**
- < 1% failures
- Response time < 1000ms (p95)
- CPU < 70%
- Memory < 80%

### 3. Peak Load Test

**Purpose:** Simulate peak traffic (market hours)

```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 500 \
  --spawn-rate 50 \
  --run-time 15m \
  --host=https://staging-api.financehub.com
```

**Expected:**
- < 2% failures
- Response time < 2000ms (p95)
- Auto-scaling triggers if configured
- System recovers after test

### 4. Stress Test

**Purpose:** Find breaking point

```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 2000 \
  --spawn-rate 100 \
  --run-time 20m \
  --host=https://staging-api.financehub.com
```

**Expected:**
- System will eventually fail
- Identify failure modes
- Document breaking point
- Don't run in production!

### 5. Endurance Test (Soak Test)

**Purpose:** Test system over extended period

```bash
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 2h \
  --host=https://staging-api.financehub.com
```

**Expected:**
- No memory leaks
- Stable response times
- No database connection leaks
- Performance doesn't degrade over time

---

## 📊 Metrics to Monitor

### Key Performance Indicators (KPIs)

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Response Time (p50) | < 200ms | > 300ms | > 500ms |
| Response Time (p95) | < 500ms | > 1000ms | > 2000ms |
| Response Time (p99) | < 1000ms | > 2000ms | > 5000ms |
| Failure Rate | < 1% | > 2% | > 5% |
| Requests Per Second (RPS) | > 100 | < 50 | < 10 |
| CPU Usage | < 50% | > 70% | > 90% |
| Memory Usage | < 60% | > 80% | > 90% |
| Database Connections | < 100 | > 150 | > 200 |

### Monitoring During Tests

**CPU & Memory:**
```bash
# Watch CPU usage
watch -n 1 'top -n 1 | head -20'

# Watch memory
watch -n 1 'free -h'

# Watch Docker stats
docker stats
```

**Database:**
```bash
# Check connection count
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**API Response Times:**
```bash
# Use curl to test specific endpoints
time curl -w "\n" https://api.financehub.com/api/v1/market/stocks/AAPL/quote/
```

---

## 🔧 Test Configuration

### Environment Variables

```bash
# Test environment
export TEST_HOST="https://staging-api.financehub.com"
export TEST_USERS="100"
export TEST_SPAWN_RATE="10"
export TEST_DURATION="10m"

# Run with environment variables
locust -f tests/performance/locustfile.py \
  --headless \
  --users ${TEST_USERS} \
  --spawn-rate ${TEST_SPAWN_RATE} \
  --run-time ${TEST_DURATION} \
  --host ${TEST_HOST}
```

### Custom Test Profiles

Create custom test profiles in `tests/performance/profiles/`:

**low_traffic.py:**
```python
from locustfile import FinanceHubUser

class LowTrafficUser(FinanceHubUser):
    wait_time = between(5, 10)  # Slower, more realistic
```

**high_traffic.py:**
```python
from locustfile import FinanceHubUser

class HighTrafficUser(FinanceHubUser):
    wait_time = between(0.1, 0.5)  # Fast, aggressive
```

Run with:
```bash
locust -f tests/performance/profiles/high_traffic.py --host=https://staging-api.financehub.com
```

---

## 📈 CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/performance-test.yml`:

```yaml
name: Performance Test

on:
  pull_request:
    paths:
      - 'Backend/**'
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install locust

      - name: Run performance test
        run: |
          locust -f tests/performance/locustfile.py \
            --headless \
            --users 50 \
            --spawn-rate 5 \
            --run-time 5m \
            --host ${{ secrets.STAGING_API_URL }} \
            --html performance-report.html

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.html

      - name: Comment PR with results
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Performance test complete! Check artifacts for detailed report.'
            })
```

### Makefile Integration

Add to Makefile:

```makefile
# Performance testing
perf-test:
	@echo "🚀 Running performance tests..."
	locust -f tests/performance/locustfile.py \
		--headless \
		--users 100 \
		--spawn-rate 10 \
		--run-time 5m \
		--host $(TEST_HOST)

perf-test-ui:
	@echo "🚀 Starting performance test UI..."
	locust -f tests/performance/locustfile.py --host $(TEST_HOST)

perf-test-stress:
	@echo "⚠️  Running stress test..."
	locust -f tests/performance/locustfile.py \
		--headless \
		--users 1000 \
		--spawn-rate 100 \
		--run-time 10m \
		--host $(TEST_HOST)
```

---

## 🎯 Best Practices

### Before Testing

1. **Use Staging Environment** - Never test in production
2. **Clear Caches** - Start with clean slate
3. **Warm Up** - Run 1-minute warm-up before real test
4. **Set Up Monitoring** - Ensure all metrics are being collected
5. **Prepare Rollback** - Have rollback plan ready

### During Testing

1. **Monitor System Metrics** - CPU, memory, disk, network
2. **Check Logs** - Look for errors and warnings
3. **Watch Database** - Connection pool, slow queries
4. **Monitor External APIs** - Don't overload third-party services
5. **Document Everything** - Take notes, screenshots

### After Testing

1. **Analyze Results** - Identify bottlenecks
2. **Fix Issues** - Address performance problems
3. **Retest** - Verify fixes work
4. **Update Baselines** - Document new baselines
5. **Report Findings** - Share with team

---

## 🐛 Troubleshooting

### High Failure Rate

**Symptoms:** > 5% request failures

**Solutions:**
- Check API is healthy: `curl -f https://api.financehub.com/health/`
- Review logs: `make logs SERVICE=backend`
- Check database connections
- Verify load balancer health
- Check rate limiting

### Slow Response Times

**Symptoms:** p95 > 2000ms

**Solutions:**
- Enable database query logging
- Check for N+1 queries
- Add database indexes
- Enable caching (Redis)
- Optimize slow endpoints
- Scale up/out

### Memory Leaks

**Symptoms:** Memory usage grows over time

**Solutions:**
- Run endurance test (2+ hours)
- Check for unclosed connections
- Review Python garbage collection
- Check for cached data not being cleared
- Profile memory usage

### Database Connection Pool Exhaustion

**Symptoms:** "Connection pool exhausted" errors

**Solutions:**
- Increase pool size in settings
- Check for connection leaks
- Add connection recycling
- Implement proper connection closing
- Use connection pooling middleware

---

## 📊 Sample Results

### Acceptable Performance

```
╭─────────────────────────────────────────────────────────╮
│ FinanceHub Performance Test Results                     │
├─────────────────────────────────────────────────────────┤
│ Users:           100                                    │
│ Spawn Rate:      10 users/sec                           │
│ Duration:        10 minutes                             │
├─────────────────────────────────────────────────────────┤
│ Total Requests:  45,231                                 │
│ Failure Rate:    0.12% ✅                               │
│ RPS:             75.4                                   │
├─────────────────────────────────────────────────────────┤
│ Response Times:                                          │
│   Median:        245 ms ✅                              │
│   Average:       312 ms                                 │
│   Min:           45 ms                                  │
│   Max:           1,234 ms                               │
│   p95:           567 ms ✅                              │
│   p99:           923 ms ✅                              │
├─────────────────────────────────────────────────────────┤
│ System Metrics:                                          │
│   CPU Usage:      45% ✅                                │
│   Memory Usage:   62% ✅                                │
│   DB Connections: 87/200 ✅                             │
╰─────────────────────────────────────────────────────────╯

✅ TEST PASSED - System is performant!
```

### Performance Issues Detected

```
╭─────────────────────────────────────────────────────────╮
│ ⚠️  PERFORMANCE ISSUES DETECTED                         │
├─────────────────────────────────────────────────────────┤
│ Issues:                                                 │
│   • p95 response time: 2,345 ms (target: < 1000ms)     │
│   • Failure rate: 3.2% (target: < 1%)                  │
│   • CPU usage: 87% (target: < 70%)                     │
├─────────────────────────────────────────────────────────┤
│ Slow Endpoints:                                         │
│   1. GET /portfolio/performance/ - avg: 3,456 ms       │
│   2. POST /analytics/complex/ - avg: 2,890 ms          │
│   3. GET /market/stocks/*/history/ - avg: 1,234 ms     │
├─────────────────────────────────────────────────────────┤
│ Recommendations:                                        │
│   1. Add Redis caching for portfolio performance       │
│   2. Optimize complex analytics query                  │
│   3. Add database index for stock history              │
│   4. Enable gzip compression                           │
╰─────────────────────────────────────────────────────────╯
```

---

## 🔄 Continuous Improvement

### Weekly Performance Testing

```bash
# Add to crontab
0 2 * * 0 cd /path/to/FinanceHub && make perf-test > /var/log/perf-test.log 2>&1
```

### Performance Regression Detection

Set up automated alerts when performance degrades:

```yaml
# In CI/CD pipeline
- name: Check performance regression
  run: |
    CURRENT_P95=$(cat performance-report.html | grep "95%" | awk '{print $2}')
    BASELINE_P95=500  # milliseconds
    
    if (( $(echo "$CURRENT_P95 > $BASELINE_P95" | bc -l) )); then
      echo "⚠️  Performance regression detected!"
      echo "Current p95: ${CURRENT_P95}ms"
      echo "Baseline: ${BASELINE_P95}ms"
      exit 1
    fi
```

---

## 📚 Resources

- **Locust Documentation:** https://docs.locust.io/
- **Performance Testing Best Practices:** https://docs.locust.io/en/stable/testing.html
- **FinanceHub DevOps Docs:** `/docs/MONITORING.md`

---

**Author:** KAREN (DevOps Engineer)
**Last Updated:** 2026-01-30
**Status:** ✅ Production Ready
