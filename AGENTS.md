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

**Component Best Practices:**
- Always add loading states (use skeletons during data fetch)
- Implement proper error boundaries
- Add optimistic UI updates where appropriate
- Use memoization for expensive calculations (React.memo, useMemo)
- Use callback memoization for event handlers (useCallback)
- Test component in isolation with Storybook-like approach
- Follow DRY principle - extract reusable logic to custom hooks

**Chart Components:**
- Use Recharts for data visualization (not Chart.js - reserved for real-time)
- Use Chart.js only for real-time streaming charts
- Define proper TypeScript interfaces for chart data
- Handle empty states gracefully
- Add tooltips and legends for better UX
- Ensure charts are responsive (ResponsiveContainer from Recharts)
- Use consistent color schemes (define in constants or theme)

**State Management Patterns:**
- Zustand for global application state
- React Context for auth/user state (persists across app)
- Local useState for component-specific UI state
- Server state from API (don't store in Zustand unless needed globally)
- Use immer middleware for complex state updates in Zustand
- Persist important state to localStorage when needed

**Performance:**
- Use Next.js dynamic imports for heavy components: `import('...')`
- Implement code splitting with route groups
- Use Image component from next/image for images
- Lazy load charts and heavy components
- Debounce API calls and search inputs (use lodash debounce)
- Throttle scroll events and resize handlers
- Use React.memo for expensive renders
- Virtualize long lists (react-window or similar)

**Accessibility:**
- Add semantic HTML (use proper HTML5 elements)
- Add ARIA labels for all interactive elements
- Ensure keyboard navigation works (tab, enter, escape)
- Use focus management in modals and dialogs
- Add alt text for all images
- Ensure color contrast meets WCAG AA standards
- Test with screen reader (story)
- Use proper heading hierarchy (h1, h2, etc.)

**Form Handling:**
- Use react-hook-form with Zod validation
- Define form schemas with proper TypeScript types
- Handle form validation errors gracefully
- Show validation messages inline
- Implement form submission states (loading, success, error)
- Reset forms after successful submission
- Use proper input types (email, number, etc.)

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

### Area 4: Testing ✅ COMPLETED

### Summary
- Created comprehensive frontend page tests for Analytics, Sentiment, Alerts
- Created component tests for all real-time components
- All tests use React Testing Library and Jest
- Proper mocking of stores and API clients

### Files Created (Frontend)
```
Frontend/src/tests/
├── pages/
│   ├── anletics.test.tsx (created)
│   ├── sentiment.test.tsx (created)
│   └── alerts.test.tsx (created)
└── components/
    └── realtime/
        ├── ConnectionStatus.test.tsx (created)
        ├── LivePriceTicker.test.tsx (created)
        ├── RealTimeChart.test.tsx (created)
        ├── OrderBook.test.tsx (created)
        └── TradeFeed.test.tsx (created)
```

### Test Coverage

#### 1. Page Tests (`tests/pages/`)
**analytics.test.tsx:**
- Renders page title and description
- Renders period selector (1d, 7d, 30d, 90d, 1y)
- Tests API calls on mount
- Tests period change interactions
- Tests loading states
- Tests data display (return, value, risk metrics)
- Tests export to JSON functionality

**sentiment.test.tsx:**
- Renders page title and description
- Renders symbol search form
- Tests symbol uppercase conversion
- Tests day filter changes
- Tests sentiment data display
- Tests API calls with filters
- Tests error handling
- Tests loading states

**alerts.test.tsx:**
- Renders page title and description
- Fetches alerts and stats on mount
- Tests statistics cards display
- Tests alert list with search and filter
- Tests filter changes
- Tests create alert dialog
- Tests alert form submission
- Tests delete, enable/disable, test, view history
- Tests alert history dialog

#### 2. Component Tests (`tests/components/realtime/`)
**ConnectionStatus.test.tsx:**
- Tests all connection states (connected, connecting, disconnected, error)
- Tests reconnect button visibility
- Tests reconnect functionality
- Tests ping time display

**LivePriceTicker.test.tsx:**
- Tests empty state when no prices
- Tests price display for multiple symbols
- Tests price change indicators
- Tests max symbol limit (10)
- Tests hover:pause functionality

**RealTimeChart.test.tsx:**
- Tests chart rendering
- Tests default timeframe
- Tests all timeframe options
- Tests timeframe changes
- Tests subscription to symbol on mount

**OrderBook.test.tsx:**
- Tests depth chart and bid/ask ladder tabs
- Tests bids and asks display
- Tests depth selector (10, 20, 50, 100)
- Tests subscription to orderbook on mount

**TradeFeed.test.tsx:**
- Tests empty state when no trades
- Tests trade display
- Tests trade time display
- Tests side filtering (All/Buys/Sells)
- Tests trade limit configuration
- Tests subscription to trades on mount

---

## Project Status Summary

### Completed Areas
1. ✅ Area 1: Frontend Real-Time Components (8 commits)
2. ✅ Area 2: WebSocket Backend Implementation (7 commits)
3. ✅ Area 3: Missing Frontend Pages (6 commits)
4. ✅ Area 4: Testing (6 commits)

**Total: 27 commits across all areas**

### Total Commits in This Session: 27
- 8 commits for Area 1 (Frontend Real-Time)
- 7 commits for Area 2 (WebSocket Backend)
- 6 commits for Area 3 (Missing Frontend Pages)
- 6 commits for Area 4 (Testing)

All changes pushed to GitHub: https://github.com/Fuuurma/FinanceHub-Backend.git

---

## Area 3: Missing Frontend Pages ✅ COMPLETED

### Summary
- Created API clients for alerts and news-sentiment
- Created type definitions for alerts and news-sentiment
- Fixed typo in portfolio-analytics filename (portfolio-analyics → portfolio-analytics)
- Created 3 new frontend pages: Analytics, Sentiment, Alerts

### Files Created (Frontend)
```
Frontend/src/
├── lib/
│   ├── api/
│   │   ├── alerts.ts (created)
│   │   ├── news-sentiment.ts (created)
│   │   └── index.ts (updated - added exports)
│   └── types/
│       ├── alerts.ts (created)
│       ├── news-sentiment.ts (created)
│       ├── portfolio-analytics.ts (renamed from portfolio-analyics.ts)
│       └── index.ts (updated - added exports)
└── app/(dashboard)/
    ├── analytics/page.tsx (created)
    ├── sentiment/page.tsx (created)
    └── alerts/page.tsx (created)
```

### Features Implemented

#### 1. Alerts API Client (`lib/api/alerts.ts`)
- **list**: Get user's alerts with filters (status, symbol, alert_type, limit, offset)
- **get**: Get single alert by ID
- **create**: Create new alert (name, alert_type, symbol, condition_value, condition_operator, delivery_channels, priority, cooldown_seconds, valid_until, description)
- **update**: Update existing alert
- **delete**: Delete alert
- **enable/disable**: Enable/disable alert
- **getHistory**: Get alert trigger history
- **getStats**: Get alert statistics (total_alerts, active_alerts, triggered_today, type_distribution)
- **test**: Test alert trigger without saving

#### 2. News Sentiment API Client (`lib/api/news-sentiment.ts`)
- **getSentiment**: Get sentiment for symbol (with days and min_relevance params)
- **getMarketTrends**: Get market-wide trends (hot topics, trending symbols, sentiment distribution)
- **getBatchSentiment**: Get sentiment for multiple symbols
- **getTrendingTopics**: Get trending news topics
- **getNewsWithSentiment**: Get news articles with sentiment (with optional sentiment filter)
- **getSentimentHistory**: Get sentiment history for symbol (hourly/daily intervals)

#### 3. Type Definitions

**Alerts Types (`lib/types/alerts.ts`):**
- `Alert`: Alert data (id, name, alert_type, symbol, condition_value, condition_operator, status, priority, triggered_count, delivery_channels, cooldown_seconds, valid_from, valid_until, created_at, last_triggered_at)
- `AlertHistoryItem`: Alert history (id, triggered_at, trigger_value, condition_met, notification_sent, notification_channels)
- `AlertStats`: Alert statistics (total_alerts, active_alerts, triggered_today, type_distribution)
- `AlertCreateInput`: Input for creating alerts
- `AlertUpdateInput`: Input for updating alerts

**News Sentiment Types (`lib/types/news-sentiment.ts`):**
- `NewsArticle`: Article data (id, title, description, source, author, published_at, url, image_url, symbols, sentiment_score, sentiment_label, relevance_score)
- `SentimentAnalysis`: Sentiment data (symbol, overall_sentiment, sentiment_score, article_count, positive_count, negative_count, neutral_count, average_sentiment_7d, articles, sentiment_trend, key_topics, analyzed_at)
- `MarketTrends`: Market trends (time_period, hot_topics, trending_symbols, sentiment_distribution, most_mentioned, fetched_at)
- `SentimentHistory`: Sentiment history (symbol, history, analyzed_at)
- `TrendingTopic`: Trending topic (topic, sentiment_score, article_count, related_symbols)

#### 4. Analytics Page (`app/(dashboard)/analytics/page.tsx`)
- Period selector (1d, 7d, 30d, 90d, 1y)
- Total return card with profit/loss indicator
- Total value card with change percentage
- Performance by asset breakdown with pie chart icons
- Risk metrics card (volatility, beta, sharpe ratio)
- Period summary card (start/end dates, transactions)
- Refresh and Export to JSON buttons
- Loading skeletons while fetching data

#### 5. Sentiment Page (`app/(dashboard)/sentiment/page.tsx`)
- Symbol search form with uppercase conversion
- Day filter selector (1, 7, 14, 30 days)
- Sentiment overview card:
  - Overall sentiment badge (Positive/Negative/Neutral)
  - Sentiment score display
  - Article count
  - Positive/negative/neutral breakdown
  - Key topics tags
- Sentiment trend visualization (7-day movement)
- Recent news list:
  - Title, source, publication date
  - Sentiment badge
  - Read more link to original source
- Loading and error states

#### 6. Alerts Page (`app/(dashboard)/alerts/page.tsx`)
- Statistics cards row (total_alerts, active_alerts, triggered_today, success rate)
- Tab-based layout (Alert List / Create New)
- Alert list with:
  - Search by name or symbol
  - Filter by status (all, active, disabled, triggered, expired)
  - Alert cards showing name, symbol, type, trigger condition, triggered count, created date
  - Enable/disable toggle (based on status)
  - View history button
  - Test alert button
  - Delete alert button
  - Status badges
- Create alert dialog with form fields:
  - Alert name
  - Symbol (uppercase input)
  - Alert type (price above/below, percent change, volume spike)
  - Trigger value
  - Operator (>=, <=, ==)
  - Priority (1-10)
  - Cooldown seconds
- Alert history dialog:
  - List of trigger events
  - Condition met badge
  - Notification sent indicator
- Loading skeletons for list view
- Create New tab reuses create dialog

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

---

## Backend Patterns & Best Practices (2026)

### Constants File Structure

Use centralized constants to avoid magic numbers scattered across the codebase:

```python
# Backend/src/utils/constants/api.py
"""
API Constants
Centralized configuration for API limits, timeouts, and pagination.
"""

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
DEFAULT_OFFSET = 0

# Limits
ALERT_COOLDOWN_SECONDS = 300
ALERT_LIST_LIMIT = 50
ALERT_HISTORY_LIMIT = 20

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60
CACHE_TTL_MEDIUM = 300
CACHE_TTL_LONG = 3600

# Rate Limits
RATE_LIMIT_ANON = "100/hour"
RATE_LIMIT_AUTH = "1000/hour"

# Error Codes
ERROR_NOT_FOUND = "not_found"
ERROR_VALIDATION = "validation_error"
ERROR_DATABASE = "database_error"
```

Usage in API endpoints:
```python
from utils.constants.api import ALERT_LIST_LIMIT, ALERT_COOLDOWN_SECONDS

@router.get("/", response=List[AlertOut])
async def list_alerts(
    request,
    limit: int = Query(default=ALERT_LIST_LIMIT, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    # ...
```

### N+1 Query Prevention

**Don't do this:**
```python
# N+1 query - queries prices for each holding
@property
def current_price(self):
    latest = self.asset.prices.order_by("-date").first()
    return latest.close if latest else None
```

**Do this instead:**
```python
# Uses cached last_price field (pre-computed for performance)
@property
def current_price(self):
    return self.asset.last_price

# Use select_related when querying holdings
holdings = self.holdings.select_related('asset').filter(is_deleted=False)
```

### Database Transactions

Wrap multi-step operations in transactions for atomicity:

```python
from django.db import transaction

@router.post("/watchlist", response=WatchlistOut, auth=jwt_auth)
@transaction.atomic
def create_watchlist(request, data: WatchlistCreateIn):
    """Create watchlist with atomic transaction."""
    watchlist = Watchlist.objects.create(...)
    if data.symbols:
        assets_map = _get_assets_by_symbol(data.symbols)
        assets_to_add = [assets_map[s.upper()] for s in data.symbols if s.upper() in assets_map]
        if assets_to_add:
            watchlist.assets.add(*assets_to_add)
    return WatchlistOut(...)
```

### Model Indexes

Always add indexes for frequently queried fields:

```python
class Watchlist(UUIDModel, TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "watchlists"  # Explicit table name
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["user", "is_public"]),
        ]
```

### Error Handling Patterns

Use specific error types instead of generic exception handling:

```python
from utils.constants.api import ERROR_NOT_FOUND, ERROR_VALIDATION, ERROR_DATABASE

class AlertErrorResponse(Schema):
    error: str
    code: str = "error"

def handle_database_error(func):
    """Decorator for improved error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Alert.DoesNotExist:
            return AlertErrorResponse(error="Alert not found", code=ERROR_NOT_FOUND)
        except ValueError as e:
            return AlertErrorResponse(error=str(e), code=ERROR_VALIDATION)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return AlertErrorResponse(error="An error occurred", code=ERROR_DATABASE)
    return wrapper
```

### Database Connection Pooling

Configure connection pooling in settings for production:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        },
        "CONN_MAX_AGE": 600,  # Connection reuse (10 minutes)
    }
}
```

### Bulk Operations for N+1 Prevention

**Don't do this (N+1):**
```python
# Queries DB for each symbol
for symbol in data.symbols:
    asset = Asset.objects.filter(symbol__iexact=symbol).first()
    if asset:
        watchlist.assets.add(asset)
```

**Do this (bulk fetch):**
```python
# Single query for all symbols
def _get_assets_by_symbol(symbols: List[str]) -> Dict[str, Asset]:
    if not symbols:
        return {}
    return {
        asset.symbol.upper(): asset
        for asset in Asset.objects.filter(symbol__in=[s.upper() for s in symbols])
    }

# Then use the map
assets_map = _get_assets_by_symbol(data.symbols)
assets_to_add = [assets_map[s.upper()] for s in data.symbols if s.upper() in assets_map]
watchlist.assets.add(*assets_to_add)
```

### Pagination in List Endpoints

Always add pagination to list endpoints:

```python
from utils.constants.api import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, DEFAULT_OFFSET

@router.get("/watchlist", response=List[WatchlistOut], auth=jwt_auth)
def list_watchlists(
    request,
    limit: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(default=DEFAULT_OFFSET, ge=0),
):
    watchlists = Watchlist.objects.filter(user=request.user)[offset:offset + limit]
    return [WatchlistOut(...) for w in watchlists]
```

### CORS Configuration

Enable CORS middleware in settings for frontend integration:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be at top
    ...
]

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
```

### Rate Limiting

Configure rate limiting in settings:

```python
# settings.py
RATELIMIT_ENABLE = True
RATELIMIT_AUTHENTICATED = True
RATELIMIT_AUTHENTICATED_RATE = "1000/hour"
RATELIMIT_ANON_RATE = "100/hour"
RATELIMIT_USE_REDIS = True
RATELIMIT_KEY_PREFIX = "ratelimit"
```

### Security Settings

Never hardcode secrets - use environment variables:

```python
# settings.py - BAD (hardcoded)
SECRET_KEY = "django-insecure-nmwss$g4$o%6e=z(k#8r2p"
DEBUG = True

# settings.py - GOOD (from env)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-this-in-production")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
```

```bash
# .env
DJANGO_SECRET_KEY=your-secure-random-key-here-min-50-chars
DEBUG=False
```

