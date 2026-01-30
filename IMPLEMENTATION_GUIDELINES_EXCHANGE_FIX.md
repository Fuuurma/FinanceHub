# 🛠️ IMPLEMENTATION GUIDELINES: Exchange Table Fix

**For:** Development Team / Coders
**Date:** January 30, 2026
**Status:** READY FOR IMPLEMENTATION

---

## 🎯 DECISION REQUIRED

Before implementing, TEAM MUST decide:

**Question:** Which is the ACTIVE project?

**Option A:** Outer `/src/` (monolith) → Use **Solution A**  
**Option B:** Backend `/Backend/src/` (microservice) → Use **Solution B**  
**Option C:** Both (transitional) → Use **Solution B**

---

## 📋 SOLUTION A: Keep Outer Project (Rollback Backend)

### Assumptions:
- Outer project is PRIMARY
- Backend project is DEPRECATED or being phased out
- Database belongs to outer project

### Steps:

#### 1. Rollback Backend Migration (5 min)
```bash
cd Backend/src
python manage.py migrate assets 0011
```

#### 2. Delete Backend Migration File (1 min)
```bash
rm Backend/src/assets/migrations/0012_exchange_mic_exchange_operating_hours_and_more.py
```

#### 3. Revert Backend Exchange Model (5 min)
**File:** `Backend/src/assets/models/exchange.py`

**CHANGE FROM:**
```python
class Exchange(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    mic = models.CharField(max_length=10, unique=True, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='exchanges')
    timezone = models.CharField(max_length=50, blank=True)
    operating_hours = models.TextField(blank=True)
    website = models.URLField(blank=True)
```

**BACK TO:**
```python
class Exchange(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    timezone = models.CharField(max_length=50, blank=True)
```

#### 4. Remove Backend-Added Columns from Database (2 min)
```sql
ALTER TABLE assets_exchange DROP COLUMN mic;
ALTER TABLE assets_exchange DROP COLUMN operating_hours;
ALTER TABLE assets_exchange DROP COLUMN website;
```

#### 5. Verify (2 min)
```bash
cd Backend/src
python manage.py check
python manage.py shell
>>> from assets.models.exchange import Exchange
>>> Exchange.objects.count()
52
```

#### 6. Test Seed Command (2 min)
```bash
python manage.py seed_exchanges
# Should say: "Created: 0, Updated: 52" (no duplicates)
```

**Total Time:** 17 minutes  
**Risk:** LOW  
**Data Loss:** None

---

## 📋 SOLUTION B: Use Backend Project (Migrate Outer)

### Assumptions:
- Backend project is FUTURE
- Outer project is being MIGRATED to Backend
- Richer schema (mic, operating_hours, website) is needed

### Steps:

#### 1. Update Outer Exchange Model (5 min)
**File:** `FinanceHub/src/assets/models/exchange.py`

**CHANGE TO:**
```python
class Exchange(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    mic = models.CharField(max_length=10, unique=True, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='exchanges')
    timezone = models.CharField(max_length=50, blank=True)
    operating_hours = models.TextField(blank=True, help_text="Trading hours in JSON format")
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
```

#### 2. Copy Migration to Outer Project (2 min)
```bash
cp Backend/src/assets/migrations/0012_exchange_mic_exchange_operating_hours_and_more.py \
   src/assets/migrations/
```

#### 3. Run Migration in Outer Project (2 min)
```bash
cd src
python manage.py migrate assets
```

#### 4. Test Outer Project (3 min)
```bash
python manage.py shell
>>> from assets.models.exchange import Exchange
>>> e = Exchange.objects.first()
>>> e.mic
'XLME'
>>> e.operating_hours
'{"monday_friday": "09:00-17:00"}'
>>> e.website
'https://www.lme.com'
```

#### 5. Update All References (10 min)
Search for all Exchange model usage in outer project:
```bash
cd src
grep -r "Exchange.objects" --include="*.py"
grep -r "ForeignKey.*Exchange" --include="*.py")
grep -r "ManyToManyField.*Exchange" --include="*.py")
```

Update any code that assumes old schema.

#### 6. Test Seed Commands (2 min)
```bash
python manage.py seed_exchanges
# Should work correctly
```

**Total Time:** 24 minutes  
**Risk:** MEDIUM  
**Data Loss:** None  
**Benefits:** Richer data schema, more complete exchange information

---

## 📋 SOLUTION C: Create New Table (Clean Slate)

### Assumptions:
- Both current tables are problematic
- Want fresh start with better naming
- Can afford migration time

### Steps:

#### 1. Create New Model (5 min)
**File:** `Backend/src/assets/models/trading_venue.py`

```python
from django.db import models
from assets.models.country import Country
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class TradingVenue(UUIDModel, TimestampedModel):
    """
    Trading venue/marketplace where assets are traded.
    Replaces the old Exchange model.
    """
    class VenueType(models.TextChoices):
        STOCK = 'stock', 'Stock Exchange'
        CRYPTO = 'crypto', 'Cryptocurrency Exchange'
        COMMODITY = 'commodity', 'Commodity Exchange'
        DERIVATIVE = 'derivative', 'Derivatives Exchange'
        FOREX = 'forex', 'Foreign Exchange'
    
    code = models.CharField(max_length=10, unique=True, help_text="Exchange code e.g., NYSE")
    name = models.CharField(max_length=100)
    mic = models.CharField(max_length=10, unique=True, blank=True, null=True, help_text="ISO 10383 MIC")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='trading_venues')
    timezone = models.CharField(max_length=50, blank=True)
    operating_hours = models.JSONField(blank=True, null=True, help_text="Trading hours as JSON")
    website = models.URLField(blank=True)
    venue_type = models.CharField(max_length=20, choices=VenueType.choices, default=VenueType.STOCK)
    
    # Additional metadata
    description = models.TextField(blank=True)
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True)
    
    # Tracking
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
```

#### 2. Create Migration (2 min)
```bash
cd Backend/src
python manage.py makemigrations assets
```

#### 3. Run Migration (1 min)
```bash
python manage.py migrate
```

#### 4. Create New Seed Command (30 min)
**File:** `Backend/src/utils/management/commands/seed_trading_venues.py`

Copy `seed_exchanges.py` and adapt to:
- Use `TradingVenue` model instead of `Exchange`
- Set `venue_type` based on exchange type
- Populate `operating_hours` as JSON instead of TextField

#### 5. Update Asset Model (10 min)
**File:** `Backend/src/assets/models/asset.py`

**CHANGE:**
```python
# OLD
exchanges = models.ManyToManyField(
    "assets.Exchange", blank=True, related_name="assets"
)

# NEW
trading_venues = models.ManyToManyField(
    "assets.TradingVenue", blank=True, related_name="assets"
)
```

#### 6. Migrate Existing Data (10 min)
Create data migration script:
```python
def migrate_exchanges_to_venues(apps, schema_editor):
    Exchange = apps.get_model('assets', 'Exchange')
    TradingVenue = apps.get_model('assets', 'TradingVenue')
    
    for exchange in Exchange.objects.all():
        TradingVenue.objects.create(
            code=exchange.code,
            name=exchange.name,
            mic=getattr(exchange, 'mic', None),
            country=exchange.country,
            timezone=exchange.timezone,
            operating_hours=json.loads(getattr(exchange, 'operating_hours', '{}')),
            website=getattr(exchange, 'website', ''),
        )
```

#### 7. Update All References (30 min)
Search and replace in codebase:
- `Exchange` → `TradingVenue`
- `exchanges` → `trading_venues`
- Update all queries
- Update all serializers
- Update all admin panels

**Total Time:** 98 minutes (~2 hours)  
**Risk:** HIGH  
**Data Loss:** None  
**Benefits:** Clean architecture, better naming, fresh start

---

## ✅ VERIFICATION CHECKLIST

After implementing ANY solution, verify:

### Database Level:
- [ ] Exchange table has correct columns
- [ ] 52 exchanges exist
- [ ] No duplicate exchanges
- [ ] All FKs point to correct tables

### Application Level:
- [ ] Backend project starts without errors
- [ ] Outer project starts without errors (if applicable)
- [ ] Django admin can access Exchange model
- [ ] Seed commands work
- [ ] No migration conflicts

### Code Level:
- [ ] All Exchange imports resolve correctly
- [ ] No "column does not exist" errors
- [ ] FK relationships work
- [ ] M2M relationships work

---

## 🚨 RISK ASSESSMENT

### Solution A (Rollback Backend):
- **Risk Level:** LOW
- **Data Loss:** None
- **Breaking Changes:** Backend project loses new fields
- **Rollback:** Easy

### Solution B (Migrate Outer):
- **Risk Level:** MEDIUM
- **Data Loss:** None
- **Breaking Changes:** Outer project needs migration
- **Rollback:** Moderate

### Solution C (New Table):
- **Risk Level:** HIGH
- **Data Loss:** None (migration preserves data)
- **Breaking Changes:** Many code changes required
- **Rollback:** Difficult

---

## 📊 RECOMMENDATION

### My Recommendation: **Solution B**

**Why:**
1. Backend model has BETTER schema (more complete)
2. 52 exchanges already have rich data (mic, operating_hours, website)
3. Aligns with microservices architecture (seems to be the direction)
4. Minimal data migration needed
5. Future-proof

**If Uncertain:** Start with **Solution A** (easiest rollback)

---

## 🎯 NEXT ACTIONS

### For Tech Lead:
1. **DECIDE:** Which solution to implement (A, B, or C)
2. **ASSIGN:** Developer to implement
3. **REVIEW:** This document with team
4. **APPROVE:** Implementation plan

### For Developer:
1. **READ:** This document completely
2. **UNDERSTAND:** Chosen solution
3. **IMPLEMENT:** Step-by-step
4. **TEST:** Verification checklist
5. **DOCUMENT:** Any deviations

### For QA:
1. **VERIFY:** All checklist items pass
2. **TEST:** Seed commands
3. **REPORT:** Any issues found

---

**Document Status:** READY FOR IMPLEMENTATION  
**Last Updated:** January 30, 2026  
**Next Review:** After implementation
