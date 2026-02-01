# #️⃣ TASK: C-035 - Dividend Tracking System

**Task ID:** C-035
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Linus) + Frontend Coder (Turing)
**Status:** 🚧 IN PROGRESS (Frontend: Turing) - Components Complete
**Priority:** P1 HIGH
**Estimated Time:** 14-18 hours
**Deadline:** February 25, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a comprehensive dividend tracking system that:
- Tracks dividend payments for positions
- Projects future dividend income
- Displays dividend calendar
- Calculates dividend yield
- Tracks dividend growth history
- Alerts on upcoming dividend payments

---

## 📋 REQUIREMENTS

### 1. Dividend Models

```python
# apps/backend/src/investments/models/dividends.py
class DividendPayment(models.Model):
    position = ForeignKey(Position)
    amount = DecimalField(max_digits=12, decimal_places=4)
    ex_dividend_date = DateField()
    record_date = DateField()
    payment_date = DateField()
    frequency = CharField()  # 'monthly', 'quarterly', 'semi-annual', 'annual'
    currency = CharField(max_length=3)
    created_at = DateTimeField(auto_now_add=True)

class DividendProjection(models.Model):
    position = ForeignKey(Position)
    projected_amount = DecimalField(max_digits=12, decimal_places=4)
    expected_ex_date = DateField()
    expected_payment_date = DateField()
    probability = CharField()  # 'confirmed', 'estimated', 'projected'
    created_at = DateTimeField(auto_now_add=True)

class DividendSummary(models.Model):
    user = ForeignKey(User)
    portfolio = ForeignKey(Portfolio)
    total_dividends_ytd = DecimalField()
    total_dividends_last_12m = DecimalField()
    projected_annual_dividends = DecimalField()
    dividend_yield = DecimalField()
    average_yield = DecimalField()
    monthly_dividend_income = DecimalField()
    last_updated = DateTimeField(auto_now=True)

class DividendAlert(models.Model):
    user = ForeignKey(User)
    position = ForeignKey(Position)
    alert_type = CharField()  # 'ex_date', 'payment_date', 'change'
    alert_date = DateField()
    is_active = BooleanField(default=True)
    notified = BooleanField(default=False)
```

### 2. Dividend Service

```python
# apps/backend/src/investments/services/dividend_service.py
class DividendService:
    def record_dividend_payment(self, position_id: int, amount: Decimal,
                                ex_date: date, payment_date: date):
        """Record an actual dividend payment"""
        pass

    def calculate_dividend_yield(self, position: Position) -> Decimal:
        """
        Dividend Yield = Annual Dividends / Current Price
        """
        pass

    def project_future_dividends(self, position: Position,
                                months_forward: int = 12):
        """
        Project future dividend payments based on:
        - Historical payment frequency
        - Most recent payment amount
        - Company dividend history
        """
        pass

    def get_dividend_calendar(self, portfolio_id: int,
                             start_date: date, end_date: date):
        """
        Get all dividend payments in date range
        """
        pass

    def calculate_dividend_summary(self, portfolio_id: int):
        """
        Calculate portfolio-level dividend metrics:
        - Total dividends YTD
        - Total dividends last 12 months
        - Projected annual dividends
        - Average dividend yield
        - Monthly dividend income
        """
        pass

    def get_dividend_history(self, position: Position, years: int = 5):
        """
        Get dividend payment history for a position
        Show dividend growth over time
        """
        pass

    def update_dividend_projections(self, portfolio_id: int):
        """
        Refresh dividend projections based on latest data
        Called nightly via background task
        """
        pass

    def get_upcoming_dividends(self, portfolio_id: int, days: int = 30):
        """
        Get upcoming dividend payments for user's portfolio
        """
        pass
```

### 3. API Endpoints

```python
# apps/backend/src/investments/api/dividends.py
from ninja import Router

router = Router()

@router.get("/dividends/summary/{portfolio_id}")
def get_dividend_summary(request, portfolio_id: int):
    """Get dividend summary for portfolio"""
    pass

@router.get("/dividends/calendar")
def get_dividend_calendar(request, portfolio_id: int,
                          start_date: date, end_date: date):
    """Get dividend calendar"""
    pass

@router.get("/dividends/upcoming")
def get_upcoming_dividends(request, portfolio_id: int, days: int = 30):
    """Get upcoming dividend payments"""
    pass

@router.get("/dividends/position/{position_id}")
def get_position_dividends(request, position_id: int):
    """Get dividend history for a position"""
    pass

@router.get("/dividends/projections/{portfolio_id}")
def get_dividend_projections(request, portfolio_id: int, months: int = 12):
    """Get projected future dividends"""
    pass

@router.post("/dividends/alerts")
def create_dividend_alert(request, position_id: int, alert_type: str):
    """Create alert for dividend events"""
    pass

@router.get("/dividends/yield-ranking")
def get_yield_ranking(request, portfolio_id: int):
    """Rank positions by dividend yield"""
    pass
```

### 4. Frontend Components

```typescript
// apps/frontend/src/components/dividends/DividendSummaryCard.tsx
interface DividendSummary {
  totalDividendsYTD: number;
  totalDividendsLast12m: number;
  projectedAnnualDividends: number;
  dividendYield: number;
  monthlyDividendIncome: number;
}

export function DividendSummaryCard({ portfolioId }: Props) {
  // Display portfolio dividend summary
  // Show YTD dividends
  // Show projected annual income
  // Show dividend yield
}

// apps/frontend/src/components/dividends/DividendCalendar.tsx
export function DividendCalendar({ portfolioId }: Props) {
  // Calendar view of dividend payments
  // Highlight ex-dividend dates
  // Show payment dates
  // Color code by amount
  // Filter by date range
}

// apps/frontend/src/components/dividends/DividendHistoryChart.tsx
export function DividendHistoryChart({ positionId }: Props) {
  // Line chart of dividend payments over time
  // Show dividend growth
  // Compare to benchmark
  // Display yield on cost
}

// apps/frontend/src/components/dividends/UpcomingDividends.tsx
export function UpcomingDividends({ portfolioId }: Props) {
  // List of upcoming dividend payments
  // Sort by date
  // Show company, amount, date
  // Set reminders
}
```

### 5. Data Sources

**Dividend Data:**
- Historical payments from portfolio transactions
- Future projections from financial data API
- Company announcements (future enhancement)
- User can manually record dividend payments

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Dividend payment tracking
- [ ] Dividend yield calculation per position
- [ ] Portfolio dividend summary (YTD, 12m, projected)
- [ ] Dividend calendar view
- [ ] Upcoming dividends list
- [ ] Dividend history chart (5 years)
- [ ] Dividend growth tracking
- [ ] Dividend projections (next 12 months)
- [ ] Dividend yield ranking
- [ ] Alerts for ex-dividend dates
- [ ] Alerts for payment dates
- [ ] Monthly dividend income projection
- [ ] API endpoints for all operations
- [ ] Tests for dividend service
- [ ] Responsive UI components

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/investments/models/dividends.py`
- `apps/backend/src/investments/services/dividend_service.py`
- `apps/backend/src/investments/api/dividends.py`
- `apps/backend/src/investments/tests/test_dividends.py`
- `apps/frontend/src/components/dividends/DividendSummaryCard.tsx`
- `apps/frontend/src/components/dividends/DividendCalendar.tsx`
- `apps/frontend/src/components/dividends/DividendHistoryChart.tsx`
- `apps/frontend/src/components/dividends/UpcomingDividends.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- Position model exists
- Portfolio model exists
- Transaction model exists

**Related Tasks:**
- C-026: Automatic Dividend Tracking (completes this)

---

## 📊 DIVIDEND METRICS

### Key Metrics
1. **Current Yield** = Annual Dividend / Current Price
2. **Yield on Cost** = Annual Dividend / Purchase Price
3. **YTD Dividends** = Sum of dividends Jan 1 to today
4. **12-Month Dividends** = Sum of last 12 months
5. **Projected Annual** = Current monthly rate × 12
6. **Dividend Growth** = YoY change in dividend payments

### Portfolio Aggregation
- Total YTD dividends across all positions
- Average portfolio yield (weighted by position value)
- Monthly dividend income (projected)
- Dividend diversification (sectors, companies)

---

## 📊 DELIVERABLES

1. **Models:** DividendPayment, DividendProjection, DividendSummary
2. **Service:** DividendService with calculation methods
3. **API:** All dividend-related endpoints
4. **Frontend:** Summary card, calendar, charts, upcoming list
5. **Tests:** Unit tests for yield calculations
6. **Background Task:** Update projections nightly

---

## 💬 NOTES

**Implementation Approach:**
- Use transaction history to record dividend payments
- Project future dividends based on frequency
- Support quarterly, monthly, annual dividends
- Handle special dividends (one-time payments)
- Track dividend growth over time

**Data Accuracy:**
- Cross-check dividend data with financial API
- Allow users to manually edit dividend records
- Flag inconsistent data
- Audit trail for all changes

**User Features:**
- Set alerts for ex-dividend dates
- Set alerts for payment dates
- Compare dividend income across portfolios
- Export dividend history for tax reporting

**Libraries:**
- Backend: `django-crontab` for scheduled tasks
- Frontend: `recharts` or `chart.js` for dividend history

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Linus) + Frontend Coder (Turing)
**User Value:** HIGH - dividend investors need this

---

#️⃣ *C-035: Dividend Tracking System*
*Track dividend income, project future payments, monitor yield*
