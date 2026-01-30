# FinanceHub - Project Context

**Project Type:** Web App / Financial Platform
**Status:** Active Development
**Last Updated:** January 29, 2026

---

## Project Overview

FinanceHub is a comprehensive financial platform for tracking, analyzing, and managing investments across multiple asset classes including stocks, crypto, ETFs, and more. The platform provides real-time market data, portfolio tracking, AI-powered insights, and advanced analytics.

---

## Tech Stack

### Backend
- **Runtime:** Python 3.11+
- **Framework:** Django 5 + Django Ninja (REST API)
- **Database:** MySQL 8.0 + TimescaleDB (time-series)
- **Task Queue:** Dramatiq (background tasks)
- **Caching:** Redis 7
- **Real-time:** Django Channels (WebSockets)
- **ASGI Server:** Daphne
- **Data Processing:** Polars

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5
- **UI Library:** shadcn/ui (60+ components)
- **Styling:** Tailwind CSS 4
- **State Management:** Zustand
- **Charts:** Recharts + Chart.js
- **Forms:** React Hook Form + Zod

### Infrastructure
- **Deployment:** Vercel (frontend), Railway/Render (backend)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry

---

## Project Structure

```
FinanceHub/
├── Backend/src/
│   ├── api/              # Django Ninja API endpoints
│   ├── assets/           # Asset models and data
│   ├── core/             # Django settings
│   ├── data/             # Data fetching/processing
│   ├── fundamentals/     # Fundamental analysis
│   ├── investments/      # Portfolio management
│   ├── portfolios/       # Portfolio models
│   ├── screener/         # Stock screening
│   ├── search/           # Asset search
│   ├── tasks/            # Celery tasks
│   ├── users/            # Authentication
│   ├── utils/            # Utilities
│   └── websocket_consumers/
└── Frontend/src/
    ├── app/              # Next.js pages
    ├── components/       # React components
    ├── contexts/         # React contexts
    ├── hooks/            # Custom hooks
    ├── lib/              # Utilities
    └── stores/           # Zustand stores
```

---

## Key Features

- ✅ Real-time market data (18+ data sources)
- ✅ Portfolio tracking and management
- ✅ Stock screener with advanced filters
- ✅ AI-powered financial advisor
- ✅ Fundamental analysis
- ✅ Trading integration
- ✅ WebSocket real-time updates
- ✅ Multi-asset support (stocks, crypto, ETFs)
- ✅ 60+ UI components

---

## Current Status

### Completed
- ✅ Django Ninja backend with comprehensive API
- ✅ Next.js frontend with 60+ shadcn/ui components
- ✅ MySQL + TimescaleDB database
- ✅ Redis caching and WebSocket support
- ✅ 200+ features documented

### In Progress
- 🚧 AI advisor integration
- 🚧 Trading features
- 🚧 Advanced analytics

### Known Issues
- ⚠️ Test coverage needs improvement

---

## Getting Started

```bash
# Backend
cd Backend/src
python manage.py runserver
dramatiq tasks
daphne daphne_config:application

# Frontend
cd Frontend/src
npm run dev
npm run build
```

---

## Documentation

FinanceHub has extensive documentation:
- `README.md` - Quick start guide
- `AGENTS.md` - Comprehensive coding guidelines (77KB)
- `FEATURES_SPECIFICATION.md` - 200+ features documented
- `IMPLEMENTATION_ROADMAP.md` - Development roadmap
- `WHERE_TO_START.md` - Entry points for contributors

---

## AI Agent Rules

When working on FinanceHub:

1. Use Django Ninja for all backend API endpoints
2. Use TypeScript strict mode in frontend
3. Use shadcn/ui components (don't build from scratch)
4. Use Zustand for state management
5. Implement proper error handling
6. Use environment variables for configuration
7. Follow the extensive AGENTS.md guidelines

---

## Notes

One of the most well-documented projects in the portfolio. Just needs PROJECT_STATUS.md to be complete.
