# Monitoring & Alerting for FinanceHub

## Overview

FinanceHub uses AWS CloudWatch, CloudWatch Logs, and CloudWatch X-Ray for comprehensive monitoring, logging, and distributed tracing.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │   CloudWatch  │  │ CloudWatch    │  │    CloudWatch    │    │
│  │   Metrics     │  │    Logs       │  │      X-Ray       │    │
│  │               │  │               │  │                  │    │
│  │  • CPU        │  │  • App Logs   │  │  • Tracing       │    │
│  │  • Memory     │  │  • Access     │  │  • Latency       │    │
│  │  • Requests   │  │  • Errors     │  │  • Errors        │    │
│  │  • Errors     │  │  • Security   │  │  • Dependencies  │    │
│  └───────┬───────┘  └───────┬───────┘  └────────┬─────────┘    │
│          │                  │                   │               │
│          └──────────────────┴───────────────────┘               │
│                              │                                   │
│                              ▼                                   │
│                   ┌─────────────────────┐                       │
│                   │   CloudWatch        │                       │
│                   │   Alarms            │                       │
│                   │   → SNS → Slack     │                       │
│                   └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics Collection

### Infrastructure Metrics

#### ECS Fargate Metrics
| Metric | Description | Alarm Threshold |
|--------|-------------|-----------------|
| `CPUUtilization` | CPU usage per task | > 80% for 5 minutes |
| `MemoryUtilization` | Memory usage per task | > 85% for 5 minutes |
| `TaskCount` | Number of running tasks | < 2 tasks |
| `CPUUtilization (Average)` | Average CPU across all tasks | > 70% for 10 minutes |

#### RDS PostgreSQL Metrics
| Metric | Description | Alarm Threshold |
|--------|-------------|-----------------|
| `CPUUtilization` | Database CPU usage | > 75% for 5 minutes |
| `FreeableMemory` | Available memory | < 1 GB for 5 minutes |
| `DatabaseConnections` | Active connections | > 80 for 5 minutes |
| `ReadLatency` | Read query latency | > 100ms for 5 minutes |
| `WriteLatency` | Write query latency | > 100ms for 5 minutes |
| `ReplicationLag` | Replica lag | > 5 seconds |

#### ElastiCache Redis Metrics
| Metric | Description | Alarm Threshold |
|--------|-------------|-----------------|
| `CPUUtilization` | Cache CPU usage | > 80% for 5 minutes |
| `FreeableMemory` | Available memory | < 500 MB for 5 minutes |
| `CurrConnections` | Active connections | > 100 for 5 minutes |
| `CacheHitRate` | Cache hit percentage | < 80% for 10 minutes |
| `Evictions` | Keys evicted | > 100/minute |

#### Application Load Balancer Metrics
| Metric | Description | Alarm Threshold |
|--------|-------------|-----------------|
| `RequestCount` | Total requests | N/A |
| `TargetResponseTime` | Backend response time | > 2 seconds (P95) |
| `HTTPCode_Target_5XX` | Server errors | > 5% for 5 minutes |
| `HTTPCode_Target_4XX` | Client errors | > 10% for 5 minutes |
| `UnHealthyHostCount` | Unhealthy targets | > 0 for 2 minutes |

### Application Metrics (Custom)

#### Backend API Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request latency
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Active connections
active_connections = Gauge(
    'active_connections',
    'Active database connections'
)

# Background job queue size
queue_size = Gauge(
    'background_job_queue_size',
    'Number of jobs in queue',
    ['queue_name']
)
```

#### Frontend Metrics
```typescript
// Web Vitals (tracked by browser)
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1
- FCP (First Contentful Paint): < 1.8s
- TTI (Time to Interactive): < 3.8s
```

### Business Metrics
| Metric | Description | Source |
|--------|-------------|--------|
| `active_users` | Daily active users | Database query |
| `api_calls` | API call volume | CloudWatch Logs |
| `errors_total` | Total errors | CloudWatch Logs |
| `portfolio_updates` | Portfolio update operations | Application logs |
| `trades_executed` | Trades placed | Application logs |

## Logging Strategy

### Log Levels
| Level | Usage | Examples |
|-------|-------|----------|
| `CRITICAL` | System-wide failures | Database connection lost |
| `ERROR` | Application errors | Unhandled exceptions |
| `WARNING` | Potential issues | Deprecated API usage |
| `INFO` | Informational events | User login, API calls |
| `DEBUG` | Diagnostic info | Variable values, flow |

### Log Format (Structured JSON)
```json
{
  "timestamp": "2026-01-30T12:34:56.789Z",
  "level": "INFO",
  "logger": "financehub.api",
  "message": "API request received",
  "context": {
    "request_id": "abc-123",
    "user_id": "user@example.com",
    "method": "GET",
    "endpoint": "/api/portfolio/123",
    "status": 200,
    "duration_ms": 45
  },
  "tags": ["api", "portfolio"],
  "environment": "production"
}
```

### Log Examples

#### Backend (Python)
```python
import structlog

logger = structlog.get_logger()

# API request
logger.info(
    "api_request",
    method=request.method,
    path=request.path,
    status_code=response.status_code,
    duration_ms=duration,
    user_id=request.user.id if request.user.is_authenticated else None
)

# Error
logger.error(
    "database_error",
    error=str(e),
    query=query,
    user_id=user.id
)

# Business event
logger.info(
    "portfolio_created",
    user_id=user.id,
    portfolio_id=portfolio.id,
    portfolio_type=portfolio.portfolio_type
)
```

#### Frontend (TypeScript)
```typescript
import { logger } from '@/lib/logger'

// User action
logger.info('button_clicked', {
  button: 'save_portfolio',
  page: '/portfolio/123',
  user_id: userId
})

// Error
logger.error('api_error', {
  endpoint: '/api/portfolio',
  status: 500,
  message: error.message
})

// Performance
logger.info('page_load', {
  page: '/dashboard',
  load_time_ms: performance.now()
})
```

## Alerting Strategy

### Alert Severity Levels
| Severity | Response Time | Notification Channels |
|----------|--------------|----------------------|
| **P0 - Critical** | < 5 minutes | PagerDuty, Slack, SMS, Call |
| **P1 - High** | < 15 minutes | Slack, Email |
| **P2 - Medium** | < 1 hour | Slack, Email |
| **P3 - Low** | Next business day | Email |

### Critical Alerts (P0)

#### High Error Rate
```yaml
- Name: High API Error Rate
  Metric: http_requests_total{status=~"5.."}
  Threshold: > 5% of requests
  Duration: 5 minutes
  Severity: P0
  Actions:
    - Page on-call engineer
    - Post to #incidents Slack
    - Create GitHub issue
```

#### Database Connection Failure
```yaml
- Name: Database Unavailable
  Metric: DatabaseConnections == 0
  Duration: 1 minute
  Severity: P0
  Actions:
    - Page on-call engineer
    - Post to #incidents Slack
    - Check RDS status
```

#### Service Down
```yaml
- Name: All ECS Tasks Failed
  Metric: TaskCount == 0
  Duration: 2 minutes
  Severity: P0
  Actions:
    - Page on-call engineer
    - Post to #incidents Slack
    - Check ECS task status
```

### High Priority Alerts (P1)

#### High Latency
```yaml
- Name: High API Latency
  Metric: http_request_duration_seconds (P95) > 2s
  Duration: 5 minutes
  Severity: P1
  Actions:
    - Post to #alerts Slack
    - Send email
    - Check database performance
```

#### High Memory Usage
```yaml
- Name: ECS Memory High
  Metric: MemoryUtilization > 85%
  Duration: 5 minutes
  Severity: P1
  Actions:
    - Post to #alerts Slack
    - Check for memory leaks
    - Consider scaling
```

#### Disk Space Low
```yaml
- Name: RDS Disk Space Low
  Metric: FreeStorageSpace < 10 GB
  Duration: 10 minutes
  Severity: P1
  Actions:
    - Post to #alerts Slack
    - Schedule maintenance
    - Expand storage if needed
```

### Medium Priority Alerts (P2)

#### Cache Hit Rate Low
```yaml
- Name: Cache Miss High
  Metric: CacheHitRate < 80%
  Duration: 10 minutes
  Severity: P2
  Actions:
    - Post to #alerts Slack
    - Review cache strategy
```

#### Queue Backup
```yaml
- Name: Background Job Queue High
  Metric: background_job_queue_size > 1000
  Duration: 10 minutes
  Severity: P2
  Actions:
    - Post to #alerts Slack
    - Add more workers
```

### Low Priority Alerts (P3)

#### Cost Spike
```yaml
- Name: Unusual Cost Increase
  Metric: AWS daily cost > 2x average
  Duration: 1 day
  Severity: P3
  Actions:
    - Send email
    - Review AWS Cost Explorer
```

## Dashboards

### Main Dashboard: Infrastructure Overview
**Widgets**:
- ECS CPU & Memory (all services)
- RDS CPU, Connections, Storage
- ElastiCache CPU, Memory, Hit Rate
- ALB Request Count, Latency, Error Rate
- CloudFront Requests, Bytes Transferred
- Custom Application Metrics

### Application Dashboard
**Widgets**:
- Request rate (requests/second)
- Error rate (errors/second)
- P50, P95, P99 latency
- Active users
- Background job queue size
- Business metrics (trades, portfolios)

### Database Dashboard
**Widgets**:
- Connection pool utilization
- Query performance (slow queries)
- Replication lag
- Transaction throughput
- Lock waits
- Cache hit ratio

### Error Dashboard
**Widgets**:
- Error rate by endpoint
- Top error messages
- Error rate by user
- HTTP 5xx errors
- Application exceptions

## Performance Monitoring

### Application Performance Monitoring (APM)

#### X-Ray Tracing
- **Sample rate**: 10% of requests
- **Trace retention**: 7 days
- **Annotations**:
  - User ID
  - Request ID
  - Service name
  - Environment

#### Key Traces
- API request flow
- Database query execution
- External API calls
- Background job execution

### Performance Budgets
| Metric | Budget | Current | Status |
|--------|--------|---------|--------|
| API P95 Latency | < 500ms | 350ms | ✅ Pass |
| API P99 Latency | < 1s | 800ms | ✅ Pass |
| Database Query (P95) | < 100ms | 75ms | ✅ Pass |
| Page Load (P95) | < 3s | 2.1s | ✅ Pass |
| First Contentful Paint | < 1.8s | 1.2s | ✅ Pass |

## Incident Response

### On-Call Rotation
- **Schedule**: Weekly rotation
- **Primary**: Responds to P0, P1 alerts
- **Secondary**: Backup for primary
- **Tool**: PagerDuty

### Incident Response Process

#### 1. Detection (Automated)
- Alert fires
- Creates incident in Slack (#incidents)
- Pages on-call engineer

#### 2. Acknowledgment (5 minutes)
- On-call engineer acknowledges
- Posts update to Slack
- Assigns severity level

#### 3. Investigation (15 minutes)
- Review logs and metrics
- Identify root cause
- Document findings

#### 4. Mitigation (30 minutes)
- Implement fix or workaround
- Verify resolution
- Monitor for stability

#### 5. Resolution (1 hour)
- Confirm service restored
- Close incident
- Update metrics

### Post-Incident Review
Within 48 hours of incident:
1. Create post-mortem document
2. Identify root cause
3. List action items
4. Update runbooks
5. Share with team

## Log Retention & Archival

| Log Type | Retention | Archive |
|----------|-----------|---------|
| Application Logs | 7 days | S3 Glacier (90 days) |
| Access Logs | 1 day | S3 Glacier (30 days) |
| Security Logs | 90 days | S3 Glacier (1 year) |
| Audit Logs | 1 year | S3 Glacier (7 years) |

## Cost Monitoring

### Monthly Budget
- **Infrastructure**: $2,000/month
- **Monitoring**: ~$50/month (CloudWatch)

### Cost Alerts
- Warning at 80% of budget ($1,600)
- Critical at 100% of budget ($2,000)

### Cost Optimization
- Use CloudWatch Logs Subscription Filters to archive old logs
- Sample traces instead of 100%
- Aggregate custom metrics
- Use granular CloudWatch alarms

## Monitoring Best Practices

### DO ✅
- Set up alerts before deploying to production
- Use structured logging (JSON)
- Include request correlation IDs
- Monitor both infrastructure and application
- Regularly review and tune alerts
- Document runbooks for common scenarios

### DON'T ❌
- Don't ignore alerts (investigate all)
- Don't set alert thresholds too low/sensitive
- Don't log sensitive data (PII, credentials)
- Don't keep logs forever (expensive)
- Don't monitor without actionability
- Don't forget to update dashboards

## Tools & Integrations

### Monitoring Tools
- **AWS CloudWatch**: Metrics, logs, alarms
- **AWS X-Ray**: Distributed tracing
- **Prometheus**: Custom metrics (optional)
- **Grafana**: Dashboards (optional)

### Alerting Tools
- **AWS SNS**: Alert notifications
- **Slack**: Team notifications
- **PagerDuty**: On-call management
- **Email**: Low-priority alerts

### Log Analysis
- **CloudWatch Logs Insights**: Query logs
- **AWS Athena**: Query archived logs
- **Elasticsearch**: Full-text search (optional)

---

**Last Updated**: 2026-01-30
**Maintained By**: DevOps Team
**Next Review**: 2026-02-28
