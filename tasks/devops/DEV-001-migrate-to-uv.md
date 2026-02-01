# Task: Migrate to uv for Faster Python Package Management

**Priority:** MEDIUM-HIGH
**Status:** OPEN
**Assigned To:** DevOps Team (Karen)
**Created:** February 1, 2026
**Estimated Time:** 3-4 hours

## Overview

Migrate from `pip` to `uv` (by Astral) for Python package management. **uv is 8-10x faster than pip** without caching and **80-115x faster** with warm cache, while also providing automatic virtual environment management.

## Why uv?

### Performance Improvements
- **Installation:** 8-10x faster than pip (without cache)
- **Cached installs:** 80-115x faster than pip
- **Virtual env creation:** 80x faster than `python -m venv`
- **Disk usage:** Minimal with global cache and Copy-on-Write

### Additional Benefits
- **Automatic venv management** - No need to manually create/activate virtual environments
- **Single static binary** - No Python dependency needed
- **Drop-in pip replacement** - Works with existing workflows
- **Built-in caching** - Global module cache across projects
- **Lock file support** - Compatible with requirements.txt and pyproject.toml

## Current State Analysis

### Current Setup (pip-based)

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim-bookworm AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
```

**Current Issues:**
- Slow dependency installation (can take 2-5 minutes)
- Manual venv creation
- No global cache between builds
- Re-downloads packages on every build

### Current Requirements
Located: `apps/backend/requirements.txt` (need to verify location)

## Migration Plan

### Phase 1: Install uv & Test Locally (30 minutes)

1. **Verify uv installation:**
```bash
# Already installed on host machine
uv --version

# Install in Docker image
```

2. **Test with current requirements:**
```bash
cd apps/backend
# Create venv and install dependencies
uv venv
uv pip install -r requirements.txt

# Compare times
time pip install -r requirements.txt
time uv pip install -r requirements.txt
```

### Phase 2: Update Dockerfile (1 hour)

**Option A: Minimal Change (Recommended)**
Replace pip with uv, keep same structure:

```dockerfile
# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim-bookworm AS builder

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libmariadb-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create venv with uv (faster than python -m venv)
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Use uv pip install (much faster)
RUN uv pip install -r requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim-bookworm AS runtime

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY --chown=appuser:appuser . .
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1
```

**Option B: Multi-stage with Cache (Advanced)**

Add global cache mount for even faster rebuilds:

```dockerfile
# Add Docker build cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt
```

### Phase 3: Update docker-compose.yml (30 minutes)

No changes needed - Dockerfile abstraction handles it.

But can add volume for global cache:

```yaml
services:
  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    volumes:
      # Global uv cache (persistent across rebuilds)
      - uv-cache:/root/.cache/uv:rw
      # ... other volumes

volumes:
  uv-cache:
```

### Phase 4: Update Development Workflow (1 hour)

**Before (pip):**
```bash
# Create venv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add new package
pip install django-ninja
pip freeze > requirements.txt
```

**After (uv):**
```bash
# uv creates and manages venv automatically
# Just install (uv creates venv if needed)
uv pip install -r requirements.txt

# Add new package
uv pip install django-ninja
uv pip freeze > requirements.txt

# Or better: use uv sync with pyproject.toml
uv sync
```

### Phase 5: CI/CD Updates (30 minutes)

**Update `.github/workflows/ci.yml`:**

```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Set up Python
  run: uv venv

- name: Install dependencies
  run: |
    uv pip install -r apps/backend/requirements.txt
    # Or use cache
    uv pip install -r apps/backend/requirements.txt --cache-dir /tmp/uv-cache
```

## Performance Expectations

### Build Time Improvements

**Current (pip):**
- Fresh build: 2-5 minutes
- Cached build: 30-60 seconds
- Venv creation: 5-10 seconds

**With uv:**
- Fresh build: 20-40 seconds (8-10x faster)
- Cached build: 1-5 seconds (80-115x faster)
- Venv creation: 0.1 seconds (80x faster)

### Development Workflow Improvements

**Adding a new package:**
- pip: 5-10 seconds
- uv: 0.5-2 seconds (5-10x faster)

**Recreating environment:**
- pip: 30-60 seconds
- uv: 1-3 seconds (30-50x faster)

## Migration Steps

### Step 1: Pre-Migration Testing (30 min)
```bash
cd apps/backend

# Backup current requirements
cp requirements.txt requirements.txt.backup

# Test uv with current requirements
uv venv .venv.uv
source .venv.uv/bin/activate
uv pip install -r requirements.txt

# Verify everything works
python manage.py check
python manage.py migrate --check
```

### Step 2: Update Dockerfile (30 min)
1. Update `apps/backend/Dockerfile` with uv installation
2. Replace `pip install` with `uv pip install`
3. Replace `python -m venv` with `uv venv`
4. Test build: `docker-compose build backend`

### Step 3: Update Development Documentation (30 min)
Update README and setup instructions to use uv:

```bash
# Quick start
git clone <repo>
cd apps/backend
uv pip install -r requirements.txt
python manage.py runserver
```

### Step 4: Update CI/CD (30 min)
Update GitHub Actions workflows to use uv.

### Step 5: Remove pip Artifacts (15 min)
```bash
# Remove old venv
rm -rf venv .venv

# Update .gitignore to exclude .venv
echo ".venv/" >> .gitignore
```

## Potential Issues & Solutions

### Issue 1: Some packages don't work with uv
**Solution:** uv has high pip compatibility (95%+). If a package fails:
- Report to uv: https://github.com/astral-sh/uv/issues
- Fallback: Use pip for that specific package

### Issue 2: Different dependency resolution
**Solution:** uv uses same PubGrub solver as pip-tools. Should be identical.

### Issue 3: Docker layer caching
**Solution:** Use Docker buildkit cache mounts:
```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt
```

## Rollback Plan

If migration fails:
1. Keep requirements.txt.backup
2. Revert Dockerfile changes
3. Continue using pip

**But uv is designed as a drop-in replacement, so rollback should not be needed.**

## Success Criteria

✅ Docker build time reduced by 70%+
✅ Local environment setup faster
✅ All tests pass with uv
✅ No breaking changes to functionality
✅ CI/CD builds faster

## Files to Modify

1. `/apps/backend/Dockerfile` - Main migration
2. `/docker-compose.yml` - Optional cache volume
3. `/.github/workflows/*.yml` - CI updates
4. `/README.md` - Documentation updates

## Additional Benefits

### Better Developer Experience
```bash
# No need to activate venv explicitly
uv run python manage.py runserver
uv run python manage.py migrate
uv run pytest
```

### Script Compatibility
```bash
# Scripts work without modification
uv pip install -r requirements.txt
uv pip freeze
uv pip list
```

## Comparison Table

| Feature | pip | uv |
|---------|-----|-----|
| Speed (cold) | 1x (baseline) | 8-10x faster |
| Speed (warm) | 1x (baseline) | 80-115x faster |
| Venv creation | Slow | 80x faster |
| Language | Python | Rust |
| Cache | Per-project | Global cache |
| Dependencies | Needs Python | Standalone binary |
| Resolution | Standard | PubGrub (same as pip-tools) |

## References

- uv Documentation: https://docs.astral.sh/uv/
- uv GitHub: https://github.com/astral-sh/uv
- Blog post: https://astral.sh/blog/uv
- Docker integration: https://docs.astral.sh/uv/guides/integration/docker/
- Performance benchmarks: https://github.com/astral-sh/uv/blob/main/BENCHMARKS.md

## Next Steps

1. **Immediate (Today):**
   - Test uv locally with current requirements
   - Measure performance improvement
   - Verify all packages install correctly

2. **Short-term (This Week):**
   - Update Dockerfile
   - Test Docker builds
   - Update documentation

3. **Ongoing:**
   - Monitor for any issues
   - Update team on new workflow
   - Consider migrating to `uv sync` with lock files

## Related Tasks

- **D-014:** Security Scanning Integration (already complete)
- **TEST-002:** Backend Testing Infrastructure Setup
- **D-009:** CI/CD Pipeline Enhancement (already complete)

---

**Recommendation:** MIGRATE - Significant performance improvements with minimal risk
