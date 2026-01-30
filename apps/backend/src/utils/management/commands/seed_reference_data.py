from django.core.management.base import BaseCommand
from assets.models import Sector, Industry, Timezone
from utils.seed_data import GICS_SECTORS, GICS_INDUSTRIES, COMMON_TIMEZONES


class Command(BaseCommand):
    help = "Seed reference data for sectors, industries, and timezones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sectors-only",
            action="store_true",
            help="Only seed sectors and industries",
        )
        parser.add_argument(
            "--timezones-only",
            action="store_true",
            help="Only seed timezones",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        sectors_only = options.get("sectors_only")
        timezones_only = options.get("timezones_only")
        reset = options.get("reset")

        if reset:
            if not sectors_only:
                Timezone.objects.all().delete()
                self.stdout.write(self.style.WARNING("Deleted all timezones"))
            if not timezones_only:
                Industry.objects.all().delete()
                Sector.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING("Deleted all sectors and industries")
                )

        if not timezones_only:
            self.seed_sectors_and_industries()

        if not sectors_only:
            self.seed_timezones()

        self.stdout.write(self.style.SUCCESS("Reference data seeded successfully"))

    def seed_sectors_and_industries(self):
        self.stdout.write("Seeding sectors and industries...")

        sectors_created = 0
        for sector_data in GICS_SECTORS:
            sector, created = Sector.objects.update_or_create(
                code=sector_data["code"],
                defaults={
                    "name": sector_data["name"],
                    "description": sector_data["description"],
                    "gics_code": sector_data["gics_code"],
                },
            )
            if created:
                sectors_created += 1

        self.stdout.write(f"Created {sectors_created} sectors")

        industries_created = 0
        for sector_name, sector_code, industries in GICS_INDUSTRIES:
            try:
                sector = Sector.objects.get(code=sector_code)
            except Sector.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Sector {sector_code} not found, skipping industries"
                    )
                )
                continue

            for industry_code, industry_name, gics_code in industries:
                industry, created = Industry.objects.update_or_create(
                    sector=sector,
                    code=industry_code,
                    defaults={
                        "name": industry_name,
                        "gics_code": gics_code,
                    },
                )
                if created:
                    industries_created += 1

        self.stdout.write(f"Created {industries_created} industries")
        self.stdout.write(self.style.SUCCESS("Sectors and industries seeded"))

    def seed_timezones(self):
        self.stdout.write("Seeding timezones...")

        timezones_created = 0
        for tz_data in COMMON_TIMEZONES:
            tz, created = Timezone.objects.update_or_create(
                name=tz_data["name"],
                defaults={
                    "utc_offset": tz_data["utc_offset"],
                    "utc_offset_str": f"UTC{tz_data['utc_offset']:+d}",
                    "abbreviation": tz_data["abbreviation"],
                    "is_dst_observed": tz_data["is_dst_observed"],
                },
            )
            if created:
                timezones_created += 1

        self.stdout.write(f"Created {timezones_created} timezones")
        self.stdout.write(self.style.SUCCESS("Timezones seeded"))
