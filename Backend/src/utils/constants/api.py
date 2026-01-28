"""
API Constants
Centralized configuration for API limits, timeouts, and pagination.
Following best practices to avoid magic numbers scattered across codebase.
"""

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
DEFAULT_OFFSET = 0

# Limits - Alerts
ALERT_COOLDOWN_SECONDS = 300
ALERT_LIST_LIMIT = 50
ALERT_HISTORY_LIMIT = 20
ALERT_MAX_PRIORITY = 10

# Limits - Realtime Data
REALTIME_TRADES_LIMIT = 20
REALTIME_LIMIT_MIN = 1
REALTIME_LIMIT_MAX = 100

# Limits - Fundamentals
FUNDAMENTALS_LIMIT_MIN = 1
FUNDAMENTALS_LIMIT_MAX = 20
BATCH_FETCH_LIMIT_MIN = 1
BATCH_FETCH_LIMIT_MAX = 500

# Limits - Market Data
MARKET_MOVERS_LIMIT = 20

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60
CACHE_TTL_MEDIUM = 300
CACHE_TTL_LONG = 3600

# Rate Limits
RATE_LIMIT_ANON = "100/hour"
RATE_LIMIT_AUTH = "1000/hour"

# Rate Limit Groups (requests per hour)
RATE_LIMIT_READ = "500/hour"
RATE_LIMIT_WRITE = "100/hour"
RATE_LIMIT_ANALYTICS = "200/hour"
RATE_LIMIT_REALTIME = "1000/hour"
RATE_LIMIT_DATA_INTENSIVE = "50/hour"

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60
CACHE_TTL_MEDIUM = 300
CACHE_TTL_LONG = 3600
CACHE_TTL_PORTFOLIO = 300  # 5 minutes for portfolio data
CACHE_TTL_ANALYTICS = 900  # 15 minutes for analytics

# API Response Codes
ERROR_NOT_FOUND = "not_found"
ERROR_VALIDATION = "validation_error"
ERROR_DATABASE = "database_error"
ERROR_UNAUTHORIZED = "unauthorized"
ERROR_FORBIDDEN = "forbidden"
