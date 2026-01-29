"""
Data migration to populate sector_fk and industry_fk from existing string values.
"""

from django.db import migrations, models


def migrate_sector_industry_to_fk(apps, schema_editor):
    """Migrate sector and industry string values to foreign keys."""
    Asset = apps.get_model("assets", "Asset")
    Sector = apps.get_model("assets", "Sector")
    Industry = apps.get_model("assets", "Industry")

    assets = Asset.objects.filter(is_deleted=False)

    for asset in assets:
        sector_updated = False
        industry_updated = False

        # Try to find matching sector
        if asset.sector:
            sector = Sector.objects.filter(models__iexact=asset.sector).first()
            if not sector:
                sector = Sector.objects.filter(code__iexact=asset.sector).first()
            if sector:
                asset.sector_fk = sector
                sector_updated = True

        # Try to find matching industry
        if asset.industry:
            industry = Industry.objects.filter(name__iexact=asset.industry).first()
            if not industry:
                industry = Industry.objects.filter(code__iexact=asset.industry).first()
            if industry:
                asset.industry_fk = industry
                industry_updated = True

        if sector_updated or industry_updated:
            asset.save(update_fields=["sector_fk", "industry_fk", "updated_at"])


def reverse_migration(apps, schema_editor):
    """Reverse migration - clear FK fields."""
    Asset = apps.get_model("assets", "Asset")
    Asset.objects.filter(is_deleted=False).update(sector_fk=None, industry_fk=None)


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0008_add_sector_industry_timezone_models"),
    ]

    operations = [
        migrations.RunPython(migrate_sector_industry_to_fk, reverse_migration),
    ]
