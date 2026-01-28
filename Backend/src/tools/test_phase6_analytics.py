import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase

from utils.services.technical_indicators import (
    TechnicalIndicators,
    IndicatorType,
    get_technical_indicators
)


@pytest.mark.django_db
class TestTechnicalIndicators(TestCase):
    def setUp(self):
        self.indicators = TechnicalIndicators()
        
        self.sample_data = [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "open": 100,
                "high": 105,
                "low": 98,
                "close": 103,
                "volume": 1000
            },
            {
                "timestamp": "2026-01-02T00:00:00Z",
                "open": 103,
                "high": 108,
                "low": 101,
                "close": 106,
                "volume": 1200
            },
            {
                "timestamp": "2026-01-03T00:00:00Z",
                "open": 106,
                "high": 109,
                "low": 104,
                "close": 107,
                "volume": 900
            },
            {
                "timestamp": "2026-01-04T00:00:00Z",
                "open": 107,
                "high": 112,
                "low": 105,
                "close": 110,
                "volume": 1100
            },
            {
                "timestamp": "2026-01-05T00:00:00Z",
                "open": 110,
                "high": 115,
                "low": 108,
                "close": 112,
                "volume": 1300
            }
        ]
    
    def test_initialization(self):
        self.assertIsNotNone(self.indicators)
        self.assertEqual(self.indicators.logger.name, 'utils.services.technical_indicators')
    
    def test_calculate_sma(self):
        sma_result = self.indicators.calculate_sma(
            self.sample_data,
            period=3
        )
        
        self.assertEqual(len(sma_result), 3)
        self.assertIn("sma", sma_result[0])
        self.assertIn("close", sma_result[0])
        
        last_sma = sma_result[-1]["sma"]
        expected_sma = (110 + 112 + 107) / 3
        self.assertAlmostEqual(last_sma, expected_sma, places=2)
    
    def test_calculate_sma_insufficient_data(self):
        sma_result = self.indicators.calculate_sma(self.sample_data, period=10)
        self.assertEqual(len(sma_result), 0)
    
    def test_calculate_ema(self):
        ema_result = self.indicators.calculate_ema(
            self.sample_data,
            period=3
        )
        
        self.assertEqual(len(ema_result), 5)
        self.assertIn("ema", ema_result[0])
        self.assertIn("close", ema_result[0])
        
        first_ema = ema_result[0]["ema"]
        self.assertEqual(first_ema, 100)
    
    def test_calculate_ema_insufficient_data(self):
        ema_result = self.indicators.calculate_ema(self.sample_data, period=10)
        self.assertEqual(len(ema_result), 0)
    
    def test_calculate_rsi(self):
        rsi_result = self.indicators.calculate_rsi(self.sample_data, period=3)
        
        self.assertEqual(len(rsi_result), 2)
        self.assertIn("rsi", rsi_result[0])
        self.assertIn("close", rsi_result[0])
        
        for result in rsi_result:
            self.assertGreaterEqual(result["rsi"], 0)
            self.assertLessEqual(result["rsi"], 100)
    
    def test_calculate_rsi_insufficient_data(self):
        rsi_result = self.indicators.calculate_rsi(self.sample_data, period=15)
        self.assertEqual(len(rsi_result), 0)
    
    def test_calculate_macd(self):
        macd_result = self.indicators.calculate_macd(self.sample_data)
        
        self.assertEqual(len(macd_result), 5)
        
        for result in macd_result:
            self.assertIn("macd", result)
            self.assertIn("signal", result)
            self.assertIn("histogram", result)
            
            if result["histogram"] is not None:
                self.assertEqual(
                    result["histogram"],
                    result["macd"] - result["signal"]
                )
    
    def test_calculate_bollinger_bands(self):
        bollinger_result = self.indicators.calculate_bollinger_bands(
            self.sample_data,
            period=3,
            std_dev=2
        )
        
        self.assertEqual(len(bollinger_result), 3)
        
        for result in bollinger_result:
            self.assertIn("sma", result)
            self.assertIn("upper_band", result)
            self.assertIn("lower_band", result)
            self.assertIn("bandwidth", result)
            
            self.assertGreaterEqual(result["upper_band"], result["sma"])
            self.assertLessEqual(result["lower_band"], result["sma"])
    
    def test_calculate_stochastic(self):
        stochastic_result = self.indicators.calculate_stochastic(self.sample_data)
        
        self.assertEqual(len(stochastic_result), 2)
        
        for result in stochastic_result:
            self.assertIn("k", result)
            self.assertIn("d", result)
            
            if result["k"] is not None and result["d"] is not None:
                self.assertGreaterEqual(result["k"], 0)
                self.assertLessEqual(result["k"], 100)
    
    def test_calculate_williams_r(self):
        williams_r_result = self.indicators.calculate_williams_r(self.sample_data)
        
        self.assertEqual(len(williams_r_result), 4)
        
        for result in williams_r_result:
            self.assertIn("williams_r", result)
            
            if result["williams_r"] is not None:
                self.assertGreaterEqual(result["williams_r"], -100)
                self.assertLessEqual(result["williams_r"], 0)
    
    def test_calculate_atr(self):
        atr_result = self.indicators.calculate_atr(self.sample_data)
        
        self.assertEqual(len(atr_result), 4)
        
        for result in atr_result:
            self.assertIn("atr", result)
            self.assertGreaterEqual(result["atr"], 0)
    
    def test_calculate_obv(self):
        obv_result = self.indicators.calculate_obv(self.sample_data)
        
        self.assertEqual(len(obv_result), 5)
        
        for i, result in enumerate(obv_result):
            self.assertIn("obv", result)
            self.assertIn("volume", result)
            
            if i > 0:
                close_prev = self.sample_data[i-1]["close"]
                close_current = self.sample_data[i]["close"]
                volume = self.sample_data[i]["volume"]
                
                expected_obv_change = volume if close_current > close_prev else (-volume if close_current < close_prev else 0)
                expected_obv = obv_result[i-1]["obv"] + expected_obv_change
                
                self.assertEqual(result["obv"], expected_obv)
    
    def test_calculate_cci(self):
        cci_result = self.indicators.calculate_cci(self.sample_data)
        
        self.assertEqual(len(cci_result), 3)
        
        for result in cci_result:
            self.assertIn("cci", result)
    
    def test_singleton_instance(self):
        instance1 = get_technical_indicators()
        instance2 = get_technical_indicators()
        
        self.assertIs(instance1, instance2)


@pytest.mark.asyncio
class TestCalculateAll(TestCase):
    def setUp(self):
        self.indicators = TechnicalIndicators()
        
        self.sample_data = [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "open": 100,
                "high": 105,
                "low": 98,
                "close": 103,
                "volume": 1000
            },
            {
                "timestamp": "2026-01-02T00:00:00Z",
                "open": 103,
                "high": 108,
                "low": 101,
                "close": 106,
                "volume": 1200
            },
            {
                "timestamp": "2026-01-03T00:00:00Z",
                "open": 106,
                "high": 109,
                "low": 104,
                "close": 107,
                "volume": 900
            }
        ]
    
    async def test_calculate_all_default(self):
        results = await self.indicators.calculate_all(self.sample_data)
        
        self.assertIn("sma", results)
        self.assertIn("ema", results)
        self.assertIn("rsi", results)
        self.assertIn("macd", results)
        self.assertIn("bollinger", results)
        self.assertIn("stochastic", results)
        self.assertIn("williams_r", results)
        self.assertIn("atr", results)
        self.assertIn("obv", results)
        self.assertIn("cci", results)
        
        self.assertEqual(len(results), 10)
    
    async def test_calculate_all_selected(self):
        selected = [IndicatorType.SMA, IndicatorType.RSI, IndicatorType.MACD]
        results = await self.indicators.calculate_all(self.sample_data, selected)
        
        self.assertIn("sma", results)
        self.assertIn("rsi", results)
        self.assertIn("macd", results)
        self.assertNotIn("ema", results)
        self.assertNotIn("bollinger", results)
        
        self.assertEqual(len(results), 3)


@pytest.mark.django_db
class TestIndicatorType(TestCase):
    def test_indicator_types(self):
        self.assertEqual(IndicatorType.SMA.value, "sma")
        self.assertEqual(IndicatorType.EMA.value, "ema")
        self.assertEqual(IndicatorType.RSI.value, "rsi")
        self.assertEqual(IndicatorType.MACD.value, "macd")
        self.assertEqual(IndicatorType.BOLLINGER.value, "bollinger")
        self.assertEqual(IndicatorType.STOCHASTIC.value, "stochastic")
        self.assertEqual(IndicatorType.WILLIAMS_R.value, "williams_r")
        self.assertEqual(IndicatorType.ATR.value, "atr")
        self.assertEqual(IndicatorType.OBV.value, "obv")
        self.assertEqual(IndicatorType.CCI.value, "cci")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
