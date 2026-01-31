# Linus & Guido: Docker Restart Fix

**From:** DevOps Monitor  
**Date:** February 1, 2026

---

## Quick Fix for Docker/DB Issues

PC restarted → Docker containers down → Run this:

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Option 1: Use the script I created
./scripts/restart-services.sh

# Option 2: Manual
docker-compose up -d
docker-compose ps
```

---

## No Local PostgreSQL Needed!

You do NOT need PostgreSQL installed locally.
The database runs **inside Docker**.

Your local machine only needs:
- Docker Desktop (running)
- Python venv

---

## Script Created

I created: `scripts/restart-services.sh`

Run it to restart all services automatically.

---

**Taking accountability. Docker needs restart after PC reboot.**
