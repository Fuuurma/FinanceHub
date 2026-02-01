"""
Polygon.io Celery Tasks
Background tasks for fetching stock data, options, and technical indicators from Polygon.io
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from celery import shared_task
from django.utils import timezone
from datetime import datetime

from assets.models.asset import Asset
from investments.models import DataProvider
from investments.models.options import (
    OptionContract,
    OptionsContractSnapshot,
    OptionsGreeksHistory,
)
from data.data_providers.polygon_io.scraper import PolygonIOScraper

logger = logging.getLogger(__name__)


def parse_decimal(value: Any) -> Optional[Decimal]:
    """Parse value to Decimal, returning None for invalid values"""
    if value is None or value == "" or value == "None":
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_stock_trades(self, symbol: str, days: int = 30) -> Dict[str, Any]:
    """
    Fetch trade and quote data for a stock from Polygon.io

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        days: Number of days of historical data to fetch

    Returns:
        Dict with status and data saved
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            logger.warning(f"Asset not found for symbol: {symbol}")
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = PolygonIOScraper()

        async def fetch_data():
            async with scraper:
                # Calculate date range
                end_date = datetime.now()
                from_date = end_date - timezone.timedelta(days=days)
                from_str = from_date.strftime("%Y-%m-%d")
                to_str = end_date.strftime("%Y-%m-%d")

                # Fetch aggregate bars
                bars = await scraper.get_aggregate_bars(
                    symbol,
                    timespan="day",
                    multiplier=1,
                    from_date=from_str,
                    to_date=to_str,
                )

                # Fetch last trade
                last_trade = await scraper.get_last_trade(symbol)

                # Fetch last quote
                last_quote = await scraper.get_last_quote(symbol)

                return {
                    "bars": bars,
                    "last_trade": last_trade,
                    "last_quote": last_quote,
                }

        data = asyncio.run(fetch_data())

        # Update asset with latest price
        if data["last_trade"] and "results" in data["last_trade"]:
            trade = data["last_trade"]["results"][0]
            asset.last_price = parse_decimal(trade.get("p"))
            asset.last_trade_volume = parse_decimal(trade.get("v"))
            asset.last_updated = timezone.now()
            asset.save(
                update_fields=["last_price", "last_trade_volume", "last_updated"]
            )

        # Update data provider status
        data_provider, _ = DataProvider.objects.get_or_create(
            code="polygon_io",
            defaults={"name": "Polygon.io", "is_active": True},
        )

        return {
            "status": "success",
            "symbol": symbol,
            "data_provider": "polygon_io",
            "timestamp": timezone.now().isoformat(),
            "has_bars": bool(data["bars"] and "results" in data["bars"]),
            "has_last_trade": bool(
                data["last_trade"] and "results" in data["last_trade"]
            ),
            "has_last_quote": bool(
                data["last_quote"] and "results" in data["last_quote"]
            ),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching trades/quotes for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_options_chain(
    self, underlying_symbol: str, expiration: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch options chain for an underlying symbol

    Args:
        underlying_symbol: Underlying stock ticker (e.g., 'AAPL')
        expiration: Optional expiration date filter (YYYY-MM-DD)

    Returns:
        Dict with status and contracts saved
    """
    try:
        underlying_asset = Asset.objects.filter(
            symbol__iexact=underlying_symbol,
            asset_type__name="stock",
            is_active=True,
        ).first()

        if not underlying_asset:
            return {
                "status": "error",
                "message": f"Underlying asset not found: {underlying_symbol}",
            }

        scraper = PolygonIOScraper()

        async def fetch_chain():
            async with scraper:
                return await scraper.get_options_chain(
                    underlying_symbol=underlying_symbol,
                    expiration=expiration,
                    limit=1000,
                )

        data = asyncio.run(fetch_chain())

        if not data or "results" not in data:
            return {"status": "error", "message": "No options data returned"}

        contracts_saved = 0

        for contract_data in data["results"]:
            try:
                # Parse option contract details from Polygon.io format
                ticker = contract_data.get("ticker", "")

                # Parse contract components from ticker (e.g., O:AAPL230120C00150000)
                contract_parts = ticker.split(":")
                if len(contract_parts) == 2:
                    contract_info = contract_parts[1]
                    # AAPL230120C00150000
                    # Underlying(4) + Expiry(6) + Type(1) + Strike(8)
                    if len(contract_info) >= 19:
                        contract_underlying = contract_info[:4]
                        expiry_str = contract_info[4:10]
                        option_type = contract_info[10]
                        strike_str = contract_info[11:]

                        # Parse expiry date
                        try:
                            expiry_date = datetime.strptime(expiry_str, "%y%m%d").date()
                        except ValueError:
                            expiry_date = None

                        # Parse strike price
                        try:
                            strike_price = Decimal(strike_str) / 1000
                        except (ValueError, TypeError):
                            strike_price = None

                        # Create or update contract
                        contract, created = OptionContract.objects.update_or_create(
                            symbol=ticker,
                            defaults={
                                "underlying_asset": underlying_asset,
                                "option_type": "call" if option_type == "C" else "put",
                                "strike_price": strike_price,
                                "expiration_date": expiry_date,
                                "contract_size": contract_data.get(
                                    "contract_size", 100
                                ),
                                "exercise_style": contract_data.get(
                                    "exercise_style", "american"
                                ),
                                "exchange": contract_data.get("exchange", ""),
                                "is_active": contract_data.get("active", True),
                                "last_updated": timezone.now(),
                            },
                        )
                        contracts_saved += 1

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.debug(
                    f"Error processing contract {contract_data.get('ticker')}: {e}"
                )
                continue

        return {
            "status": "success",
            "underlying_symbol": underlying_symbol,
            "expiration": expiration,
            "contracts_saved": contracts_saved,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching options chain for {underlying_symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_option_snapshot(self, option_symbol: str) -> Dict[str, Any]:
    """
    Fetch real-time snapshot for an option contract

    Args:
        option_symbol: Full option contract ticker (e.g., 'O:AAPL230120C00150000')

    Returns:
        Dict with status and snapshot data
    """
    try:
        contract = OptionContract.objects.filter(symbol=option_symbol).first()

        if not contract:
            return {
                "status": "error",
                "message": f"Option contract not found: {option_symbol}",
            }

        scraper = PolygonIOScraper()

        async def fetch_snapshot():
            async with scraper:
                return await scraper.get_option_snapshot(option_ticker=option_symbol)

        data = asyncio.run(fetch_snapshot())

        if not data or "results" not in data:
            return {"status": "error", "message": "No snapshot data returned"}

        snapshot_data = data["results"][0]

        # Save snapshot
        OptionsContractSnapshot.objects.create(
            contract=contract,
            last_price=parse_decimal(snapshot_data.get("last", {}).get("price")),
            bid=parse_decimal(snapshot_data.get("bid", {}).get("price")),
            ask=parse_decimal(snapshot_data.get("ask", {}).get("price")),
            volume=parse_decimal(snapshot_data.get("volume")),
            open_interest=parse_decimal(snapshot_data.get("open_interest")),
            implied_volatility=parse_decimal(snapshot_data.get("implied_volatility")),
            delta=parse_decimal(snapshot_data.get("greeks", {}).get("delta")),
            gamma=parse_decimal(snapshot_data.get("greeks", {}).get("gamma")),
            theta=parse_decimal(snapshot_data.get("greeks", {}).get("theta")),
            vega=parse_decimal(snapshot_data.get("greeks", {}).get("vega")),
            rho=parse_decimal(snapshot_data.get("greeks", {}).get("rho")),
            trade_count=snapshot_data.get("trade_count"),
            timestamp=timezone.now(),
        )

        return {
            "status": "success",
            "option_symbol": option_symbol,
            "snapshot_saved": True,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching option snapshot for {option_symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_technical_indicators(
    self, symbol: str, indicator: str = "sma", window: int = 50, timespan: str = "day"
) -> Dict[str, Any]:
    """
    Fetch technical indicators for a stock

    Args:
        symbol: Stock ticker symbol
        indicator: Technical indicator (sma, ema, rsi, macd, bbands)
        window: Window size for the indicator
        timespan: Time window size (minute, hour, day, week, month)

    Returns:
        Dict with status and indicator data
    """
    try:
        asset = Asset.objects.filter(
            symbol__iexact=symbol,
            asset_type__name="stock",
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = PolygonIOScraper()

        async def fetch_indicator():
            async with scraper:
                if indicator == "sma":
                    return await scraper.get_sma(
                        symbol, window=window, timespan=timespan
                    )
                elif indicator == "ema":
                    return await scraper.get_ema(
                        symbol, window=window, timespan=timespan
                    )
                elif indicator == "rsi":
                    return await scraper.get_rsi(
                        symbol, window=window, timespan=timespan
                    )
                elif indicator == "macd":
                    return await scraper.get_macd(
                        symbol, fast=12, slow=26, signal=9, timespan=timespan
                    )
                elif indicator == "bbands":
                    return await scraper.get_bollinger_bands(
                        symbol, window=window, timespan=timespan
                    )
                else:
                    return None

        data = asyncio.run(fetch_indicator())

        if not data or "results" not in data:
            return {"status": "error", "message": f"No {indicator} data returned"}

        results = data["results"]
        values = results.get("values", [])

        # Save to appropriate model or log
        logger.info(f"Fetched {len(values)} {indicator} values for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "indicator": indicator,
            "values_count": len(values),
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching {indicator} for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_gainers_losers(
    self, direction: str = "gainers", market: str = "stocks"
) -> Dict[str, Any]:
    """
    Fetch top gainers or losers from the market

    Args:
        direction: 'gainers' or 'losers'
        market: Market type ('stocks', 'crypto', 'fx', 'indices')

    Returns:
        Dict with status and tickers
    """
    try:
        scraper = PolygonIOScraper()

        async def fetch_data():
            async with scraper:
                return await scraper.get_gainers_losers(
                    direction=direction, market=market
                )

        data = asyncio.run(fetch_data())

        if not data or "results" not in data:
            return {"status": "error", "message": "No data returned"}

        tickers = [t["ticker"] for t in data["results"]]

        # Update asset prices for these tickers
        for ticker in tickers[:20]:  # Process top 20
            fetch_stock_trades.delay(ticker, days=1)

        return {
            "status": "success",
            "direction": direction,
            "market": market,
            "tickers_count": len(tickers),
            "tickers": tickers[:10],  # Return top 10
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching {direction} for {market}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def fetch_market_snapshots(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetch snapshot data for multiple tickers

    Args:
        tickers: List of tickers to fetch (optional, if not provided uses popular stocks)

    Returns:
        Dict with status and snapshot data
    """
    try:
        if not tickers:
            # Get popular active stocks
            tickers = list(
                Asset.objects.filter(
                    asset_type__name="stock",
                    is_active=True,
                ).values_list("symbol", flat=True)[:50]
            )

        if not tickers:
            return {"status": "error", "message": "No tickers provided or found"}

        scraper = PolygonIOScraper()

        async def fetch_data():
            async with scraper:
                tickers_str = ",".join(tickers)
                return await scraper.get_snapshot(tickers=tickers_str)

        data = asyncio.run(fetch_data())

        if not data or "results" not in data:
            return {"status": "error", "message": "No snapshot data returned"}

        snapshots_saved = 0

        for snapshot in data["results"]:
            ticker = snapshot.get("T") or snapshot.get("ticker")
            if not ticker:
                continue

            asset = Asset.objects.filter(symbol__iexact=ticker).first()
            if not asset:
                continue

            # Update asset with snapshot data
            if "last" in snapshot:
                asset.last_price = parse_decimal(snapshot["last"].get("p"))
            if "v" in snapshot:
                asset.last_trade_volume = parse_decimal(snapshot["v"])

            asset.last_updated = timezone.now()
            asset.save(
                update_fields=["last_price", "last_trade_volume", "last_updated"]
            )
            snapshots_saved += 1

        return {
            "status": "success",
            "tickers_requested": len(tickers),
            "snapshots_saved": snapshots_saved,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching market snapshots: {e}")
        raise self.retry(exc=e)


@shared_task
def sync_polygon_io_provider_status() -> Dict[str, Any]:
    """
    Check Polygon.io API status and update provider configuration

    Returns:
        Dict with provider status
    """
    try:
        scraper = PolygonIOScraper()

        async def check_status():
            async with scraper:
                # Try to fetch aggregate bars for a well-known stock
                result = await scraper.get_aggregate_bars(
                    "AAPL", timespan="day", multiplier=1, limit=1
                )
                return result and "results" in result

        is_working = asyncio.run(check_status())

        data_provider, created = DataProvider.objects.get_or_create(
            code="polygon_io",
            defaults={
                "name": "Polygon.io",
                "is_active": is_working,
            },
        )

        if not created:
            data_provider.is_active = is_working
            data_provider.save()

        return {
            "status": "success",
            "provider": "polygon_io",
            "is_active": is_working,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error checking Polygon.io status: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def fetch_stocks_batch(
    self, tickers: List[str], historical_days: int = 30
) -> Dict[str, Any]:
    """
    Fetch data for multiple stocks in batch

    Args:
        tickers: List of stock tickers
        historical_days: Number of days of historical data

    Returns:
        Dict with processing summary
    """
    try:
        processed = 0
        successful = 0
        failed = 0

        for ticker in tickers:
            try:
                result = fetch_stock_trades.delay(ticker, days=historical_days)
                processed += 1
                successful += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Failed to queue fetch for {ticker}: {e}")
                failed += 1
                continue

        return {
            "status": "completed",
            "total_tickers": len(tickers),
            "queued": successful,
            "failed": failed,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error in batch stock fetch: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def fetch_all_options_chains(self) -> Dict[str, Any]:
    """
    Fetch options chains for all active stocks

    Returns:
        Dict with processing summary
    """
    try:
        stocks = Asset.objects.filter(
            asset_type__name="stock",
            is_active=True,
        ).values_list("symbol", flat=True)[:100]

        queued = 0
        for symbol in stocks:
            try:
                fetch_options_chain.delay(symbol)
                queued += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
                logger.error(f"Failed to queue options chain for {symbol}: {e}")
                continue

        return {
            "status": "completed",
            "stocks_queued": queued,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Error fetching all options chains: {e}")
        return {"status": "error", "message": str(e)}
