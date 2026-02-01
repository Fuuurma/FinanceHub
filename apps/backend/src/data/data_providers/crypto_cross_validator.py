"""
Crypto Data Cross-Validation Service
Validates and cross-references data between CoinGecko and CoinMarketCap
"""
import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

import polars as pl

from data.data_providers.coingecko.scraper import CoinGeckoScraper
from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class CrossValidationResult:
    """Result of cross-validation between providers"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.coingecko_data: Optional[Dict] = None
        self.coinmarketcap_data: Optional[Dict] = None
        self.price_match: Optional[bool] = None
        self.price_difference: Optional[Decimal] = None
        self.price_difference_percent: Optional[Decimal] = None
        self.volume_match: Optional[bool] = None
        self.volume_difference: Optional[Decimal] = None
        self.market_cap_match: Optional[bool] = None
        self.market_cap_difference: Optional[Decimal] = None
        self.overall_confidence: Optional[float] = None  # 0-1
        self.recommended_source: Optional[str] = None  # 'coingecko' or 'coinmarketcap'
        self.validation_timestamp: Optional[datetime] = None
    
    def calculate_confidence(self) -> float:
        """Calculate overall confidence in data quality (0-1)"""
        factors = []
        
        # Price match (weight: 0.4)
        if self.price_match is not None:
            factors.append(0.4 * (1.0 if self.price_match else max(0, 1.0 - min(0.1, abs(float(self.price_difference_percent))))))
        
        # Volume match (weight: 0.3)
        if self.volume_match is not None:
            factors.append(0.3 * (1.0 if self.volume_match else 0.5))
        
        # Market cap match (weight: 0.3)
        if self.market_cap_match is not None:
            factors.append(0.3 * (1.0 if self.market_cap_match else 0.5))
        
        self.overall_confidence = sum(factors) if factors else 0.0
        return self.overall_confidence
    
    def determine_recommended_source(self) -> str:
        """Determine which provider to use based on confidence"""
        if not self.coingecko_data and not self.coinmarketcap_data:
            return 'coinmarketcap'  # Default fallback
        
        if not self.coingecko_data:
            return 'coinmarketcap'
        
        if not self.coinmarketcap_data:
            return 'coingecko'
        
        # Both available - use confidence-based selection
        if self.calculate_confidence() > 0.85:
            # High confidence - use CoinGecko (primary)
            self.recommended_source = 'coingecko'
        elif self.calculate_confidence() > 0.7:
            # Medium confidence - use CoinMarketCap as backup
            self.recommended_source = 'coinmarketcap'
        else:
            # Low confidence - use CoinGecko but flag for review
            self.recommended_source = 'coingecko'
        
        return self.recommended_source
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'price_match': self.price_match,
            'price_difference': float(self.price_difference) if self.price_difference else None,
            'price_difference_percent': float(self.price_difference_percent) if self.price_difference_percent else None,
            'volume_match': self.volume_match,
            'market_cap_match': self.market_cap_match,
            'overall_confidence': self.overall_confidence,
            'recommended_source': self.recommended_source,
            'validation_timestamp': self.validation_timestamp.isoformat() if self.validation_timestamp else None
        }


class CryptoCrossValidator:
    """
    Cross-validation service for crypto data
    
    Features:
    - Fetches data from both CoinGecko and CoinMarketCap
    - Validates consistency between providers
    - Calculates confidence scores
    - Recommends best data source
    - Detects anomalies and outliers
    """
    
    def __init__(self):
        self.coingecko = CoinGeckoScraper()
        self.coinmarketcap = CoinMarketCapScraper()
        
        # Validation thresholds
        self.price_tolerance_percent = Decimal('0.01')  # 1%
        self.volume_tolerance_percent = Decimal('0.05')  # 5%
        self.market_cap_tolerance_percent = Decimal('0.05')  # 5%
        
        # Cache for validation results
        self.validation_cache: Dict[str, Tuple[CrossValidationResult, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)
    
    async def validate_symbol(self, symbol: str, force_refresh: bool = False) -> CrossValidationResult:
        """
        Validate data for a symbol against both providers
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            force_refresh: Ignore cache and fetch fresh data
        
        Returns:
            CrossValidationResult with validation metrics
        """
        # Check cache first
        if not force_refresh and symbol in self.validation_cache:
            cached_result, cached_time = self.validation_cache[symbol]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.debug(f"Using cached validation for {symbol}")
                return cached_result
        
        result = CrossValidationResult(symbol)
        result.validation_timestamp = datetime.now()
        
        try:
            # Fetch data from both providers concurrently
            coingecko_task = self._fetch_coingecko_data(symbol)
            cmc_task = self._fetch_coinmarketcap_data(symbol)
            
            cg_data, cmc_data = await asyncio.gather(
                coingecko_task,
                cmc_task,
                return_exceptions=True
            )
            
            # Store fetched data
            if not isinstance(cg_data, Exception):
                result.coingecko_data = cg_data
            
            if not isinstance(cmc_data, Exception):
                result.coinmarketcap_data = cmc_data
            
            # Perform validation if both sources available
            if result.coingecko_data and result.coinmarketcap_data:
                self._validate_prices(result)
                self._validate_volumes(result)
                self._validate_market_caps(result)
            elif result.coingecko_data:
                logger.warning(f"Only CoinGecko data available for {symbol}")
            elif result.coinmarketcap_data:
                logger.warning(f"Only CoinMarketCap data available for {symbol}")
            else:
                logger.error(f"No data available for {symbol} from any provider")
            
            # Calculate confidence and determine recommended source
            result.calculate_confidence()
            result.determine_recommended_source()
            
            # Cache the result
            self.validation_cache[symbol] = (result, datetime.now())
            
            logger.info(f"Validated {symbol}: confidence={result.overall_confidence:.2f}, source={result.recommended_source}")
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error validating {symbol}: {str(e)}")
        
        return result
    
    async def _fetch_coingecko_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from CoinGecko"""
        try:
            # Get coin data
            coin_data = await self.coingecko.get_coin(symbol.lower())
            
            if not coin_data:
                return None
            
            # Extract relevant fields
            market_data = coin_data.get('market_data', {})
            
            return {
                'provider': 'coingecko',
                'price': Decimal(str(market_data.get('current_price', 0))),
                'market_cap': Decimal(str(market_data.get('market_cap', {}).get('usd', 0))),
                'volume_24h': Decimal(str(market_data.get('total_volume', {}).get('usd', 0))),
                'change_24h': Decimal(str(market_data.get('price_change_percentage_24h', 0))),
                'name': coin_data.get('name'),
                'symbol': coin_data.get('symbol', '').upper()
            }
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching CoinGecko data for {symbol}: {str(e)}")
            return None
    
    async def _fetch_coinmarketcap_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from CoinMarketCap"""
        try:
            # Get quotes
            quotes = await self.coinmarketcap.get_quotes_latest(symbol=symbol)
            
            if not quotes or len(quotes) == 0:
                return None
            
            quote = quotes[0]
            quote_data = quote.get('quote', {}).get('USD', {})
            
            return {
                'provider': 'coinmarketcap',
                'price': Decimal(str(quote_data.get('price', 0))),
                'market_cap': Decimal(str(quote_data.get('market_cap', 0))),
                'volume_24h': Decimal(str(quote_data.get('volume_24h', 0))),
                'change_24h': Decimal(str(quote_data.get('percent_change_24h', 0))),
                'name': quote.get('name'),
                'symbol': quote.get('symbol')
            }
        
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching CoinMarketCap data for {symbol}: {str(e)}")
            return None
    
    def _validate_prices(self, result: CrossValidationResult):
        """Validate price consistency between providers"""
        if not result.coingecko_data or not result.coinmarketcap_data:
            return
        
        cg_price = result.coingecko_data.get('price')
        cmc_price = result.coinmarketcap_data.get('price')
        
        if cg_price and cmc_price:
            # Calculate absolute and percentage difference
            difference = abs(cg_price - cmc_price)
            difference_percent = (difference / cg_price) * 100
            
            result.price_difference = difference
            result.price_difference_percent = difference_percent
            
            # Check if within tolerance
            result.price_match = difference_percent <= self.price_tolerance_percent
            
            logger.debug(
                f"Price validation for {result.symbol}: "
                f"CG=${cg_price}, CMC=${cmc_price}, "
                f"diff=${difference} ({difference_percent:.2f}%)"
            )
    
    def _validate_volumes(self, result: CrossValidationResult):
        """Validate volume consistency between providers"""
        if not result.coingecko_data or not result.coinmarketcap_data:
            return
        
        cg_volume = result.coingecko_data.get('volume_24h')
        cmc_volume = result.coinmarketcap_data.get('volume_24h')
        
        if cg_volume and cmc_volume:
            # Skip if either is zero (avoid division by zero)
            if cg_volume == 0 or cmc_volume == 0:
                return
            
            # Calculate percentage difference
            difference_percent = abs((cg_volume - cmc_volume) / cg_volume) * 100
            
            result.volume_difference = abs(cg_volume - cmc_volume)
            result.volume_match = difference_percent <= self.volume_tolerance_percent
            
            logger.debug(
                f"Volume validation for {result.symbol}: "
                f"CG=${cg_volume}, CMC=${cmc_volume}, "
                f"diff={difference_percent:.2f}%"
            )
    
    def _validate_market_caps(self, result: CrossValidationResult):
        """Validate market cap consistency between providers"""
        if not result.coingecko_data or not result.coinmarketcap_data:
            return
        
        cg_market_cap = result.coingecko_data.get('market_cap')
        cmc_market_cap = result.coinmarketcap_data.get('market_cap')
        
        if cg_market_cap and cmc_market_cap:
            # Skip if either is zero
            if cg_market_cap == 0 or cmc_market_cap == 0:
                return
            
            # Calculate percentage difference
            difference_percent = abs((cg_market_cap - cmc_market_cap) / cg_market_cap) * 100
            
            result.market_cap_difference = abs(cg_market_cap - cmc_market_cap)
            result.market_cap_match = difference_percent <= self.market_cap_tolerance_percent
            
            logger.debug(
                f"Market cap validation for {result.symbol}: "
                f"CG=${cg_market_cap}, CMC=${cmc_market_cap}, "
                f"diff={difference_percent:.2f}%"
            )
    
    async def validate_batch(self, symbols: List[str]) -> Dict[str, CrossValidationResult]:
        """
        Validate multiple symbols in batch
        
        Args:
            symbols: List of crypto symbols
        
        Returns:
            Dict mapping symbols to validation results
        """
        logger.info(f"Batch validating {len(symbols)} symbols...")
        
        results = {}
        
        # Create tasks for all symbols
        tasks = [self.validate_symbol(symbol) for symbol in symbols]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for symbol, result in zip(symbols, task_results):
            if isinstance(result, Exception):
                logger.error(f"Error validating {symbol}: {str(result)}")
                results[symbol] = CrossValidationResult(symbol)  # Empty result
            else:
                results[symbol] = result
        
        # Calculate statistics
        avg_confidence = sum(r.overall_confidence for r in results.values() if r.overall_confidence) / len(results)
        cg_count = sum(1 for r in results.values() if r.coingecko_data)
        cmc_count = sum(1 for r in results.values() if r.coinmarketcap_data)
        both_count = sum(1 for r in results.values() if r.coingecko_data and r.coinmarketcap_data)
        
        logger.info(
            f"Batch validation complete: avg_confidence={avg_confidence:.2f}, "
            f"CG={cg_count}, CMC={cmc_count}, both={both_count}"
        )
        
        return results
    
    def get_validation_summary(self) -> dict:
        """Get summary of all cached validations"""
        if not self.validation_cache:
            return {
                'total_validations': 0,
                'avg_confidence': 0.0,
                'coingecko_available': 0,
                'coinmarketcap_available': 0,
                'both_available': 0
            }
        
        results = [r for r, _ in self.validation_cache.values()]
        
        return {
            'total_validations': len(results),
            'avg_confidence': sum(r.overall_confidence for r in results if r.overall_confidence) / len(results),
            'coingecko_available': sum(1 for r in results if r.coingecko_data),
            'coinmarketcap_available': sum(1 for r in results if r.coinmarketcap_data),
            'both_available': sum(1 for r in results if r.coingecko_data and r.coinmarketcap_data),
            'price_match_count': sum(1 for r in results if r.price_match),
            'recommended_sources': {
                'coingecko': sum(1 for r in results if r.recommended_source == 'coingecko'),
                'coinmarketcap': sum(1 for r in results if r.recommended_source == 'coinmarketcap')
            }
        }
    
    async def detect_anomalies(self, symbols: List[str], threshold: float = 0.5) -> List[dict]:
        """
        Detect anomalies in crypto data based on cross-validation
        
        Args:
            symbols: List of crypto symbols to check
            threshold: Confidence threshold below which is considered anomaly
        
        Returns:
            List of anomalies with details
        """
        anomalies = []
        
        for symbol in symbols:
            result = await self.validate_symbol(symbol)
            
            if result.overall_confidence is not None and result.overall_confidence < threshold:
                anomalies.append({
                    'symbol': symbol,
                    'confidence': result.overall_confidence,
                    'recommended_source': result.recommended_source,
                    'price_difference_percent': float(result.price_difference_percent) if result.price_difference_percent else None,
                    'timestamp': result.validation_timestamp.isoformat() if result.validation_timestamp else None
                })
        
        logger.info(f"Detected {len(anomalies)} anomalies out of {len(symbols)} symbols")
        return anomalies
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")


# Singleton instance
_crypto_cross_validator: Optional[CryptoCrossValidator] = None


def get_crypto_cross_validator() -> CryptoCrossValidator:
    """Get singleton cross-validator instance"""
    global _crypto_cross_validator
    
    if _crypto_cross_validator is None:
        _crypto_cross_validator = CryptoCrossValidator()
    
    return _crypto_cross_validator