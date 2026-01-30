---
title: "Database Schema Fixes & Migrations"
status: pending
priority: p0
estimate: "3 days"
created: "2026-01-30"
assigned_to: gaudi
depends_on:
  - d-001
---

## Summary

Fix critical database schema issues identified in DATABASE_SCHEMA.md. These P0 issues must be fixed to ensure data integrity and performance.

## Issues to Fix

### P0 - Critical Database Issues

#### 1. Remove Deprecated Columns from Asset Model

**File:** `apps/backend/src/assets/models/asset.py`

**Issue:** CharField columns exist but are deprecated:
```python
sector = models.CharField(max_length=150, blank=True, null=True)
industry = models.CharField(max_length=150, blank=True, null=True)
```

**Fix Steps:**

1. Check if data exists in these columns:
```bash
cd apps/backend
python manage.py shell
>>> from assets.models import Asset
>>> Asset.objects.filter(sector__isnull=False).count()
>>> Asset.objects.filter(industry__isnull=False).count()
```

2. If no data, create migration to remove:
```bash
python manage.py makemigrations assets --name remove_deprecated_columns
```

3. If data exists, document and plan migration strategy

#### 2. Add Uniqueness Constraint on (ticker, exchange)

**Issue:** No uniqueness constraint on (ticker, exchange) combination

**Fix:**
```bash
cd apps/backend
python manage.py makemigrations assets --name add_ticker_exchange_unique
```

**Migration content:**
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    atomic = False

    def forwards(apps, schema_editor):
        # Add constraint concurrently to avoid locking
        schema_editor.execute(
            '''
            ALTER TABLE assets_asset
            ADD CONSTRAINT assets_asset_ticker_exchange_unique
            UNIQUE (ticker, exchange_id)
            '''
        )

    def backwards(self, schema_editor):
        schema_editor.execute(
            'ALTER TABLE assets_asset DROP CONSTRAINT assets_asset_ticker_exchange_unique'
        )
```

**Note:** Use `atomic = False` and `CONCURRENTLY` for PostgreSQL to avoid locks.

#### 3. Add Soft Delete to Models Missing It

**Issue:** These models missing `SoftDeleteModel`:
- `Country`
- `Sector`
- `Industry`
- `Currency`
- `Benchmark`
- `NewsArticle`
- `Alert`

**Fix for each model:**

**Example for Country:**
```python
# apps/backend/src/assets/models/reference/country.py

from utils.models.base import SoftDeleteModel

class Country(SoftDeleteModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    # ... other fields
```

**Steps:**
1. Add `SoftDeleteModel` inheritance
2. Create migration
3. Test soft delete works

#### 4. Add Missing Database Indexes

**Issue:** Missing indexes on frequently queried fields

**Create migration:**
```bash
cd apps/backend
python manage.py makemigrations assets --name add_performance_indexes
```

**Indexes to add:**
```python
# portfolios/holdings
class Migration(migrations.Migration):
    def forwards(self, schema_editor):
        with schema_editor.connection.cursor() as cursor:
            # Composite index for portfolio holdings queries
            cursor.execute('''
                CREATE INDEX CONCURRENTLY
                idx_portfolios_holding_portfolio_asset
                ON portfolios_holding (portfolio_id, asset_id)
            ''')

            # Index for price history lookups
            cursor.execute('''
                CREATE INDEX CONCURRENTLY
                idx_assets_priceshistoric_asset_timestamp
                ON assets_assetpriceshistoric (asset_id, timestamp DESC)
            ''')

            # Index for user watchlists
            cursor.execute('''
                CREATE INDEX CONCURRENTLY
                idx_investments_watchlist_user_asset
                ON investments_watchlist (user_id, asset_id)
            ''')

    def backwards(self, schema_editor):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('DROP INDEX IF EXISTS idx_portfolios_holding_portfolio_asset')
            cursor.execute('DROP INDEX IF EXISTS idx_assets_priceshistoric_asset_timestamp')
            cursor.execute('DROP INDEX IF EXISTS idx_investments_watchlist_user_asset')
```

**Use `CONCURRENTLY` to avoid table locks.**

#### 5. Fix Alert Model - Add UUIDModel Inheritance

**File:** `apps/backend/src/investments/models/alert.py`

**Issue:** Alert model uses standard Model, not UUIDModel

**Fix:**
```python
# Current
class Alert(models.Model):
    # ...

# Should be
from utils.models.base import UUIDModel

class Alert(UUIDModel):
    # ...
```

**Note:** This requires a data migration to populate UUIDs for existing records.

## Files to Modify

1. `apps/backend/src/assets/models/asset.py` - Remove deprecated columns
2. `apps/backend/src/assets/models/reference/country.py` - Add SoftDeleteModel
3. `apps/backend/src/assets/models/reference/sector.py` - Add SoftDeleteModel
4. `apps/backend/src/assets/models/reference/industry.py` - Add SoftDeleteModel
5. `apps/backend/src/assets/models/reference/currency.py` - Add SoftDeleteModel
6. `apps/backend/src/portfolios/models/benchmark.py` - Add SoftDeleteModel
7. `apps/backend/src/investments/models/news.py` - Add SoftDeleteModel to NewsArticle
8. `apps/backend/src/investments/models/alert.py` - Change to UUIDModel

## Files to Create

1. `apps/backend/src/assets/migrations/XXXX_remove_deprecated_columns.py`
2. `apps/backend/src/assets/migrations/XXXX_add_ticker_exchange_unique.py`
3. `apps/backend/src/assets/migrations/XXXX_add_performance_indexes.py`
4. Various migrations for SoftDeleteModel additions

## Testing

```bash
# Check deprecated columns
python manage.py shell
>>> from assets.models import Asset
>>> Asset.objects.exclude(sector__isnull=True).exclude(sector='').count()
>>> Asset.objects.exclude(industry__isnull=True).exclude(industry='').count()

# Verify no data loss after migration
python manage.py check --deploy

# Test soft delete
python manage.py shell
>>> from assets.models import Country
>>> country = Country.objects.first()
>>> country.delete()  # Should set is_deleted=True
>>> Country.objects.filter(is_deleted=True).count()
>>> Country.all_objects.filter(is_deleted=True).count()  # With soft delete

# Test uniqueness constraint
python manage.py shell
>>> from assets.models import Asset
>>> asset1 = Asset.objects.first()
>>> asset2 = Asset(ticker=asset1.ticker, exchange=asset1.exchange, ...)
>>> asset2.save()  # Should raise IntegrityError
```

## Success Criteria

1. ✅ Deprecated columns removed or documented
2. ✅ Unique constraint on (ticker, exchange)
3. ✅ All reference models have soft delete
4. ✅ Alert model uses UUIDModel
5. ✅ Performance indexes created
6. ✅ No data loss in migrations

## Related Issues

- DATABASE_SCHEMA.md Issues 2, 3, 4
- BACKEND_IMPROVEMENTS.md (model issues)
