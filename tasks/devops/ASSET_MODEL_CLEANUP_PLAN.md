# ASSET MODEL CLEANUP PLAN

**Date:** January 31, 2026
**Task:** D-002 Part 2 - Remove Deprecated Columns
**Status:** Ready for Migration

---

## Current State

**File:** `apps/backend/src/assets/models/asset.py`

### Deprecated Columns (to be removed):
```python
# Line 106-111 - DEPRECATED
industry = models.CharField(
    max_length=150,
    blank=True,
    null=True,
    help_text="[DEPRECATED] Use industry_fk instead",
)

# Line 112-117 - DEPRECATED  
sector = models.CharField(
    max_length=150,
    blank=True,
    null=True,
    help_text="[DEPRECATED] Use sector_fk instead",
)
```

### Replacement Columns (already exist):
```python
# Line 87-93
sector_fk = models.ForeignKey(
    "assets.Sector",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="assets",
    help_text="Sector (foreign key)",
)

# Line 95-102
industry_fk = models.ForeignKey(
    "assets.Industry",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="assets",
    help_text="Industry (foreign key)",
)
```

---

## Migration Plan

### Step 1: Check for Data

**When Django environment is available:**

```bash
cd apps/backend/src
python manage.py shell
```

```python
from assets.models import Asset

# Check if data exists in deprecated columns
industry_count = Asset.objects.filter(industry__isnull=False).count()
sector_count = Asset.objects.filter(sector__isnull=False).count()

print(f"Assets with industry data: {industry_count}")
print(f"Assets with sector data: {sector_count}")
```

### Step 2A: If NO Data (Simple Removal)

If counts are 0, create migration:

```bash
cd apps/backend/src
python manage.py makemigrations assets --name remove_deprecated_sector_industry_columns
```

**Edit migration file:**
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('assets', 'previous_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='industry',
        ),
        migrations.RemoveField(
            model_name='asset', 
            name='sector',
        ),
    ]
```

### Step 2B: If Data Exists (Data Migration)

If counts > 0, migrate data first:

```python
# Data migration script
from assets.models import Asset

def migrate_sector_industry_data():
    updated = 0
    
    # Migrate sector data
    for asset in Asset.objects.filter(sector__isnull=False):
        if asset.sector and not asset.sector_fk:
            # Find matching Sector by name
            from assets.models import Sector
            try:
                sector = Sector.objects.filter(name__iexact=asset.sector).first()
                if sector:
                    asset.sector_fk = sector
                    updated += 1
            except:
                pass
    
    # Migrate industry data  
    for asset in Asset.objects.filter(industry__isnull=False):
        if asset.industry and not asset.industry_fk:
            # Find matching Industry by name
            from assets.models import Industry
            try:
                industry = Industry.objects.filter(name__iexact=asset.industry).first()
                if industry:
                    asset.industry_fk = industry
                    updated += 1
            except:
                pass
    
    # Bulk save
    Asset.objects.bulk_update([a for a in Asset.objects.all() if a.sector_fk or a.industry_fk], ['sector_fk', 'industry_fk'])
    
    print(f"Migrated {updated} assets")

# Run migration
migrate_sector_industry_data()
```

Then remove columns (Step 2A).

### Step 3: Apply Migration

```bash
cd apps/backend/src
python manage.py migrate
```

### Step 4: Verify

```python
from assets.models import Asset

# Verify columns are gone
try:
    Asset.objects.filter(industry="test").count()
    print("ERROR: industry column still exists!")
except FieldDoesNotExist:
    print("✓ industry column removed")

try:
    Asset.objects.filter(sector="test").count()
    print("ERROR: sector column still exists!")
except FieldDoesNotExist:
    print("✓ sector column removed")

# Verify foreign keys work
count = Asset.objects.filter(sector_fk__isnull=False).count()
print(f"✓ Assets with sector_fk: {count}")

count = Asset.objects.filter(industry_fk__isnull=False).count()
print(f"✓ Assets with industry_fk: {count}")
```

---

## Timeline

**Prerequisites:**
- ✅ SoftDeleteModel added to Sector, Industry (done)
- ✅ Foreign keys already exist (done)
- ⏳ Django environment available

**Estimated Time:** 30-60 minutes (depending on data volume)

---

## Rollback Plan

If issues occur:

```bash
cd apps/backend/src
python manage.py migrate assets zero
# Then reapply previous migrations
```

Or create reverse migration:
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('assets', 'remove_deprecated_sector_industry_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='industry',
            field=models.CharField(max_length=150, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='sector', 
            field=models.CharField(max_length=150, blank=True, null=True),
        ),
    ]
```

---

## Testing Checklist

After migration:

- [ ] `python manage.py check` - No errors
- [ ] `python manage.py test` - All tests pass
- [ ] Asset.objects.count() - Same as before
- [ ] Foreign key queries work: `Asset.objects.filter(sector_fk__name="Technology")`
- [ ] No reference to removed fields in code
- [ ] API endpoints work correctly

---

**Status:** Documentation complete, ready for implementation when Django environment available

**Part of:** D-002 Database Migrations
