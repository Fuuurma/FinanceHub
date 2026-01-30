# FinanceHub Team Onboarding Guide

**Author:** KAREN (DevOps Engineer)
**Date:** 2026-01-30
**Purpose:** Get new developers up and running quickly

---

## 🎯 Welcome to FinanceHub!

This guide will help you set up your development environment and understand how to work with the FinanceHub codebase.

---

## 📋 Prerequisites

Before you start, make sure you have:

**Required:**
- macOS or Linux (Windows support via WSL)
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL client (optional, for direct DB access)

**Recommended:**
- VS Code or PyCharm
- Postman or Insomnia (for API testing)
- pgAdmin or DBeaver (for database GUI)

---

## 🚀 Quick Start (30 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/Fuuurma/FinanceHub-Backend.git
cd FinanceHub-Backend
```

### 2. Install Dependencies

**Backend:**
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-testing.txt
```

**Frontend:**
```bash
cd ../Frontend
npm install
npm install --save-dev  # For testing dependencies
```

### 3. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://financehub:password@localhost:5432/financehub
POSTGRES_DB=financehub
POSTGRES_USER=financehub
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (get from team lead)
ALPHA_VANTAGE_API_KEY=your-key-here
FINNHUB_API_KEY=your-key-here
```

### 4. Start Development Environment

**Option A: Using Makefile (Recommended)**
```bash
cd ..
make dev  # Starts all services
```

**Option B: Using Docker Compose**
```bash
make docker-up  # Or: docker-compose up -d
```

**Option C: Manual**
```bash
# Terminal 1: Backend
cd Backend
source venv/bin/activate
python manage.py runserver

# Terminal 2: Frontend
cd Frontend
npm run dev
```

### 5. Initialize Database

```bash
cd Backend
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed sample data (optional)
python manage.py seed_data
```

### 6. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/api/v1/health/

# Frontend
open http://localhost:3000

# Run tests
make test
```

---

## 📚 Project Structure

```
FinanceHub-Backend/
├── Backend/                    # Django backend
│   ├── src/
│   │   ├── accounts/           # User accounts
│   ├── portfolio/              # Portfolio management
│   ├── market/                 # Market data
│   └── analytics/              # Analytics
│   ├── tests/                  # Backend tests
│   ├── manage.py               # Django management
│   └── requirements.txt        # Python dependencies
│
├── Frontend/                   # Next.js frontend
│   ├── app/                    # Next.js 14 app directory
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── charts/             # Chart components
│   │   └── forms/              # Form components
│   ├── lib/                    # Utilities
│   ├── tests/                  # Frontend tests
│   └── package.json            # Node dependencies
│
├── scripts/                    # Automation scripts
│   ├── backup.sh               # Database backup
│   ├── restore.sh              # Database restore
│   ├── migrate.sh              # Migration helper
│   └── health-check.sh         # Health checks
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md           # CI/CD guide
│   ├── MONITORING.md           # Monitoring guide
│   └── INFRASTRUCTURE.md       # Architecture docs
│
├── runbooks/                   # Operational procedures
│   ├── API_PERFORMANCE_ISSUES.md
│   └── DEPLOYMENT_FAILURE.md
│
├── Makefile                    # Development commands
├── docker-compose.yml          # Local development
└── README.md                   # This file
```

---

## 🛠️ Common Tasks

### Running Tests

```bash
# All tests
make test

# Backend only
cd Backend && pytest

# Frontend only
cd Frontend && npm test

# E2E tests
cd Frontend && npx playwright test

# With coverage
make test-coverage
```

### Code Quality

```bash
# Lint all code
make lint

# Format code
make format

# Type check
make typecheck

# Security scan
make security-scan
```

### Database Management

```bash
# Create migration
make migrate-create NAME="add_user_field"

# Apply migrations
make migrate

# Rollback migration
make migrate-rollback

# Check migration status
make migrate-status

# Access database shell
make db-shell
```

### Docker Development

```bash
# Start all services
make docker-up

# View logs
make logs

# Stop services
make docker-down

# Rebuild containers
make docker-build
```

---

## 🎨 Development Workflow

### Feature Development

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
```bash
# Edit files
# Run tests frequently
make test

# Check code quality
make lint
```

3. **Commit Changes**
```bash
git add .
git commit -m "feat: add your feature description"
```

4. **Push & Create PR**
```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

### Commit Message Conventions

Follow Conventional Commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: maintenance tasks
perf: performance improvements
```

### Code Review Process

1. Open pull request
2. Ensure CI checks pass
3. Request review from team
4. Address feedback
5. Merge after approval

---

## 🐛 Debugging Tips

### Backend Issues

**Check Logs:**
```bash
make logs SERVICE=backend
# Or: docker-compose logs -f backend
```

**Django Shell:**
```bash
cd Backend
python manage.py shell

# Debug database
from portfolio.models import Portfolio
print(Portfolio.objects.all())
```

**Database Queries:**
```bash
# View slow queries
make db-slow-queries

# Check connection count
make db-connections
```

### Frontend Issues

**Browser DevTools:**
- Open DevTools (F12)
- Check Console for errors
- Network tab for API calls
- React DevTools for component state

**Clear Cache:**
```bash
cd Frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Common Issues

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

**Database Connection Error:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart if needed
make docker-restart SERVICE=db
```

**Migration Conflicts:**
```bash
# Fake migration to skip
./scripts/migrate.sh fake

# Or rollback
./scripts/migrate.sh rollback <app> zero
```

---

## 📖 Learning Resources

### Internal Documentation

- **DEVOPS_README.md** - DevOps overview
- **docs/DEPLOYMENT.md** - CI/CD guide
- **docs/MONITORING.md** - Monitoring setup
- **docs/INFRASTRUCTURE.md** - System architecture
- **tasks.md** - Development task list

### External Resources

**Backend (Django):**
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Best Practices](https://docs.python-guide.org/)

**Frontend (Next.js):**
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [shadcn/ui Components](https://ui.shadcn.com/)

**Database (PostgreSQL):**
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Prisma ORM](https://www.prisma.io/docs/)

**DevOps:**
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/actions)

---

## 🔐 Security Best Practices

### Never Commit

- API keys or secrets
- Passwords
- `.env` files
- Database backups
- Personal credentials

### Always Use

- Environment variables for secrets
- Pre-commit hooks for code quality
- HTTPS for API calls
- Input validation & sanitization
- Authentication for sensitive endpoints

### Report Security Issues

If you find a security vulnerability:

1. **Don't** create a public issue
2. **Do** email security@financehub.com
3. **Do** include details and reproduction steps
4. Wait for confirmation before disclosing

---

## 🤝 Getting Help

### Ask Questions

1. **Check Documentation First**
   - Search existing docs
   - Check runbooks for common issues

2. **Ask in Team Channels**
   - Slack: #financehub-dev
   - Create GitHub discussion

3. **Create Issue** (for bugs/features)
   - Use issue templates
   - Provide details and reproduction steps

### Office Hours

- **Daily Standup:** 9:30 AM EST
- **Tech Demos:** Fridays 3:00 PM EST
- **Planning:** Mondays 10:00 AM EST

---

## ✅ Onboarding Checklist

### Week 1

- [ ] Complete Quick Start
- [ ] Set up development environment
- [ ] Read project documentation
- [ ] Run all tests successfully
- [ ] Make first small commit

### Week 2

- [ ] Fix a bug from issues
- [ ] Review 1-2 pull requests
- [ ] Attend team standups
- [ ] Set up pre-commit hooks

### Month 1

- [ ] Complete a feature end-to-end
- [ ] Deploy to staging (with supervision)
- [ ] Write/update documentation
- [ ] Present work to team

---

## 🎉 You're Ready!

You've completed the onboarding guide. Welcome to the FinanceHub team!

### Next Steps

1. **Join team channels** - Slack, GitHub team
2. **Introduce yourself** - Team meeting
3. **Pick a task** - Check `tasks.md` or GitHub issues
4. **Start contributing** - Make your first PR!

### Keep Learning

- Read more documentation
- Ask questions
- Experiment in dev environment
- Attend team demos

---

**Author:** KAREN (DevOps Engineer)
**Last Updated:** 2026-01-30
**Version:** 1.0

Need help? Ask in #financehub-dev or create an issue!
