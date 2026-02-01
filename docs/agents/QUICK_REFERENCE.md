# FinanceHub - Agent Quick Reference

**For AI Agents:** Fast lookup for common tasks. Use `grep` or search to find what you need.

---

## 🚨 QUICK START (Read This First)

```bash
# 1. Always start here
cat /Users/sergi/Desktop/Projects/FinanceHub/docs/agents/QUICK_REFERENCE.md

# 2. Read your role-specific prompt
cat /Users/sergi/Desktop/Projects/FinanceHub/docs/agents/*_INITIAL_PROMPT.md

# 3. Check task list
cat /Users/sergi/Desktop/Projects/FinanceHub/tasks/TASK_TRACKER.md
```

---

## 📖 DOCUMENTATION QUICK LINKS

| Need | Location |
|------|----------|
| **Development Guides** | `/Users/sergi/Desktop/Projects/development-guides/` |
| **Backend Patterns** | `development-guides/01-BACKEND-DEVELOPMENT.md` |
| **Frontend Patterns** | `development-guides/02-FRONTEND-DEVELOPMENT.md` |
| **Code Standards** | `development-guides/06-CODE-STANDARDS.md` |
| **Security Rules** | `development-guides/04-SECURITY-BEST-PRACTICES.md` |
| **Database** | `development-guides/03-DATABASE-OPTIMIZATION.md` |
| **Cheatsheets** | `development-guides/cheatsheets/` |
| **API Examples** | `apps/backend/src/core/api/examples/` |

---

## 🔍 FIND FILES FAST

### Search patterns for common needs:

| Need | Command |
|------|---------|
| Find component | `find . -name "*Name*" -type f` |
| Find API endpoint | `grep -r "router" apps/backend/src/api/` |
| Find type definition | `grep -r "interface\|type" apps/frontend/src/lib/types/` |
| Find test file | `find . -name "*test*" -o -name "*spec*"` |
| Find styles | `grep -r "className" apps/frontend/src/` |
| Find API calls | `grep -r "axios\|fetch" apps/frontend/src/` |

---

## 🎯 COMMON WORKFLOWS

### Backend Task
```bash
# 1. Read backend guide
cat /Users/sergi/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md

# 2. Find existing endpoint pattern
find . -path "*/api/*" -name "*.py" | head -5

# 3. Read similar endpoint
cat apps/backend/src/api/assets.py

# 4. Check models
find . -path "*/models*" -name "*.py" | grep -i asset
```

### Frontend Task
```bash
# 1. Read frontend guide
cat /Users/sergi/Desktop/Projects/development-guides/02-FRONTEND-DEVELOPMENT.md

# 2. Find similar component
find . -path "*/components/*" -name "*.tsx" | grep -i chart

# 3. Read component
cat apps/frontend/src/components/charts/RealTimeChart.tsx

# 4. Check types
find . -path "*/types*" -name "*.ts" | xargs grep -l "Asset\|Price"
```

### Security Task
```bash
# 1. Read security rules
cat /Users/sergi/Desktop/Projects/development-guides/04-SECURITY-BEST-PRACTICES.md

# 2. Check FinanceHub security docs
find docs/security -name "*.md"
```

---

## 📁 KEY DIRECTORIES

```
FinanceHub/
├── apps/backend/src/
│   ├── api/              # API endpoints (Django Ninja)
│   ├── assets/           # Asset models
│   ├── core/             # Settings, config
│   ├── data/             # Data providers
│   ├── investments/      # Portfolio logic
│   ├── trading/          # Trading engine
│   └── users/            # Auth
│
├── apps/frontend/src/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   │   ├── alerts/
│   │   ├── charts/
│   │   ├── dashboard/
│   │   ├── layout/
│   │   ├── paper-trading/
│   │   ├── risk/
│   │   ├── screener/
│   │   └── ui/           # shadcn/ui
│   ├── contexts/         # React contexts
│   ├── hooks/            # Custom hooks
│   ├── lib/              # API clients, utils
│   └── stores/           # Zustand stores
│
├── docs/
│   ├── agents/           # Agent prompts & guides
│   ├── development/      # Project-specific docs
│   ├── security/         # Security assessments
│   └── roles/            # Role definitions
│
└── tasks/
    └── TASK_TRACKER.md   # Task assignments
```

---

## 🛠️ DEVELOPMENT GUIDES BY TOPIC

| Topic | File |
|-------|------|
| Django Ninja API | `development-guides/01-BACKEND-DEVELOPMENT.md` |
| Next.js App Router | `development-guides/02-FRONTEND-DEVELOPMENT.md` |
| TypeScript | `development-guides/06-CODE-STANDARDS.md` |
| Security | `development-guides/04-SECURITY-BEST-PRACTICES.md` |
| Database | `development-guides/03-DATABASE-OPTIMIZATION.md` |
| Deployment | `development-guides/05-DEPLOYMENT-GUIDE.md` |
| Django Ninja Cheatsheet | `development-guides/cheatsheets/DJANGO-NINJA-CHEATSHEET.md` |
| Next.js Cheatsheet | `development-guides/cheatsheets/NEXTJS-14-CHEATSHEET.md` |
| TypeScript Cheatsheet | `development-guides/cheatsheets/TYPESCRIPT-CHEATSHEET.md` |

---

## 📋 ROLE-SPECIFIC QUICK LINKS

| Role | Initial Prompt | Role Guide |
|------|----------------|------------|
| **GAUDÍ** (Lead) | GAUDI_INITIAL_PROMPT.md | ROLE_GAUDI.md |
| **SCRIBE** (Docs) | SCRIBE_INITIAL_PROMPT.md | - |
| **ARIA** (Frontend) | ARIA_INITIAL_PROMPT.md | - |
| **CHARO** (Security) | CHARO_INITIAL_PROMPT.md | ROLE_CHARO.md |
| **KAREN** (DevOps) | KAREN_INITIAL_PROMPT.md | ROLE_KAREN.md |
| **CODERS** (General) | CODERS_INITIAL_PROMPT.md | ROLE_CODERS.md |
| **MIES** (Design) | MIES_INITIAL_PROMPT.md | ROLE_MIES.md |
| **GRACE** (Testing) | GRACE_INITIAL_PROMPT.md | ROLE_GRACE.md |
| **HADI** (Backend) | HADI_INITIAL_PROMPT.md | ROLE_HADI.md |

---

## ⚡ COMMON COMMANDS

### Backend
```bash
cd apps/backend/src

# Run server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start background workers
dramatiq -A src.scheduler_tasks worker -l info

# Start WebSocket streams
python manage.py start_realtime_streams
```

### Frontend
```bash
cd apps/frontend/src

# Install deps
npm install

# Dev server
npm run dev

# Build
npm run build

# Lint
npm run lint

# Test
npm test
```

### Database
```bash
# MySQL
mysql -u root -p finance_hub_dev

# Redis
redis-cli

# Check Redis
redis-cli ping
```

---

## 🔒 SECURITY CHECKLIST

Before any work, verify:
- [ ] No hardcoded credentials
- [ ] No API keys in code
- [ ] Input validation on all endpoints
- [ ] Authentication on protected routes
- [ ] CORS properly configured
- [ ] No sensitive data in logs

---

## 📊 PROJECT STATUS

| Component | Status | Progress |
|-----------|--------|----------|
| Backend | ✅ Complete | 95% |
| Frontend | ✅ In Progress | 75% |
| Security | 🔄 In Progress | S-009 to S-016 |
| DevOps | ✅ In Progress | D-013, D-014 complete |

---

## 🆘 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Import errors | Check `requirements.txt` / `package.json` |
| TypeScript errors | Run `npm run typecheck` |
| Linting | Run `npm run lint` or `ruff check` |
| Database issues | Check `python manage.py check` |
| WebSocket not connecting | Verify Redis running (`redis-cli ping`) |
| Auth failures | Check JWT token in headers |

---

## 📝 FILE NAMING CONVENTIONS

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `RealTimeChart.tsx` |
| Utils | camelCase | `formatCurrency.ts` |
| Hooks | camelCase with `use` | `useMarketData.ts` |
| Types | PascalCase | `AssetTypes.ts` |
| API files | snake_case | `market_data.py` |
| Config | SCREAMING_SNAKE | `SECRET_KEY` |

---

## 🔗 EXTERNAL RESOURCES

| Need | URL |
|------|-----|
| Django Ninja | https://django-ninja.dev/ |
| Next.js | https://nextjs.org/docs |
| TypeScript | https://www.typescriptlang.org/ |
| shadcn/ui | https://ui.shadcn.com/ |
| Tailwind | https://tailwindcss.com/ |
| React | https://react.dev/ |

---

**Last Updated:** February 1, 2026  
**For:** AI Agents working on FinanceHub
