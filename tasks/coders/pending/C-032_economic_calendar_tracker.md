# 📅 TASK: C-032 - Economic Calendar Tracker

**Task ID:** C-032
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Guido)
**Status:** ⏳ PENDING
**Priority:** P2 MEDIUM
**Estimated Time:** 10-14 hours
**Deadline:** February 18, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create an economic calendar that tracks and displays:
- Federal Reserve meetings
- GDP releases
- Employment reports (Non-Farm Payrolls)
- CPI/PPI inflation data
- Retail sales
- Consumer confidence
- Housing market data
- Manufacturing PMI
- Other economic indicators

---

## 📋 REQUIREMENTS

### 1. Economic Event Models

```python
# apps/backend/src/investments/models/economic_events.py
class EconomicEvent(models.Model):
    name = CharField()
    description = TextField(blank=True)
    country = CharField()  # 'US', 'EU', 'UK', 'JP', 'CN', etc.
    indicator_type = CharField()  # 'gdp', 'employment', 'inflation', etc.
    importance = CharField()  # 'low', 'medium', 'high'
    release_date = DateField()
    release_time = TimeField()
    timezone = CharField()  # 'US/Eastern', 'Europe/London', etc.
    actual_value = DecimalField(null=True)
    forecast_value = DecimalField(null=True)
    previous_value = DecimalField(null=True)
    unit = CharField()  # '%', 'K', 'M', 'B', 'points', etc.
    source = CharField()  # 'Bureau of Labor Statistics', etc.
    url = URLField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class EconomicEventAlert(models.Model):
    user = ForeignKey(User)
    event = ForeignKey(EconomicEvent)
    remind_before = DurationField()  # Remind X time before event
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```

### 2. Economic Calendar Service

```python
# apps/backend/src/investments/services/economic_calendar_service.py
class EconomicCalendarService:
    def get_upcoming_events(self, country: str = None,
                           importance: str = None,
                           days_forward: int = 30):
        """Get upcoming economic events"""
        pass

    def get_events_by_date(self, date: date):
        """Get all events for specific date"""
        pass

    def get_events_by_type(self, indicator_type: str):
        """Get all events of specific type (GDP, employment, etc.)"""
        pass

    def get_high_impact_events(self, days_forward: int = 7):
        """Get high importance events (market movers)"""
        pass

    def update_event_values(self, event_id: int, actual: Decimal):
        """Update event when actual value is released"""
        pass

    def create_alert(self, user_id: int, event_id: int, remind_before: str):
        """Create reminder for user before event"""
        pass

    def check_upcoming_alerts(self):
        """Check for events that need alerts sent (background task)"""
        pass
```

### 3. API Endpoints

```python
# apps/backend/src/investments/api/economic_calendar.py
from ninja import Router

router = Router()

@router.get("/economic-calendar/events")
def get_events(request, country: str = None, importance: str = None,
               start_date: date = None, end_date: date = None):
    """Get economic events with filters"""
    pass

@router.get("/economic-calendar/events/{event_id}")
def get_event_detail(request, event_id: int):
    """Get detailed event information"""
    pass

@router.get("/economic-calendar/high-impact")
def get_high_impact_events(request, days: int = 7):
    """Get high importance events (market movers)"""
    pass

@router.post("/economic-calendar/alerts")
def create_event_alert(request, event_id: int, remind_before: str):
    """Create alert for economic event"""
    pass

@router.get("/economic-calendar/alerts")
def get_user_alerts(request):
    """Get user's economic event alerts"""
    pass

@router.delete("/economic-calendar/alerts/{alert_id}")
def delete_alert(request, alert_id: int):
    """Delete economic event alert"""
    pass
```

### 4. Frontend Component

```typescript
// apps/frontend/src/components/calendar/EconomicCalendar.tsx
interface EconomicEvent {
  id: number;
  name: string;
  country: string;
  importance: 'low' | 'medium' | 'high';
  releaseDate: Date;
  releaseTime: string;
  actual?: number;
  forecast?: number;
  previous?: number;
  unit: string;
}

export function EconomicCalendar() {
  // Calendar view (month/week/day)
  // Filter by country, importance
  // Show upcoming high-impact events
  // Set reminders for events
  // Display actual/forecast/previous values
  // Historical event lookup
}
```

### 5. Data Seeding

**Initial Data (Major Events):**
```python
# Federal Reserve meetings (8 per year, FOMC)
# GDP releases (quarterly, 4 per year)
# Non-Farm Payrolls (monthly, first Friday)
# CPI (monthly)
# PPI (monthly)
# Retail sales (monthly)
# Consumer confidence (monthly)
# Existing home sales (monthly)
# PMI Manufacturing (monthly)
# And more...
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Economic event model created
- [ ] Calendar view of events (month/week/day)
- [ ] Filter by country, importance, date range
- [ ] High-impact events highlighted
- [ ] Show actual/forecast/previous values
- [ ] Set alerts/reminders for events
- [ ] Event detail view with description
- [ ] Historical events lookup
- [ ] Data seeding for major economic events
- [ ] API endpoints for all operations
- [ ] Tests for calendar service
- [ ] Responsive calendar UI

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/investments/models/economic_events.py`
- `apps/backend/src/investments/services/economic_calendar_service.py`
- `apps/backend/src/investments/api/economic_calendar.py`
- `apps/backend/src/investments/tests/test_economic_calendar.py`
- `apps/frontend/src/components/calendar/EconomicCalendar.tsx`
- `apps/backend/src/investments/seed_economic_events.py`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- User authentication
- Notification system (for alerts)
- Frontend calendar library

**Related Tasks:**
- C-024: Earnings Calendar (similar pattern, can reuse code)

---

## 📊 ECONOMIC INDICATORS TO INCLUDE

### High Importance (Market Movers)
1. **Federal Reserve Meetings** - FOMC rate decisions
2. **GDP (Gross Domestic Product)** - Quarterly
3. **Non-Farm Payrolls** - Monthly employment
4. **CPI (Consumer Price Index)** - Inflation
5. **PPI (Producer Price Index)** - Inflation

### Medium Importance
6. **Retail Sales** - Consumer spending
7. **Consumer Confidence** - Sentiment
8. **Existing Home Sales** - Housing market
9. **PMI Manufacturing** - Factory activity
10. **Durable Goods Orders** - Business investment

### Low Importance
11. **Building Permits** - Housing starts indicator
12. **Industrial Production** - Factory output
13. **Wholesale Inventories** - Supply chain
14. **Trade Balance** - Imports/exports
15. **Initial Jobless Claims** - Weekly layoffs

---

## 📅 CALENDAR FEATURES

### View Modes
- **Month View:** See all events in a month
- **Week View:** Detailed week view with times
- **Day View:** Detailed view of single day
- **List View:** chronological list of upcoming events

### Filters
- By country (US, EU, UK, JP, CN, etc.)
- By importance (high, medium, low)
- By type (GDP, employment, inflation, etc.)
- By date range

### Alerting
- Remind 1 hour before event
- Remind 1 day before event
- Remind 1 week before event
- Push notifications (if implemented)

---

## 📊 DELIVERABLES

1. **Models:** EconomicEvent, EconomicEventAlert
2. **Service:** EconomicCalendarService with all methods
3. **API:** Event retrieval, alerting endpoints
4. **Frontend:** Economic calendar component with calendar view
5. **Seeding:** Initial data for major events
6. **Tests:** Unit tests for service methods

---

## 💬 NOTES

**Data Sources:**
- Manual data entry for now
- Future: API integration with economic data providers
- Federal Reserve website for FOMC meetings
- Bureau of Labor Statistics for employment data

**Implementation Approach:**
- Use existing calendar infrastructure from C-024
- Reuse alerting system from notifications
- Standardize timezone handling
- Cache high-impact events for performance

**Libraries:**
- Frontend: `react-calendar` or `date-fns`
- Backend: `python-dateutil` for timezone handling

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Guido)
**Similar To:** C-024 (Earnings Calendar) - can reuse patterns

---

📅 *C-032: Economic Calendar Tracker*
*Track economic events that move markets - Fed, GDP, employment*
