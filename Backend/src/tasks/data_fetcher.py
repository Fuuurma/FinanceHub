"""
Background Tasks for Scheduled Data Fetching
Implements scheduled jobs for fetching and updating financial data
"""
import dramatiq
import orjson
import polars as pl
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries
from django.conf import settings
from datetime import datetime, timedelta
import logging
import asyncio
from typing import List, Dict, Optional

from data.data_providers.alphaVantage.scraper import AlphaVantageScraper
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Initialize Dramatiq broker
broker = StubBroker()
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))  # 1 hour
broker.add_middleware(TimeLimit(limit=1000 * 60 * 30))  # 30 minutes
broker.add_middleware(Retries(max_retries=3))

# Initialize scrapers with new BaseAPIFetcher-based architecture
alpha_scraper = AlphaVantageScraper()

# Popular stocks to fetch regularly
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
    'V', 'JNJ', 'WMT', 'PG', 'XOM', 'BAC', 'KO', 'PEP', 'COST',
    'DIS', 'NFLX', 'ADBE', 'INTC', 'AMD', 'CRM', 'QCOM', 'AVGO',
    'CSCO', 'IBM', 'ORCL', 'ACN', 'TXN', 'NOW', 'INTU', 'LMT',
    'BA', 'NOC', 'RTX', 'GD', 'HON', 'MMM', 'CAT', 'DE', 'GE'
]

# Popular cryptocurrencies to fetch regularly
POPULAR_CRYPTOS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT',
    'MATIC', 'LTC', 'AVAX', 'LINK', 'UNI', 'ATOM', 'XLM',
    'ETC', 'XMR', 'ALGO', 'VET', 'FIL', 'NEAR', 'AAVE', 'XTZ'
]

# Performance optimized batch processor using polars
def process_batch_data(data: List[Dict]) -> pl.DataFrame:
    """
    Process batch financial data using polars for performance
    
    Args:
        data: List of dictionaries containing financial data
        
    Returns:
        Polars DataFrame with processed data
    """
    if not data:
        return pl.DataFrame()
    
    # Convert to polars DataFrame for fast processing
    try:
        # Use orjson for fast JSON serialization if data is JSON string
        if isinstance(data[0], str):
            parsed_data = []
            for item in data:
                parsed_data.append(orjson.loads(item))
            df = pl.DataFrame(parsed_data)
        else:
            df = pl.DataFrame(data)
        
        # Process data efficiently
        processed_df = (
            df
            .with_columns([
                # Add calculated columns if they exist
                pl.col('close').alias('price') if 'close' in df.columns else pl.lit(None).alias('price'),
                pl.col('volume').alias('trading_volume') if 'volume' in df.columns else pl.lit(None).alias('trading_volume'),
            ])
            # Fill nulls efficiently
            .fill_null(0)
            # Sort by timestamp if available
            .sort('timestamp' if 'timestamp' in df.columns else 'date')
        )
        
        return processed_df
    except Exception as e:
        logger.error(f"Error processing batch data: {str(e)}")
        return pl.DataFrame()


@dramatiq.actor(broker=broker, max_retries=3)
async def fetch_stocks_alpha(symbols: Optional[List[str]] = None) -> dict:
    """
    Fetch stock data from Alpha Vantage using new key rotation system
    Runs every 5 minutes (rate limited)
    
    Performance optimized with async and batch processing
    """
    try:
        if symbols is None:
            symbols = POPULAR_STOCKS[:10]  # Fetch top 10 due to rate limits
        
        logger.info(f"Fetching stock data from Alpha Vantage for {len(symbols)} symbols")
        
        results = await alpha_scraper.fetch_multiple_stocks(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"Alpha Vantage: {success_count}/{len(symbols)} stocks fetched successfully")
        
        # Process batch data efficiently
        if success_count > 0:
            successful_data = [data for data in results.values() if data]
            processed_df = process_batch_data(successful_data)
            logger.info(f"Processed {len(processed_df)} records with polars")
        
        return {
            'source': 'alpha_vantage',
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in fetch_stocks_alpha: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=2)
async def fetch_all_markets() -> dict:
    """
    Fetch data from all sources using async operations
    Runs every 30 minutes
    """
    try:
        logger.info("Starting full market data fetch from all sources")
        
        # Run tasks concurrently for better performance
        stock_task = fetch_stocks_alpha()
        
        # Add other tasks as they get implemented with BaseAPIFetcher
        # crypto_tasks = [fetch_cryptos_binance(), fetch_cryptos_coingecko()]
        
        results = {
            'stocks_alpha': await stock_task,
            # 'cryptos_binance': await crypto_tasks[0],
            # 'cryptos_coingecko': await crypto_tasks[1],
        }
        
        logger.info(f"Full market fetch completed: {results}")
        
        return {
            'completed_at': datetime.now().isoformat(),
            'sources': list(results.keys())
        }
    except Exception as e:
        logger.error(f"Error in fetch_all_markets: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=2)
async def update_asset_price(symbol: str, source: str = 'alpha_vantage') -> dict:
    """
    Update price for a single asset using async operations
    Can be triggered manually or via alerts
    """
    try:
        logger.info(f"Updating price for {symbol} from {source}")
        
        if source == 'alpha_vantage':
            scraper = alpha_scraper
        else:
            return {'error': f'Unknown source: {source}'}
        
        # Use async fetch_and_save_stock method
        success = await scraper.fetch_and_save_stock(symbol)
        
        return {
            'symbol': symbol,
            'source': source,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in update_asset_price for {symbol}: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=1)
def clean_old_data(days: int = 365) -> dict:
    """
    Clean old historical price data efficiently
    Runs daily with optimized batch deletion
    """
    try:
        logger.info(f"Cleaning price data older than {days} days")
        
        from assets.models.historic.prices import AssetPricesHistoric
        from django.utils import timezone
        from django.db.models import Q
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Batch delete for performance
        deleted_count = 0
        batch_size = 1000
        
        while True:
            # Use efficient bulk delete with limit
            batch_ids = AssetPricesHistoric.objects.filter(
                timestamp__lt=cutoff_date
            ).values_list('id', flat=True)[:batch_size]
            
            if not batch_ids:
                break
                
            _, deleted = AssetPricesHistoric.objects.filter(
                id__in=list(batch_ids)
            ).delete()
            
            deleted_count += deleted[0]
            logger.info(f"Deleted batch of {deleted[0]} records")
        
        logger.info(f"Cleaned {deleted_count} old price records")
        
        return {
            'deleted_count': deleted_count,
            'cutoff_days': days,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in clean_old_data: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
async def batch_update_assets(symbols: List[str], source: str = 'alpha_vantage') -> dict:
    """
    Batch update multiple assets efficiently using async operations
    
    Args:
        symbols: List of asset symbols to update
        source: Data source provider
        
    Returns:
        Dictionary with batch update results
    """
    try:
        logger.info(f"Batch updating {len(symbols)} assets from {source}")
        
        if source == 'alpha_vantage':
            scraper = alpha_scraper
        else:
            return {'error': f'Unsupported source for batch update: {source}'}
        
        # Process in smaller batches for rate limiting
        batch_size = 5
        results = []
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_results = []
            
            # Process batch concurrently
            tasks = [
                scraper.fetch_and_save_stock(symbol)
                for symbol in batch
            ]
            batch_success = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, success in zip(batch, batch_success):
                if isinstance(success, Exception):
                    logger.error(f"Error updating {symbol}: {str(success)}")
                    results.append({'symbol': symbol, 'success': False, 'error': str(success)})
                else:
                    results.append({'symbol': symbol, 'success': success})
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        success_count = sum(1 for r in results if r.get('success', False))
        
        return {
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in batch_update_assets: {str(e)}")
        return {'error': str(e)}


def schedule_tasks():
    """
    Schedule all background tasks efficiently
    This should be called during application startup
    """
    logger.info("Scheduling background tasks...")
    
    # Fetch stocks every 5 minutes (rate limited)
    fetch_stocks_alpha.send_with_options(
        delay=1000 * 60 * 5,  # 5 minutes
        repeat=True
    )
    
    # Fetch all markets every 30 minutes
    fetch_all_markets.send_with_options(
        delay=1000 * 60 * 30,  # 30 minutes
        repeat=True
    )
    
    # Clean old data daily
    clean_old_data.send_with_options(
        delay=1000 * 60 * 60 * 24,  # 24 hours
        repeat=True
    )
    
    # Batch update popular stocks hourly
    batch_update_assets.send_with_options(
        args=[POPULAR_STOCKS[:20], 'alpha_vantage'],
        delay=1000 * 60 * 60,  # 60 minutes
        repeat=True
    )
    
    logger.info("All background tasks scheduled successfully")


if __name__ == "__main__":
    # Run a single task for testing
    print("Testing background tasks...")
    
    # Test stock fetch
    result = asyncio.run(fetch_stocks_alpha(['AAPL', 'GOOGL', 'MSFT']))
    print(f"Stock fetch result: {result}")
    
    # Test single asset update
    result = asyncio.run(update_asset_price('TSLA', 'alpha_vantage'))
    print(f"Asset update result: {result}")
    
    # Test batch update
    result = asyncio.run(batch_update_assets(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']))
    print(f"Batch update result: {result}")
