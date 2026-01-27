"""
Background Tasks for Scheduled Data Fetching
Implements scheduled jobs for fetching and updating financial data
"""
import dramatiq
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries
from django.conf import settings
from datetime import datetime, timedelta
import logging

from data.data_providers.yahooFinance.scraper import YahooFinanceScraper
from data.data_providers.alphaVantage.scraper import AlphaVantageScraper
from data.data_providers.binance.scraper import BinanceScraper
from data.data_providers.coinGecko.scraper import CoinGeckoScraper, get_popular_cryptos
from data.data_providers.coinMarketCap.scraper import CoinMarketCapScraper
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Initialize Dramatiq broker
broker = StubBroker()
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))  # 1 hour
broker.add_middleware(TimeLimit(limit=1000 * 60 * 30))  # 30 minutes
broker.add_middleware(Retries(max_retries=3))

# Initialize scrapers
yahoo_scraper = YahooFinanceScraper()
alpha_scraper = AlphaVantageScraper(api_key=getattr(settings, 'ALPHA_VANTAGE_API_KEY', None))
binance_scraper = BinanceScraper()
coingecko_scraper = CoinGeckoScraper()
coinmarketcap_scraper = CoinMarketCapScraper()


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


@dramatiq.actor(broker=broker, max_retries=3)
def fetch_stocks_yahoo(symbols: list = None) -> dict:
    """
    Fetch stock data from Yahoo Finance
    Runs every 15 minutes
    """
    try:
        if symbols is None:
            symbols = POPULAR_STOCKS[:20]  # Fetch top 20
        
        logger.info(f"Fetching stock data from Yahoo Finance for {len(symbols)} symbols")
        
        results = yahoo_scraper.fetch_multiple_stocks(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"Yahoo Finance: {success_count}/{len(symbols)} stocks fetched successfully")
        
        return {
            'source': 'yahoo',
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in fetch_stocks_yahoo: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
def fetch_stocks_alpha(symbols: list = None) -> dict:
    """
    Fetch stock data from Alpha Vantage
    Runs every 5 minutes (rate limited)
    """
    try:
        if symbols is None:
            symbols = POPULAR_STOCKS[:10]  # Fetch top 10 due to rate limits
        
        logger.info(f"Fetching stock data from Alpha Vantage for {len(symbols)} symbols")
        
        results = alpha_scraper.fetch_multiple_stocks(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"Alpha Vantage: {success_count}/{len(symbols)} stocks fetched successfully")
        
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


@dramatiq.actor(broker=broker, max_retries=3)
def fetch_cryptos_binance(symbols: list = None) -> dict:
    """
    Fetch crypto data from Binance
    Runs every 5 minutes
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTOS[:20]
        
        logger.info(f"Fetching crypto data from Binance for {len(symbols)} symbols")
        
        results = binance_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"Binance: {success_count}/{len(symbols)} cryptos fetched successfully")
        
        return {
            'source': 'binance',
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in fetch_cryptos_binance: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
def fetch_cryptos_coingecko(symbols: list = None) -> dict:
    """
    Fetch crypto data from CoinGecko
    Runs every 15 minutes (rate limited)
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTOS[:20]
        
        logger.info(f"Fetching crypto data from CoinGecko for {len(symbols)} symbols")
        
        results = coingecko_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"CoinGecko: {success_count}/{len(symbols)} cryptos fetched successfully")
        
        return {
            'source': 'coingecko',
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in fetch_cryptos_coingecko: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
def fetch_cryptos_coinmarketcap(symbols: list = None) -> dict:
    """
    Fetch crypto data from CoinMarketCap
    Runs every 15 minutes (rate limited)
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTOS[:20]
        
        logger.info(f"Fetching crypto data from CoinMarketCap for {len(symbols)} symbols")
        
        results = coinmarketcap_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        
        logger.info(f"CoinMarketCap: {success_count}/{len(symbols)} cryptos fetched successfully")
        
        return {
            'source': 'coinmarketcap',
            'total': len(symbols),
            'success': success_count,
            'failed': len(symbols) - success_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in fetch_cryptos_coinmarketcap: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=2)
def fetch_all_markets() -> dict:
    """
    Fetch data from all sources
    Runs every 30 minutes
    """
    try:
        logger.info("Starting full market data fetch from all sources")
        
        results = {
            'stocks_yahoo': fetch_stocks_yahoo(),
            'stocks_alpha': fetch_stocks_alpha(),
            'cryptos_binance': fetch_cryptos_binance(),
            'cryptos_coingecko': fetch_cryptos_coingecko(),
            'cryptos_coinmarketcap': fetch_cryptos_coinmarketcap(),
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
def update_asset_price(symbol: str, source: str = 'yahoo') -> dict:
    """
    Update price for a single asset
    Can be triggered manually or via alerts
    """
    try:
        logger.info(f"Updating price for {symbol} from {source}")
        
        if source == 'yahoo':
            scraper = yahoo_scraper
        elif source == 'alpha':
            scraper = alpha_scraper
        elif source == 'binance':
            scraper = binance_scraper
        elif source == 'coingecko':
            scraper = coingecko_scraper
        elif source == 'coinmarketcap':
            scraper = coinmarketcap_scraper
        else:
            return {'error': f'Unknown source: {source}'}
        
        success = scraper.fetch_and_save_crypto(symbol) if 'crypto' in source.lower() or source in ['binance', 'coingecko', 'coinmarketcap'] else scraper.fetch_and_save_stock(symbol)
        
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
    Clean old historical price data
    Runs daily
    """
    try:
        logger.info(f"Cleaning price data older than {days} days")
        
        from assets.models.historic.prices import AssetPricesHistoric
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        deleted_count, _ = AssetPricesHistoric.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned {deleted_count} old price records")
        
        return {
            'deleted_count': deleted_count,
            'cutoff_days': days,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in clean_old_data: {str(e)}")
        return {'error': str(e)}


def schedule_tasks():
    """
    Schedule all background tasks
    This should be called during application startup
    """
    logger.info("Scheduling background tasks...")
    
    # Fetch stocks every 15 minutes
    fetch_stocks_yahoo.send_with_options(
        delay=1000 * 60 * 15,  # 15 minutes
        repeat=True
    )
    
    # Fetch stocks from Alpha Vantage every 5 minutes (rate limited)
    fetch_stocks_alpha.send_with_options(
        delay=1000 * 60 * 5,  # 5 minutes
        repeat=True
    )
    
    # Fetch cryptos every 5 minutes
    fetch_cryptos_binance.send_with_options(
        delay=1000 * 60 * 5,  # 5 minutes
        repeat=True
    )
    
    # Fetch cryptos from CoinGecko every 15 minutes (rate limited)
    fetch_cryptos_coingecko.send_with_options(
        delay=1000 * 60 * 15,  # 15 minutes
        repeat=True
    )
    
    # Fetch cryptos from CoinMarketCap every 15 minutes (rate limited)
    fetch_cryptos_coinmarketcap.send_with_options(
        delay=1000 * 60 * 15,  # 15 minutes
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
    
    logger.info("All background tasks scheduled successfully")


if __name__ == "__main__":
    # Run a single task for testing
    print("Testing background tasks...")
    
    # Test stock fetch
    result = fetch_stocks_yahoo(['AAPL', 'GOOGL', 'MSFT'])
    print(f"Stock fetch result: {result}")
    
    # Test crypto fetch
    result = fetch_cryptos_binance(['BTC', 'ETH', 'SOL'])
    print(f"Crypto fetch result: {result}")
    
    # Test single asset update
    result = update_asset_price('TSLA', 'yahoo')
    print(f"Asset update result: {result}")
