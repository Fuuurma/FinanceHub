"""
Django Management Command: Seed Exchanges

Seed the Exchange table with major global stock, crypto, and commodity exchanges.

Usage:
    python manage.py seed_exchanges
"""

import os
import sys
from django.core.management.base import BaseCommand
from django.db import transaction

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import django

django.setup()

from assets.models.exchange import Exchange
from assets.models.country import Country


class Command(BaseCommand):
    help = "Seed the Exchange table with major global exchanges"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            dest="clear",
            help="Clear existing exchanges before seeding",
        )

    def handle(self, *args, **options):
        # Clear existing data if requested
        if options.get("clear"):
            self.stdout.write(self.style.WARNING("Clearing existing exchanges..."))
            Exchange.objects.all().delete()

        # Get country references
        countries = {c.code: c for c in Country.objects.all()}

        # Major global exchanges data
        exchanges_data = [
            # North America - Stock Exchanges
            {
                "code": "NYSE",
                "name": "New York Stock Exchange",
                "mic": "XNYS",
                "country_code": "US",
                "timezone": "America/New_York",
                "operating_hours": '{"monday_friday": "09:30-16:00", "timezone": "EST"}',
                "website": "https://www.nyse.com",
            },
            {
                "code": "NASDAQ",
                "name": "NASDAQ Stock Market",
                "mic": "XNAS",
                "country_code": "US",
                "timezone": "America/New_York",
                "operating_hours": '{"monday_friday": "09:30-16:00", "timezone": "EST"}',
                "website": "https://www.nasdaq.com",
            },
            {
                "code": "TSX",
                "name": "Toronto Stock Exchange",
                "mic": "XTSE",
                "country_code": "CA",
                "timezone": "America/Toronto",
                "operating_hours": '{"monday_friday": "09:30-16:00", "timezone": "EST"}',
                "website": "https://www.tsx.com",
            },
            {
                "code": "BMV",
                "name": "Mexican Stock Exchange",
                "mic": "XMEX",
                "country_code": "MX",
                "timezone": "America/Mexico_City",
                "operating_hours": '{"monday_friday": "08:30-15:00", "timezone": "CST"}',
                "website": "https://www.bmv.com.mx",
            },
            # Europe - Stock Exchanges
            {
                "code": "LSE",
                "name": "London Stock Exchange",
                "mic": "XLON",
                "country_code": "GB",
                "timezone": "Europe/London",
                "operating_hours": '{"monday_friday": "08:00-16:30", "timezone": "GMT"}',
                "website": "https://www.londonstockexchange.com",
            },
            {
                "code": "EURONEXT",
                "name": "Euronext",
                "mic": "XEUR",
                "country_code": "NL",
                "timezone": "Europe/Amsterdam",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.euronext.com",
            },
            {
                "code": "XETRA",
                "name": "Xetra",
                "mic": "XBER",
                "country_code": "DE",
                "timezone": "Europe/Berlin",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.xetra.com",
            },
            {
                "code": "SIX",
                "name": "SIX Swiss Exchange",
                "mic": "XSWX",
                "country_code": "CH",
                "timezone": "Europe/Zurich",
                "operating_hours": '{"monday_friday": "09:00-17:20", "timezone": "CET"}',
                "website": "https://www.six-group.com",
            },
            {
                "code": "MIL",
                "name": "Borsa Italiana",
                "mic": "XMIL",
                "country_code": "IT",
                "timezone": "Europe/Rome",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.borsaitaliana.it",
            },
            {
                "code": "FP",
                "name": "Euronext Paris",
                "mic": "XPAR",
                "country_code": "FR",
                "timezone": "Europe/Paris",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.euronext.com",
            },
            {
                "code": "IBEX",
                "name": "Bolsa de Madrid",
                "mic": "XMAD",
                "country_code": "ES",
                "timezone": "Europe/Madrid",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.bolsamadrid.es",
            },
            {
                "code": "ASE",
                "name": "Euronext Amsterdam",
                "mic": "XAMS",
                "country_code": "NL",
                "timezone": "Europe/Amsterdam",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.euronext.com",
            },
            {
                "code": "OSE",
                "name": "Oslo Børs",
                "mic": "XOSL",
                "country_code": "NO",
                "timezone": "Europe/Oslo",
                "operating_hours": '{"monday_friday": "09:00-16:20", "timezone": "CET"}',
                "website": "https://www.oslobors.no",
            },
            {
                "code": "OMX",
                "name": "Nasdaq Stockholm",
                "mic": "XSTO",
                "country_code": "SE",
                "timezone": "Europe/Stockholm",
                "operating_hours": '{"monday_friday": "09:00-17:30", "timezone": "CET"}',
                "website": "https://www.nasdaqomxnordic.com",
            },
            {
                "code": "HEL",
                "name": "Nasdaq Helsinki",
                "mic": "XHEL",
                "country_code": "FI",
                "timezone": "Europe/Helsinki",
                "operating_hours": '{"monday_friday": "10:00-18:30", "timezone": "EET"}',
                "website": "https://www.nasdaqhelsinki.com",
            },
            {
                "code": "CPH",
                "name": "Nasdaq Copenhagen",
                "mic": "XCSE",
                "country_code": "DK",
                "timezone": "Europe/Copenhagen",
                "operating_hours": '{"monday_friday": "09:00-17:00", "timezone": "CET"}',
                "website": "https://www.nasdaqcopenhagen.com",
            },
            {
                "code": "WSE",
                "name": "Warsaw Stock Exchange",
                "mic": "XWAR",
                "country_code": "PL",
                "timezone": "Europe/Warsaw",
                "operating_hours": '{"monday_friday": "09:00-17:20", "timezone": "CET"}',
                "website": "https://www.gpw.pl",
            },
            {
                "code": "PX",
                "name": "Prague Stock Exchange",
                "mic": "XPRG",
                "country_code": "CZ",
                "timezone": "Europe/Prague",
                "operating_hours": '{"monday_friday": "09:00-16:20", "timezone": "CET"}',
                "website": "https://www.pse.cz",
            },
            {
                "code": "BUD",
                "name": "Budapest Stock Exchange",
                "mic": "XBUD",
                "country_code": "HU",
                "timezone": "Europe/Budapest",
                "operating_hours": '{"monday_friday": "09:00-17:00", "timezone": "CET"}',
                "website": "https://www.bse.hu",
            },
            {
                "code": "MOEX",
                "name": "Moscow Exchange",
                "mic": "XMOEX",
                "country_code": "RU",
                "timezone": "Europe/Moscow",
                "operating_hours": '{"monday_friday": "09:30-18:45", "timezone": "MSK"}',
                "website": "https://www.moex.com",
            },
            # Asia-Pacific - Stock Exchanges
            {
                "code": "TSE",
                "name": "Tokyo Stock Exchange",
                "mic": "XTKS",
                "country_code": "JP",
                "timezone": "Asia/Tokyo",
                "operating_hours": '{"monday_friday": "09:00-15:00", "timezone": "JST"}',
                "website": "https://www.jpx.co.jp",
            },
            {
                "code": "HKEX",
                "name": "Hong Kong Stock Exchange",
                "mic": "XHKG",
                "country_code": "HK",
                "timezone": "Asia/Hong_Kong",
                "operating_hours": '{"monday_friday": "09:30-16:00", "timezone": "HKT"}',
                "website": "https://www.hkex.com.hk",
            },
            {
                "code": "SSE",
                "name": "Shanghai Stock Exchange",
                "mic": "XSHG",
                "country_code": "CN",
                "timezone": "Asia/Shanghai",
                "operating_hours": '{"monday_friday": "09:30-15:00", "timezone": "CST"}',
                "website": "https://english.sse.com.cn",
            },
            {
                "code": "SZSE",
                "name": "Shenzhen Stock Exchange",
                "mic": "XSHZ",
                "country_code": "CN",
                "timezone": "Asia/Shanghai",
                "operating_hours": '{"monday_friday": "09:30-15:00", "timezone": "CST"}',
                "website": "https://www.szse.cn",
            },
            {
                "code": "KRX",
                "name": "Korea Exchange",
                "mic": "XKRX",
                "country_code": "KR",
                "timezone": "Asia/Seoul",
                "operating_hours": '{"monday_friday": "09:00-15:30", "timezone": "KST"}',
                "website": "https://www.krx.co.kr",
            },
            {
                "code": "TWSE",
                "name": "Taiwan Stock Exchange",
                "mic": "XTAI",
                "country_code": "TW",
                "timezone": "Asia/Taipei",
                "operating_hours": '{"monday_friday": "09:00-13:30", "timezone": "TST"}',
                "website": "https://www.twse.com.tw",
            },
            {
                "code": "ASX",
                "name": "Australian Securities Exchange",
                "mic": "XASX",
                "country_code": "AU",
                "timezone": "Australia/Sydney",
                "operating_hours": '{"monday_friday": "10:00-16:00", "timezone": "AEST"}',
                "website": "https://www.asx.com.au",
            },
            {
                "code": "NZX",
                "name": "New Zealand Exchange",
                "mic": "XNZE",
                "country_code": "NZ",
                "timezone": "Pacific/Auckland",
                "operating_hours": '{"monday_friday": "10:00-17:00", "timezone": "NZST"}',
                "website": "https://www.nzx.com",
            },
            {
                "code": "SGX",
                "name": "Singapore Exchange",
                "mic": "XSES",
                "country_code": "SG",
                "timezone": "Asia/Singapore",
                "operating_hours": '{"monday_friday": "09:00-17:00", "timezone": "SGT"}',
                "website": "https://www.sgx.com",
            },
            {
                "code": "BSE",
                "name": "Bombay Stock Exchange",
                "mic": "XBOM",
                "country_code": "IN",
                "timezone": "Asia/Kolkata",
                "operating_hours": '{"monday_friday": "09:15-15:30", "timezone": "IST"}',
                "website": "https://www.bseindia.com",
            },
            {
                "code": "NSE",
                "name": "National Stock Exchange of India",
                "mic": "XNSE",
                "country_code": "IN",
                "timezone": "Asia/Kolkata",
                "operating_hours": '{"monday_friday": "09:15-15:30", "timezone": "IST"}',
                "website": "https://www.nseindia.com",
            },
            {
                "code": "IDX",
                "name": "Indonesia Stock Exchange",
                "mic": "XIDX",
                "country_code": "ID",
                "timezone": "Asia/Jakarta",
                "operating_hours": '{"monday_friday": "09:00-15:00", "timezone": "WIB"}',
                "website": "https://www.idx.co.id",
            },
            {
                "code": "MYX",
                "name": "Bursa Malaysia",
                "mic": "XKLS",
                "country_code": "MY",
                "timezone": "Asia/Kuala_Lumpur",
                "operating_hours": '{"monday_friday": "09:00-17:00", "timezone": "MYT"}',
                "website": "https://www.bursamalaysia.com",
            },
            {
                "code": "PSE",
                "name": "Philippine Stock Exchange",
                "mic": "XPHS",
                "country_code": "PH",
                "timezone": "Asia/Manila",
                "operating_hours": '{"monday_friday": "09:30-15:30", "timezone": "PHT"}',
                "website": "https://www.pse.ph",
            },
            {
                "code": "HOSE",
                "name": "Ho Chi Minh City Stock Exchange",
                "mic": "XHVN",
                "country_code": "VN",
                "timezone": "Asia/Ho_Chi_Minh",
                "operating_hours": '{"monday_friday": "09:00-15:00", "timezone": "ICT"}',
                "website": "https://www.hsx.vn",
            },
            {
                "code": "SET",
                "name": "Stock Exchange of Thailand",
                "mic": "XBKK",
                "country_code": "TH",
                "timezone": "Asia/Bangkok",
                "operating_hours": '{"monday_friday": "10:00-16:30", "timezone": "ICT"}',
                "website": "https://www.set.or.th",
            },
            {
                "code": "PKSE",
                "name": "Pakistan Stock Exchange",
                "mic": "XKAR",
                "country_code": "PK",
                "timezone": "Asia/Karachi",
                "operating_hours": '{"monday_friday": "09:30-16:00", "timezone": "PKT"}',
                "website": "https://www.psx.com.pk",
            },
            # Crypto Exchanges
            {
                "code": "Binance",
                "name": "Binance",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.binance.com",
            },
            {
                "code": "Coinbase",
                "name": "Coinbase Exchange",
                "mic": "XCBE",
                "country_code": "US",
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.coinbase.com",
            },
            {
                "code": "Kraken",
                "name": "Kraken",
                "mic": None,
                "country_code": "US",
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.kraken.com",
            },
            {
                "code": "Bybit",
                "name": "Bybit",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.bybit.com",
            },
            {
                "code": "OKX",
                "name": "OKX",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.okx.com",
            },
            {
                "code": "Bitfinex",
                "name": "Bitfinex",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.bitfinex.com",
            },
            {
                "code": "KuCoin",
                "name": "KuCoin",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.kucoin.com",
            },
            {
                "code": "Bitstamp",
                "name": "Bitstamp",
                "mic": "XSTG",
                "country_code": "LU",
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.bitstamp.net",
            },
            {
                "code": "Gate.io",
                "name": "Gate.io",
                "mic": None,
                "country_code": None,
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.gate.io",
            },
            {
                "code": "Gemini",
                "name": "Gemini",
                "mic": "XCNG",
                "country_code": "US",
                "timezone": "UTC",
                "operating_hours": '{"24_7": true}',
                "website": "https://www.gemini.com",
            },
            # Commodity & Futures Exchanges
            {
                "code": "CME",
                "name": "Chicago Mercantile Exchange",
                "mic": "XCME",
                "country_code": "US",
                "timezone": "America/Chicago",
                "operating_hours": '{"sunday_friday": "18:00-17:00", "timezone": "CT"}',
                "website": "https://www.cmegroup.com",
            },
            {
                "code": "ICE",
                "name": "Intercontinental Exchange",
                "mic": "XICE",
                "country_code": "US",
                "timezone": "America/New_York",
                "operating_hours": '{"sunday_friday": "20:00-17:00", "timezone": "ET"}',
                "website": "https://www.theice.com",
            },
            {
                "code": "LME",
                "name": "London Metal Exchange",
                "mic": "XLME",
                "country_code": "GB",
                "timezone": "Europe/London",
                "operating_hours": '{"monday_friday": "01:00-19:00", "timezone": "GMT"}',
                "website": "https://www.lme.com",
            },
        ]

        # Use transaction for atomic operation
        with transaction.atomic():
            # Track statistics
            created_count = 0
            updated_count = 0

            for exchange_data in exchanges_data:
                code = exchange_data["code"]
                country_code = exchange_data.get("country_code", None)

                # Get country object
                country = countries.get(country_code, None) if country_code else None
                exchange_data["country"] = country

                # Remove country_code as it's not a model field
                exchange_data.pop("country_code", None)

                # Check if exchange already exists
                exchange = Exchange.objects.filter(code=code).first()

                if exchange:
                    # Update existing exchange
                    for key, value in exchange_data.items():
                        if key != "code":  # Don't update the primary key
                            setattr(exchange, key, value)
                    exchange.save()
                    updated_count += 1
                else:
                    # Create new exchange
                    Exchange.objects.create(**exchange_data)
                    created_count += 1

            # Display results
            total_count = len(exchanges_data)
            stock_count = sum(
                1
                for e in exchanges_data
                if not e.get("website", "").startswith("https://www.binance")
                and "24_7" not in e.get("operating_hours", "{}")
            )
            crypto_count = sum(
                1 for e in exchanges_data if "24_7" in e.get("operating_hours", "{}")
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully seeded {total_count} exchanges:")
            )
            self.stdout.write(f"  - Stock/Commodity: {stock_count}")
            self.stdout.write(f"  - Crypto: {crypto_count}")
            self.stdout.write(f"  - Created: {created_count}")
            self.stdout.write(f"  - Updated: {updated_count}")
            self.stdout.write(
                f"  - Total: {Exchange.objects.count()} exchanges in database"
            )

            self.stdout.write(self.style.SUCCESS("✅ Exchanges seeded successfully!"))
