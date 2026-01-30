# FinanceHub - Complete DevOps Setup

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Make (optional, for convenience)

### Installation

```bash
# Clone repository
git clone https://github.com/Fuuurma/FinanceHub-Backend.git
cd FinanceHub-Backend

# Install dependencies
make install

# Start development environment
make dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs

---

## Development Workflow

### Using Make (Recommended)

```bash
# Start all services
make dev

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Run security scans
make security-scan

# Build Docker images
make build

# Deploy to staging
make deploy-staging
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         User Layer                      │
│  Web Browser │ Mobile App               │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│         Load Balancer                   │
│  Nginx / ALB (AWS)                      │
└─────┬───────────────────────┬───────────┘
      │                       │
┌─────▼──────────┐    ┌──────▼──────────┐
│   Frontend      │    │   Backend       │
│   (Next.js)     │    │   (Django)      │
│   Port: 3000    │    │   Port: 8000    │
└─────┬───────────┘    └──────┬──────────┘
      │                       │
      └───────────┬───────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
┌─────▼──────────┐    ┌──────▼──────────┐
│  PostgreSQL     │    │    Redis        │
│  Port: 5432     │    │    Port: 6379   │
└─────────────────┘    └─────────────────┘
```

---

## Testing

### Backend Tests
```bash
# Run all tests
make test-backend

# Run specific test
cd Backend/src
pytest tests/test_analytics.py -v

# With coverage
pytest --cov=. --cov-report=html

# Run marked tests
pytest -m unit -v
pytest -m integration -v
```

### Frontend Tests
```bash
# Run unit tests
make test-frontend

# Run E2E tests
make test-e2e

# Watch mode
make test-watch
```

### CI/CD Pipeline
Tests run automatically on:
- Pull requests
- Pushes to main
- Daily schedule (security scans)

---

## Deployment

### Environments
- **Staging**: https://staging.financehub.com
- **Production**: https://financehub.com

### Deployment Process
```bash
# Deploy to staging
make deploy-staging

# Verify deployment
./scripts/health-check.sh staging
./scripts/smoke-test.sh staging

# Deploy to production
make deploy-production
```

### Rollback
```bash
# Rollback production
./scripts/rollback.sh production
```

---

## Monitoring

### Health Checks
```bash
# Check all services
make health

# Check specific service
curl http://localhost:8000/api/health
curl http://localhost:3000/health
```

### Logs
```bash
# All logs
make logs-tail

# Backend logs
make logs-backend

# Frontend logs
make logs-frontend
```

### CloudWatch Metrics
- CPU/Memory utilization
- Request count and latency
- Error rates
- Database performance
- Cache hit rates

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check database is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### Container Keeps Restarting
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# - Check environment variables
# - Verify database migrations
# - Check for missing dependencies
```

#### Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

---

## Documentation

### User Guides
- [TESTING_README.md](./TESTING_README.md) - Testing guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - CI/CD documentation
- [MONITORING.md](./MONITORING.md) - Monitoring guide
- [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) - System architecture
- [SECURITY_SCANNING.md](./SECURITY_SCANNING.md) - Security procedures

### Runbooks
- [API_PERFORMANCE_ISSUES.md](./runbooks/API_PERFORMANCE_ISSUES.md)
- [DEPLOYMENT_FAILURE.md](./runbooks/DEPLOYMENT_FAILURE.md)
- [HIGH_CPU_MEMORY.md](./runbooks/HIGH_CPU_MEMORY.md) - TBD
- [DATABASE_ISSUES.md](./runbooks/DATABASE_ISSUES.md) - TBD
- [CACHE_ISSUES.md](./runbooks/CACHE_ISSUES.md) - TBD

---

## Environment Variables

### Required for Development
```bash
# Copy example env file
cp .env.example .env

# Edit with your values
# Minimum required:
# - DJANGO_SECRET_KEY
# - DATABASE_URL
# - REDIS_URL
```

### Required for Production
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

# Database (Production)
DATABASE_URL (RDS)

# Secrets (via AWS Secrets Manager)
DJANGO_SECRET_KEY
API_KEYS

# Notification
SLACK_WEBHOOK
```

---

## Quick Reference

### Essential Commands
```bash
make dev              # Start development
make test             # Run all tests
make lint             # Lint code
make build            # Build images
make deploy-staging   # Deploy to staging
make health           # Check health
make logs-tail        # View logs
```

### Docker Commands
```bash
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f        # View logs
docker-compose exec backend bash  # Shell access
docker-compose restart        # Restart services
```

### Database Commands
```bash
make db-migrate       # Run migrations
make db-makemigrations  # Create migrations
make db-shell         # Database shell
make db-reset         # Reset database
```

---

## Support

### Getting Help
- Check runbooks in `./runbooks/`
- Review documentation in `./docs/`
- Check GitHub issues
- Contact DevOps team

### Reporting Issues
1. Check existing issues
2. Create bug report with:
   - Symptoms
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs/screenshots

---

## Development Best Practices

### Code Quality
- Write tests for new features
- Run linters before committing
- Follow code style guidelines
- Document complex logic

### Git Workflow
- Create feature branches
- Write descriptive commit messages
- Create pull requests for review
- Update documentation

### Testing
- Test locally before pushing
- Ensure CI passes
- Add tests for bugs fixed
- Update test data as needed

---

## Contributing

### Setup Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### Before Committing
```bash
make lint
make test
make security-scan
```

### Commit Message Format
```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
```

---

**Last Updated**: 2026-01-30
**Version**: 1.0.0
**Maintainer**: DevOps Team
