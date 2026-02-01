import asyncio
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import pandas as pd
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class YahooFinanceFetcher:
    """
    Yahoo Finance Fetcher
    Free, no API key required
    No official rate limits but use responsibly
    """

    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_ticker_info(self, ticker: str) -> Dict:
        """
        Get comprehensive ticker information

        Returns company info, financials, analyst recommendations, etc.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # Add additional data
            info["recommendations"] = ticker_obj.recommendations
            info["calendar"] = ticker_obj.calendar
            info["major_holders"] = ticker_obj.major_holders
            info["institutional_holders"] = ticker_obj.institutional_holders

            await asyncio.sleep(0.5)  # Rate limiting
            return info

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching Yahoo Finance info for {ticker}: {str(e)}")
            return {}

    async def get_historical_data(
        self, ticker: str, start_date: date, end_date: date, interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data

        Args:
            ticker: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h,
                                    1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(start=start_date, end=end_date, interval=interval)

            await asyncio.sleep(0.5)
            return hist

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return pd.DataFrame()

    async def get_dividends(self, ticker: str) -> pd.Series:
        """Get all historical dividends"""
        try:
            ticker_obj = yf.Ticker(ticker)
            return ticker_obj.dividends
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching dividends for {ticker}: {str(e)}")
            return pd.Series()

    async def get_splits(self, ticker: str) -> pd.Series:
        """Get all historical stock splits"""
        try:
            ticker_obj = yf.Ticker(ticker)
            return ticker_obj.splits
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching splits for {ticker}: {str(e)}")
            return pd.Series()

    async def get_actions(self, ticker: str) -> pd.DataFrame:
        """Get all corporate actions (dividends + splits)"""
        try:
            ticker_obj = yf.Ticker(ticker)
            return ticker_obj.actions
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching actions for {ticker}: {str(e)}")
            return pd.DataFrame()

    async def get_financials(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements

        Returns:
            {
                'income_statement': DataFrame,
                'balance_sheet': DataFrame,
                'cash_flow': DataFrame,
                'quarterly_income_statement': DataFrame,
                'quarterly_balance_sheet': DataFrame,
                'quarterly_cash_flow': DataFrame
            }
        """
        try:
            ticker_obj = yf.Ticker(ticker)

            return {
                "income_statement": ticker_obj.financials,
                "balance_sheet": ticker_obj.balance_sheet,
                "cash_flow": ticker_obj.cashflow,
                "quarterly_income_statement": ticker_obj.quarterly_financials,
                "quarterly_balance_sheet": ticker_obj.quarterly_balance_sheet,
                "quarterly_cash_flow": ticker_obj.quarterly_cashflow,
            }

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching financials for {ticker}: {str(e)}")
            return {}

    async def get_options_chain(self, ticker: str, date: Optional[str] = None) -> Dict:
        """
        Get options chain

        Args:
            ticker: Stock symbol
            date: Expiration date (YYYY-MM-DD), if None returns nearest expiry

        Returns:
            {
                'calls': DataFrame,
                'puts': DataFrame
            }
        """
        try:
            ticker_obj = yf.Ticker(ticker)

            if date:
                opts = ticker_obj.option_chain(date)
            else:
                # Get nearest expiry
                opts = ticker_obj.option_chain(ticker_obj.options[0])

            return {"calls": opts.calls, "puts": opts.puts}

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching options for {ticker}: {str(e)}")
            return {}

    async def get_multiple_tickers(
        self, tickers: List[str], start_date: date, end_date: date, interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Download data for multiple tickers at once (more efficient)

        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            Multi-index DataFrame with tickers as columns
        """
        try:
            data = yf.download(
                tickers=" ".join(tickers),
                start=start_date,
                end=end_date,
                interval=interval,
                group_by="ticker",
                auto_adjust=True,
                prepost=False,
                threads=True,
                proxy=None,
            )

            await asyncio.sleep(1)  # Rate limiting
            return data

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching multiple tickers: {str(e)}")
            return pd.DataFrame()
