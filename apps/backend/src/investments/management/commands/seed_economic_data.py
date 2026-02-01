"""
Management command to seed FRED economic indicators
Populates the database with popular economic indicators for the dashboard
"""

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Seed FRED economic indicators for the dashboard"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fetch-data",
            action="store_true",
            help="Fetch actual data from FRED API (requires FRED_API_KEY)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Number of observations to fetch per indicator",
        )

    def handle(self, *args, **options):
        from investments.models.economic_indicator import (
            EconomicIndicator,
            EconomicDataPoint,
        )
        from data.data_providers.fred.scraper import FREDScraper

        fetch_data = options["fetch_data"]
        limit = options["limit"]

        # Popular series to seed
        popular_series = [
            # GDP and Growth
            {"series_id": "GDP", "title": "Gross Domestic Product", "category": "gdp"},
            {
                "series_id": "GDPC1",
                "title": "Real Gross Domestic Product",
                "category": "gdp",
            },
            # Inflation
            {
                "series_id": "CPIAUCSL",
                "title": "Consumer Price Index",
                "category": "inflation",
            },
            {
                "series_id": "CPILFESL",
                "title": "Core CPI (Less Food & Energy)",
                "category": "inflation",
            },
            {
                "series_id": "PCEPI",
                "title": "Personal Consumption Expenditures",
                "category": "inflation",
            },
            # Employment
            {
                "series_id": "UNRATE",
                "title": "Unemployment Rate",
                "category": "employment",
            },
            {
                "series_id": "PAYEMS",
                "title": "All Employees: Nonfarm Payrolls",
                "category": "employment",
            },
            # Interest Rates
            {
                "series_id": "FEDFUNDS",
                "title": "Federal Funds Effective Rate",
                "category": "interest_rates",
            },
            {
                "series_id": "DGS10",
                "title": "10-Year Treasury Constant Maturity",
                "category": "interest_rates",
            },
            {
                "series_id": "DGS2",
                "title": "2-Year Treasury Constant Maturity",
                "category": "interest_rates",
            },
            # Housing
            {"series_id": "HOUST", "title": "Housing Starts", "category": "housing"},
            {
                "series_id": "PERMIT",
                "title": "New Private Housing Units Authorized",
                "category": "housing",
            },
            # Consumer
            {
                "series_id": "UMCSENT",
                "title": "University of Michigan Consumer Sentiment",
                "category": "consumer",
            },
            # Industrial
            {
                "series_id": "IPMAN",
                "title": "Industrial Production Index",
                "category": "industrial",
            },
        ]

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Seeding FRED Economic Indicators")
        self.stdout.write("=" * 60 + "\n")

        if fetch_data:
            api_key = os.getenv("FRED_API_KEY")
            if not api_key:
                self.stdout.write(
                    self.style.ERROR(
                        "FRED_API_KEY not set. Set it in .env or use --metadata-only."
                    )
                )
                return

            scraper = FREDScraper(api_key=api_key)

            for series_info in popular_series:
                series_id = series_info["series_id"]
                self.stdout.write(f"Processing {series_id}...")

                try:
                    # Fetch series info
                    info = scraper.get_series_info(series_id)
                    if not info or "seriess" not in info:
                        self.stdout.write(self.style.WARNING(f"  ✗ Series not found"))
                        continue

                    series_data = info["seriess"][0]

                    # Create or update indicator
                    indicator, created = EconomicIndicator.objects.update_or_create(
                        series_id=series_id,
                        defaults={
                            "title": series_data.get("title", series_info["title"]),
                            "description": series_data.get("notes", ""),
                            "units": series_data.get("units", ""),
                            "frequency": series_data.get("frequency", ""),
                            "seasonal_adjustment": series_data.get(
                                "seasonal_adjustment", ""
                            ),
                            "last_updated": timezone.now(),
                            "observation_start": timezone.datetime.strptime(
                                series_data.get("observation_start", "1900-01-01"),
                                "%Y-%m-%d",
                            ).date()
                            if series_data.get("observation_start")
                            else None,
                            "observation_end": timezone.datetime.strptime(
                                series_data.get("observation_end", "1900-01-01"),
                                "%Y-%m-%d",
                            ).date()
                            if series_data.get("observation_end")
                            else None,
                            "popularity_score": series_data.get("popularity", 50),
                            "tags": [series_info["category"]],
                        },
                    )

                    # Fetch observations
                    obs_data = scraper.get_series_data(series_id, limit=limit)
                    if obs_data and "observations" in obs_data:
                        count = 0
                        for obs in obs_data["observations"][:limit]:
                            if obs.get("value") and obs["value"] != ".":
                                try:
                                    EconomicDataPoint.objects.update_or_create(
                                        indicator=indicator,
                                        date=timezone.datetime.strptime(
                                            obs["date"], "%Y-%m-%d"
                                        ).date(),
                                        realtime_start=timezone.datetime.strptime(
                                            obs.get("realtime_start", obs["date"]),
                                            "%Y-%m-%d",
                                        ).date(),
                                        defaults={
                                            "value": obs["value"],
                                            "realtime_end": timezone.datetime.strptime(
                                                obs.get("realtime_end", obs["date"]),
                                                "%Y-%m-%d",
                                            ).date(),
                                        },
                                    )
                                    count += 1
                                except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                                    logger.error(f"Error saving data point: {e}")

                        status = "Created" if created else "Updated"
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ {status} - {count} observations")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ No observations found")
                        )

                except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Error: {e}"))
                    logger.error(f"Error processing {series_id}: {e}")

        else:
            # Create metadata only (no data fetching)
            for series_info in popular_series:
                series_id = series_info["series_id"]
                self.stdout.write(f"Creating {series_id}...")

                indicator, created = EconomicIndicator.objects.get_or_create(
                    series_id=series_id,
                    defaults={
                        "title": series_info["title"],
                        "description": f"Economic indicator for {series_info['title']}",
                        "units": "N/A",
                        "frequency": "m",
                        "seasonal_adjustment": "",
                        "last_updated": timezone.now(),
                        "popularity_score": 50,
                        "tags": [series_info["category"]],
                    },
                )

                status = "Created" if created else "Already exists"
                self.stdout.write(self.style.SUCCESS(f"  ✓ {status}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Seed complete!")
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nTotal indicators: {EconomicIndicator.objects.count()}")
        self.stdout.write(f"Total data points: {EconomicDataPoint.objects.count()}")

        if not fetch_data:
            self.stdout.write(
                "\nRun with --fetch-data to fetch actual data from FRED API"
            )
            self.stdout.write(
                "Example: python manage.py seed_economic_data --fetch-data --limit 50"
            )
