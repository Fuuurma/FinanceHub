# FinanceHub - Complete Architecture Documentation

**Architect:** GAUDÍ (AI System Architect)
**Version:** 2.0
**Last Updated:** January 30, 2026
**Status:** Production-Ready

---

## 🏛️ EXECUTIVE SUMMARY

FinanceHub is a **Bloomberg Terminal-inspired financial platform** built with modern architecture principles:

- **Frontend:** Next.js 14 + TypeScript + shadcn/ui + Zustand
- **Backend:** Django 4.2 + Django Ninja + Celery/Dramatiq
- **Database:** MySQL 8.0 (production) with Redis caching
- **Real-time:** Django Channels + WebSocket + Binance WebSocket
- **Infrastructure:** Docker + Docker Compose + GitHub Actions CI/CD
- **Monitoring:** Prometheus + Grafana + Sentry (planned)

**Architecture Style:** Microservices-ready monolith with event-driven background processing

---

## 📊 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        FinanceHub Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │    │    Backend   │    │  Background  │      │
│  │   Next.js    │◄──►│   Django     │◄──►│    Workers   │      │
│  │   TypeScript │    │   Django     │    │ Celery/Dram  │      │
│  │   Zustand    │    │    Ninja     │    │              │      │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │
│                             │                    │              │
│                      ┌──────┴───────┐    ┌──────┴───────┐      │
│                      │   WebSocket  │    │  External    │      │
│                      │   Channels   │    │   APIs       │      │
│                      └──────┬───────┘    └──────┬───────┘      │
│                             │                    │              │
│                      ┌──────┴───────┐    ┌──────┴───────┐      │
│                      │  PostgreSQL │    │    Redis     │      │
│                      │  Database   │    │    Cache     │      │
│                      └─────────────┘    └─────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Layers:

1. **Presentation Layer** (Frontend)
   - Next.js 14 App Router
   - TypeScript strict mode
   - shadcn/ui component library
   - Zustand state management
   - Tailwind CSS 4 styling

2. **API Layer** (Backend)
   - Django Ninja (Fast API-like)
   - 30+ API endpoints
   - JWT authentication
   - Rate limiting
   - CORS enabled

3. **Business Logic Layer**
   - Domain-driven design
   - Service layer pattern
   - Repository pattern
   - Validation layer
   - Error handling middleware

4. **Data Access Layer**
   - Django ORM
   - Custom managers
   - Query optimization
   - Connection pooling
   - Transaction management

5. **Background Processing Layer**
   - Celery (long-running tasks)
   - Dramatiq (real-time tasks)
   - RabbitMQ broker
   - Redis result backend
   - Scheduled tasks (beat)

6. **Real-time Communication Layer**
   - Django Channels
   - WebSocket protocol
   - Redis channel layer
   - Binance WebSocket integration
   - Server-Sent Events (SSE)

7. **Infrastructure Layer**
   - Docker containers
   - Docker Compose orchestration
   - Nginx reverse proxy
   - GitHub Actions CI/CD
   - Monitoring (Prometheus/Grafana)

---

## 🎨 FRONTEND ARCHITECTURE

### Technology Stack:

```typescript
Frontend Stack:
├── Framework: Next.js 14 (App Router)
├── Language: TypeScript 5.3
├── Styling: Tailwind CSS 4
├── UI Components: shadcn/ui (Radix UI + Tailwind)
├── State Management: Zustand 10 stores
├── Data Fetching: React Query + SWR
├── Charts: lightweight-charts, Recharts
├── Forms: React Hook Form + Zod
├── Tables: TanStack Table
└── Build Tool: Turbopack (Next.js 14)
```

### Directory Structure:

```
Frontend/src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (dashboard)/              # Dashboard route group
│   │   ├── page.tsx              # Main dashboard
│   │   ├── portfolio/
│   │   ├── trading/
│   │   └── analytics/
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   ├── charts/                   # Chart components
│   ├── forms/                    # Form components
│   └── analytics/                # Analytics components
├── stores/                       # Zustand stores
│   ├── portfolioStore.ts
│   ├── realtimeStore.ts
│   ├── holdingsStore.ts
│   └── ... (9 more stores)
├── hooks/                        # Custom React hooks
│   ├── useWebSocket.ts
│   ├── useLocalStorage.ts
│   └── ... (20+ hooks)
├── lib/                          # Utilities
│   ├── api/                      # API client
│   ├── types/                    # TypeScript types
│   ├── constants/                # Constants
│   └── utils/                    # Helper functions
└── tests/                        # Tests
```

### State Management (Zustand):

**10 Domain-Specific Stores:**

1. **portfolioStore.ts** (6,294 bytes)
   - Portfolio data, positions, allocations
   - Performance metrics
   - Risk calculations

2. **realtimeStore.ts** (6,635 bytes) ⭐
   - WebSocket connection state
   - Real-time price updates
   - Trade feed
   - Order book data
   - Connection management

3. **holdingsStore.ts** (9,904 bytes)
   - Asset holdings
   - P&L calculations
   - Holdings allocation

4. **screenerStore.ts** (6,133 bytes)
   - Stock screener filters
   - Screen results
   - Filter state

5. **tradingStore.ts** (4,774 bytes)
   - Order entry
   - Trade execution
   - Order history

6. **watchlistStore.ts** (4,374 bytes)
   - Watchlist management
   - Symbol tracking

7. **analyticsStore.ts** (4,954 bytes)
   - Analytics data
   - Performance metrics

8. **chartsStore.ts** (4,067 bytes)
   - Chart configurations
   - Timeframe settings

9. **marketStore.ts** (2,283 bytes)
   - Market overview
   - Market status

10. **economicStore.ts** (3,885 bytes)
    - Economic calendar
    - Economic indicators

**Why Zustand?**
- ✅ Lightweight (~1KB)
- ✅ No boilerplate
- ✅ TypeScript-first
- ✅ Easy to test
- ✅ No Context Provider hell
- ✅ DevTools integration

### Component Architecture:

**Design Patterns:**

1. **Compound Components**
   ```typescript
   <DataTable>
     <DataTable.Header />
     <DataTable.Body />
     <DataTable.Footer />
   </DataTable>
   ```

2. **Render Props**
   ```typescript
   <Chart
     render={(data) => <LineChart data={data} />}
   />
   ```

3. **Custom Hooks Pattern**
   ```typescript
   function Component() {
     const { data, loading } = usePortfolioData()
     // ...
   }
   ```

4. **Higher-Order Components (HOC)**
   ```typescript
   withAuth(ProfilePage)
   withErrorBoundary(Dashboard)
   ```

### Real-time Data Flow:

```
Binance WebSocket → Django Channels → Frontend WebSocket
                                        ↓
                                 realtimeStore.updatePrice()
                                        ↓
                                   React Re-render
```

**WebSocket Client Architecture:**

```typescript
// lib/api/websocket.ts
class WebSocketClient {
  private ws: WebSocket | null
  private reconnectTimer: NodeJS.Timeout
  private subscriptions: Set<string>

  connect(token?: string): Promise<void>
  disconnect(): void
  subscribe(request: SubscriptionRequest): void
  unsubscribe(symbol: string, dataTypes: DataType[]): void
  on(event: string, callback: Function): void
}
```

### Performance Optimizations:

1. **Code Splitting**
   - Route-based splitting
   - Component-based splitting
   - Dynamic imports

2. **Image Optimization**
   - Next.js Image component
   - WebP format
   - Lazy loading

3. **Bundle Size Optimization**
   - Tree shaking
   - Minification
   - Gzip compression
   - Target: < 250KB initial bundle

4. **Rendering Optimizations**
   - React.memo() for expensive components
   - useMemo() for expensive calculations
   - useCallback() for event handlers
   - Virtualization for long lists

---

## 🔧 BACKEND ARCHITECTURE

### Technology Stack:

```python
Backend Stack:
├── Framework: Django 4.2
├── API: Django Ninja (Fast, OpenAPI auto-docs)
├── Auth: Django Ninja JWT
├── Real-time: Django Channels 3
├── Tasks: Celery 5 + Dramatiq 1
├── Broker: RabbitMQ
├── Cache: Redis 7
├── Database: MySQL 8.0
├── Validation: Pydantic 2
└── Async: asyncio + aiohttp
```

### Directory Structure:

```
Backend/src/
├── core/                         # Django settings
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # URL routing
│   ├── asgi.py                   # ASGI config (WebSocket)
│   ├── wsgi.py                   # WSGI config (HTTP)
│   ├── api.py                    # NinjaAPI instance
│   └── celery.py                 # Celery configuration
├── api/                          # API endpoints (30+)
│   ├── unified_market_data.py
│   ├── indicators.py
│   ├── analytics.py
│   ├── realtimedata.py
│   └── ... (26 more)
├── users/                        # User domain
│   ├── models/
│   │   ├── user.py
│   │   ├── role.py
│   │   └── permission.py
│   ├── api/
│   │   └── base.py
│   └── services/
├── assets/                       # Asset domain
│   ├── models/
│   │   ├── asset.py
│   │   └── historic/
│   └── api/
│       └── asset.py
├── portfolios/                   # Portfolio domain
├── trading/                      # Trading domain
├── investments/                  # Investments domain
├── fundamentals/                 # Fundamentals domain
├── ai_advisor/                   # AI advisor domain
├── charts/                       # Charts domain
├── data/                         # Data pipeline
│   ├── processing/
│   │   └── pipeline.py
│   ├── data_fetcher/
│   ├── data_providers/
│   │   ├── yahooFinance/
│   │   ├── binance/
│   │   ├── sec_edgar/
│   │   └── ... (21 more)
│   └── base_fetcher.py
├── tasks/                        # Background tasks
│   ├── celery_tasks.py
│   ├── crypto_data_tasks.py
│   ├── scheduler_tasks.py
│   └── binance_websocket.py
├── utils/                        # Utilities
│   ├── pickle_cache.py
│   ├── services/
│   └── helpers/
└── websocket_consumers/          # WebSocket consumers
```

### API Architecture:

**API Structure (Django Ninja):**

```python
# core/api.py
api = NinjaAPI(
    title="FinanceHub API",
    version="1.0.0",
    description="Professional investment portfolio management API",
    docs_url="/docs",
)

# 30+ routers registered:
api.add_router("/users", users_router)
api.add_router("/assets", assets_router)
api.add_router("/portfolios", portfolios_router)
api.add_router("/market", unified_market_data_router)
api.add_router("/indicators", indicators_router)
# ... and 25 more
```

**API Endpoints (30+):**

1. **Users & Auth** (`/users`, `/auth`)
   - Registration, login, logout
   - JWT token refresh
   - Profile management
   - Password reset

2. **Assets** (`/assets`)
   - Asset search
   - Price history
   - Real-time quotes
   - Asset details

3. **Portfolios** (`/portfolios`)
   - Portfolio CRUD
   - Holdings management
   - Performance metrics
   - Allocations

4. **Market Data** (`/market`, `/realtime`)
   - Unified market data
   - Real-time WebSocket
   - Historical data
   - Technical indicators

5. **Trading** (`/trading`)
   - Order entry
   - Order management
   - Trade history
   - Position tracking

6. **Analytics** (`/analytics`, `/analytics/v2`)
   - Portfolio analytics
   - Risk metrics
   - Performance attribution
   - Correlation analysis

7. **AI Advisor** (`/ai/v2/*`)
   - AI insights
   - Portfolio recommendations
   - Reports generation
   - Templates

8. **Advanced Features**
   - Options pricing (`/options`)
   - Fixed income (`/fixed-income`)
   - Quantitative models (`/quantitative`)
   - Economic data (`/economic`)
   - News & sentiment (`/news`)

**Request/Response Pattern:**

```python
from ninja import Schema

class AssetResponse(Schema):
    id: int
    symbol: str
    name: str
    price: float
    change_percent: float

@api.get("/assets/{symbol}")
def get_asset(request, symbol: str) -> AssetResponse:
    asset = Asset.objects.get(symbol__iexact=symbol)
    return AssetResponse(
        id=asset.id,
        symbol=asset.symbol,
        name=asset.name,
        price=asset.current_price,
        change_percent=asset.change_percent
    )
```

**Why Django Ninja?**
- ✅ Fast (comparable to FastAPI)
- ✅ Automatic OpenAPI docs
- ✅ Pydantic validation
- ✅ Type hints
- ✅ Django ORM integration
- ✅ Easy testing

### Database Architecture:

**Database Design:**

**Domain-Driven Models:**

1. **User Domain** (`users/`)
   - User (custom auth model)
   - Role, Permission
   - UserProfile, UserSession
   - AccountType, UserStatus

2. **Asset Domain** (`assets/`)
   - Asset (stocks, crypto, ETFs)
   - AssetType, AssetClass
   - Sector, Industry
   - Country, Exchange
   - AssetPricesHistoric
   - AssetMetricsHistoric

3. **Portfolio Domain** (`portfolios/`)
   - Portfolio
   - PortfolioHolding
   - PortfolioAllocation
   - PortfolioPerformance

4. **Trading Domain** (`trading/`)
   - Order
   - Trade
   - Position

5. **Investment Domain** (`investments/`)
   - DataProvider
   - NewsArticle
   - EconomicIndicator

**Key Model Features:**

**Custom User Model:**
```python
class User(AbstractBaseUser, PermissionsMixin, UUIDModel,
           TimestampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True)
    status = models.ForeignKey("UserStatus", on_delete=models.PROTECT)
    account_type = models.ForeignKey("AccountType", on_delete=models.PROTECT)
    roles = models.ManyToManyField("Role")

    # Security
    two_factor_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    # Subscription
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    # Preferences
    preferences = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
```

**Base Models (Mixins):**
- **UUIDModel** - UUID primary key
- **TimestampedModel** - created_at, updated_at
- **SoftDeleteModel** - is_deleted, deleted_at
- **MetadataModel** - metadata JSONField

**Database Indexes:**
```python
class Meta:
    indexes = [
        models.Index(fields=["email", "is_active"]),
        models.Index(fields=["username", "is_active"]),
        models.Index(fields=["status", "is_active"]),
        models.Index(fields=["account_type"]),
        models.Index(fields=["created_at"]),
    ]
```

**Why MySQL?**
- ✅ Production-ready
- ✅ ACID compliant
- ✅ Full-text search
- ✅ JSON support
- ✅ Connection pooling
- ✅ Replication support

**Database Optimizations:**
- Connection pooling (CONN_MAX_AGE=600)
- Query optimization (select_related, prefetch_related)
- Database indexes on foreign keys
- Read replicas (planned)
- Query result caching (Redis)

---

## 🔄 REAL-TIME ARCHITECTURE

### WebSocket Implementation:

**Technology: Django Channels + Redis**

```
Frontend           Django Channels          Redis            Binance WS
    │                    │                    │                  │
    ├── WebSocket ────► │  Consumer          │                  │
    │◄── Updates ───────│  Layer             │                  │
    │                   │    │                │                  │
    │                   │  Redis ◄────────────┼───── Ticker ────┤
    │                   │  Channel           │                  │
    │                   │  Layer             │                  │
    │                   │                    │                  │
```

### Backend WebSocket:

**Consumer Pattern:**
```python
# websocket_consumers/market.py
class MarketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("market", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle subscription

    async def ticker_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
```

**Binance WebSocket Integration:**
```python
# tasks/binance_websocket.py
@dramatiq.actor
async def start_binance_websocket_stream(symbols):
    ws_client = get_binance_ws_client()

    # Subscribe to mini ticker
    for symbol in symbols:
        await ws_client.subscribe_mini_ticker(
            symbol,
            callback=lambda data: _broadcast_ticker_update(symbol, data)
        )

    # Broadcast to Django Channels
    await channel_layer.group_send(
        f"ticker_{symbol}",
        {"type": "ticker.update", "data": data}
    )
```

### Frontend WebSocket:

**WebSocket Client:**
```typescript
// lib/api/websocket.ts
class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  async connect(token?: string) {
    const wsUrl = `ws://localhost:8000/ws/market/?token=${token}`
    this.ws = new WebSocket(wsUrl)

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      this.emit('data', message)
    }

    this.ws.onerror = () => {
      this.emit('connection', {
        state: CONNECTION_STATES.ERROR
      })
    }

    this.ws.onclose = () => {
      this.reconnect()
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++
        this.connect()
      }, 1000 * Math.pow(2, this.reconnectAttempts))
    }
  }
}
```

**Real-time Store Integration:**
```typescript
// stores/realtimeStore.ts
export const useRealtimeStore = create<RealTimeStore>((set) => ({
  connectionState: CONNECTION_STATES.DISCONNECTED,
  prices: {},

  connect: async (token) => {
    const wsClient = getWebSocketClient()

    wsClient.on('data', (message) => {
      if (message.dataType === 'price') {
        set((state) => ({
          prices: {
            ...state.prices,
            [message.symbol]: message.data
          }
        }))
      }
    })

    await wsClient.connect(token)
  }
}))
```

### Real-time Data Flow:

**Price Update Flow:**
```
1. Binance WebSocket emits price update
   ↓
2. Backend receives via BinanceWebSocketClient
   ↓
3. Data normalized and validated
   ↓
4. Broadcast to Redis channel layer
   ↓
5. Django Channels consumer receives
   ↓
6. Frontend WebSocket receives message
   ↓
7. realtimeStore.updatePrice() called
   ↓
8. React components re-render
```

**Supported Real-time Data:**
- Mini ticker updates (price, volume)
- Trade execution data
- Order book depth
- Portfolio updates
- Order status updates
- Alert notifications

---

## 🔐 AUTHENTICATION & SECURITY

### Authentication Architecture:

**JWT-Based Authentication:**

```
Login Flow:
1. User submits credentials
   ↓
2. Backend validates (UserManager)
   ↓
3. Generates JWT access token (15 min)
   ↓
4. Generates refresh token (7 days)
   ↓
5. Returns tokens to frontend
   ↓
6. Frontend stores in secure HTTP-only cookie
   ↓
7. Subsequent requests include Bearer token
   ↓
8. Backend validates JWT
   ↓
9. Request proceeds if valid
```

**JWT Configuration:**
```python
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "BLACKLIST_ENABLED": True,  # Token blacklisting
}
```

**Permission System:**

**Role-Based Access Control (RBAC):**
```python
class User(AbstractBaseUser, PermissionsMixin):
    roles = models.ManyToManyField("Role")

    def has_permission(self, permission_code: str) -> bool:
        if self.is_superuser:
            return True

        return self.roles.filter(
            permissions__code=permission_code,
            permissions__is_active=True
        ).exists()
```

**Decorator Pattern:**
```python
from ninja import Schema
from users.models import User

def require_permission(permission_code: str):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.user.has_permission(permission_code):
                raise HttpError(403, "Permission denied")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

@api.get("/admin/reports")
@require_permission("view_reports")
def get_reports(request):
    # Only users with "view_reports" permission
    pass
```

### Security Features:

**Account Security:**
- ✅ Two-factor authentication (2FA)
- ✅ Failed login attempt tracking
- ✅ Account lockout after N attempts
- ✅ Password strength validation
- ✅ Email verification required
- ✅ Phone verification (optional)

**API Security:**
- ✅ Rate limiting (100/hour anon, 1000/hour auth)
- ✅ CORS configured
- ✅ CSRF protection
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection
- ✅ Secret key rotation

**Rate Limiting:**
```python
RATELIMIT_ENABLE = True
RATELIMIT_AUTHENTICATED = True
RATELIMIT_AUTHENTICATED_RATE = "1000/hour"
RATELIMIT_ANON_RATE = "100/hour"
RATELIMIT_USE_REDIS = True
```

---

## 📦 BACKGROUND PROCESSING ARCHITECTURE

### Task Queue System:

**Dual Queue Architecture:**

```
┌──────────────────────────────────────────────────────────┐
│                    Task Queues                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │    Celery    │    │   Dramatiq   │                  │
│  │              │    │              │                  │
│  │ Long-running │    │  Real-time   │                  │
│  │ Scheduled    │    │  Fast tasks  │                  │
│  │ Periodic     │    │  Low latency │                  │
│  └──────┬───────┘    └──────┬───────┘                  │
│         │                    │                          │
│         └────────┬───────────┘                          │
│                  │                                      │
│           ┌──────┴───────┐                             │
│           │  RabbitMQ    │                             │
│           │    Broker    │                             │
│           └──────────────┘                             │
│                  │                                      │
│           ┌──────┴───────┐     ┌──────────────┐       │
│           │   PostgreSQL │     │    Redis     │       │
│           │   Database   │     │ Result Cache │       │
│           └──────────────┘     └──────────────┘       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Celery Configuration:

**Usage: Long-running, scheduled tasks**

```python
# core/celery.py
app = Celery('financehub')

app.conf.beat_schedule = {
    'fetch-daily-prices': {
        'task': 'tasks.fetch_all_market_data',
        'schedule': crontab(hour=18, minute=0),  # 6 PM EST
    },
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': crontab(hour=0, minute=0),   # Midnight
    },
}
```

### Dramatiq Configuration:

**Usage: Real-time, low-latency tasks**

```python
# core/settings.py
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.rabbitmq.RabbitmqBroker",
    "OPTIONS": {"url": "amqp://localhost:5672"},
    "MIDDLEWARE": [
        "dramatiq.middleware.Prometheus",
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Retries",
    ],
}

DRAMATIQ_RESULT_BACKEND = {
    "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
    "BACKEND_OPTIONS": {"url": "redis://127.0.0.1:6379/1"},
}
```

### Task Types:

**Data Collection Tasks:**
1. **High Frequency** (Dramatiq)
   - Crypto price updates (every 2 min)
   - Stock price updates (every 5 min)
   - Health checks (every 1 min)

2. **Medium Frequency** (Dramatiq)
   - Data validation (every 10 min)
   - Trending cryptos (every 15 min)
   - Market rankings (every 30 min)

3. **Low Frequency** (Celery)
   - Historical data updates (daily)
   - Data cleanup (daily)
   - Report generation (weekly)

**Real-time WebSocket Tasks:**
```python
@dramatiq.actor
async def start_binance_websocket_stream(symbols):
    """Start Binance WebSocket for 15 crypto pairs"""
    ws_client = get_binance_ws_client()

    # Subscribe to ticker updates
    for symbol in symbols:
        await ws_client.subscribe_mini_ticker(symbol)

    # Broadcast to Django Channels
    await ws_client.listen_with_reconnect()
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Container Orchestration:

**Docker Compose (Development):**

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: finance_hub
      POSTGRES_USER: financehub
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build:
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  worker:
    build:
      dockerfile: Dockerfile.backend
    command: python start_dramatiq_worker.py
    depends_on:
      - postgres
      - redis
```

### CI/CD Pipeline:

**GitHub Actions (`.github/workflows/`):**

**CI Pipeline:**
```yaml
# .github/workflows/ci.yml
on: [pull_request, push]

jobs:
  backend-lint:
    - Black (formatting)
    - isort (imports)
    - Flake8 (linting)
    - MyPy (type checking)

  backend-tests:
    - Pytest
    - Coverage (min 70%)
    - Upload to Codecov

  frontend-lint:
    - ESLint
    - TypeScript type check

  frontend-tests:
    - Jest
    - React Testing Library
    - Coverage upload

  security-scan:
    - Trivy (vulnerabilities)
    - pip-audit (Python)
    - npm audit (Node)

  build-verify:
    - Production build
    - Bundle size check
```

**Deploy Pipeline:**
```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    - Build Docker image
    - Push to ECR
    - Deploy to ECS staging
    - Run smoke tests

  deploy-production:
    - Verify staging health
    - Build Docker image
    - Push to ECR
    - Deploy to ECS production
    - Monitor for 10 min
```

### Infrastructure (Planned Production):

**AWS Architecture:**
```
┌─────────────────────────────────────────────────┐
│              AWS Production Architecture          │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   CloudFront │    │   Route 53   │          │
│  │     CDN      │    │     DNS      │          │
│  └──────┬───────┘    └──────────────┘          │
│         │                                        │
│  ┌──────┴───────┐    ┌──────────────┐          │
│  │   ALB/WAF    │◄───│   Certificate │          │
│  │  Load Bal.   │    │   Manager     │          │
│  └──────┬───────┘    └──────────────┘          │
│         │                                        │
│  ┌──────┴────────────────────────┐              │
│  │        ECS Cluster            │              │
│  │  ┌─────────┐  ┌─────────┐     │              │
│  │  │Backend  │  │Frontend │     │              │
│  │  │ (8 tasks)│  │ (4 tasks)│    │              │
│  │  └─────────┘  └─────────┘     │              │
│  │  ┌─────────┐  ┌─────────┐     │              │
│  │  │ Worker  │  │Dramatiq │     │              │
│  │  │ (4 tasks)│  │ (2 tasks)│    │              │
│  │  └─────────┘  └─────────┘     │              │
│  └────────────────────────────────┘              │
│         │         │         │                    │
│  ┌──────┴─────┐ ┌┴─────────┐ ┌┴────────┐       │
│  │  RDS       │ │ElastiCache│ │RabbitMQ │       │
│  │  PostgreSQL │ │  Redis   │ │         │       │
│  └─────────────┘ └──────────┘ └─────────┘       │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Services:**
- **ECS** - Container orchestration
- **RDS** - Managed PostgreSQL
- **ElastiCache** - Managed Redis
- **RabbitMQ** - Message broker (self-managed)
- **ALB** - Application Load Balancer
- **CloudFront** - CDN
- **Route 53** - DNS
- **WAF** - Web Application Firewall
- **Certificate Manager** - SSL/TLS certificates

---

## 📈 PERFORMANCE & SCALABILITY

### Performance Optimizations:

**Frontend:**
1. **Code Splitting** - Route-based + component-based
2. **Tree Shaking** - Remove unused code
3. **Minification** - Reduce bundle size
4. **Gzip Compression** - Compress responses
5. **Image Optimization** - Next.js Image component
6. **Memoization** - React.memo, useMemo, useCallback
7. **Virtualization** - Long lists (react-window)
8. **Lazy Loading** - Components, images
9. **Prefetching** - Next.js link prefetching

**Backend:**
1. **Database Query Optimization**
   - select_related() - Foreign key reduction
   - prefetch_related() - M2M reduction
   - only()/defer() - Field selection
   - QuerySet indexing
   - Database indexes

2. **Caching Strategy**
   - Redis caching (query results, API responses)
   - Cache invalidation (time-based, event-based)
   - Cache warming (scheduled tasks)
   - Pickle cache for analytics

3. **Connection Pooling**
   ```python
   DATABASES = {
       'default': {
           'CONN_MAX_AGE': 600,  # 10 minutes
       }
   }
   ```

4. **API Optimization**
   - Pagination (cursor-based, page-based)
   - Field selection (GraphQL-like)
   - Response compression
   - Rate limiting

5. **Background Processing**
   - Offload heavy tasks to Celery/Dramatiq
   - Async processing
   - Batch processing

### Scalability Strategy:

**Horizontal Scaling:**
- Stateless application design
- Load balancer ready
- Session storage in Redis
- Shared nothing architecture

**Vertical Scaling:**
- Database indexing
- Query optimization
- Connection pooling
- Caching

**Caching Layers:**
```
Browser Cache (1 min)
    ↓ Miss
CDN Cache (CloudFront) (5 min)
    ↓ Miss
Application Cache (Redis) (15 min)
    ↓ Miss
Database Query Cache (MySQL) (1 hour)
    ↓ Miss
Database (PostgreSQL)
```

---

## 🔧 TECHNOLOGY DECISIONS

### Why These Technologies?

**Frontend:**
1. **Next.js 14**
   - ✅ Server-side rendering (SEO)
   - ✅ API routes
   - ✅ File-based routing
   - ✅ Automatic code splitting
   - ✅ Built-in optimizations

2. **TypeScript**
   - ✅ Type safety
   - ✅ Better IDE support
   - ✅ Catch bugs early
   - ✅ Self-documenting code

3. **shadcn/ui**
   - ✅ Accessible (Radix UI)
   - ✅ Customizable (Tailwind)
   - ✅ Copy-paste components (no npm install)
   - ✅ Modern design

4. **Zustand**
   - ✅ Lightweight
   - ✅ Easy to learn
   - ✅ No boilerplate
   - ✅ TypeScript-first

**Backend:**
1. **Django**
   - ✅ Batteries included
   - ✅ Mature ecosystem
   - ✅ Security features
   - ✅ Admin interface

2. **Django Ninja**
   - ✅ Fast (comparable to FastAPI)
   - ✅ Automatic API docs
   - ✅ Pydantic validation
   - ✅ Django ORM integration

3. **Django Channels**
   - ✅ Native WebSocket support
   - ✅ ASGI compliant
   - ✅ Redis channel layer
   - ✅ Scalable

4. **Celery + Dramatiq**
   - ✅ Celery: Long-running tasks
   - ✅ Dramatiq: Real-time tasks
   - ✅ Both support RabbitMQ
   - ✅ Mature ecosystem

**Infrastructure:**
1. **Docker**
   - ✅ Consistent environments
   - ✅ Easy deployment
   - ✅ Resource isolation
   - ✅ Microservices ready

2. **MySQL vs PostgreSQL**
   - ✅ Chose MySQL for maturity
   - ✅ Full-text search
   - ✅ JSON support
   - ✅ Easier scaling (read replicas)

3. **Redis**
   - ✅ Fast in-memory cache
   - ✅ Channel layer for WebSocket
   - ✅ Result backend for tasks
   - ✅ Session storage

---

## 📊 MONITORING & OBSERVABILITY

### Logging Strategy:

**Structured Logging (JSON):**
```python
# utils/helpers/logger/logger.py
import structlog

logger = structlog.get_logger()
logger.info("user_logged_in", user_id=user.id, ip=request.META['REMOTE_ADDR'])
```

**Log Levels:**
- DEBUG - Development debugging
- INFO - General information
- WARNING - Warnings (non-critical)
- ERROR - Errors (exceptions)
- CRITICAL - Critical failures

**Log Destinations:**
- Development: Console + File
- Production: CloudWatch Logs

### Monitoring Stack:

**Application Monitoring:**
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards
- **Sentry** - Error tracking

**Key Metrics:**
- API response times (P50, P95, P99)
- Database query times
- Error rates
- Task queue lengths
- WebSocket connections
- Cache hit rates
- CPU/memory usage

**Health Checks:**
```python
@api.get("/health")
def health_check(request):
    return {
        "status": "healthy",
        "database": check_database(),
        "redis": check_redis(),
        "rabbitmq": check_rabbitmq(),
    }
```

---

## 🎯 ARCHITECTURAL PRINCIPLES

### Design Principles:

1. **Domain-Driven Design (DDD)**
   - Clear domain boundaries
   - Ubiquitous language
   - Bounded contexts
   - Aggregate roots

2. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

3. **DRY (Don't Repeat Yourself)**
   - Reusable components
   - Shared utilities
   - Base classes
   - Mixins

4. **KISS (Keep It Simple, Stupid)**
   - Simple solutions
   - Avoid over-engineering
   - Clear code
   - Minimal dependencies

5. **Separation of Concerns**
   - Frontend vs Backend
   - API vs Business Logic
   - Services vs Models
   - Presentation vs Domain

### Patterns Used:

1. **Repository Pattern**
   - Data access abstraction
   - Query builders
   - Custom managers

2. **Service Layer Pattern**
   - Business logic
   - Orchestration
   - Transaction management

3. **Factory Pattern**
   - Object creation
   - Pipeline factories
   - Provider factories

4. **Strategy Pattern**
   - Provider selection
   - Algorithm selection
   - Validation strategies

5. **Observer Pattern**
   - WebSocket updates
   - Event broadcasting
   - Pub/Sub (Redis)

---

## 🚀 FUTURE ARCHITECTURE ENHANCEMENTS

### Planned Improvements:

1. **Microservices Migration**
   - Split user service
   - Split market data service
   - Split portfolio service
   - API Gateway (Kong/AWS API Gateway)

2. **Event-Driven Architecture**
   - Event bus (Kafka/RabbitMQ)
   - Event sourcing
   - CQRS (Command Query Responsibility Segregation)

3. **Advanced Caching**
   - CDN caching (CloudFront)
   - Edge computing (Cloudflare Workers)
   - Distributed caching (Redis Cluster)

4. **Database Improvements**
   - Read replicas
   - Database sharding
   - Connection pooling (PgBouncer)
   - Query optimization

5. **Real-time Enhancements**
   - GraphQL subscriptions
   - Server-Sent Events (SSE)
   - WebRTC for P2P data

6. **AI/ML Infrastructure**
   - ML model serving (TorchServe, TensorFlow Serving)
   - Feature store
   - Model monitoring
   - A/B testing framework

---

## 📚 ARCHITECTURE DOCUMENTATION

### Key Documents:

- **DATA_PIPELINE_SUMMARY.md** - Data processing architecture
- **DEPLOYMENT.md** - CI/CD pipeline
- **BACKEND_TASKS.md** - Background tasks
- **TASKS.md** - Development tasks
- **FEATURES_SPECIFICATION.md** - Feature specs
- **IMPLEMENTATION_ROADMAP.md** - Roadmap

### Code Locations:

**Frontend:** `/Frontend/src/`
- App Router: `app/`
- Components: `components/`
- Stores: `stores/`
- Hooks: `hooks/`

**Backend:** `/Backend/src/`
- API: `api/`
- Models: `<domain>/models/`
- Tasks: `tasks/`
- Data: `data/`

---

**End of Architecture Documentation**

**Architect:** GAUDí
**Version:** 2.0
**Status:** Production-Ready
**Last Updated:** January 30, 2026

---

## 🎓 KEY TAKEAWAYS

1. **Monolith with Microservices-Ready Design**
   - Clear domain boundaries
   - Easy to extract services
   - Shared database (for now)

2. **Event-Driven Background Processing**
   - Celery for heavy tasks
   - Dramatiq for real-time
   - WebSocket for live updates

3. **Scalable Architecture**
   - Stateless app servers
   - Load balancer ready
   - Database read replicas (planned)

4. **Modern Frontend Stack**
   - Next.js 14 (App Router)
   - TypeScript (strict mode)
   - Zustand (state management)
   - shadcn/ui (components)

5. **Production-Ready**
   - Docker containerization
   - CI/CD pipeline
   - Monitoring (Prometheus/Grafana)
   - Error tracking (Sentry)

---

**Next Steps for Architect:**
1. Review performance metrics
2. Identify bottlenecks
3. Plan microservices extraction
4. Design event-driven architecture
5. Implement advanced caching strategy
