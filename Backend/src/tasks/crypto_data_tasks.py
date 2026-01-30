"""
Crypto Data Background Tasks (Enhanced with Cross-Validation)
Uses UnifiedCryptoProvider for intelligent provider switching
"""

import dramatiq
import asyncio
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries
from datetime import datetime
import logging
from typing import List, Dict, Optional

from data.data_providers.unified_crypto_provider import get_unified_crypto_provider
from data.data_providers.crypto_cross_validator import get_crypto_cross_validator
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Initialize Dramatiq broker
broker = StubBroker()
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))
broker.add_middleware(TimeLimit(time_limit=1000 * 60 * 30))
broker.add_middleware(Retries(max_retries=3))

# Popular crypto pairs
POPULAR_CRYPTOS = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "ADA",
    "DOGE",
    "SOL",
    "DOT",
    "MATIC",
    "LTC",
    "AVAX",
    "LINK",
    "UNI",
    "ATOM",
    "XLM",
    "ETC",
    "XMR",
    "ALGO",
    "VET",
    "FIL",
    "NEAR",
    "AAVE",
    "XTZ",
]


@dramatiq.actor(broker=broker, max_retries=3)
async def fetch_crypto_batch(
    symbols: Optional[List[str]] = None,
    use_validation: bool = True,
    force_refresh: bool = False,
) -> dict:
    """
    Fetch crypto data in batch using UnifiedCryptoProvider

    Features:
    - Intelligent provider switching
    - Cross-validation for data quality
    - Polars-optimized batch processing
    - Tiered caching

    Args:
        symbols: List of crypto symbols (default: POPULAR_CRYPTOS)
        use_validation: Use cross-validation (slower but more reliable)
        force_refresh: Ignore cache
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTOS[:50]  # Top 50 by default

        logger.info(
            f"Fetching crypto batch for {len(symbols)} symbols (validation={use_validation})"
        )

        # Get unified provider
        provider = get_unified_crypto_provider()

        # Fetch batch
        start_time = datetime.now()
        results = await provider.fetch_batch_cryptos(
            symbols, use_validation=use_validation, force_refresh=force_refresh
        )

        # Calculate success rate
        successful = sum(1 for v in results.values() if v is not None)
        failed = len(symbols) - successful
        success_rate = (successful / len(symbols)) * 100

        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info(
            f"Crypto batch complete: {successful}/{len(symbols)} successful "
            f"({success_rate:.1f}%) in {elapsed:.1f}s"
        )

        # Get provider summary
        provider_summary = provider.get_provider_summary()

        return {
            "source": "unified_crypto_provider",
            "total": len(symbols),
            "success": successful,
            "failed": failed,
            "success_rate": success_rate,
            "elapsed_seconds": elapsed,
            "use_validation": use_validation,
            "provider_summary": {
                "primary": provider_summary["primary_provider"],
                "secondary": provider_summary["secondary_provider"],
                "coingecko_healthy": provider_summary["provider_health"]["coingecko"][
                    "is_healthy"
                ],
                "coinmarketcap_healthy": provider_summary["provider_health"][
                    "coinmarketcap"
                ]["is_healthy"],
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in fetch_crypto_batch: {str(e)}")
        return {"error": str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
async def fetch_crypto_quotes(
    symbol: str, use_validation: bool = False, force_refresh: bool = False
) -> Optional[dict]:
    """
    Fetch single crypto quote with cross-validation

    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')
        use_validation: Use cross-validation
        force_refresh: Ignore cache

    Returns:
        Unified crypto data or None
    """
    try:
        logger.info(f"Fetching quote for {symbol}")

        # Get unified provider
        provider = get_unified_crypto_provider()

        # Fetch data
        data = await provider.fetch_crypto_data(
            symbol, use_validation=use_validation, force_refresh=force_refresh
        )

        if data:
            logger.info(
                f"Successfully fetched quote for {symbol}: ${data.get('price', 0)}"
            )
        else:
            logger.warning(f"Failed to fetch quote for {symbol}")

        return data

    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {str(e)}")
        return None


@dramatiq.actor(broker=broker, max_retries=3)
async def fetch_trending_cryptos(limit: int = 10) -> List[dict]:
    """
    Fetch trending cryptocurrencies

    Args:
        limit: Number of trending cryptos to return

    Returns:
        List of trending crypto data
    """
    try:
        logger.info(f"Fetching {limit} trending cryptos...")

        # Get unified provider
        provider = get_unified_crypto_provider()

        # Fetch trending
        trending = await provider.get_trending_cryptos(limit)

        logger.info(f"Retrieved {len(trending)} trending cryptos")

        return trending

    except Exception as e:
        logger.error(f"Error fetching trending cryptos: {str(e)}")
        return []


@dramatiq.actor(broker=broker, max_retries=3)
async def fetch_top_cryptos(
    limit: int = 100, sort_by: str = "market_cap"
) -> List[dict]:
    """
    Fetch top cryptocurrencies by ranking

    Args:
        limit: Number of results
        sort_by: Sort field (market_cap, volume, change_24h)

    Returns:
        List of top crypto data
    """
    try:
        logger.info(f"Fetching top {limit} cryptos by {sort_by}...")

        # Get unified provider
        provider = get_unified_crypto_provider()

        # Fetch top cryptos
        top_cryptos = await provider.get_top_cryptos(limit, sort_by)

        logger.info(f"Retrieved {len(top_cryptos)} top cryptos")

        return top_cryptos

    except Exception as e:
        logger.error(f"Error fetching top cryptos: {str(e)}")
        return []


@dramatiq.actor(broker=broker, max_retries=0)
async def validate_crypto_batch(symbols: List[str]) -> dict:
    """
    Cross-validate crypto data between CoinGecko and CoinMarketCap

    Args:
        symbols: List of crypto symbols to validate

    Returns:
        Validation results summary
    """
    try:
        logger.info(f"Validating {len(symbols)} cryptos...")

        # Get cross-validator
        validator = get_crypto_cross_validator()

        # Validate batch
        results = await validator.validate_batch(symbols)

        # Calculate statistics
        total = len(results)
        avg_confidence = (
            sum(r.overall_confidence for r in results.values() if r.overall_confidence)
            / total
            if total > 0
            else 0
        )

        cg_count = sum(1 for r in results.values() if r.coingecko_data)
        cmc_count = sum(1 for r in results.values() if r.coinmarketcap_data)
        both_count = sum(
            1 for r in results.values() if r.coingecko_data and r.coinmarketcap_data
        )

        logger.info(
            f"Validation complete: avg_confidence={avg_confidence:.2f}, "
            f"CG={cg_count}, CMC={cmc_count}, both={both_count}"
        )

        return {
            "source": "crypto_cross_validator",
            "total_validations": total,
            "avg_confidence": avg_confidence,
            "coingecko_available": cg_count,
            "coinmarketcap_available": cmc_count,
            "both_available": both_count,
            "validation_results": {
                symbol: result.to_dict() for symbol, result in results.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in validate_crypto_batch: {str(e)}")
        return {"error": str(e)}


@dramatiq.actor(broker=broker, max_retries=0)
async def detect_crypto_anomalies(
    symbols: Optional[List[str]] = None, threshold: float = 0.5
) -> List[dict]:
    """
    Detect anomalies in crypto data

    Anomalies are defined as data with confidence < threshold

    Args:
        symbols: List of crypto symbols to check (default: POPULAR_CRYPTOS)
        threshold: Confidence threshold (default: 0.5)

    Returns:
        List of detected anomalies
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTOS[:50]

        logger.info(
            f"Checking {len(symbols)} symbols for anomalies (threshold={threshold})"
        )

        # Get cross-validator
        validator = get_crypto_cross_validator()

        # Detect anomalies
        anomalies = await validator.detect_anomalies(symbols, threshold)

        logger.info(
            f"Detected {len(anomalies)} anomalies out of {len(symbols)} symbols"
        )

        return anomalies

    except Exception as e:
        logger.error(f"Error detecting crypto anomalies: {str(e)}")
        return []


@dramatiq.actor(broker=broker, max_retries=0)
async def get_provider_health() -> dict:
    """
    Get health status of all crypto providers

    Returns:
        Provider health summary
    """
    try:
        # Get unified provider
        provider = get_unified_crypto_provider()

        # Get summary
        summary = provider.get_provider_summary()

        logger.info(
            f"Provider health: CG={summary['provider_health']['coingecko']['is_healthy']}, "
            f"CMC={summary['provider_health']['coinmarketcap']['is_healthy']}"
        )

        return summary

    except Exception as e:
        logger.error(f"Error getting provider health: {str(e)}")
        return {"error": str(e)}


@dramatiq.actor(broker=broker, max_retries=0)
async def get_validation_summary() -> dict:
    """
    Get summary of all cached validations

    Returns:
        Validation statistics summary
    """
    try:
        # Get cross-validator
        validator = get_crypto_cross_validator()

        # Get summary
        summary = validator.get_validation_summary()

        return summary

    except Exception as e:
        logger.error(f"Error getting validation summary: {str(e)}")
        return {"error": str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
async def clear_validation_cache() -> dict:
    """Clear validation cache"""
    try:
        logger.info("Clearing validation cache...")

        # Get cross-validator
        validator = get_crypto_cross_validator()

        # Clear cache
        validator.clear_cache()

        logger.info("Validation cache cleared")

        return {
            "source": "crypto_cross_validator",
            "status": "cleared",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error clearing validation cache: {str(e)}")
        return {"error": str(e)}


# Scheduler tasks
@dramatiq.actor(broker=broker, max_retries=3)
async def periodic_crypto_update() -> dict:
    """
    Periodic crypto data update
    Runs every 5 minutes for top 50 cryptos with validation
    """
    try:
        logger.info("Running periodic crypto update...")

        # Fetch top 50 with validation
        result = await fetch_crypto_batch(
            symbols=POPULAR_CRYPTOS[:50], use_validation=True, force_refresh=False
        )

        logger.info(
            f"Periodic update complete: {result.get('success', 0)}/{result.get('total', 0)} successful"
        )

        return result

    except Exception as e:
        logger.error(f"Error in periodic_crypto_update: {str(e)}")
        return {"error": str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
async def periodic_health_check() -> dict:
    """
    Periodic provider health check
    Runs every 10 minutes
    """
    try:
        logger.info("Running provider health check...")

        # Get provider health
        health = await get_provider_health()

        # Log status
        for provider_name, provider_data in health["provider_health"].items():
            status = "healthy" if provider_data["is_healthy"] else "unhealthy"
            logger.info(f"{provider_name}: {status}")

        return health

    except Exception as e:
        logger.error(f"Error in periodic_health_check: {str(e)}")
        return {"error": str(e)}
