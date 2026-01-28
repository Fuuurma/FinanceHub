import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

import polars as pl
import numpy as np
from django.utils import timezone

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class IndicatorType(Enum):
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER = "bollinger"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    ATR = "atr"
    OBV = "obv"
    CCI = "cci"


class TechnicalIndicators:
    def __init__(self):
        self.logger = logger
    
    def calculate_sma(
        self,
        data: List[Dict[str, Any]],
        period: int,
        price_key: str = "close"
    ) -> List[Dict[str, float]]:
        df = pl.DataFrame(data)
        
        if len(df) < period:
            return []
        
        df = df.with_columns(
            pl.col(price_key).rolling_mean(window_size=period).alias("sma")
        )
        
        result = df.select([
            pl.col("timestamp"),
            pl.col(price_key),
            pl.col("sma")
        ]).to_dicts()
        
        return result
    
    def calculate_ema(
        self,
        data: List[Dict[str, Any]],
        period: int,
        price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []
        
        df = pl.DataFrame(data)
        
        multiplier = 2 / (period + 1)
        
        ema_values = []
        close_prices = df[price_key].to_list()
        
        ema = close_prices[0]
        ema_values.append(ema)
        
        for price in close_prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)
        
        timestamps = df["timestamp"].to_list()
        
        return [
            {
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "ema": ema_values[i]
            }
            for i in range(len(timestamps))
        ]
    
    def calculate_rsi(
        self,
        data: List[Dict[str, Any]],
        period: int = 14,
        price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period + 1:
            return []
        
        df = pl.DataFrame(data)
        
        close_prices = df[price_key].to_list()
        
        deltas = []
        for i in range(1, len(close_prices)):
            delta = close_prices[i] - close_prices[i-1]
            deltas.append(delta)
        
        gains = []
        losses = []
        for delta in deltas:
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(delta))
        
        rsi_values = [None] * period
        
        for i in range(period, len(gains)):
            avg_gain = np.mean(gains[max(0, i-period):i+1])
            avg_loss = np.mean(losses[max(0, i-period):i+1])
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        timestamps = df["timestamp"].to_list()[period:]
        close_prices_result = close_prices[period:]
        
        return [
            {
                "timestamp": timestamps[i],
                "close": close_prices_result[i],
                "rsi": rsi_values[i]
            }
            for i in range(len(timestamps))
        ]
    
    def calculate_macd(
        self,
        data: List[Dict[str, Any]],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < slow_period:
            return []
        
        df = pl.DataFrame(data)
        close_prices = df[price_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        ema_fast = self._calculate_ema_array(close_prices, fast_period)
        ema_slow = self._calculate_ema_array(close_prices, slow_period)
        
        macd_line = []
        for i in range(len(ema_slow)):
            macd_line.append(ema_fast[i] - ema_slow[i])
        
        signal_line = self._calculate_ema_array(macd_line, signal_period)
        
        histogram = []
        for i in range(len(signal_line)):
            histogram.append(macd_line[i] - signal_line[i])
        
        result = []
        min_len = min(len(timestamps), len(macd_line))
        
        for i in range(min_len):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "macd": macd_line[i] if i < len(macd_line) else None,
                "signal": signal_line[i] if i < len(signal_line) else None,
                "histogram": histogram[i] if i < len(histogram) else None
            })
        
        return result
    
    def _calculate_ema_array(self, data: List[float], period: int) -> List[float]:
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = data[0]
        ema_values = [ema]
        
        for price in data[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_bollinger_bands(
        self,
        data: List[Dict[str, Any]],
        period: int = 20,
        std_dev: float = 2.0,
        price_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []
        
        df = pl.DataFrame(data)
        
        df = df.with_columns(
            pl.col(price_key).rolling_mean(window_size=period).alias("sma")
        )
        
        rolling_std = df[price_key].rolling_std(window_size=period).to_list()
        
        upper_band = []
        lower_band = []
        sma_values = df["sma"].to_list()
        close_prices = df[price_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        for i in range(len(sma_values)):
            if rolling_std[i] is None:
                upper_band.append(None)
                lower_band.append(None)
            else:
                upper_band.append(sma_values[i] + (std_dev * rolling_std[i]))
                lower_band.append(sma_values[i] - (std_dev * rolling_std[i]))
        
        result = []
        for i in range(len(timestamps)):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "sma": sma_values[i],
                "upper_band": upper_band[i],
                "lower_band": lower_band[i],
                "bandwidth": upper_band[i] - lower_band[i] if upper_band[i] and lower_band[i] else None
            })
        
        return result
    
    def calculate_stochastic(
        self,
        data: List[Dict[str, Any]],
        k_period: int = 14,
        d_period: int = 3,
        smooth_k: int = 3,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < k_period + d_period:
            return []
        
        df = pl.DataFrame(data)
        
        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        raw_k = []
        for i in range(k_period, len(high_prices)):
            high_range = max(high_prices[i-k_period:i+1])
            low_range = min(low_prices[i-k_period:i+1])
            
            if low_range == high_range:
                k_value = 50
            else:
                k_value = 100 * ((close_prices[i] - low_range) / (high_range - low_range))
            
            raw_k.append(k_value)
        
        full_k = [None] * (k_period + d_period - 1) + raw_k
        
        k_values = self._calculate_sma_array(full_k, smooth_k)
        
        d_values = []
        for k in k_values:
            if k is None:
                d_values.append(None)
            else:
                d_values.append(self._calculate_sma_value([k], d_period))
        
        result = []
        min_len = min(len(timestamps), len(k_values))
        
        for i in range(min_len):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "k": k_values[i],
                "d": d_values[i]
            })
        
        return result
    
    def _calculate_sma_array(self, data: List[Optional[float]], period: int) -> List[Optional[float]]:
        if len(data) < period:
            return data[:]
        
        sma_values = data[:period-1]
        
        for i in range(period - 1, len(data)):
            window = [x for x in data[i-period+1:i+1] if x is not None]
            if window:
                sma_values.append(np.mean(window))
            else:
                sma_values.append(None)
        
        return sma_values
    
    def _calculate_sma_value(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return 0
        return np.mean(data[-period:])
    
    def calculate_williams_r(
        self,
        data: List[Dict[str, Any]],
        period: int = 14,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []
        
        df = pl.DataFrame(data)
        
        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        williams_r_values = [None] * (period - 1)
        
        for i in range(period - 1, len(close_prices)):
            high_range = max(high_prices[i-period+1:i+1])
            low_range = min(low_prices[i-period+1:i+1])
            
            if high_range == low_range:
                wr = 0
            else:
                wr = -100 * ((high_range - close_prices[i]) / (high_range - low_range))
            
            williams_r_values.append(wr)
        
        result = []
        min_len = min(len(timestamps), len(williams_r_values))
        
        for i in range(min_len):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "williams_r": williams_r_values[i]
            })
        
        return result
    
    def calculate_atr(
        self,
        data: List[Dict[str, Any]],
        period: int = 14,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []
        
        df = pl.DataFrame(data)
        
        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        true_ranges = []
        for i in range(1, len(close_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i-1])
            low_close = abs(low_prices[i] - close_prices[i-1])
            
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        atr_values = []
        for i in range(len(true_ranges)):
            start_idx = max(0, i - period + 1)
            window = true_ranges[start_idx:i+1]
            
            if window:
                atr = np.mean(window)
            else:
                atr = 0
            
            atr_values.append(atr)
        
        result = []
        offset = len(timestamps) - len(atr_values)
        
        for i in range(len(atr_values)):
            result.append({
                "timestamp": timestamps[offset + i],
                "close": close_prices[offset + i],
                "atr": atr_values[i]
            })
        
        return result
    
    def calculate_obv(
        self,
        data: List[Dict[str, Any]],
        volume_key: str = "volume",
        close_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < 2:
            return []
        
        df = pl.DataFrame(data)
        
        close_prices = df[close_key].to_list()
        volumes = df[volume_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        obv_values = [0]
        
        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i-1]:
                obv = obv_values[-1] + volumes[i]
            elif close_prices[i] < close_prices[i-1]:
                obv = obv_values[-1] - volumes[i]
            else:
                obv = obv_values[-1]
            
            obv_values.append(obv)
        
        result = []
        min_len = min(len(timestamps), len(obv_values))
        
        for i in range(min_len):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "volume": volumes[i],
                "obv": obv_values[i]
            })
        
        return result
    
    def calculate_cci(
        self,
        data: List[Dict[str, Any]],
        period: int = 20,
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close"
    ) -> List[Dict[str, float]]:
        if len(data) < period:
            return []
        
        df = pl.DataFrame(data)
        
        high_prices = df[high_key].to_list()
        low_prices = df[low_key].to_list()
        close_prices = df[close_key].to_list()
        timestamps = df["timestamp"].to_list()
        
        typical_prices = []
        for i in range(len(close_prices)):
            tp = (high_prices[i] + low_prices[i] + close_prices[i]) / 3
            typical_prices.append(tp)
        
        sma_tp = self._calculate_sma_array(typical_prices, period)
        
        mean_deviations = []
        for i in range(len(typical_prices)):
            start_idx = max(0, i - period + 1)
            window = typical_prices[start_idx:i+1]
            
            if window and sma_tp[i]:
                deviations = [abs(x - sma_tp[i]) for x in window]
                mean_dev = np.mean(deviations) if deviations else 0
            else:
                mean_dev = 0
            
            mean_deviations.append(mean_dev)
        
        cci_values = []
        for i in range(len(mean_deviations)):
            if mean_deviations[i] == 0:
                cci = 0
            else:
                cci = (typical_prices[i] - sma_tp[i]) / (0.015 * mean_deviations[i])
            
            cci_values.append(cci)
        
        result = []
        min_len = min(len(timestamps), len(cci_values))
        
        for i in range(min_len):
            result.append({
                "timestamp": timestamps[i],
                "close": close_prices[i],
                "cci": cci_values[i]
            })
        
        return result
    
    async def calculate_all(
        self,
        data: List[Dict[str, Any]],
        indicators: Optional[List[IndicatorType]] = None
    ) -> Dict[str, List[Dict[str, float]]]:
        if indicators is None:
            indicators = [
                IndicatorType.SMA,
                IndicatorType.EMA,
                IndicatorType.RSI,
                IndicatorType.MACD,
                IndicatorType.BOLLINGER,
                IndicatorType.STOCHASTIC,
                IndicatorType.WILLIAMS_R,
                IndicatorType.ATR,
                IndicatorType.OBV,
                IndicatorType.CCI
            ]
        
        results = {}
        
        tasks = []
        
        if IndicatorType.SMA in indicators:
            tasks.append(("sma", asyncio.to_thread(
                self.calculate_sma, data, period=20
            )))
        
        if IndicatorType.EMA in indicators:
            tasks.append(("ema", asyncio.to_thread(
                self.calculate_ema, data, period=20
            )))
        
        if IndicatorType.RSI in indicators:
            tasks.append(("rsi", asyncio.to_thread(
                self.calculate_rsi, data, period=14
            )))
        
        if IndicatorType.MACD in indicators:
            tasks.append(("macd", asyncio.to_thread(
                self.calculate_macd, data
            )))
        
        if IndicatorType.BOLLINGER in indicators:
            tasks.append(("bollinger", asyncio.to_thread(
                self.calculate_bollinger_bands, data
            )))
        
        if IndicatorType.STOCHASTIC in indicators:
            tasks.append(("stochastic", asyncio.to_thread(
                self.calculate_stochastic, data
            )))
        
        if IndicatorType.WILLIAMS_R in indicators:
            tasks.append(("williams_r", asyncio.to_thread(
                self.calculate_williams_r, data
            )))
        
        if IndicatorType.ATR in indicators:
            tasks.append(("atr", asyncio.to_thread(
                self.calculate_atr, data
            )))
        
        if IndicatorType.OBV in indicators:
            tasks.append(("obv", asyncio.to_thread(
                self.calculate_obv, data
            )))
        
        if IndicatorType.CCI in indicators:
            tasks.append(("cci", asyncio.to_thread(
                self.calculate_cci, data
            )))
        
        for indicator_name, task in tasks:
            try:
                results[indicator_name] = await task
                self.logger.debug(f"Calculated {indicator_name} indicator")
            except Exception as e:
                self.logger.error(f"Failed to calculate {indicator_name}: {e}")
                results[indicator_name] = []
        
        return results


_technical_indicators_instance: Optional[TechnicalIndicators] = None


def get_technical_indicators() -> TechnicalIndicators:
    global _technical_indicators_instance
    if _technical_indicators_instance is None:
        _technical_indicators_instance = TechnicalIndicators()
    return _technical_indicators_instance
