"""
Tests for Data Fetching Background Tasks
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import dramatiq
from django.test import TestCase, override_settings
from django.conf import settings
import django

# Setup Django
django.setup()

from tasks.data_fetcher import (
    fetch_stocks_yahoo,
    fetch_stocks_alpha,
    fetch_cryptos_binance,
    fetch_cryptos_coingecko,
    fetch_cryptos_coinmarketcap,
    fetch_all_markets,
    update_asset_price,
    clean_old_data,
    POPULAR_STOCKS,
    POPULAR_CRYPTOS
)


@pytest.mark.dramatiq
class TestBackgroundTasks(TestCase):
    """Test background task scheduling and execution"""
    
    def setUp(self):
        self.broker = dramatiq.get_broker()
    
    @patch('tasks.data_fetcher.yahoo_scraper')
    def test_fetch_stocks_yahoo_success(self, mock_scraper):
        """Test successful stock fetch from Yahoo"""
        mock_scraper.fetch_multiple_stocks.return_value = {
            'AAPL': True,
            'MSFT': True,
            'GOOGL': False
        }
        
        result = fetch_stocks_yahoo(['AAPL', 'MSFT', 'GOOGL'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], 'yahoo')
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['success'], 2)
        self.assertEqual(result['failed'], 1)
        self.assertIn('timestamp', result)
    
    @patch('tasks.data_fetcher.yahoo_scraper')
    def test_fetch_stocks_yahoo_default_symbols(self, mock_scraper):
        """Test Yahoo fetch with default symbols"""
        mock_scraper.fetch_multiple_stocks.return_value = {
            symbol: True for symbol in POPULAR_STOCKS[:20]
        }
        
        result = fetch_stocks_yahoo()
        
        self.assertEqual(result['total'], 20)
        self.assertEqual(result['success'], 20)
    
    @patch('tasks.data_fetcher.alpha_scraper')
    def test_fetch_stocks_alpha_success(self, mock_scraper):
        """Test successful stock fetch from Alpha Vantage"""
        mock_scraper.fetch_multiple_stocks.return_value = {
            'AAPL': True,
            'MSFT': True,
            'TSLA': False
        }
        
        result = fetch_stocks_alpha(['AAPL', 'MSFT', 'TSLA'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], 'alpha_vantage')
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['success'], 2)
        self.assertEqual(result['failed'], 1)
    
    @patch('tasks.data_fetcher.binance_scraper')
    def test_fetch_cryptos_binance_success(self, mock_scraper):
        """Test successful crypto fetch from Binance"""
        mock_scraper.fetch_multiple_cryptos.return_value = {
            'BTC': True,
            'ETH': True,
            'SOL': False
        }
        
        result = fetch_cryptos_binance(['BTC', 'ETH', 'SOL'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], 'binance')
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['success'], 2)
    
    @patch('tasks.data_fetcher.coingecko_scraper')
    def test_fetch_cryptos_coingecko_success(self, mock_scraper):
        """Test successful crypto fetch from CoinGecko"""
        mock_scraper.fetch_multiple_cryptos.return_value = {
            'BTC': True,
            'ETH': True,
            'ADA': False
        }
        
        result = fetch_cryptos_coingecko(['BTC', 'ETH', 'ADA'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], 'coingecko')
        self.assertEqual(result['total'], 3)
    
    @patch('tasks.data_fetcher.coinmarketcap_scraper')
    def test_fetch_cryptos_coinmarketcap_success(self, mock_scraper):
        """Test successful crypto fetch from CoinMarketCap"""
        mock_scraper.fetch_multiple_cryptos.return_value = {
            'BTC': True,
            'ETH': False
        }
        
        result = fetch_cryptos_coinmarketcap(['BTC', 'ETH'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], 'coinmarketcap')
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['success'], 1)
    
    @patch('tasks.data_fetcher.fetch_stocks_yahoo')
    @patch('tasks.data_fetcher.fetch_stocks_alpha')
    @patch('tasks.data_fetcher.fetch_cryptos_binance')
    @patch('tasks.data_fetcher.fetch_cryptos_coingecko')
    @patch('tasks.data_fetcher.fetch_cryptos_coinmarketcap')
    def test_fetch_all_markets_success(self, mock_cmc, mock_cg, mock_binance, mock_alpha, mock_yahoo):
        """Test fetching from all markets"""
        mock_yahoo.return_value = {'success': True}
        mock_alpha.return_value = {'success': True}
        mock_binance.return_value = {'success': True}
        mock_cg.return_value = {'success': True}
        mock_cmc.return_value = {'success': True}
        
        result = fetch_all_markets()
        
        self.assertIsInstance(result, dict)
        self.assertIn('completed_at', result)
        self.assertEqual(len(result['sources']), 5)
    
    @patch('tasks.data_fetcher.yahoo_scraper')
    def test_update_asset_price_stock(self, mock_scraper):
        """Test updating a single stock price"""
        mock_scraper.fetch_and_save_stock.return_value = True
        
        result = update_asset_price('AAPL', 'yahoo')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['source'], 'yahoo')
        self.assertTrue(result['success'])
        mock_scraper.fetch_and_save_stock.assert_called_once_with('AAPL')
    
    @patch('tasks.data_fetcher.binance_scraper')
    def test_update_asset_price_crypto(self, mock_scraper):
        """Test updating a single crypto price"""
        mock_scraper.fetch_and_save_crypto.return_value = True
        
        result = update_asset_price('BTC', 'binance')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], 'BTC')
        self.assertEqual(result['source'], 'binance')
        self.assertTrue(result['success'])
        mock_scraper.fetch_and_save_crypto.assert_called_once_with('BTC')
    
    def test_update_asset_price_unknown_source(self):
        """Test updating with unknown source"""
        result = update_asset_price('AAPL', 'unknown')
        
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
    
    @patch('tasks.data_fetcher.AssetPricesHistoric')
    def test_clean_old_data(self, mock_prices):
        """Test cleaning old historical data"""
        mock_prices.objects.filter.return_value.delete.return_value = (1000, {})
        
        result = clean_old_data(days=365)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['deleted_count'], 1000)
        self.assertEqual(result['cutoff_days'], 365)
    
    @patch('tasks.data_fetcher.yahoo_scraper')
    def test_fetch_error_handling(self, mock_scraper):
        """Test error handling in fetch tasks"""
        mock_scraper.fetch_multiple_stocks.side_effect = Exception("Network error")
        
        result = fetch_stocks_yahoo(['AAPL'])
        
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
        self.assertIn('Network error', result['error'])


class TestTaskScheduling(TestCase):
    """Test task scheduling configuration"""
    
    def test_popular_stocks_defined(self):
        """Test that popular stocks list is defined"""
        self.assertIsInstance(POPULAR_STOCKS, list)
        self.assertGreater(len(POPULAR_STOCKS), 0)
        self.assertIn('AAPL', POPULAR_STOCKS)
        self.assertIn('MSFT', POPULAR_STOCKS)
        self.assertIn('TSLA', POPULAR_STOCKS)
    
    def test_popular_cryptos_defined(self):
        """Test that popular cryptos list is defined"""
        self.assertIsInstance(POPULAR_CRYPTOS, list)
        self.assertGreater(len(POPULAR_CRYPTOS), 0)
        self.assertIn('BTC', POPULAR_CRYPTOS)
        self.assertIn('ETH', POPULAR_CRYPTOS)
        self.assertIn('SOL', POPULAR_CRYPTOS)
    
    def test_constants_length(self):
        """Test that constants have reasonable length"""
        self.assertGreaterEqual(len(POPULAR_STOCKS), 30)
        self.assertGreaterEqual(len(POPULAR_CRYPTOS), 20)


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
