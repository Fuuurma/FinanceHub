# 📋 CODER TASK ASSIGNMENTS - WEEK OF JAN 31

**Date:** January 31, 2026
**Status:** ✅ ACTIVE
**Assigned by:** GAUDÍ
**Coordinated by:** Karen (DevOps)

---

## 👥 CODER ROSTER

### Backend Coders
- **Linus** - Django models, services, REST APIs
- **Guido** - Celery tasks, data pipelines, external integrations

### Frontend Coder
- **Turing** - React components, Next.js, UI/UX, state management

---

## 🎯 PRIORITY TASK MATRIX

### 🔴 CRITICAL (P0) - Start Immediately

#### C-015: Position Size Calculator ✅
**Assigned to:** Guido
**Status:** ✅ COMPLETE (awaiting review)
**Estimated:** 8-12 hours
**Deadline:** Feb 1, 5:00 PM

**What's Done:**
- ✅ Risk management service created
- ✅ Position size calculator implemented
- ✅ Risk/reward ratio analysis
- ✅ Portfolio risk score
- ✅ API endpoints documented
- ✅ Frontend component specs
- ✅ Test cases defined

**Next:** Review, test, commit PR

---

#### C-022: Strategy Backtesting Engine
**Assigned to:** Linus
**Status:** 🔄 IN PROGRESS
**Estimated:** 18-24 hours
**Deadline:** Feb 3, 5:00 PM

**Enhanced Guide:**
- ✅ BaseStrategy abstract interface
- ✅ Preset strategies (SMA crossover, RSI mean reversion)
- ✅ Backtesting engine architecture
- ✅ Performance metrics (Sharpe, Sortino, max drawdown)
- ✅ 5 common mistakes, 7 FAQ
- ✅ Complete working code

**Files to Create:**
- `apps/backend/src/backtesting/base.py` - BaseStrategy abstract class
- `apps/backend/src/backtesting/strategies.py` - Preset strategies
- `apps/backend/src/backtesting/engine.py` - Backtesting engine
- `apps/backend/src/backtesting/metrics.py` - Performance calculations
- `apps/backend/src/api/backtesting.py` - REST API endpoints
- `apps/backend/src/tests/test_backtesting.py` - Test suite

**Deliverables:**
- [ ] BaseStrategy abstract class with `generate_signals()` method
- [ ] SMA crossover strategy implementation
- [ ] RSI mean reversion strategy implementation
- [ ] Backtesting engine with historical data
- [ ] Performance metrics calculation
- [ ] 3 REST API endpoints
- [ ] Test coverage > 80%

---

#### C-036: Paper Trading System
**Assigned to:** Guido
**Status:** ⏳ PENDING (after C-015)
**Estimated:** 16-20 hours
**Deadline:** Feb 5, 5:00 PM

**Enhanced Guide:**
- ✅ Complete database models
- ✅ Trading service implementation
- ✅ 6 REST API endpoints
- ✅ Portfolio tracking
- ✅ Performance tracking
- ✅ Slippage simulation
- ✅ 5 common mistakes, 7 FAQ

**Files to Create:**
- `apps/backend/src/models/paper_trading.py` - Database models
- `apps/backend/src/services/paper_trading.py` - Trading logic
- `apps/backend/src/api/paper_trading.py` - REST API
- `apps/backend/src/tests/test_paper_trading.py` - Tests

**Deliverables:**
- [ ] PaperTradingAccount model (cash, portfolio_value, total_return)
- [ ] PaperTrade model (symbol, quantity, entry_price, exit_price, etc.)
- [ ] PaperTradingService (buy, sell, get_portfolio, calculate_performance)
- [ ] 6 REST API endpoints
- [ ] Slippage simulation (0.1% default)
- [ ] Test coverage > 80%

---

### 🟡 HIGH PRIORITY (P1)

#### C-016: Customizable Dashboards
**Assigned to:** Turing
**Status:** ⏳ PENDING
**Estimated:** 14-18 hours
**Deadline:** Feb 4, 5:00 PM

**Frontend Focus:**
- Dashboard layout editor
- Widget component system
- Drag-and-drop interface
- User preferences persistence
- Dashboard templates

**Tech Stack:**
- React components
- Next.js App Router
- Zustand for state management
- React Grid Layout for drag-and-drop

**Deliverables:**
- [ ] Dashboard editor component
- [ ] Widget library (portfolio chart, watchlist, news, etc.)
- [ ] Layout persistence API
- [ ] User dashboard model
- [ ] 5+ pre-built templates
- [ ] Responsive design

---

#### C-017: Market Heat Map Visualization
**Assigned to:** Turing
**Status:** ⏳ PENDING (after C-016)
**Estimated:** 10-14 hours
**Deadline:** Feb 6, 5:00 PM

**Frontend Focus:**
- Treemap visualization
- Color gradients (red/green)
- Sector/category grouping
- Interactive tooltips
- Real-time updates

**Tech Stack:**
- D3.js or Recharts
- WebSocket integration
- Sector data API

**Deliverables:**
- [ ] HeatMap component
- [ ] Sector grouping logic
- [ ] Color gradient scales
- [ ] Interactive tooltips
- [ ] Real-time data updates
- [ ] Responsive design

---

#### C-030: Broker API Integration
**Assigned to:** Guido
**Status:** ⏳ PENDING (after C-036)
**Estimated:** 14-18 hours
**Deadline:** Feb 8, 5:00 PM

**Integration Focus:**
- Alpaca API (stocks)
- Binance API (crypto)
- IBKR API (advanced)
- Order management
- Account synchronization
- Trade execution

**Deliverables:**
- [ ] Broker API base class
- [ ] Alpaca integration
- [ ] Binance integration
- [ ] Order management service
- [ ] Account sync service
- [ ] Trade execution API
- [ ] Error handling and retry logic
- [ ] Test coverage > 80%

---

#### C-037: Social Sentiment Analysis
**Assigned to:** Linus
**Status:** ⏳ PENDING (after C-022)
**Estimated:** 18-24 hours
**Deadline:** Feb 7, 5:00 PM

**Enhanced Guide:**
- ✅ VADER + TextBlob sentiment analyzer
- ✅ Twitter API v2 integration (Tweepy)
- ✅ Reddit PRAW integration
- ✅ Ticker detection regex
- ✅ Sentiment aggregation
- ✅ 5 common mistakes, 7 FAQ
- ✅ Complete working code

**Files to Create:**
- `apps/backend/src/services/sentiment.py` - Sentiment analysis service
- `apps/backend/src/integrations/twitter.py` - Twitter API v2
- `apps/backend/src/integrations/reddit.py` - Reddit PRAW
- `apps/backend/src/api/sentiment.py` - REST API
- `apps/backend/src/tests/test_sentiment.py` - Tests

**Deliverables:**
- [ ] SentimentAnalyzer class (VADER + TextBlob)
- [ ] Twitter scraper (API v2 with Tweepy)
- [ ] Reddit scraper (PRAW)
- [ ] Ticker detection ($AAPL, $TSLA, etc.)
- [ ] Sentiment aggregation by ticker
- [ ] REST API endpoints
- [ ] Test coverage > 80%

---

#### C-038: Options Chain Visualization
**Assigned to:** Turing
**Status:** ⏳ PENDING (after C-017)
**Estimated:** 16-20 hours
**Deadline:** Feb 9, 5:00 PM

**Enhanced Guide:**
- ✅ Black-Scholes implementation
- ✅ Greeks calculator (Delta, Gamma, Theta, Vega, Rho)
- ✅ Implied volatility (Newton-Raphson)
- ✅ Yahoo Finance yfinance integration
- ✅ IV rank, max pain, put/call ratio
- ✅ 5 common mistakes, 7 FAQ
- ✅ Complete working code

**Frontend + Backend:**
- Backend: Options data fetching and calculations
- Frontend: Options chain visualization
- Greeks display
- IV charts

**Deliverables:**
- [ ] Options service (yfinance integration)
- [ ] Greeks calculator
- [ ] Implied volatility calculator
- [ ] Options chain API
- [ ] Options chain visualization component
- [ ] Greeks display component
- [ ] Test coverage > 80%

---

#### C-040: Robo-Advisor Asset Allocation
**Assigned to:** Linus
**Status:** ⏳ PENDING (after C-037)
**Estimated:** 18-24 hours
**Deadline:** Feb 10, 5:00 PM

**Enhanced Guide:**
- ✅ Modern Portfolio Theory (MPT)
- ✅ Efficient frontier calculation
- ✅ Black-Litterman model
- ✅ Risk tolerance questionnaire
- ✅ Goal-based allocation
- ✅ Monte Carlo simulation
- ✅ Rebalancing recommendations
- ✅ 5 common mistakes, 7 FAQ
- ✅ Complete working code

**Files to Create:**
- `apps/backend/src/services/robo_advisor.py` - MPT engine
- `apps/backend/src/models/robo_advisor.py` - Questionnaire models
- `apps/backend/src/api/robo_advisor.py` - REST API
- `apps/backend/src/tests/test_robo_advisor.py` - Tests

**Deliverables:**
- [ ] MPT optimization engine (scipy.optimize)
- [ ] Efficient frontier calculation
- [ ] Risk tolerance questionnaire (10 questions)
- [ ] Goal-based allocation (retirement, house, etc.)
- [ ] Monte Carlo simulation
- [ ] Rebalancing recommendations
- [ ] REST API endpoints
- [ ] Test coverage > 80%

---

### 🟢 MEDIUM PRIORITY (P2) - Later This Week

#### C-011: Portfolio Analytics Enhancement
**Assigned to:** Linus
**Estimated:** 10-14 hours

#### C-012: Portfolio Rebalancing Tools
**Assigned to:** Guido
**Estimated:** 12-16 hours

#### C-013: AI-Powered News Summarization
**Assigned to:** Guido (OpenAI API)
**Estimated:** 14-18 hours

#### C-014: Interactive Chart Drawing Tools
**Assigned to:** Turing (TradingView widgets)
**Estimated:** 12-16 hours

#### C-019: Data Export Functionality
**Assigned to:** Guido (CSV, PDF, Excel)
**Estimated:** 8-12 hours

#### C-020: Advanced Alerts & Notifications
**Assigned to:** Linus (Email, push, webhook)
**Estimated:** 14-18 hours

#### C-021: Advanced Technical Indicators
**Assigned to:** Linus (RSI, MACD, Bollinger)
**Estimated:** 16-20 hours

#### C-023: Options Greeks Calculator
**Assigned to:** Linus
**Estimated:** 12-16 hours

#### C-024: Earnings Calendar & Events
**Assigned to:** Guido
**Estimated:** 10-14 hours

#### C-025: CSV Bulk Import
**Assigned to:** Guido
**Estimated:** 6-8 hours

#### C-026: Value-at-Risk (VaR) Calculator
**Assigned to:** Linus
**Estimated:** 14-18 hours

#### C-027: Universal Asset Search Engine
**Assigned to:** Guido (Elasticsearch)
**Estimated:** 12-16 hours

#### C-028: IPO Calendar & Listings
**Assigned to:** Guido
**Estimated:** 10-14 hours

#### C-029: Level 2 Market Depth
**Assigned to:** Guido
**Estimated:** 12-16 hours

#### C-031: Bond Yield Calculator
**Assigned to:** Linus
**Estimated:** 12-16 hours

#### C-032: Economic Calendar Tracker
**Assigned to:** Guido
**Estimated:** 10-14 hours

#### C-033: Keyboard Shortcuts System
**Assigned to:** Turing (React hotkeys)
**Estimated:** 10-12 hours

#### C-034: Webhooks System
**Assigned to:** Linus
**Estimated:** 12-16 hours

#### C-035: Dividend Tracking System
**Assigned to:** Guido
**Estimated:** 14-18 hours

#### C-039: Multi-Currency Portfolio Support
**Assigned to:** Linus (Forex API)
**Estimated:** 14-18 hours

---

## 🚨 CRITICAL BUGS

### ScreenerPreset Model Fix
**Assigned to:** All Coders
**Status:** 🔴 CRITICAL
**Deadline:** Feb 1, 12:00 PM (TOMORROW)

**Issue:** ScreenerPreset model missing base classes
**Impact:** Screener save/load broken
**File:** `apps/backend/src/models/screener.py`

**Required Changes:**
```python
# BEFORE (WRONG):
class ScreenerPreset:
    name = models.CharField()
    # ...

# AFTER (CORRECT):
from django.db import models

class ScreenerPreset(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... rest of fields

    class Meta:
        db_table = 'screener_presets'
```

**Test:**
```bash
cd apps/backend
python manage.py makemigrations
python manage.py migrate
python manage.py test screener
```

---

## 📊 WORKLOAD DISTRIBUTION

### Linus (Backend)
**Current Week:**
1. ✅ C-015: Position Size Calculator
2. 🔄 C-022: Strategy Backtesting Engine (18-24h)
3. ⏳ C-037: Social Sentiment Analysis (18-24h)
4. ⏳ C-040: Robo-Advisor Asset Allocation (18-24h)

**Total:** 54-72 hours this week

---

### Guido (Backend)
**Current Week:**
1. ✅ C-015: Position Size Calculator
2. 🔄 C-036: Paper Trading System (16-20h)
3. ⏳ C-030: Broker API Integration (14-18h)

**Total:** 30-38 hours this week

---

### Turing (Frontend)
**Current Week:**
1. ⏳ C-016: Customizable Dashboards (14-18h)
2. ⏳ C-017: Market Heat Map Visualization (10-14h)
3. ⏳ C-038: Options Chain Visualization (16-20h)

**Total:** 40-52 hours this week

---

## 📋 DAILY EXPECTATIONS

### Every Day (5:00 PM Report)

**Send to:** GAUDÍ + Karen

**Format:**
```email
GAUDÍ + Karen,

[Ccoder NAME] DAILY REPORT - [Date]

✅ COMPLETED:
- [Task ID]: [What was done]
  * [Files modified]
  * [Commit hash]
  * [Progress %]

🔄 IN PROGRESS:
- [Task ID]: [What I'm working on]
  * [Current progress]
  * [Estimated completion]

🚧 BLOCKERS:
- [Description]
- [What help I need]

⏰ TOMORROW:
- [What I'll work on]

❓ QUESTIONS:
- [Any questions]

- [Coder Name]
```

---

## 🎯 SUCCESS CRITERIA

### This Week
- [ ] All coders send daily reports (5:00 PM)
- [ ] ScreenerPreset model fixed (by Feb 1, 12:00 PM)
- [ ] C-015 reviewed and merged
- [ ] C-022 backtesting engine started
- [ ] C-036 paper trading started
- [ ] C-016 dashboards started
- [ ] C-017 heat map started

### Quality Standards
- [ ] All code reviewed by peers
- [ ] Test coverage > 80%
- [ ] No TypeScript errors
- [ ] No pylint warnings
- [ ] Documentation complete

### Communication Standards
- [ ] Daily reports on time
- [ ] Blockers reported immediately
- [ ] Questions asked (don't stay silent!)
- [ ] PRs reviewed within 24 hours

---

## 🚨 ESCALATION PATH

### Level 1: Peer Support
- Ask another coder for help
- Review each other's code
- Share knowledge

### Level 2: Karen (DevOps)
- Infrastructure blockers
- Database issues
- Deployment problems
- General coordination

### Level 3: GAUDÍ (Architect)
- Architectural decisions
- Priority conflicts
- Resource allocation
- Final approvals

---

## 📞 CONTACT INFORMATION

### Daily Communication
- **Channel:** Email + GitHub
- **Frequency:** Daily at 5:00 PM
- **Escalation:** Anytime for critical issues

### Office Hours
- **GAUDÍ:** Available 9 AM - 9 PM
- **Karen:** Available 9 AM - 6 PM
- **Charo:** Available for security reviews

### Emergency Contact
- **Critical blockers:** Email GAUDÍ immediately
- **Security issues:** Email Charo immediately
- **Infrastructure issues:** Email Karen immediately

---

## 🎉 RECOGNITION

### Great Work So Far
- ✅ Migration tasks (C-001 to C-010) - 60% complete
- ✅ Feature tasks (C-011 to C-015) - 5/30 complete
- ✅ Integration testing complete

### Need Improvement
- ❌ Communication (2+ days silence)
- ❌ ScreenerPreset model bug
- ❌ Task acknowledgment

### Goal This Week
- 🎯 Daily reports from all coders
- 🎯 All critical bugs fixed
- 🎯 3+ new tasks complete
- 🎯 Communication score ≥ 8/10

---

**Status:** ✅ ACTIVE
**Created:** January 31, 2026
**Next Review:** February 1, 2026 (9:00 AM standup)

---

🎨 *GAUDÍ - Building Financial Excellence*
