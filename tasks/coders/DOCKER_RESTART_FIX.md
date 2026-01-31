# Coders: Docker Restart Fix

**From:** DevOps Monitor  
**Date:** February 1, 2026

---

## Problem

PC restarted, Docker containers are down.

---

## Solution

### 1. Start Docker Desktop
Make sure Docker Desktop is running (check tray icon)

### 2. Start all services
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Start all containers
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Expected Output
```
NAME                 STATUS
financehub-postgres   Up
financehub-redis      Up
financehub-backend    Up
financehub-frontend   Up
financehub-worker     Up
```

### 4. If PostgreSQL won't start
```bash
# Check logs
docker-compose logs postgres

# Restart postgres specifically
docker-compose restart postgres

# Wait 10 seconds, then check
docker-compose ps postgres
```

### 5. If Redis won't start
```bash
docker-compose restart redis
```

---

## No Local PostgreSQL Needed!

**You do NOT need PostgreSQL installed locally.**

All databases run inside Docker containers:
- PostgreSQL: `postgres:15-alpine` (in Docker)
- Redis: `redis:7-alpine` (in Docker)

Your local machine only needs:
- Docker Desktop
- Python (for venv)

---

## Quick Test

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# 1. Check Docker
docker --version
# Expected: Docker version 24+ 

# 2. Start containers
docker-compose up -d

# 3. Wait 30 seconds
sleep 30

# 4. Check PostgreSQL
docker-compose exec postgres pg_isready -U financehub

# Expected: "postgres:5432 - accepting connections"

# 5. Test your venv
cd apps/backend
source venv/bin/activate
python -c "import dramatiq; print('Dramatiq OK')"
```

---

## Still Having Issues?

1. **Docker Desktop not running** → Start it from Applications
2. **Port conflict** → `docker-compose down` then `up -d`
3. **Permission error** → Run terminal as Administrator

Let me know what error you see!

---

**Taking accountability. Docker containers need restart after PC reboot.**
