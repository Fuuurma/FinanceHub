# API Rate Limits

## Overview

FinanceHub implements comprehensive rate limiting to prevent API abuse and ensure fair resource allocation.

## Rate Limit Tiers

| Tier | Requests/Hour | Cost |
|------|---------------|------|
| Anonymous | 100 | Free |
| Free User | 1,000 | Free |
| Premium User | 5,000 | $29/month |
| Pro User | 10,000 | $99/month |

## Endpoint-Specific Limits

| Endpoint | Method | Anonymous | Authenticated |
|----------|--------|-----------|---------------|
| `/api/market/overview` | GET | 100/hour | 1,000/hour |
| `/api/market/indices` | GET | 200/hour | 2,000/hour |
| `/api/market/data` | GET | 150/hour | 1,500/hour |
| `/api/assets/search` | GET | 50/hour | 500/hour |
| `/api/assets/{id}` | GET | 300/hour | 3,000/hour |
| `/api/portfolios/` | GET | 100/hour | 1,000/hour |
| `/api/portfolios/` | POST | 20/hour | 200/hour |
| `/api/watchlist/` | POST | 30/hour | 300/hour |
| `/api/alerts/` | POST | 20/hour | 200/hour |
| `/api/news/` | GET | 100/hour | 1,000/hour |

## Rate Limit Headers

All API responses include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1738289765
```

- **X-RateLimit-Limit**: Maximum requests allowed in the current window
- **X-RateLimit-Remaining**: Requests remaining in the current window
- **X-RateLimit-Reset**: Unix timestamp when the window resets

## Cache Headers

Cached responses include additional headers:

```
X-Cache: HIT
```

- **X-Cache**: `HIT` (response from cache) or `MISS` (freshly generated)

## Exceeded Limits

When rate limit is exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "message": "Maximum 1000 requests per hour allowed",
  "retry_after": 3600
}
```

**HTTP Status:** 429 Too Many Requests

**Headers:**
```
Retry-After: 3600
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1738289765
```

## Best Practices

### 1. Handle Rate Limits Gracefully

```python
import requests

def fetch_with_rate_limit(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_with_rate_limit(url, headers)

    return response
```

### 2. Monitor Your Usage

Track `X-RateLimit-Remaining` to stay within limits:

```python
def make_api_request(url, headers):
    response = requests.get(url, headers=headers)

    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    if remaining < 100:
        print(f"Warning: Only {remaining} requests remaining")

    return response
```

### 3. Use Caching

Cache responses to reduce API calls:

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=100)
def cached_request(url):
    response = requests.get(url)
    return response.json()
```

## Rate Limit Violations

Repeat offenders may be temporarily banned:

- **Threshold**: 10+ violations within 1 hour
- **Ban Duration**: 2 hours
- **Violations tracked**: IP address and user ID

## Monitoring

Access rate limit statistics at `/api/admin/rate-limits/` (admin only):

- Total violations
- Unique abusers
- Active bans
- Top violators

## Contact

For higher rate limits or enterprise usage, contact support@financehub.com
