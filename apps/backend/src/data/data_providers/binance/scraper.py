"""
Binance Scraper Wrapper
Provides compatibility with existing test expectations.
"""

from data.data_providers.binance.base import BinanceFetcher


# Alias for compatibility
class BinanceScraper(BinanceFetcher):
    """Binance Scraper - wrapper for BinanceFetcher"""

    pass
