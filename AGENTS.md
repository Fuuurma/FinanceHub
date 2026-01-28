# AGENTS.md - FinanceHub Coding Guidelines

This document provides guidelines for coding agents working on the FinanceHub project, a financial platform with a Django REST backend and Next.js frontend.

---

## Development Commands

### Backend (Python/Django)
```bash
cd Backend/src

# Run development server
python manage.py runserver

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
pytest                           # Run all tests
pytest tests/test_tasks.py      # Run single test file
pytest tests/test_tasks.py -k "test_fetch_stocks_yahoo"  # Run specific test
pytest -v                       # Verbose output
pytest --cov=apps               # Run with coverage

# Run background worker
celery -A src worker -l info

# Django shell
python manage.py shell
```

### Frontend (Next.js/TypeScript)
```bash
cd Frontend/src

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint

# Type checking (check tsconfig.json for setup)
npx tsc --noEmit
```

---

## Code Style Guidelines

### Backend (Python/Django)

**File Structure:**
- Models: `apps/{app_name}/models/` - Separate files for each model type
- API: `apps/{app_name}/api/` - Django Ninja routers
- Views/Controllers: Use Django Ninja routers (not traditional views)
- Services: `apps/{app_name}/services/` or `utils/services/` - Business logic

**Naming Conventions:**
- Classes: PascalCase (e.g., `Asset`, `User`, `UserProfile`)
- Functions/Variables: snake_case (e.g., `get_market_data`, `user_id`)
- Constants: UPPER_SNAKE_CASE (e.g., `POPULAR_STOCKS`, `MAX_RETRIES`)
- Private methods: Leading underscore (e.g., `_validate_user`)

**Imports:**
- Standard library first, then third-party, then local
- Use absolute imports from project root (e.g., `from assets.models.asset import Asset`)
- Group imports with blank lines between groups

**Model Guidelines:**
- Inherit from `UUIDModel`, `TimestampedModel`, `SoftDeleteModel` when appropriate
- Use `db_index=True` for frequently queried fields
- Add `Meta` class with `db_table`, `ordering`, and `indexes`
- Add `help_text` for all fields
- Use `ForeignKey` with `on_delete=models.PROTECT` or `SET_NULL` appropriately
- Use `models.JSONField` with `default=dict, blank=True` for flexible data

**API Guidelines:**
- Use Django Ninja Schema classes for request/response validation
- Create separate Schema classes for input (In) and output (Out)
- Use `get_object_or_404` for single object queries
- Return descriptive error messages
- Add docstrings to router functions

**Error Handling:**
- Use Django's built-in exception handling
- Validate input using Schema classes
- Return meaningful error messages in API responses
- Log errors using configured logger

**Testing:**
- Use pytest with Django TestCase
- Use `@patch` decorator for mocking
- Name test methods descriptively (e.g., `test_fetch_stocks_yahoo_success`)
- Use setUp method for common test data
- Test both success and failure cases

---

### Frontend (TypeScript/React)

**File Structure:**
- Pages: `app/` - Next.js App Router with route groups `(dashboard)`, `(auth)`
- Components: `components/ui/` - shadcn/ui components, `components/layout/` - layout components
- Hooks: `hooks/` - Custom React hooks (prefixed with `use`)
- Stores: `stores/` - Zustand state management
- Types: `types/` - TypeScript type definitions
- Utils: `lib/utils.ts` - Utility functions (e.g., `cn()` for className merging)
- API: `lib/api/` - API client and endpoint functions

**Naming Conventions:**
- Components: PascalCase (e.g., `Navbar`, `Button`, `MarketDashboard`)
- Functions/Variables: camelCase (e.g., `fetchMarketData`, `isLoading`)
- Types/Interfaces: PascalCase (e.g., `MarketData`, `User`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- Files: kebab-case for components (e.g., `market-dashboard.tsx`), camelCase for utilities

**Imports:**
- Use path aliases: `@/` for project root
- Group imports: third-party first, then local
- Separate named and default imports with new line
- Example:
  ```typescript
  import { useState } from 'react'
  import { useRouter } from 'next/navigation'
  import { Button } from '@/components/ui/button'
  import { cn } from '@/lib/utils'
  ```

**Component Guidelines:**
- Use 'use client' directive for client components with hooks/interactivity
- Use TypeScript strictly (no `any` types)
- Use function components with hooks (no class components)
- Destructure props in function signature
- Use shadcn/ui components as base
- Use Tailwind CSS for all styling
- Use `cn()` utility for conditional classes

**State Management:**
- Use Zustand for global state (stores in `stores/` directory)
- Create custom hooks for accessing stores (e.g., `useMarketStore`)
- Use React Context for auth/user state (AuthContext)
- Use local state with `useState` for component-specific state

**API Guidelines:**
- Use centralized `apiClient` from `@/lib/api/client`
- Define API functions in `lib/api/` by feature
- Handle errors with try-catch and set error state
- Use async/await for all API calls
- Show loading states while fetching data

**Type Safety:**
- Define interfaces for all complex data structures
- Use TypeScript's built-in types where possible
- Use generic types properly (e.g., `Promise<T>`)
- Use type assertions sparingly
- Keep types in `types/` directory

**Error Handling:**
- Wrap async operations in try-catch
- Display error messages to users (e.g., with Alert component)
- Set error state in stores/components
- Log errors to console for debugging

**Styling:**
- Use Tailwind CSS utility classes
- Use shadcn/ui components for consistent design
- Use `cn()` utility for merging classes
- Use responsive prefixes (`md:`, `lg:`) for breakpoints
- Use dark mode support (next-themes)

---

## Testing

### Backend Testing
- Run all tests: `pytest` in Backend/src
- Run single test file: `pytest tests/test_tasks.py`
- Run specific test: `pytest tests/test_tasks.py -k "test_fetch_stocks_yahoo"`
- Use `@patch` for mocking external dependencies

### Frontend Testing
- Jest configured for testing (src/jest.config.js)
- Test dependencies added: @testing-library/react, jest, jest-environment-jsdom
- Test scripts: npm run test, npm run test:watch

---

## Area 1: Frontend Real-Time Components ✅ COMPLETED

### Summary
- Created WebSocket infrastructure for real-time data streaming
- Built 5 real-time UI components with Chart.js integration
- Integrated components into existing pages
- Configured Jest testing framework
- All constants centralized in `lib/constants/realtime.ts` (no magic numbers)

### Files Created (Frontend)
```
Frontend/src/
├── .env.example
├── tsconfig.json (updated with downlevelIteration)
├── package.json (added chart.js and testing deps)
├── jest.config.js
├── jest.setup.js
├── lib/
│   ├── constants/
│   │   └── realtime.ts
│   ├── types/
│   │   ├── realtime.ts
│   │   └── index.ts (updated)
│   └── api/
│       ├── websocket.ts
│       └── client.ts
│   └── utils/
│       └── cn.ts (added)
└── stores/
    └── realtimeStore.ts
├── components/realtime/
    ├── ConnectionStatus.tsx
    ├── LivePriceTicker.tsx
    ├── RealTimeChart.tsx
    ├── OrderBook.tsx
    ├── TradeFeed.tsx
    └── __tests__/
        ├── jest.config.js
        └── jest.setup.js
```

### Components Integrated
- `app/(dashboard)/market/dashboard/page.tsx` - Added ConnectionStatus, LivePriceTicker, connect button
- `app/(dashboard)/assets/[assetId]/page.tsx` - Replaced TradingView with RealTimeChart, added OrderBook/TradeFeed

### Features Implemented
1. **WebSocket Client** (`lib/api/websocket.ts`)
   - Auto-reconnection with exponential backoff using `WS_CONFIG.RECONNECT_DELAYS`
   - Heartbeat/ping-pong mechanism using `WS_CONFIG.HEARTBEAT_INTERVAL`
   - Connection timeout using `WS_CONFIG.CONNECT_TIMEOUT`
   - Event emitter pattern for data updates
   - Subscription/unsubscription methods
   - `getWebSocketClient()` singleton, `resetWebSocketClient()`

2. **Real-Time Store** (`stores/realtimeStore.ts`)
   - Zustand store with connectionState, prices, trades, orderBooks, charts
   - connect/disconnect, subscribe/unsubscribe methods
   - updatePrice, addTrade, updateOrderBook actions
   - Trades limited to `WS_CONFIG.TRADE_FEED_LIMIT` (20)

3. **ConnectionStatus Component**
   - Visual dot (green=connected, yellow=connecting, red=disconnected/error) from realtimeStore.connectionState
   - State text from `CONNECTION_MESSAGES` constant
   - Reconnect button when DISCONNECTED or ERROR
   - Ping display using `getWebSocketClient().getPingMs()`

4. **LivePriceTicker Component**
   - Horizontal marquee (speed: `TICKER_CONFIG.SCROLL_SPEED`)
   - Display prices from realtimeStore.prices
   - Green/red flash on price change (duration: `TICKER_CONFIG.FLASH_DURATION`)
   - Pause on hover (`TICKER_CONFIG.PAUSE_ON_HOVER`)
   - Max symbols: `TICKER_CONFIG.MAX_SYMBOLS`

5. **RealTimeChart Component**
   - Uses Chart.js with react-chartjs-2
   - Props: symbol, timeframe (default: `CHART_CONFIG.DEFAULT_TIMEFRAME`)
   - Buffer size: `CHART_CONFIG.BUFFER_SIZES[timeframe]`
   - Update interval: `CHART_CONFIG.UPDATE_INTERVAL` (2000ms)
   - Timeframe selector: 1m, 5m, 15m, 1h, 4h, 1d, 1w
   - Line chart for price, bar chart for volume
   - Crosshair tooltip, responsive

6. **OrderBook Component**
   - Props: symbol, depth (default: `ORDERBOOK_CONFIG.DEFAULT_DEPTH`)
   - Tabs: "Depth Chart" | "Bid/Ask Ladder"
   - Depth Chart: Stacked bar chart (green bids, red asks)
   - Bid/Ask Ladder: Two columns with volume bars
   - Depth selector: `ORDERBOOK_CONFIG.DEPTH_OPTIONS` [10,20,50,100]
   - Update debounce: `ORDERBOOK_CONFIG.UPDATE_DEBOUNCE_MS`

7. **TradeFeed Component**
   - Props: symbol, limit (default: `WS_CONFIG.TRADE_FEED_LIMIT`)
   - Display realtimeStore.trades[symbol]
   - Columns: Time, Price, Size, Side (green buy, red sell)
   - Auto-scroll, size bar, filter: All/Buys/Sells

### Next: Area 2 - WebSocket Backend Implementation

### Completed

#### Step 1: Configure Channels in `settings.py` ✅
- Added `channels` to INSTALLED_APPS
- Set `ASGI_APPLICATION = 'core.asgi.application'`
- Configured `CHANNEL_LAYERS` with Redis backend:
  - Redis cache on `127.0.0.1:6379/1`
  - Default `LOCATION`, `OPTIONS`, `CLIENT_CLASS`
- Added `CHANNELS_WS_PROTOCOLS` for websocket support

#### Step 2: Update `core/asgi.py` ✅
- Imported ProtocolTypeRouter and URLRouter from channels.routing
- Imported AuthMiddlewareStack from channels.auth
- Imported websocket_urlpatterns from websocket_consumers.routing
- Created ProtocolTypeRouter combining WebSocket + HTTP routing
- Configured with AuthMiddlewareStack for JWT authentication
- Added allowed hosts from environment variable for CORS support

#### Step 3: WebSocket Monitoring ✅
- Created `utils/services/websocket_monitoring.py`
  - **WebSocketConnectionMetrics class**: Tracks connection metrics
    - Methods: `record_connection()`, `record_disconnection()`, `update_activity()`, `add_subscription()`, `get_metrics_summary()`, `get_connection_details()`
  - Metrics tracked per connection: connected_at, disconnected_at, subscriptions, errors
  - Subscription stats per data type: total subscriptions
  - Singleton pattern with `get_websocket_metrics()`
  - Cleanup: `cleanup_old_records()` for records older than 24 hours
  - Activity logging: connected, disconnected, subscription changes

#### Step 4: WebSocket Consumer Updates ✅
- Updated `websocket_consumers/realtime_data_consumer.py`:
  - Imported `get_websocket_metrics` from utils.services.websocket_monitoring
  - Added missing imports for get_data_orchestrator and get_cache_manager
  - Fixed disconnect method parameter name (code instead of close_code)
  - Updated `connect()` to call `metrics.record_connection(self.user_id)`
  - Updated `disconnect()` to call `metrics.record_disconnection(self.user_id)`
  - Updated `_register_connection()` to add metrics info to cache with 1-hour TTL
  - Added activity tracking via `metrics.update_activity()`
  - Enhanced error logging with metrics context
  - Updated `_update_connections_cache()` to track subscriptions in cache for monitoring

#### Step 5: Connection Pooling with Daphne ✅
- Created `Backend/src/daphne_config.py`:
  - NUM_WORKERS, THREADS_PER_WORKER, PORT configurable via environment
  - WEBSOCKET_CONCURRENCY limits for production
  - Redis connection config
  - WebSocket timeout and ping settings
  - Environment variable driven configuration
- Created `Backend/Procfile`:
  - web: daphne server on port 8000 with 600s timeout
  - worker: celery background tasks

#### Step 6: Health Check Endpoints ✅
- Created `Backend/src/api/health.py`:
  - GET /health/websockets - Overall health metrics summary
  - GET /health/websockets/connections - All active connections
  - GET /health/websockets/connections/{user_id} - User-specific connections
  - GET /health/websockets/cleanup - Clean up old records
- Registered health router in `core/api.py` as /health

#### Step 7: WebSocket Integration Tests ✅
- Created `Backend/src/tests/test_websocket_consumer.py`:
  - test_connect_success - Test basic connection
  - test_connect_with_user_id - Test connection with user context
  - test_subscribe_to_price - Test price subscription
  - test_subscribe_to_multiple_data_types - Test multiple subscriptions
  - test_unsubscribe - Test unsubscription
  - test_ping_pong - Test heartbeat mechanism
  - test_unknown_message_type - Test error handling
  - test_disconnect - Test disconnection with cleanup
  - test_case_insensitive_symbols - Test symbol normalization
  - test_invalid_subscribe_message - Test malformed messages
  - test_concurrent_subscriptions - Test concurrent requests
  - All tests use channels.testing WebsocketCommunicator
  - Mocks orchestrator, cache_manager, and metrics for isolation

### Backend Configuration Files Modified (7 commits for Area 2)
1. **Backend/src/core/settings.py**
   - Added `channels` to INSTALLED_APPS
   - Added `ASGI_APPLICATION = 'core.asgi.application'`
   - Added `CHANNEL_LAYERS` with Redis configuration
   - Added `CHANNELS_WS_PROTOCOLS = ['websocket', 'wss']`

2. **Backend/src/core/asgi.py**
   - Imported ProtocolTypeRouter and URLRouter from channels.routing
   - Imported AuthMiddlewareStack from channels.auth
   - Imported websocket_urlpatterns from websocket_consumers.routing
   - Created application = ProtocolTypeRouter({
       'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
       'http': django_asgi_app,
     })
   - Configured with AllowedHostsOriginValidator(allowed_hosts)

3. **Backend/src/utils/services/websocket_monitoring.py**
   - Created WebSocketConnectionMetrics singleton class
   - Methods: record_connection, record_disconnection, update_activity, add_subscription, remove_subscription, get_metrics_summary, get_connection_info, get_all_connections, cleanup_old_records
   - Thread-safe singleton pattern with get_websocket_metrics()

4. **Backend/src/websocket_consumers/realtime_data_consumer.py**
   - Fixed import path from websocket_consumers.websocket_monitoring to utils.services.websocket_monitoring
   - Added missing imports for get_data_orchestrator and get_cache_manager
   - Fixed disconnect method parameter name (code instead of close_code)
   - Integrated metrics tracking in connect/disconnect handlers
   - Added activity logging
   - Enhanced cache integration with 1-hour TTL

5. **Backend/src/daphne_config.py**
   - Daphne ASGI server configuration for production
   - Worker and thread settings
   - WebSocket concurrency limits
   - Redis connection configuration
   - WebSocket timeout and heartbeat settings

6. **Backend/Procfile**
   - Web process: daphne server
   - Worker process: celery background tasks

7. **Backend/src/api/health.py**
   - WebSocket health check endpoints
   - GET /health/websockets for overall metrics
   - GET /health/websockets/connections for all connections
   - GET /health/websockets/connections/{user_id} for user connections
   - GET /health/websockets/cleanup for cleanup operations

8. **Backend/src/core/api.py**
   - Imported and registered health router as /health

9. **Backend/src/tests/test_websocket_consumer.py**
   - Comprehensive WebSocket consumer tests
   - Tests for connection, subscription, unsubscription, ping-pong, errors
   - Uses channels.testing WebsocketCommunicator
   - All tests are async and use django_db marker

### Frontend Files Modified (from Area 1)
1. **Backend Configuration**:
   - `core/settings.py` - Added channels, CHANNEL_LAYERS, CHANNELS_WS_PROTOCOLS

2. **ASGI Layer**:
   - `core/asgi.py` - Updated for WebSocket + HTTP dual routing

3. **WebSocket Monitoring**:
   - `utils/services/websocket_monitoring.py` - Created monitoring utilities
   - `websocket_consumers/realtime_data_consumer.py` - Updated consumer with metrics

4. **Production Deployment**:
   - `daphne_config.py` - Daphne server configuration
   - `Procfile` - Deployment process definitions

5. **Health Monitoring**:
   - `api/health.py` - WebSocket health endpoints
   - `core/api.py` - Health router registration

6. **Testing**:
   - `tests/test_websocket_consumer.py` - WebSocket integration tests

### Next: Area 3 - Missing Frontend Pages

- Create `app/(dashboard)/analytics/page.tsx` - Portfolio analytics dashboard
- Create `app/(dashboard)/sentiment/page.tsx` - News sentiment page  
- Create `app/(dashboard)/alerts/page.tsx` - Alert management UI
- Create `lib/api/alerts.ts` - Alerts API client
- Create `lib/api/news-sentiment.ts` - News sentiment API client

---

## Common Patterns

### API Request (Frontend)
```typescript
import { apiClient } from '@/lib/api/client'

const fetchData = async () => {
  try {
    const data = await apiClient.get<DataType>('/endpoint')
    setData(data)
  } catch (error) {
    setError(error instanceof Error ? error.message : 'Failed to fetch')
  }
}
```

### Model Creation (Backend)
```python
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

class Asset(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=200)
    # Add Meta class with indexes
```

### Component with State (Frontend)
```typescript
'use client'
import { useState } from 'react'

export default function Component() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Component logic
}
```

---

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/financehub
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```
