"""
Django management command to test SEC Edgar integration
Fetches company info and filings from SEC
"""

import os
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

from data.data_providers.sec_edgar.scraper import SECEDGARScraper
from assets.models.asset import Asset
from investments.models.data_provider import DataProvider


class Command(BaseCommand):
    help = "Test SEC Edgar integration by fetching company filings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="AAPL",
            help="Symbol to fetch data for (default: AAPL)",
        )
        parser.add_argument(
            "--company", action="store_true", help="Fetch company information"
        )
        parser.add_argument(
            "--filings", action="store_true", help="Fetch company filings"
        )
        parser.add_argument(
            "--10k", action="store_true", help="Fetch annual reports (10-K)"
        )
        parser.add_argument(
            "--10q", action="store_true", help="Fetch quarterly reports (10-Q)"
        )
        parser.add_argument(
            "--8k", action="store_true", help="Fetch current reports (8-K)"
        )
        parser.add_argument(
            "--insider", action="store_true", help="Fetch insider transactions (Form 4)"
        )
        parser.add_argument(
            "--summary", action="store_true", help="Fetch filings summary"
        )
        parser.add_argument(
            "--recent",
            action="store_true",
            help="Fetch most recent filings",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of filings to fetch (default: 5)",
        )
        parser.add_argument(
            "--all", action="store_true", help="Test all SEC Edgar endpoints"
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        self.stdout.write(f"Testing SEC Edgar integration for {symbol}...\n")

        scraper = SECEDGARScraper()

        # Get or create data provider
        provider, _ = DataProvider.objects.get_or_create(
            name="sec_edgar",
            defaults={
                "display_name": "SEC Edgar",
                "api_key": "public",
                "is_active": True,
            },
        )

        # Get asset
        asset = Asset.objects.filter(ticker__iexact=symbol).first()
        if not asset:
            self.stdout.write(f"WARNING: Asset {symbol} not found in database\n")
            self.stdout.write(f"Continuing with test anyway...\n")

        # Run tests based on flags
        if options["all"] or not any(
            [
                options["company"],
                options["filings"],
                options["10k"],
                options["10q"],
                options["8k"],
                options["insider"],
                options["summary"],
                options["recent"],
            ]
        ):
            # Run all tests by default
            self.test_company_info(scraper, symbol)
            self.test_filings_summary(scraper, symbol)
            self.test_annual_reports(scraper, symbol, options["count"])
            self.test_quarterly_reports(scraper, symbol, options["count"])
            self.test_current_reports(scraper, symbol, options["count"])
            self.test_insider_transactions(scraper, symbol, options["count"])
            self.test_recent_filings(scraper, symbol, options["count"])
        else:
            if options["company"]:
                self.test_company_info(scraper, symbol)
            if options["summary"]:
                self.test_filings_summary(scraper, symbol)
            if options["10k"]:
                self.test_annual_reports(scraper, symbol, options["count"])
            if options["10q"]:
                self.test_quarterly_reports(scraper, symbol, options["count"])
            if options["8k"]:
                self.test_current_reports(scraper, symbol, options["count"])
            if options["insider"]:
                self.test_insider_transactions(scraper, symbol, options["count"])
            if options["recent"]:
                self.test_recent_filings(scraper, symbol, options["count"])
            if options["filings"]:
                self.test_company_filings(scraper, symbol, options["count"])

        self.stdout.write("\n✅ SEC Edgar integration test complete!\n")

    def test_company_info(self, scraper, symbol):
        """Test company information endpoint"""
        self.stdout.write(f"\n=== Testing Company Info for {symbol} ===\n")

        try:
            info = scraper.get_company_info(symbol)

            if not info:
                self.stdout.write("  ✗ No company info found\n")
                return

            self.stdout.write(f"  Name: {info.get('name', 'N/A')}\n")
            self.stdout.write(f"  CIK: {info.get('cik', 'N/A')}\n")
            self.stdout.write(
                f"  SIC: {info.get('sic', 'N/A')} - {info.get('sic_description', 'N/A')}\n"
            )
            self.stdout.write(f"  State: {info.get('state_of_incorporation', 'N/A')}\n")
            self.stdout.write(f"  Business: {info.get('state_of_location', 'N/A')}\n")
            self.stdout.write(
                f"  Fiscal Year End: {info.get('fiscal_year_end', 'N/A')}\n"
            )
            self.stdout.write(f"  Last Filing: {info.get('last_filing_date', 'N/A')}\n")
            self.stdout.write(f"  Total Filings: {info.get('number_of_filings', 0)}\n")

            self.stdout.write(f"  ✓ Company info test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_filings_summary(self, scraper, symbol):
        """Test filings summary endpoint"""
        self.stdout.write(f"\n=== Testing Filings Summary for {symbol} ===\n")

        try:
            summary = scraper.get_filings_summary(symbol)

            if not summary:
                self.stdout.write("  ✗ No filings summary found\n")
                return

            # Sort by count
            sorted_filings = sorted(summary.items(), key=lambda x: x[1], reverse=True)

            self.stdout.write(f"  Total filing types: {len(summary)}\n")
            self.stdout.write(f"  Top 10 filing types:\n")

            for filing_type, count in sorted_filings[:10]:
                self.stdout.write(f"    {filing_type}: {count}\n")

            self.stdout.write(f"  ✓ Filings summary test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_annual_reports(self, scraper, symbol, count):
        """Test annual reports (10-K) endpoint"""
        self.stdout.write(f"\n=== Testing Annual Reports (10-K) for {symbol} ===\n")

        try:
            reports = scraper.get_annual_reports(symbol, count=count)

            if not reports:
                self.stdout.write("  ⚠ No annual reports found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(reports)} annual reports\n")

            for i, report in enumerate(reports[:3], 1):
                self.stdout.write(f"    {i}. {report.get('filing_date', 'N/A')}\n")
                self.stdout.write(f"       Form: {report.get('form', 'N/A')}\n")
                self.stdout.write(
                    f"       Accession: {report.get('accession_number', 'N/A')[:20]}...\n"
                )

            self.stdout.write(f"  ✓ Annual reports test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_quarterly_reports(self, scraper, symbol, count):
        """Test quarterly reports (10-Q) endpoint"""
        self.stdout.write(f"\n=== Testing Quarterly Reports (10-Q) for {symbol} ===\n")

        try:
            reports = scraper.get_quarterly_reports(symbol, count=count)

            if not reports:
                self.stdout.write("  ⚠ No quarterly reports found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(reports)} quarterly reports\n")

            for i, report in enumerate(reports[:3], 1):
                self.stdout.write(f"    {i}. {report.get('filing_date', 'N/A')}\n")
                self.stdout.write(
                    f"       Report Date: {report.get('report_date', 'N/A')}\n"
                )
                self.stdout.write(
                    f"       Accession: {report.get('accession_number', 'N/A')[:20]}...\n"
                )

            self.stdout.write(f"  ✓ Quarterly reports test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_current_reports(self, scraper, symbol, count):
        """Test current reports (8-K) endpoint"""
        self.stdout.write(f"\n=== Testing Current Reports (8-K) for {symbol} ===\n")

        try:
            reports = scraper.get_current_reports(symbol, count=count)

            if not reports:
                self.stdout.write("  ⚠ No current reports found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(reports)} current reports\n")

            for i, report in enumerate(reports[:3], 1):
                self.stdout.write(f"    {i}. {report.get('filing_date', 'N/A')}\n")
                self.stdout.write(f"       Size: {report.get('size', 0)} bytes\n")
                self.stdout.write(f"       URL: {report.get('url', 'N/A')[:60]}...\n")

            self.stdout.write(f"  ✓ Current reports test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_insider_transactions(self, scraper, symbol, count):
        """Test insider transactions (Form 4) endpoint"""
        self.stdout.write(
            f"\n=== Testing Insider Transactions (Form 4) for {symbol} ===\n"
        )

        try:
            transactions = scraper.get_insider_transactions(symbol, count=count)

            if not transactions:
                self.stdout.write("  ⚠ No insider transactions found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(transactions)} insider transactions\n")

            for i, txn in enumerate(transactions[:3], 1):
                self.stdout.write(f"    {i}. {txn.get('filing_date', 'N/A')}\n")
                self.stdout.write(
                    f"       Accession: {txn.get('accession_number', 'N/A')[:20]}...\n"
                )
                self.stdout.write(f"       URL: {txn.get('url', 'N/A')[:60]}...\n")

            self.stdout.write(f"  ✓ Insider transactions test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_recent_filings(self, scraper, symbol, count):
        """Test recent filings endpoint"""
        self.stdout.write(f"\n=== Testing Recent Filings for {symbol} ===\n")

        try:
            filings = scraper.get_recent_filings_all(symbol, count=count)

            if not filings:
                self.stdout.write("  ⚠ No recent filings found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(filings)} recent filings\n")

            # Group by form type
            form_counts = {}
            for filing in filings:
                form = filing.get("form", "UNKNOWN")
                form_counts[form] = form_counts.get(form, 0) + 1

            self.stdout.write(f"  Recent filings breakdown:\n")
            for form, count in sorted(
                form_counts.items(), key=lambda x: x[1], reverse=True
            ):
                self.stdout.write(f"    {form}: {count}\n")

            self.stdout.write(f"  ✓ Recent filings test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")

    def test_company_filings(self, scraper, symbol, count):
        """Test company filings endpoint"""
        self.stdout.write(f"\n=== Testing Company Filings for {symbol} ===\n")

        try:
            filings = scraper.get_company_filings(symbol, filing_type="10-K")

            if not filings:
                self.stdout.write("  ⚠ No filings found\n")
                return

            self.stdout.write(f"  ✓ Fetched {len(filings)} filings\n")

            for i, filing in enumerate(filings[:3], 1):
                self.stdout.write(f"    {i}. {filing.get('filing_date', 'N/A')}\n")
                self.stdout.write(f"       Form: {filing.get('form', 'N/A')}\n")
                self.stdout.write(f"       URL: {filing.get('url', 'N/A')[:60]}...\n")

            self.stdout.write(f"  ✓ Company filings test passed\n")

        except Exception as e:
            self.stdout.write(f"  ✗ Error: {e}\n")
