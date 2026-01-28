"""
Tests for Fundamentals Service Layer
"""
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from django.test import TestCase
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from utils.services.fundamental_service import (
    FundamentalDataService,
    get_fundamental_service
)


class TestFundamentalDataService(TestCase):
    """Test fundamental data service methods"""

    def setUp(self):
        self.service = FundamentalDataService()

    @patch('utils.services.fundamental_service.FMPFetcher')
    async def test_get_equity_fundamentals_success(self, mock_fmp_class):
        """Test successful equity fundamentals fetch"""
        mock_fetcher = AsyncMock()
        mock_fetcher.get_company_profile.return_value = [{
            'symbol': 'AAPL',
            'companyName': 'Apple Inc.',
            'sector': 'Technology'
        }]
        mock_fetcher.get_key_metrics.return_value = [{'peRatio': 25.5}]
        mock_fetcher.get_financial_ratios.return_value = [{'roe': 0.15}]
        mock_fetcher.get_income_statement.return_value = [{'revenue': 1000000000}]
        mock_fetcher.get_balance_sheet.return_value = [{'totalAssets': 500000000}]

        mock_fmp_class.return_value.__aenter__.return_value = mock_fetcher

        result = await self.service.get_equity_fundamentals('AAPL')

        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertIn('profile', result)
        self.assertIn('key_metrics', result)
        self.assertIn('fetched_at', result)

    @patch('utils.services.fundamental_service.DeFiLlamaFetcher')
    async def test_get_crypto_protocol_metrics_success(self, mock_defi_class):
        """Test successful crypto protocol metrics fetch"""
        mock_fetcher = AsyncMock()
        mock_fetcher.get_protocol_data.return_value = {
            'name': 'Uniswap',
            'tvl': 5000000000,
            'tvlChange24h': 5.5,
            'tvlChange7d': 12.3,
            'chain': 'Ethereum',
            'category': 'DEX'
        }
        mock_fetcher.get_tvl.return_value = [{'date': '2024-01-01', 'tvl': 5000000000}]

        mock_defi_class.return_value.__aenter__.return_value = mock_fetcher

        result = await self.service.get_crypto_protocol_metrics('uniswap')

        self.assertIsInstance(result, dict)
        self.assertEqual(result['protocol'], 'uniswap')
        self.assertEqual(result['tvl'], 5000000000)
        self.assertIn('tvl_history', result)

    @patch('utils.services.fundamental_service.FREDScraper')
    async def test_get_yield_curve_success(self, mock_fred_class):
        """Test successful yield curve fetch"""
        mock_scraper = Mock()
        mock_scraper.get_full_treasury_curve.return_value = [
            {'maturity': '1M', 'rate': 0.052},
            {'maturity': '10Y', 'rate': 0.042},
        ]
        mock_scraper.get_yield_curve_spread.return_value = {'2s10s': 0.01}

        mock_fred_class.return_value = mock_scraper

        result = await self.service.get_yield_curve()

        self.assertIsInstance(result, dict)
        self.assertIn('curve', result)
        self.assertIn('spreads', result)
        self.assertIn('fetched_at', result)

    async def test_screen_stocks_basic_filters(self):
        """Test stock screener with basic filters"""
        with patch('utils.services.fundamental_service.FMPFetcher') as mock_fmp_class:
            mock_fetcher = AsyncMock()
            mock_fetcher.get_stock_screener.return_value = [
                {'symbol': 'AAPL', 'pe': 20, 'dividendYield': 0.5, 'marketCap': 500000000000},
                {'symbol': 'MSFT', 'pe': 35, 'dividendYield': 0.8, 'marketCap': 600000000000},
            ]

            mock_fmp_class.return_value.__aenter__.return_value = mock_fetcher

            results = await self.service.screen_stocks(
                market_cap_min=100000000000,
                pe_max=30,
                dividend_yield_min=0.3
            )

            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['symbol'], 'AAPL')

    @patch('utils.services.fundamental_service.FMPFetcher')
    async def test_batch_fetch_equities(self, mock_fmp_class):
        """Test batch fetching multiple equities"""
        mock_fetcher = AsyncMock()
        mock_fetcher.get_company_profile.return_value = [{'symbol': 'AAPL', 'companyName': 'Apple'}]

        mock_fmp_class.return_value.__aenter__.return_value = mock_fetcher

        results = await self.service.batch_fetch_equities(['AAPL', 'MSFT'], 'fundamentals')

        self.assertIsInstance(results, dict)
        self.assertIn('AAPL', results)
        self.assertIn('MSFT', results)

    @patch('utils.services.fundamental_service.get_cache_manager')
    async def test_cache_hit_on_fundamentals(self, mock_get_cache):
        """Test that cached data is returned when available"""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = {
            'symbol': 'AAPL',
            'profile': {'companyName': 'Apple'},
            'cached': True
        }
        mock_get_cache.return_value = mock_cache

        result = await self.service.get_equity_fundamentals('AAPL', force_refresh=False)

        self.assertEqual(result['cached'], True)
        mock_cache.get.assert_called_once()

    @patch('utils.services.fundamental_service.get_cache_manager')
    async def test_cache_miss_triggers_fetch(self, mock_get_cache):
        """Test that fetch is triggered on cache miss"""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        mock_cache.set = AsyncMock()
        mock_get_cache.return_value = mock_cache

        with patch('utils.services.fundamental_service.FMPFetcher') as mock_fmp_class:
            mock_fetcher = AsyncMock()
            mock_fetcher.get_company_profile.return_value = [{'symbol': 'AAPL', 'companyName': 'Apple'}]
            mock_fetcher.get_key_metrics.return_value = []
            mock_fetcher.get_financial_ratios.return_value = []
            mock_fetcher.get_income_statement.return_value = []
            mock_fetcher.get_balance_sheet.return_value = []
            mock_fetcher.get_cash_flow.return_value = []

            mock_fmp_class.return_value.__aenter__.return_value = mock_fetcher

            result = await self.service.get_equity_fundamentals('AAPL', force_refresh=False)

            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()

    async def test_get_equity_valuation_format(self):
        """Test equity valuation data format"""
        with patch('utils.services.fundamental_service.FMPFetcher') as mock_fmp_class:
            mock_fetcher = AsyncMock()
            mock_fetcher.get_key_metrics.return_value = [{
                'peRatio': 25.5,
                'pbRatio': 8.2,
                'psRatio': 7.1,
                'evEbitda': 18.5,
                'pegRatio': 1.8,
                'dividendYield': 0.55,
                'beta': 1.2,
                'roe': 0.25,
            }]
            mock_fetcher.get_enterprise_value.return_value = [3000000000000]
            mock_fetcher.get_market_cap.return_value = [2800000000000]

            mock_fmp_class.return_value.__aenter__.return_value = mock_fetcher

            result = await self.service.get_equity_valuation('AAPL')

            self.assertEqual(result['symbol'], 'AAPL')
            self.assertEqual(result['pe_ratio'], 25.5)
            self.assertEqual(result['pb_ratio'], 8.2)
            self.assertIn('market_cap', result)
            self.assertIn('enterprise_value', result)

    async def test_get_all_crypto_protocols(self):
        """Test fetching all crypto protocols"""
        with patch('utils.services.fundamental_service.DeFiLlamaFetcher') as mock_defi_class:
            mock_fetcher = AsyncMock()
            mock_fetcher.get_all_protocols.return_value = [
                {'name': 'Uniswap', 'tvl': 5000000000},
                {'name': 'Aave', 'tvl': 4000000000},
            ]

            async def transform_protocols(protocols):
                return protocols

            mock_fetcher.transform_protocol_list = transform_protocols

            mock_defi_class.return_value.__aenter__.return_value = mock_fetcher

            results = await self.service.get_all_crypto_protocols()

            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 2)


class TestFundamentalServiceSingleton(TestCase):
    """Test service singleton pattern"""

    def test_get_fundamental_service_returns_instance(self):
        """Test that get_fundamental_service returns a service instance"""
        service = get_fundamental_service()
        self.assertIsInstance(service, FundamentalDataService)

    def test_get_fundamental_service_returns_same_instance(self):
        """Test that get_fundamental_service returns the same instance"""
        service1 = get_fundamental_service()
        service2 = get_fundamental_service()
        self.assertIs(service1, service2)
