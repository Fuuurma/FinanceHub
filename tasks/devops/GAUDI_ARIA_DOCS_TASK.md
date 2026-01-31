# Gaudi: Create ARIA Task for Documentation Fix

**From:** DevOps Monitor  
**Date:** February 1, 2026  
**Priority:** Medium

---

## Issue

Project was migrated from MySQL to PostgreSQL, but documentation still says MySQL.

### Files with Wrong Info

| File | Issue |
|------|-------|
| `.opencode/ROADMAP.md` | Says "MySQL 8.0" |
| `docs/agents/AGENTS.md` | Says "PostgreSQL" (correct) |
| `tasks/architect/DOC_REVIEW_TODO.md` | Notes this issue |

### Actual Tech Stack (PostgreSQL)
- Database: **PostgreSQL 15** (in Docker)
- No MySQL installed locally needed
- All coders use Docker PostgreSQL

---

## Task for ARIA

**Create task:** Update all documentation to reflect PostgreSQL

**Steps:**
1. Update `.opencode/ROADMAP.md` - Change MySQL → PostgreSQL
2. Update `docs/agents/AGENTS.md` - Verify PostgreSQL mention
3. Update any other docs referencing MySQL
4. Remove MySQL migration scripts in `tasks/coders/`

**Effort:** 1-2 hours

---

## Coders Having Docker Issues

**Problem:** Docker containers down after PC restart

**Solution:**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Should show:
# postgres     Up
# redis        Up
# backend      Up
# frontend     Up
# worker       Up

# If postgres is down:
docker-compose restart postgres
docker-compose logs postgres
```

**No need for local PostgreSQL** - it's all in Docker.

---

**Taking accountability. Please create ARIA task.**
