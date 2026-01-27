# FinanceHub

A comprehensive financial platform for tracking, analyzing, and managing investments across multiple asset classes including stocks, crypto, ETFs, and more.

## Project Structure

```
FinanceHub/
├── Backend/                    # Django REST API backend
│   └── src/
│       ├── assets/            # Asset models and API
│       ├── core/             # Core Django settings and configuration
│       ├── data/             # Data fetching and processing
│       ├── investments/      # Portfolio and transaction management
│       ├── portfolios/       # Portfolio models and API
│       ├── screener/         # Stock screening service
│       ├── search/           # Asset search functionality
│       ├── tasks/            # Celery background tasks
│       ├── users/            # User authentication and management
│       ├── utils/            # Helper utilities
│       └── websockets/       # Real-time WebSocket connections
│
└── Frontend/                 # Next.js frontend
    └── src/
        ├── app/             # Next.js app router pages
        ├── components/      # React components
        ├── contexts/        # React contexts
        ├── hooks/           # Custom React hooks
        ├── stores/          # Zustand state management
        └── types/          # TypeScript type definitions
```

## Backend Architecture

### Core Features
- **Django REST Framework** for API endpoints
- **Celery** for background task processing
- **WebSockets** (Channels) for real-time data
- **Multiple data providers**: Yahoo Finance, Binance, CoinGecko, Alpha Vantage

### Data Pipeline
- Automated data fetching from multiple sources
- Data processing pipeline with technical indicators
- Historical price and metrics storage
- Real-time price updates via WebSockets

### Services
- **Assets API**: Retrieve and manage asset information
- **Portfolios API**: Track portfolio holdings and performance
- **Screener**: Advanced stock screening with multiple filters
- **Search**: Full-text search for assets
- **Watchlist**: Manage asset watchlists
- **Alerts**: Price and indicator alerts

## Frontend Architecture

### Technology Stack
- **Next.js 14** with App Router
- **React 18** with TypeScript
- **Zustand** for state management
- **Tailwind CSS** for styling
- **shadcn/ui** component library

### State Management
- **Market Store**: Real-time market data
- **Screener Store**: Screening criteria and results
- **Watchlist Store**: User watchlists
- **Auth Context**: Authentication state

### Pages
- **Authentication**: Login, Register
- **Market Dashboard**: Overview of market data
- **Market Overview**: Indices, sectors, news
- **Market Indices**: Global indices tracking
- **Market Stocks**: Stock listings and analysis

## Progress

### Completed Features

#### Backend
- ✅ Asset models (stocks, crypto, ETFs, indices)
- ✅ User authentication system
- ✅ Portfolio management
- ✅ Data processing pipeline
- ✅ Celery background tasks
- ✅ WebSocket consumers for real-time data
- ✅ Search service
- ✅ Screener service
- ✅ WebSockets routing

#### Frontend
- ✅ Authentication pages (login, register)
- ✅ Auth context and hooks
- ✅ Market store (Zustand)
- ✅ Screener store (Zustand)
- ✅ Watchlist store (Zustand)
- ✅ Market dashboard page
- ✅ Market overview page
- ✅ Market indices page
- ✅ Market stocks page
- ✅ UI components (shadcn/ui)

### In Progress
- 🔄 API endpoint configuration
- 🔄 WebSocket connection handling
- 🔄 Type definitions

### Upcoming
- ⏳ Portfolio tracking pages
- ⏳ Screener UI
- ⏳ Watchlist management UI
- ⏳ Asset detail pages
- ⏳ Charting components
- ⏳ Trading interface
- ⏳ Settings pages

## Setup

### Backend
```bash
cd Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd Frontend
npm install
npm run dev
```

### Celery Worker
```bash
cd Backend
celery -A src worker -l info
```

### Redis (Required for WebSockets)
```bash
redis-server
```

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

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user

### Assets
- `GET /api/assets/` - List all assets
- `GET /api/assets/{symbol}/` - Get asset details
- `GET /api/assets/{symbol}/price/` - Get current price

### Portfolios
- `GET /api/portfolios/` - List user portfolios
- `POST /api/portfolios/` - Create portfolio
- `GET /api/portfolios/{id}/` - Get portfolio details

### Screener
- `POST /api/screener/run/` - Run stock screener
- `GET /api/screener/presets/{preset}/` - Load preset

### Search
- `GET /api/search/?q={query}` - Search assets

### Watchlist
- `GET /api/watchlist/` - List watchlists
- `POST /api/watchlist/` - Create watchlist
- `DELETE /api/watchlist/{id}/` - Delete watchlist

## WebSocket Channels

### Market Data
- `ws/market/` - Real-time market data

### User Updates
- `ws/user/` - User-specific updates (watchlist, alerts)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License.
