"""
Test command for FRED API integration
Tests various FRED endpoints and data fetching
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Test FRED API integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--series",
            type=str,
            help="Test specific series ID (e.g., GDP, CPIAUCSL, UNRATE)",
        )
        parser.add_argument(
            "--count", type=int, default=5, help="Number of observations to fetch"
        )
        parser.add_argument(
            "--start-date", type=str, help="Observation start date (YYYY-MM-DD)"
        )
        parser.add_argument(
            "--end-date", type=str, help="Observation end date (YYYY-MM-DD)"
        )
        parser.add_argument("--gdp", action="store_true", help="Test GDP endpoints")
        parser.add_argument(
            "--inflation", action="store_true", help="Test CPI inflation endpoints"
        )
        parser.add_argument(
            "--employment", action="store_true", help="Test employment indicators"
        )
        parser.add_argument(
            "--interest-rates", action="store_true", help="Test interest rates"
        )
        parser.add_argument(
            "--housing", action="store_true", help="Test housing indicators"
        )
        parser.add_argument("--all", action="store_true", help="Test all endpoints")

    def handle(self, *args, **options):
        from data.data_providers.fred.scraper import FREDScraper

        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            self.stdout.write(
                self.style.ERROR("FRED_API_KEY environment variable not set")
            )
            return

        scraper = FREDScraper(api_key=api_key)

        if options["all"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing ALL FRED Endpoints")
            self.stdout.write("=" * 60 + "\n")

            self._test_all(scraper, options)

        elif options["series"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(f"Testing Series: {options['series'].upper()}")
            self.stdout.write("=" * 60 + "\n")

            self._test_series(scraper, options["series"], options)

        elif options["gdp"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing GDP Endpoints")
            self.stdout.write("=" * 60 + "\n")

            self._test_gdp(scraper, options)

        elif options["inflation"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing Inflation Endpoints")
            self.stdout.write("=" * 60 + "\n")

            self._test_inflation(scraper, options)

        elif options["employment"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing Employment Indicators")
            self.stdout.write("=" * 60 + "\n")

            self._test_employment(scraper, options)

        elif options["interest_rates"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing Interest Rates")
            self.stdout.write("=" * 60 + "\n")

            self._test_interest_rates(scraper, options)

        elif options["housing"]:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing Housing Indicators")
            self.stdout.write("=" * 60 + "\n")

            self._test_housing(scraper, options)

        else:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Testing Basic FRED Endpoints")
            self.stdout.write("=" * 60 + "\n")

            self._test_basic(scraper, options)

    def _test_series(self, scraper, series_id, options):
        """Test a specific series"""
        self.stdout.write(f"Fetching data for {series_id}...")

        data = scraper.get_series_data(
            series_id,
            observation_start=options.get("start_date"),
            observation_end=options.get("end_date"),
            limit=options["count"],
        )

        if data and "observations" in data:
            obs_count = len(data["observations"])
            self.stdout.write(self.style.SUCCESS(f"✓ Fetched {obs_count} observations"))

            if obs_count > 0:
                latest = data["observations"][-1]
                self.stdout.write(f"  Latest: {latest['date']} = {latest['value']}")

                if obs_count > 1:
                    earliest = data["observations"][0]
                    self.stdout.write(
                        f"  Earliest: {earliest['date']} = {earliest['value']}"
                    )

            info = scraper.get_series_info(series_id)
            if info and "seriess" in info:
                series_info = info["seriess"][0]
                self.stdout.write(f"  Title: {series_info.get('title', 'N/A')}")
                self.stdout.write(f"  Units: {series_info.get('units', 'N/A')}")
                self.stdout.write(f"  Frequency: {series_info.get('frequency', 'N/A')}")
        else:
            self.stdout.write(self.style.ERROR(f"✗ Failed to fetch {series_id}"))

    def _test_gdp(self, scraper, options):
        """Test GDP endpoints"""
        self.stdout.write("1. Real GDP (GDPC1)")
        data = scraper.get_gdp(real_gdp=True)
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n2. Nominal GDP (GDP)")
        data = scraper.get_gdp(real_gdp=False)
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_inflation(self, scraper, options):
        """Test inflation endpoints"""
        self.stdout.write("1. Consumer Price Index (CPI)")
        data = scraper.get_cpi(core=False)
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n2. Core CPI (Excludes Food & Energy)")
        data = scraper.get_cpi(core=True)
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n3. Inflation Data Bundle")
        data = scraper.get_inflation_data()
        if data:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fetched {len(data)} series"))
            for name, value in data.items():
                self.stdout.write(f"    - {name}: {value}")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_employment(self, scraper, options):
        """Test employment indicators"""
        self.stdout.write("1. Unemployment Rate")
        data = scraper.get_unemployment_rate()
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}%")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_interest_rates(self, scraper, options):
        """Test interest rate endpoints"""
        self.stdout.write("1. Federal Funds Rate")
        data = scraper.get_federal_funds_rate()
        if data and "observations" in data:
            latest = data["observations"][-1]
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {latest['date']}: {latest['value']}%")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n2. Treasury Yields")
        yields = scraper.get_all_treasury_yields()

        if yields:
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Fetched {len(yields)} maturities")
            )
            for maturity, data in yields.items():
                rate = data.get("rate")
                date = data.get("date")
                self.stdout.write(f"    - {maturity}: {rate}% ({date})")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n3. Yield Curve Spreads")
        spreads = scraper.get_yield_curve_spread()
        if spreads:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fetched {len(spreads)} spreads"))
            for name, value in spreads.items():
                self.stdout.write(f"    - {name}: {value:.2f}")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_housing(self, scraper, options):
        """Test housing indicators"""
        self.stdout.write("1. Housing Data")
        data = scraper.get_housing_data()

        if data:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fetched {len(data)} indicators"))

            if "housing_starts" in data:
                starts = data["housing_starts"]
                self.stdout.write(
                    f"    - Housing Starts: {starts['value']} ({starts['date']})"
                )

            if "building_permits" in data:
                permits = data["building_permits"]
                self.stdout.write(
                    f"    - Building Permits: {permits['value']} ({permits['date']})"
                )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n2. Mortgage Rates")
        rates = scraper.get_mortgage_rates()

        if rates:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fetched {len(rates)} rates"))
            for term, data in rates.items():
                rate = data.get("rate")
                date = data.get("date")
                self.stdout.write(f"    - {term}: {rate}% ({date})")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_basic(self, scraper, options):
        """Test basic FRED endpoints"""
        self.stdout.write("1. Get Series Info (GDP)")
        info = scraper.get_series_info("GDP")
        if info and "seriess" in info:
            series_info = info["seriess"][0]
            self.stdout.write(self.style.SUCCESS(f"  ✓ {series_info.get('title')}"))
            self.stdout.write(f"    - ID: {series_info.get('id')}")
            self.stdout.write(f"    - Units: {series_info.get('units')}")
            self.stdout.write(f"    - Frequency: {series_info.get('frequency')}")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n2. Get Categories")
        categories = scraper.get_categories()
        if categories:
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Fetched {len(categories)} categories")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n3. Get Releases")
        releases = scraper.get_releases()
        if releases:
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Fetched {len(releases)} releases")
            )
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n4. Search Series")
        results = scraper.get_series_search("inflation", limit=5)
        if results:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Found {len(results)} series"))
            for series in results[:3]:
                self.stdout.write(f"    - {series.get('id')}: {series.get('title')}")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

        self.stdout.write("\n5. Latest Macro Data")
        macro = scraper.get_latest_macro_data()
        if macro:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fetched macro dashboard data"))
            if "unemployment" in macro and macro["unemployment"].get("observations"):
                latest = macro["unemployment"]["observations"][-1]
                self.stdout.write(f"    - Unemployment: {latest['value']}%")
        else:
            self.stdout.write(self.style.ERROR("  ✗ Failed"))

    def _test_all(self, scraper, options):
        """Test all endpoints"""
        self._test_gdp(scraper, options)
        self.stdout.write("\n")

        self._test_inflation(scraper, options)
        self.stdout.write("\n")

        self._test_employment(scraper, options)
        self.stdout.write("\n")

        self._test_interest_rates(scraper, options)
        self.stdout.write("\n")

        self._test_housing(scraper, options)
        self.stdout.write("\n")

        self._test_basic(scraper, options)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("FRED Test Suite Complete")
        self.stdout.write("=" * 60)
