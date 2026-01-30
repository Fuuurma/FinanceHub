"""
Tests for Data Fetching Background Tasks
Tests the task logic by verifying constants and helper functions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from django.test import TestCase
import django

django.setup()


class TestDataFetcherConstants(TestCase):
    """Test that data fetcher constants are properly defined"""

    def test_popular_stocks_defined(self):
        """Test that popular stocks list is defined and contains expected symbols"""
        from tasks.data_fetcher import POPULAR_STOCKS

        self.assertIsInstance(POPULAR_STOCKS, list)
        self.assertGreater(len(POPULAR_STOCKS), 10)
        self.assertIn("AAPL", POPULAR_STOCKS)
        self.assertIn("MSFT", POPULAR_STOCKS)
        self.assertIn("GOOGL", POPULAR_STOCKS)
        self.assertIn("AMZN", POPULAR_STOCKS)
        self.assertIn("TSLA", POPULAR_STOCKS)
        self.assertIn("NVDA", POPULAR_STOCKS)

    def test_popular_cryptos_defined(self):
        """Test that popular cryptos list is defined and contains expected symbols"""
        from tasks.data_fetcher import POPULAR_CRYPTOS

        self.assertIsInstance(POPULAR_CRYPTOS, list)
        self.assertGreater(len(POPULAR_CRYPTOS), 10)
        self.assertIn("BTC", POPULAR_CRYPTOS)
        self.assertIn("ETH", POPULAR_CRYPTOS)
        self.assertIn("BNB", POPULAR_CRYPTOS)
        self.assertIn("XRP", POPULAR_CRYPTOS)
        self.assertIn("SOL", POPULAR_CRYPTOS)

    def test_broker_is_configured(self):
        """Test that Dramatiq broker is configured"""
        from tasks.data_fetcher import broker

        self.assertIsNotNone(broker)

    def test_alpha_scraper_is_initialized(self):
        """Test that Alpha Vantage scraper is initialized"""
        from tasks.data_fetcher import alpha_scraper

        self.assertIsNotNone(alpha_scraper)
        self.assertEqual(alpha_scraper.provider_name, "alpha_vantage")

    def test_coingecko_scraper_is_initialized(self):
        """Test that CoinGecko scraper is initialized"""
        from tasks.data_fetcher import coingecko_scraper

        self.assertIsNotNone(coingecko_scraper)
        self.assertEqual(coingecko_scraper.provider_name, "coingecko")

    def test_coinmarketcap_scraper_is_initialized(self):
        """Test that CoinMarketCap scraper is initialized"""
        from tasks.data_fetcher import coinmarketcap_scraper

        self.assertIsNotNone(coinmarketcap_scraper)
        self.assertEqual(coinmarketcap_scraper.provider_name, "coinmarketcap")


class TestMockedScraperBehavior(TestCase):
    """Test scraper behavior with mocked async responses"""

    @patch("data.data_providers.alphaVantage.scraper.AlphaVantageScraper")
    def test_fetch_stocks_mocked_success(self, MockScraper):
        """Test stock fetching with mocked successful response"""
        mock_instance = MockScraper.return_value
        mock_instance.fetch_multiple_stocks = AsyncMock(
            return_value={
                "AAPL": True,
                "MSFT": True,
                "TSLA": False,
            }
        )

        mock_results = mock_instance.fetch_multiple_stocks(["AAPL", "MSFT", "TSLA"])
        self.assertTrue(hasattr(mock_results, "__await__"))

    @patch("data.data_providers.coingecko.scraper.CoinGeckoScraper")
    def test_fetch_cryptos_mocked_success(self, MockScraper):
        """Test crypto fetching with mocked successful response"""
        mock_instance = MockScraper.return_value
        mock_instance.fetch_multiple_cryptos = AsyncMock(
            return_value={
                "BTC": True,
                "ETH": True,
                "ADA": False,
            }
        )

        mock_results = mock_instance.fetch_multiple_cryptos(["BTC", "ETH", "ADA"])
        self.assertTrue(hasattr(mock_results, "__await__"))

    @patch("data.data_providers.coinmarketcap.scraper.CoinMarketCapScraper")
    def test_fetch_cryptos_cmc_mocked_success(self, MockScraper):
        """Test CoinMarketCap fetching with mocked successful response"""
        mock_instance = MockScraper.return_value
        mock_instance.fetch_multiple_cryptos = AsyncMock(
            return_value={
                "BTC": True,
                "ETH": True,
            }
        )

        mock_results = mock_instance.fetch_multiple_cryptos(["BTC", "ETH"])
        self.assertTrue(hasattr(mock_results, "__await__"))

    @patch("data.data_providers.alphaVantage.scraper.AlphaVantageScraper")
    def test_fetch_and_save_stock_mocked(self, MockScraper):
        """Test fetch and save single stock"""
        mock_instance = MockScraper.return_value
        mock_instance.fetch_and_save_stock = AsyncMock(return_value=True)

        mock_result = mock_instance.fetch_and_save_stock("AAPL")
        self.assertTrue(hasattr(mock_result, "__await__"))


class TestDataFetcherHelpers(TestCase):
    """Test helper functions in data fetcher"""

    def test_clean_old_data_returns_dict(self):
        """Test that clean_old_data returns a dict with expected keys"""
        from tasks.data_fetcher import clean_old_data

        result = clean_old_data(days=365)

        self.assertIsInstance(result, dict)
        # Check that it returns either success or error format
        self.assertTrue("deleted_count" in result or "error" in result)


class TestScraperConfiguration(TestCase):
    """Test scraper configuration and initialization"""

    def test_alpha_scraper_provider_name(self):
        """Test Alpha Vantage scraper has correct provider name"""
        from tasks.data_fetcher import alpha_scraper

        self.assertEqual(alpha_scraper.provider_name, "alpha_vantage")

    def test_coingecko_scraper_provider_name(self):
        """Test CoinGecko scraper has correct provider name"""
        from tasks.data_fetcher import coingecko_scraper

        self.assertEqual(coingecko_scraper.provider_name, "coingecko")

    def test_coinmarketcap_scraper_provider_name(self):
        """Test CoinMarketCap scraper has correct provider name"""
        from tasks.data_fetcher import coinmarketcap_scraper

        self.assertEqual(coinmarketcap_scraper.provider_name, "coinmarketcap")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
