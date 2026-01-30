# FinanceHub

A comprehensive financial platform for tracking, analyzing, and managing investments across multiple asset classes including stocks, crypto, ETFs, and more.

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FinanceHub Platform                       │
├─────────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐         ┌──────────────────┐  │
│  │   FRONTEND       │         │    BACKEND       │  │
│  │   Next.js 16    │◄────────┤   Django 5       │  │
│  │   React 19       │  HTTP   │   Django Ninja    │  │
│  │   TypeScript      │         │   REST API       │  │
│  │   Tailwind CSS    │         │                  │  │
│  └──────────────────┘         └────────┬─────────┘  │
│          │                            │              │
│          │ WebSocket                  │              │
│          └──────────────────────────────┼──────────────┘
│                                     │             │
│                            ┌────────┴────────┐  │
│                            │   MySQL 8.0      │  │
│                            │   TimescaleDB     │  │
│                            │   Redis 7        │  │
│                            └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
FinanceHub/
├── Backend/                    # Django REST API backend
│   └── src/
│       ├── assets/            # Asset models and API
│       ├── core/             # Core Django settings and configuration
│       ├── data/             # Data fetching and processing
│       ├── fundamentals/      # Fundamental analysis
│       ├── investments/      # Portfolio and transaction management
│       ├── portfolios/       # Portfolio models and API
│       ├── screener/         # Stock screening service
│       ├── search/           # Asset search functionality
│       ├── tasks/            # Celery background tasks
│       ├── users/            # User authentication and management
│       ├── utils/            # Helper utilities
│       └── websocket_consumers/  # Real-time WebSocket connections
│
└── Frontend/                 # Next.js frontend
    └── src/
        ├── app/             # Next.js app router pages
        ├── components/      # React components
        │   ├── analytics/    # Analytics visualization components
        │   ├── realtime/     # Real-time data components
        │   ├── layout/       # Layout components
        │   └── ui/           # shadcn/ui components (60+)
        ├── contexts/        # React contexts
        ├── hooks/           # Custom React hooks
        ├── lib/             # Libraries and utilities
        │   ├── api/          # API clients
        │   ├── types/        # TypeScript type definitions
        │   └── utils/        # Utility functions
        └── stores/          # Zustand state management
```

---

## Technology Stack

### Backend
- **Django 5** + Django Ninja (REST API)
- **MySQL 8.0** (primary database)
- **TimescaleDB** (time-series extensions for MySQL/PostgreSQL)
- **Redis 7** (caching + Celery broker + WebSockets)
- **Dramatiq** (background task processing)
- **Daphne** (ASGI server for WebSockets)
- **Polars** (data processing)
- **WebSockets** (Channels) for real-time data

### Frontend
- **Next.js 16** with App Router
- **React 19**
- **TypeScript 5**
- **Zustand** (state management)
- **Recharts + Chart.js** (charting libraries)
- **Tailwind CSS 4**
- **shadcn/ui** (60+ pre-built components)

### Data Providers (18 sources)
- Yahoo Finance
- Alpha Vantage (10+ keys)
- SEC EDGAR (filings)
- RSS News Aggregator
- Stocktwits Sentiment
- FRED Economic Data
- ExchangeRate.Host (FX)
- Binance (crypto + WebSocket)
- CoinGecko (crypto)
- CoinMarketCap (crypto)
- Polygon.io (stocks + WebSocket)
- IEX Cloud (fundamentals)
- Finnhub (stocks + WebSocket + news)
- NewsAPI (150,000+ sources)
- Massive API
- Twelve Data
- Reddit sentiment
- And more...

---

## Current Status (January 28, 2026)

### Backend Progress: 95% Complete ✅

| Component | Status | Details |
|-----------|---------|---------|
| Data Providers | ✅ Complete | 18 providers integrated |
| API Key Rotation | ✅ Complete | Intelligent selection with rate limit handling |
| Caching System | ✅ Complete | L1 (memory), L2 (Redis), L3 (database) - 85-95% hit rate |
| Orchestration | ✅ Complete | Call planner, unified data interface, batch fetching |
| WebSocket Streaming | ✅ Complete | Binance + Finnhub streaming with authentication |
| Background Tasks | ✅ Complete | Dramatiq workers for scheduled updates |
| REST API | ✅ Complete | 30+ endpoints for market data, assets, portfolios |
| Technical Analytics | ✅ Complete | 10+ indicators (SMA, EMA, RSI, MACD, Bollinger, etc.) |
| Alert System | ✅ Complete | Price, technical, volume, portfolio alerts with WebSocket delivery |
| Monitoring Dashboard | ✅ Complete | Real-time latency, health scoring, error tracking, cache metrics |
| TimescaleDB | ✅ Complete | Time-series storage, hypertables, compression, archiving |
| WebSocket Authentication | ✅ Complete | JWT auth, rate limiting, quotas, abuse detection |
| Asset Models | ✅ Complete | Stocks, crypto, ETFs, indices with historical data |
| User Authentication | ✅ Complete | Registration, login, JWT tokens |
| Portfolio Management | ✅ Complete | Holdings, transactions, performance tracking |
| Screener Service | ✅ Complete | Advanced filtering with multiple criteria |
| Search Service | ✅ Complete | Full-text search across all assets |
| Fundamental Data | ✅ Complete | Company info, financial statements, earnings |
| News & Sentiment | ✅ Complete | 150,000+ sources with sentiment analysis |

### Frontend Progress: 75% Complete ✅

| Component | Status | Details |
|-----------|---------|---------|
| Project Foundation | ✅ Complete | Next.js 16, TypeScript, Tailwind, shadcn/ui setup |
| Authentication | ✅ Complete | Login, register, auth context with JWT |
| Real-Time Components | ✅ Complete | 5 components (ConnectionStatus, LivePriceTicker, RealTimeChart, OrderBook, TradeFeed) |
| Portfolio Management | ✅ Complete | Watchlist, holdings, transactions pages with full CRUD |
| Alerts System | ✅ Complete | Alerts page with full management, history tracking |
| Sentiment Analysis | ✅ Complete | Sentiment page with symbol search, day filters |
| Market Data Pages | ✅ Complete | Dashboard, overview, indices, stocks pages |
| Analytics Charts | ✅ Complete | 8 chart components created (pie, bar, line, area charts) |
| Analytics Dashboard | ✅ Complete | Components integrated and working |
| API Clients | ✅ Complete | 13 API client files, centralized client infrastructure |
| Type Definitions | ✅ Complete | 14 type definition files, comprehensive interfaces |
| State Management | ✅ Complete | 4 Zustand stores (market, watchlist, screener, realtime) |
| Component Library | ✅ Complete | 80+ components (60+ shadcn/ui + 20+ custom) |
| Asset Detail Pages | ✅ Complete | Full detail pages implemented |
| Screener UI | ✅ Complete | FilterPanel, ResultsPanel, ScreenerChart all working |
| Settings Page | ✅ Complete | 4 tabs: Appearance, Notifications, Account, Security |
| Testing Infrastructure | 🔄 In Progress | Jest configured, 183 tests (121 passing, 62 failing) |
| Mobile Responsiveness | 🔄 Partial | Some pages responsive, needs full audit |
| Accessibility | ❌ Not Started | ARIA labels, keyboard navigation not implemented |

---

## Backend Architecture

### Core Services
- **Assets API**: Retrieve and manage asset information across all asset classes
- **Portfolios API**: Track portfolio holdings, performance, and analytics
- **Screener API**: Advanced stock screening with multiple filters
- **Search API**: Full-text search across all assets
- **Watchlist API**: Manage asset watchlists (CRUD operations)
- **Alerts API**: Price, technical, volume alerts with WebSocket delivery
- **News & Sentiment API**: News aggregation with sentiment analysis
- **Fundamentals API**: Company fundamentals, financial statements, earnings
- **Portfolio Analytics API**: Performance metrics, risk analysis, rebalancing suggestions

### Data Pipeline
- Automated data fetching from 18+ sources
- Data processing pipeline with technical indicators (10+ indicators)
- Historical price and metrics storage in MySQL + TimescaleDB
- Multi-tier caching (L1: memory, L2: Redis, L3: database)
- Real-time price updates via WebSockets
- Background task processing with Dramatiq

### WebSocket Channels
- `ws/market/{symbol}/{data_type}` - Real-time market data
- `ws/user/` - User-specific updates (watchlist, alerts, notifications)
- JWT-based authentication
- Rate limiting and quotas
- Connection monitoring and analytics

---

## Frontend Architecture

### Pages (25+)
- **Authentication**: Login, Register
- **Market**: Dashboard, Overview, Indices, Stocks
- **Portfolio**: Watchlist, Holdings, Transactions, Analytics
- **Investments**: Alerts, Sentiment Analysis
- **Assets**: Asset listings, Asset detail pages
- **Fundamentals**: Company fundamentals data

### Components (80+)
- **Analytics Components** (8): Charts for performance, allocation, risk, benchmarks
- **Real-Time Components** (5): Connection status, price ticker, charts, order book, trade feed
- **UI Components** (60+): shadcn/ui components (button, card, dialog, table, etc.)
- **Layout Components**: Navbar, sidebar, dashboard layout
- **Chart Components**: Various visualizations for market data and analytics

### State Management
- **Market Store**: Real-time market data and streaming
- **Watchlist Store**: User watchlists and asset tracking
- **Screener Store**: Screening criteria and results
- **Realtime Store**: WebSocket connection state and real-time data
- **Auth Context**: User authentication and session management

### API Clients (13)
- Centralized API client with error handling
- Dedicated clients for: auth, assets, portfolios, watchlist, holdings, transactions, alerts, sentiment, fundamentals, markets, analytics

---

## Setup Instructions

### Backend

```bash
cd Backend/src

# Install dependencies
pip install -r ../requirements.txt

# Set up database
python manage.py makemigrations
python manage.py migrate

# Start development server
python manage.py runserver

# Start background worker
dramatiq -A src.scheduler_tasks worker -l info

# Start WebSocket streams
python manage.py start_realtime_streams
```

### Frontend

```bash
cd Frontend/src

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Run tests
npm test
```

### Required Services

**MySQL Database:**
```bash
# Install MySQL 8.0
# Create database: finance_hub_dev
# Create user with permissions
# Update .env with database credentials
```

**Redis (Required for WebSockets + Celery):**
```bash
# Install Redis 7
redis-server
```

---

## Environment Variables

### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=finance_hub_dev
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# API Keys (register as needed)
COINGECKO_API_KEY=your-key
COINMARKETCAP_API_KEY=your-key
BINANCE_API_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key
FINNHUB_API_KEY=your-key
POLYGON_API_KEY=your-key
IEX_API_KEY=your-key
NEWSAPI_KEY=your-key
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user

### Assets
- `GET /api/assets/` - List all assets
- `GET /api/assets/{symbol}/` - Get asset details
- `GET /api/assets/{symbol}/price/` - Get current price
- `GET /api/assets/search/` - Search assets

### Portfolios
- `GET /api/portfolios/` - List user portfolios
- `POST /api/portfolios/` - Create portfolio
- `GET /api/portfolios/{id}/` - Get portfolio details
- `GET /api/portfolios/{id}/holdings/` - Get portfolio holdings
- `GET /api/portfolios/{id}/transactions/` - Get portfolio transactions
- `GET /api/portfolios/{id}/summary/` - Get portfolio summary
- `GET /api/portfolios/{id}/performance/` - Get performance metrics
- `GET /api/portfolios/{id}/risk-analysis/` - Get risk analysis
- `GET /api/portfolios/{id}/rebalance-suggestions/` - Get rebalancing suggestions

### Watchlist
- `GET /api/watchlist/` - List watchlists
- `POST /api/watchlist/` - Create watchlist
- `GET /api/watchlist/{id}/` - Get watchlist details
- `PUT /api/watchlist/{id}/` - Update watchlist
- `DELETE /api/watchlist/{id}/` - Delete watchlist
- `POST /api/watchlist/{id}/assets/` - Add asset to watchlist
- `DELETE /api/watchlist/{id}/assets/{symbol}/` - Remove asset from watchlist

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/` - Create alert
- `GET /api/alerts/{id}/` - Get alert details
- `PUT /api/alerts/{id}/` - Update alert
- `DELETE /api/alerts/{id}/` - Delete alert
- `POST /api/alerts/{id}/test/` - Test alert trigger
- `GET /api/alerts/{id}/history/` - Get alert trigger history
- `GET /api/alerts/stats/` - Get alert statistics

### Market Data
- `GET /api/market/overview/` - Market overview
- `GET /api/market/indices/` - Global indices
- `GET /api/market/stocks/` - Stock listings
- `GET /api/market/{symbol}/price/` - Get current price
- `GET /api/market/{symbol}/history/` - Get historical prices
- `GET /api/market/{symbol}/indicators/` - Get technical indicators

### Sentiment & News
- `GET /api/sentiment/{symbol}/` - Get sentiment analysis
- `GET /api/news/` - Get news articles
- `GET /api/news/search/` - Search news

### Screener
- `POST /api/screener/run/` - Run stock screener
- `GET /api/screener/presets/` - Get available presets

---

## WebSocket Channels

### Market Data
- `ws/market/{symbol}/price` - Real-time price updates
- `ws/market/{symbol}/orderbook` - Order book depth
- `ws/market/{symbol}/trades` - Trade stream

### User Updates
- `ws/user/` - User-specific updates (watchlist, alerts, notifications)

### Authentication
- WebSocket connections require JWT token
- Rate limiting per connection
- Per-user quotas for subscriptions

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following AGENTS.md guidelines
4. Run tests for both backend and frontend
5. Commit your changes
6. Push to your branch
7. Open a Pull Request

See `AGENTS.md` for detailed coding guidelines and best practices.

---

## License

This project is licensed under the MIT License.

---

## Documentation

Comprehensive documentation is organized in the [docs/](docs/) directory:

- **[Documentation Index](docs/INDEX.md)** - Master index of all documentation
- **[Architecture](docs/architecture/)** - System design and database schema
- **[Development](docs/development/)** - Development guides and implementation
- **[Operations](docs/operations/)** - DevOps and infrastructure
- **[Security](docs/security/)** - Security assessments and guidelines
- **[Agents](docs/agents/)** - Agent communication and workflows
- **[References](docs/references/)** - Reference guides and onboarding

### Quick Reference

| Task | Documentation |
|------|---------------|
| **Setup** | [docs/references/SETUP_COMPLETE.md](docs/references/SETUP_COMPLETE.md) |
| **Development** | [docs/development/](docs/development/) |
| **Deployment** | [docs/operations/DEPLOYMENT.md](docs/operations/DEPLOYMENT.md) |
| **Security** | [docs/security/SECURITY.md](docs/security/SECURITY.md) |
| **Architecture** | [docs/architecture/](docs/architecture/) |
| **Monitoring** | [docs/operations/MONITORING.md](docs/operations/MONITORING.md) |

---

### Additional Documentation

- **AGENTS.md** - Coding guidelines and conventions
- **.opencode/ROADMAP.md** - Backend and frontend development phases
- **.opencode/FRONTEND_ROADMAP.md** - Frontend-specific roadmap
- **.opencode/STATUS.md** - Current project status
- **.opencode/TODOLIST.md** - Active task tracking

---

## Quick Links

- **Backend API Docs**: http://localhost:8000/api/docs (when running)
- **Frontend**: http://localhost:3000 (when running)
- **Repository**: https://github.com/Fuuurma/FinanceHub.git

## Repository Structure

This is a **monorepo** containing:
- **Backend**: Django/Python REST API (`Backend/`)
- **Frontend**: Next.js TypeScript UI (`Frontend/`)

---

**Last Updated**: January 30, 2026
**Monorepo Migration**: ✅ 100% Complete
**Backend Status**: 95% Complete
**Frontend Status**: 65% Complete
