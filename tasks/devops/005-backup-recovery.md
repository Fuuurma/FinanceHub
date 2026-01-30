---
title: "Backup, Disaster Recovery & Performance"
status: pending
priority: p2
estimate: "2 days"
created: "2026-01-30"
assigned_to: gaudi
depends_on:
  - d-001
  - d-002
---

## Summary

Implement database backup strategy, connection pooling, and performance optimizations. Based on INFRASTRUCTURE_ANALYSIS.md findings.

## Issues to Fix

### P2 - Medium Priority

#### 1. Add Database Backup Service

**File:** `docker-compose.yml`

**Add backup service:**
```yaml
services:
  backup:
    image: postgres:15-alpine
    container_name: financehub-backup
    volumes:
      - postgres_data:/source
      - ${BACKUP_DIR:-./backups}:/destination
    environment:
      - PGHOST=postgres
      - PGUSER=financehub
      - PGPASSWORD=${POSTGRES_PASSWORD}
      - PGDATABASE=finance_hub
    command: >
      sh -c "
      while true; do
        pg_dump -h postgres -U financehub -d finance_hub \
          -F c -Z 9 \
          -f /destination/backup_$(date +%Y%m%d_%H%M%S).dump
        # Keep last 30 days
        find /destination -name '*.dump' -mtime +30 -delete
        sleep 86400  # Daily backup
      done
      "
    profiles:
      - with-backup
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
    external: true
```

**Add backup script for local development:**
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.dump"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"

docker-compose exec -T postgres pg_dump \
  -U financehub \
  -d finance_hub \
  -F c \
  -Z 9 \
  > "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"
echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Verify backup
docker-compose exec -T postgres pg_restore \
  --list "$BACKUP_FILE" > /dev/null

if [ $? -eq 0 ]; then
  echo "Backup verification: OK"
else
  echo "Backup verification: FAILED"
  rm "$BACKUP_FILE"
  exit 1
fi
```

**Add restore script:**
```bash
#!/bin/bash
# scripts/restore.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file.dump>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "File not found: $BACKUP_FILE"
  exit 1
fi

echo "Stopping services..."
docker-compose down

echo "Dropping database..."
docker-compose exec -T postgres psql -U financehub -d postgres -c "DROP DATABASE finance_hub;"
docker-compose exec -T postgres psql -U financehub -d postgres -c "CREATE DATABASE finance_hub;"

echo "Restoring backup..."
docker-compose exec -T postgres pg_restore -C -d finance_hub < "$BACKUP_FILE"

echo "Restarting services..."
docker-compose up -d

echo "Restore complete!"
```

#### 2. Configure Database Connection Pooling

**File:** `apps/backend/src/core/settings/database.py`

**Add connection pooling:**
```python
# settings/database.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'finance_hub'),
        'USER': os.environ.get('DATABASE_USER', 'financehub'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST', 'postgres'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
        
        # Connection pooling
        'CONN_MAX_AGE': 60,  # Keep connections alive for 60 seconds
        'OPTIONS': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 5,
            'keepalives_count': 5,
        },
    }
}

# For production with pgbouncer:
# Use django-dbconnection-pool or configure pgbouncer sidecar
```

**For production, add pgbouncer:**
```yaml
# docker-compose.override.yml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer:latest-alpine
    container_name: financehub-pgbouncer
    environment:
      - DATABASES=finance_hub=host=postgres port=5432 dbname=finance_hub
      - PGBOUNCER_AUTH_TYPE=md5
      - PGBOUNCER_AUTH_FILE=/etc/pgbouncer/userlist.txt
      - PGBOUNCER_POOL_MODE=transaction
      - PGBOUNCER_MAX_CLIENT_CONN=100
      - PGBOUNCER_DEFAULT_POOL_SIZE=20
      - PGBOUNCER_MIN_POOL_SIZE=5
      - PGBOUNCER_RESERVE_POOL_SIZE=5
    volumes:
      - ./pgbouncer/userlist.txt:/etc/pgbouncer/userlist.txt:ro
    ports:
      - "6432:6432"
    depends_on:
      postgres:
        condition: service_healthy
    profiles:
      - with-pgbouncer
```

#### 3. Configure Redis Caching

**File:** `apps/backend/src/core/settings/cache.py`

**Add Redis caching:**
```python
# settings/cache.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('CACHE_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'financehub',
        'TIMEOUT': 300,  # Default 5 minutes
    }
}

# For session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### 4. Add Django Cache Invalidation

**File:** `apps/backend/src/utils/services/cache_manager.py`

**Create cache manager:**
```python
# utils/services/cache_manager.py
from django.core.cache import cache
from django.conf import settings
from typing import Optional
import hashlib
import json

class CacheManager:
    """Centralized cache management for FinanceHub"""
    
    @staticmethod
    def make_key(prefix: str, *args) -> str:
        """Create cache key with prefix"""
        key_data = ':'.join(str(arg) for arg in args)
        return f"{settings.CACHE_KEY_PREFIX or 'financehub'}:{prefix}:{key_data}"
    
    @staticmethod
    def get_price(symbol: str, timeframe: str = '1d') -> Optional[dict]:
        """Get cached price data"""
        key = CacheManager.make_key('price', symbol, timeframe)
        return cache.get(key)
    
    @staticmethod
    def set_price(symbol: str, data: dict, timeout: int = 300) -> None:
        """Cache price data"""
        key = CacheManager.make_key('price', symbol)
        cache.set(key, data, timeout)
    
    @staticmethod
    def invalidate_price(symbol: str) -> None:
        """Invalidate price cache for symbol"""
        # Invalidate all timeframes
        for tf in ['1d', '1h', '15m', '5m', '1m']:
            key = CacheManager.make_key('price', symbol, tf)
            cache.delete(key)
    
    @staticmethod
    def invalidate_portfolio(user_id: str) -> None:
        """Invalidate portfolio cache for user"""
        pattern = f"{settings.CACHE_KEY_PREFIX}:portfolio:{user_id}:*"
        # Use cache.delete_many with pattern matching
        keys = cache.keys(pattern)
        if keys:
            cache.delete_many(keys)
    
    @staticmethod
    def get_market_summary() -> Optional[dict]:
        """Get cached market summary"""
        key = CacheManager.make_key('market', 'summary')
        return cache.get(key)
    
    @staticmethod
    def set_market_summary(data: dict, timeout: int = 60) -> None:
        """Cache market summary (short TTL for real-time feel)"""
        key = CacheManager.make_key('market', 'summary')
        cache.set(key, data, timeout)

# Singleton instance
cache_manager = CacheManager()
```

#### 5. Optimize Docker Build with Multi-stage Builds

**File:** `apps/backend/Dockerfile`

**Optimize backend build:**
```dockerfile
# apps/backend/Dockerfile

# Stage 1: Dependencies
FROM python:3.11-slim as dependencies

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Application
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY manage.py .
COPY apps/ apps/
COPY utils/ utils/

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings.production

# Non-root user for security
RUN useradd --create-home --shell /bin/bash financehub
RUN chown -R financehub:financehub /app
USER financehub

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**Frontend Dockerfile optimization:**
```dockerfile
# apps/frontend/Dockerfile

# Build stage
FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/next.config.js ./

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "start"]
```

## Files to Modify

1. `docker-compose.yml` - Add backup service, health checks (from D-004)
2. `apps/backend/src/core/settings/database.py` - Add connection pooling
3. `apps/backend/src/core/settings/cache.py` - Add Redis caching
4. `apps/backend/Dockerfile` - Multi-stage build
5. `apps/frontend/Dockerfile` - Multi-stage build

## Files to Create

1. `scripts/backup.sh` - Backup script
2. `scripts/restore.sh` - Restore script
3. `apps/backend/src/utils/services/cache_manager.py` - Cache manager
4. `pgbouncer/userlist.txt` - For connection pooling (production)
5. `.dockerignore` - Already created in D-001

## Testing

```bash
# Test backup
chmod +x scripts/backup.sh
./scripts/backup.sh
ls -la backups/

# Test restore
# ./scripts/restore.sh backups/backup_20260130_120000.dump

# Test connection pooling
cd apps/backend
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute('SELECT 1')
...     print(cursor.fetchone())

# Verify cache works
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test_key', 'test_value', 60)
>>> cache.get('test_key')
'test_value'

# Test Docker build size
docker images | grep financehub
```

## Success Criteria

1. ✅ Automated daily backups
2. ✅ Backup retention (30 days)
3. ✅ Restore procedure documented
4. ✅ Connection pooling configured
5. ✅ Redis caching configured
6. ✅ Docker images optimized (multi-stage builds)
7. ✅ Build context reduced (.dockerignore)

## Related Issues

- INFRASTRUCTURE_ANALYSIS.md Issues 3, 4, 8
- BACKEND_IMPROVEMENTS.md (performance issues)
