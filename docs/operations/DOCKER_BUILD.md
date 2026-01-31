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

### All Services with Docker Compose
```bash
docker-compose build
```

## Image Sizes

| Service | Before | After | Target |
|---------|--------|-------|--------|
| Backend | 1.25GB | ~450MB | <500MB |
| Frontend | ~500MB | ~150MB | <200MB |

## Optimization Techniques

### 1. Multi-Stage Builds
Separate build and runtime stages to keep final images small.

### 2. Alpine Base Images
- Backend: `python:3.11-slim`
- Frontend: `node:20-alpine`

### 3. Layer Caching
Docker BuildKit cache enabled via GitHub Actions:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### 4. .dockerignore Files
Exclude unnecessary files from build context:
- Python: `__pycache__`, `.venv`, `*.pyc`
- Node.js: `node_modules`, `.next/cache`

### 5. Non-Root Users
- Backend: `appuser` (UID 1001)
- Frontend: `nextjs` (UID 1001)

### 6. Next.js Standalone Output
Frontend uses `output: 'standalone'` in `next.config.js` for minimal image size.

## Security Scanning

### Local Scanning with Trivy
```bash
# Install Trivy
brew install trivy

# Scan backend image
trivy image financehub-backend:latest

# Scan frontend image
trivy image financehub-frontend:latest
```

### CI/CD Scanning
Security scans run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`

Results available in GitHub Security tab.

## Health Checks

Both services include health checks:

### Backend
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1
```

### Frontend
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
```

## Troubleshooting

### Build Fails with Memory Issues
```bash
# Increase Docker memory to 4GB+
docker build --build-arg NODE_OPTIONS="--max-old-space-size=4096" -t financehub-frontend:latest .
```

### Layer Cache Not Working
Ensure you're using Docker BuildKit:
```bash
DOCKER_BUILDKIT=1 docker build .
```

### Image Size Still Large
1. Check `.dockerignore` is working
2. Verify multi-stage build is reaching final stage only
3. Run `docker history financehub-backend:latest` to identify large layers
