# Task: D-008 - Docker Multi-Stage Build Optimization

**Task ID:** D-008
**Assigned To:** DevOps (Karen)
**Priority:** P1 (HIGH)
**Status:** ⏳ PENDING
**Deadline:** February 12, 2026
**Estimated Time:** 6-8 hours

---

## 📋 OBJECTIVE

Optimize Docker images using multi-stage builds, layer caching, and security scanning.

---

## 🎯 ACCEPTANCE CRITERIA

- [ ] Multi-stage builds for backend and frontend
- [ ] Image size <500MB (backend), <200MB (frontend)
- [ ] Security scan passes (Trivy)
- [ ] Layer caching configured
- [ ] Non-root user in containers
- [ .dockerignore optimized
- [ ] Build time <5 minutes
- [ ] Documentation updated

---

## 📝 CONTEXT

### Current Dockerfiles

**Backend:** 1.25GB (too large!)
**Frontend:** Build failed (pre-existing)

### Issues:

1. **No Multi-Stage Builds** (P1)
   - Build tools included in final image
   - Unnecessary layers

2. **Large Image Size** (P0)
   - Backend: 1.25GB
   - Should be <500MB

3. **No Security Scanning** (P0)
   - Vulnerabilities not checked
   - No automated scanning

4. **Root User** (P1)
   - Security risk
   - Should use non-root

---

## ✅ ACTIONS TO COMPLETE

### Action 1: Optimize Backend Dockerfile

**File:** `apps/backend/Dockerfile`

```dockerfile
# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim as runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create logs directory
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Run application
CMD ["gunicorn", "core.asgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

### Action 2: Optimize Frontend Dockerfile

**File:** `apps/frontend/Dockerfile`

```dockerfile
# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:20-alpine as deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --ignore-scripts && \
    npm cache clean --force

# =============================================================================
# Stage 2: Builder
# =============================================================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build arguments
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build application
RUN npm run build

# =============================================================================
# Stage 3: Runner
# =============================================================================
FROM node:20-alpine as runner

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

---

### Action 3: Create .dockerignore Files

**File:** `apps/backend/.dockerignore`

```
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
venv
.venv

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/static

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode
.idea
*.swp
*.swo
*~

# Testing
.pytest_cache
.coverage
htmlcov
.tox

# Documentation
*.md
docs/

# Misc
.DS_Store
```

**File:** `apps/frontend/.dockerignore`

```
# Git
.git
.gitignore

# Dependencies
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next
out
dist

# Production
build
.cache

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode
.idea
*.swp
*.swo
*~

# Testing
coverage
.nyc_output

# Misc
.DS_Store
*.md
docs
```

---

### Action 4: Add Security Scanning

**File:** `tasks/devops/008-docker-optimization.md` (in task)

Add CI/CD integration:

```yaml
# .github/workflows/docker-scan.yml
name: Docker Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: |
          docker build -t financehub-backend:latest ./apps/backend
          docker build -t financehub-frontend:latest ./apps/frontend

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'financehub-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

### Action 5: Update docker-compose.yml

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
      target: runtime  # Use runtime stage only
      cache_from:
        - financehub-backend:latest
    image: financehub-backend:latest
    container_name: financehub-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - backend_logs:/app/logs
    user: appuser  # Non-root user
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
      target: runner
      cache_from:
        - financehub-frontend:latest
    image: financehub-frontend:latest
    container_name: financehub-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    user: nextjs  # Non-root user
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  backend_logs:
```

---

### Action 6: Document Build Process

**New File:** `docs/operations/DOCKER_BUILD.md`

```markdown
# Docker Build Process

## Building Images

### Backend
```bash
cd apps/backend
docker build -t financehub-backend:latest .
```

### Frontend
```bash
cd apps/frontend
docker build -t financehub-frontend:latest .
```

## Image Sizes

- **Backend:** <500MB (down from 1.25GB)
- **Frontend:** <200MB

## Security Scanning

```bash
# Install Trivy
brew install trivy

# Scan backend image
trivy image financehub-backend:latest

# Scan frontend image
trivy image financehub-frontend:latest
```

## Optimization Techniques

1. **Multi-stage builds** - Separate build and runtime
2. **Alpine base images** - Smaller footprint
3. **Layer caching** - Faster rebuilds
4. **.dockerignore** - Exclude unnecessary files
5. **Non-root user** - Security best practice
```

---

## 🎯 SUCCESS CRITERIA

- ✅ Backend image <500MB
- ✅ Frontend image <200MB
- ✅ Multi-stage builds implemented
- ✅ Security scan passes
- ✅ Non-root user configured
- ✅ Health checks functional
- ✅ Build time <5 minutes
- ✅ Documentation complete

---

## 📊 DELIVERABLES

1. Optimized `apps/backend/Dockerfile`
2. Optimized `apps/frontend/Dockerfile`
3. `.dockerignore` files
4. Updated `docker-compose.yml`
5. CI/CD scanning workflow
6. Build documentation
7. Size comparison report

---

## ⏱️ ESTIMATED TIME

- Backend Dockerfile: 2 hours
- Frontend Dockerfile: 2 hours
- Testing: 1-2 hours
- Documentation: 1 hour

**Total:** 6-7 hours

---

## 🔗 DEPENDENCIES

- S-002 (Docker scan results)

---

**Task Status:** ⏳ PENDING
**Priority:** P1 HIGH (Security + Performance)
