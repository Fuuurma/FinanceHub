"""
Yahoo Finance Scraper Wrapper
Provides compatibility with existing test expectations.
"""

from data.data_providers.yahooFinance.base import YahooFinanceFetcher


# Alias for compatibility
class YahooFinanceScraper(YahooFinanceFetcher):
    """Yahoo Finance Scraper - wrapper for YahooFinanceFetcher"""

    pass


def get_popular_stocks():
    """Get list of popular stocks"""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "JNJ"]


def get_spy_tickers():
    """Get S&P 500 tickers (sample list)"""
    return [
        "AAPL",
        "MSFT",
        "AMZN",
        "GOOGL",
        "META",
        "NVDA",
        "TSLA",
        "JPM",
        "V",
        "JNJ",
        "WMT",
        "PG",
        "MA",
        "UNH",
        "HD",
        "DIS",
        "BAC",
        "ADBE",
        "CRM",
        "PFE",
        "KO",
        "PEP",
        "CSCO",
        "T",
        "NKE",
        "MRK",
        "ABT",
        "ABBV",
        "ACN",
        "LLY",
    ]
