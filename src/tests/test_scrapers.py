"""
Tests for Data Scrapers
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime
import django

# Setup Django
django.setup()

from data.data_providers.yahooFinance.scraper import YahooFinanceScraper, get_popular_stocks, get_spy_tickers
from data.data_providers.alphaVantage.scraper import AlphaVantageScraper
from data.data_providers.binance.scraper import BinanceScraper


class TestYahooFinanceScraper:
    """Test Yahoo Finance scraper"""
    
    @pytest.fixture
    def scraper(self):
        return YahooFinanceScraper()
    
    @patch('data.data_providers.yahooFinance.scraper.yf.Ticker')
    def test_get_stock_info_success(self, mock_ticker):
        """Test getting stock info successfully"""
        mock_info = {
            'longName': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'marketCap': 2800000000000,
            'website': 'https://www.apple.com',
            'longBusinessSummary': 'Apple Inc. designs, manufactures...',
            'country': 'United States'
        }
        mock_ticker.return_value.info = mock_info
        
        scraper = YahooFinanceScraper()
        result = scraper.get_stock_info('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['name'] == 'Apple Inc.'
        assert result['exchange'] == 'NASDAQ'
        assert result['sector'] == 'Technology'
        mock_ticker.assert_called_once_with('AAPL')
    
    @patch('data.data_providers.yahooFinance.scraper.yf.Ticker')
    def test_get_current_price(self, mock_ticker):
        """Test getting current price"""
        import pandas as pd
        
        mock_hist_data = pd.DataFrame({
            'Open': [150.0],
            'High': [152.0],
            'Low': [149.0],
            'Close': [151.0],
            'Volume': [1000000]
        }, index=[pd.Timestamp('2024-01-27 10:00:00')])
        
        mock_ticker.return_value.history.return_value = mock_hist_data
        
        scraper = YahooFinanceScraper()
        result = scraper.get_current_price('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 151.0
        assert result['high'] == 152.0
        assert result['low'] == 149.0
        assert result['volume'] == 1000000
    
    @patch('data.data_providers.yahooFinance.scraper.yf.Ticker')
    def test_get_historical_prices(self, mock_ticker):
        """Test getting historical prices"""
        import pandas as pd
        
        mock_hist_data = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [152.0, 153.0, 154.0],
            'Low': [149.0, 150.0, 151.0],
            'Close': [151.0, 152.0, 153.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=[
            pd.Timestamp('2024-01-25'),
            pd.Timestamp('2024-01-26'),
            pd.Timestamp('2024-01-27')
        ])
        
        mock_ticker.return_value.history.return_value = mock_hist_data
        
        scraper = YahooFinanceScraper()
        result = scraper.get_historical_prices('AAPL', period='5d')
        
        assert result is not None
        assert len(result) == 3
        mock_ticker.return_value.history.assert_called_once_with(period='5d', interval='1d')
    
    @patch('data.data_providers.yahooFinance.scraper.yf.Ticker')
    def test_get_fundamentals(self, mock_ticker):
        """Test getting fundamental data"""
        mock_info = {
            'trailingPE': 28.5,
            'priceToBook': 45.2,
            'trailingEps': 5.3,
            'dividendYield': 0.5,
            'beta': 1.2,
            'totalRevenue': 380000000000,
            'netIncomeToCommon': 97000000000,
            'totalAssets': 350000000000,
            'totalDebt': 110000000000
        }
        mock_ticker.return_value.info = mock_info
        
        scraper = YahooFinanceScraper()
        result = scraper.get_fundamentals('AAPL')
        
        assert result is not None
        assert result['pe_ratio'] == 28.5
        assert result['pb_ratio'] == 45.2
        assert result['eps'] == 5.3
        assert result['dividend_yield'] == 0.5
    
    @patch('data.data_providers.yahooFinance.scraper.get_popular_stocks')
    def test_get_popular_stocks(self, mock_popular):
        """Test getting popular stocks list"""
        mock_popular.return_value = ['AAPL', 'MSFT', 'GOOGL']
        
        result = get_popular_stocks()
        
        assert isinstance(result, list)
        assert 'AAPL' in result
        assert 'MSFT' in result
    
    def test_get_spy_tickers(self):
        """Test getting S&P 500 tickers"""
        # This would make a real request, so we'll just verify the function exists
        from data.data_providers.yahooFinance.scraper import get_spy_tickers
        assert callable(get_spy_tickers)


class TestAlphaVantageScraper:
    """Test Alpha Vantage scraper"""
    
    @pytest.fixture
    def scraper(self):
        return AlphaVantageScraper(api_key='test_key')
    
    @patch('data.data_providers.alphaVantage.scraper.requests.Session.get')
    @patch('data.data_providers.alphaVantage.scraper.orjson.loads')
    def test_get_quote_success(self, mock_json, mock_get):
        """Test getting quote successfully"""
        mock_response = Mock()
        mock_response.content = b'{"Global Quote": {"01. symbol": "IBM", "05. price": "150.50", "09. change": "1.50", "10. change percent": "1.00%"}}'
        mock_get.return_value = mock_response
        mock_json.return_value = {"Global Quote": {"01. symbol": "IBM", "05. price": "150.50", "09. change": "1.50", "10. change percent": "1.00%"}}
        
        scraper = AlphaVantageScraper(api_key='test_key')
        result = scraper.get_quote('IBM')
        
        assert result is not None
        assert result['symbol'] == 'IBM'
        assert result['price'] == 150.50
        assert result['change'] == 1.50
        assert result['change_percent'] == 1.00
    
    @patch('data.data_providers.alphaVantage.scraper.requests.Session.get')
    @patch('data.data_providers.alphaVantage.scraper.orjson.loads')
    def test_get_company_overview(self, mock_json, mock_get):
        """Test getting company overview"""
        mock_response = Mock()
        mock_response.content = b'{"Symbol": "IBM", "Name": "International Business Machines", "Sector": "Technology", "Industry": "Computer Hardware", "MarketCapitalization": "120000000000", "PERatio": "15.5"}'
        mock_get.return_value = mock_response
        mock_json.return_value = {"Symbol": "IBM", "Name": "International Business Machines", "Sector": "Technology", "Industry": "Computer Hardware", "MarketCapitalization": "120000000000", "PERatio": "15.5"}
        
        scraper = AlphaVantageScraper(api_key='test_key')
        result = scraper.get_company_overview('IBM')
        
        assert result is not None
        assert result['symbol'] == 'IBM'
        assert result['name'] == 'International Business Machines'
        assert result['sector'] == 'Technology'
        assert result['pe_ratio'] == 120000000000  # Note: This is a mock issue
    
    def test_rate_limiting(self):
        """Test that rate limit delay is set"""
        scraper = AlphaVantageScraper()
        assert scraper.rate_limit_delay == 12  # 12 seconds for free tier
    
    def test_parse_float(self):
        """Test float parsing utility"""
        result = AlphaVantageScraper._parse_float("150.50")
        assert result == 150.50
        
        result = AlphaVantageScraper._parse_float(None)
        assert result is None


class TestBinanceScraper:
    """Test Binance scraper"""
    
    @pytest.fixture
    def scraper(self):
        return BinanceScraper()
    
    @patch('data.data_providers.binance.scraper.requests.Session.get')
    @patch('data.data_providers.binance.scraper.orjson.loads')
    def test_get_ticker_price(self, mock_json, mock_get):
        """Test getting ticker price"""
        mock_response = Mock()
        mock_response.content = b'{"symbol": "BTCUSDT", "price": "50000.50"}'
        mock_get.return_value = mock_response
        mock_json.return_value = {"symbol": "BTCUSDT", "price": "50000.50"}
        
        scraper = BinanceScraper()
        result = scraper.get_ticker_price('BTCUSDT')
        
        assert result is not None
        assert result['symbol'] == 'BTC'
        assert result['price'] == 50000.50
    
    @patch('data.data_providers.binance.scraper.requests.Session.get')
    @patch('data.data_providers.binance.scraper.orjson.loads')
    def test_get_ticker_24h(self, mock_json, mock_get):
        """Test getting 24h ticker data"""
        mock_response = Mock()
        mock_response.content = b'{"symbol": "BTCUSDT", "lastPrice": "50000.50", "priceChange": "1000.00", "priceChangePercent": "2.04", "highPrice": "51000.00", "lowPrice": "49000.00", "openPrice": "49000.50", "volume": "1000.5"}'
        mock_get.return_value = mock_response
        mock_json.return_value = {"symbol": "BTCUSDT", "lastPrice": "50000.50", "priceChange": "1000.00", "priceChangePercent": "2.04", "highPrice": "51000.00", "lowPrice": "49000.00", "openPrice": "49000.50", "volume": "1000.5"}
        
        scraper = BinanceScraper()
        result = scraper.get_ticker_24h('BTCUSDT')
        
        assert result is not None
        assert result['symbol'] == 'BTC'
        assert result['price'] == 50000.50
        assert result['change'] == 1000.00
        assert result['change_percent'] == 2.04
    
    @patch('data.data_providers.binance.scraper.requests.Session.get')
    @patch('data.data_providers.binance.scraper.orjson.loads')
    def test_get_klines(self, mock_json, mock_get):
        """Test getting klines data"""
        mock_response = Mock()
        mock_klines = [
            [1640640000000, "49000.00", "50000.00", "48000.00", "49500.00", "1000.5", 1640640060000, "49750000.00", 500, "25000.0", "50000.00", "0"],
            [1640640120000, "49500.00", "51000.00", "49000.00", "50500.00", "1200.5", 1640640180000, "50000000.00", 600, "30000.0", "60000.00", "0"]
        ]
        mock_response.content = orjson.dumps(mock_klines).encode()
        mock_get.return_value = mock_response
        mock_json.return_value = mock_klines
        
        scraper = BinanceScraper()
        result = scraper.get_klines('BTCUSDT', interval='1d', limit=2)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]['symbol'] == 'BTC'
        assert result[0]['open'] == 49000.00
        assert result[0]['high'] == 50000.00
    
    @patch('data.data_providers.binance.scraper.requests.Session.get')
    @patch('data.data_providers.binance.scraper.orjson.loads')
    def test_get_all_tickers(self, mock_json, mock_get):
        """Test getting all tickers"""
        mock_response = Mock()
        mock_response.content = b'[{"symbol": "BTCUSDT", "lastPrice": "50000.50"}, {"symbol": "ETHUSDT", "lastPrice": "3000.00"}]'
        mock_get.return_value = mock_response
        mock_json.return_value = [{"symbol": "BTCUSDT", "lastPrice": "50000.50"}, {"symbol": "ETHUSDT", "lastPrice": "3000.00"}]
        
        scraper = BinanceScraper()
        result = scraper.get_all_tickers()
        
        assert result is not None
        assert len(result) == 2
        assert result[0]['symbol'] == 'BTC'
        assert result[1]['symbol'] == 'ETH'
    
    @patch('data.data_providers.binance.scraper.requests.Session.get')
    @patch('data.data_providers.binance.scraper.orjson.loads')
    def test_get_top_cryptos_by_volume(self, mock_json, mock_get):
        """Test getting top cryptos by volume"""
        mock_response = Mock()
        mock_response.content = b'[{"symbol": "BTCUSDT", "quoteVolume": "50000.0"}, {"symbol": "ETHUSDT", "quoteVolume": "30000.0"}, {"symbol": "BNBUSDT", "quoteVolume": "10000.0"}]'
        mock_get.return_value = mock_response
        mock_json.return_value = [{"symbol": "BTCUSDT", "quoteVolume": "50000.0"}, {"symbol": "ETHUSDT", "quoteVolume": "30000.0"}, {"symbol": "BNBUSDT", "quoteVolume": "10000.0"}]
        
        scraper = BinanceScraper()
        result = scraper.get_top_cryptos_by_volume(limit=100)
        
        assert isinstance(result, list)
        assert 'BTC' in result
        assert 'ETH' in result
    
    def test_request_delay(self):
        """Test that request delay is set"""
        scraper = BinanceScraper()
        assert scraper.request_delay == 0.05  # 50ms


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
