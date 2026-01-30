"""
AI Template Generation Celery Tasks
Pre-generated templates refreshed twice daily.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


# Symbol lists for template generation
TOP_EQUITY_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JPM', 'V',
    'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM',
    'PFE', 'TMO', 'ABBV', 'ACN', 'DHR', 'LLY', 'NKE', 'MRK', 'COST', 'ABT',
    'AMD', 'INTC', 'QCOM', 'TXN', 'AVGO', 'NOW', 'AMAT', 'MU', 'LRCX', 'MS',
    'GS', 'BLK', 'C', 'AXP', 'WFC', 'USB', 'PNC', 'TFC', 'COF', 'SCHW',
]

TOP_CRYPTO_SYMBOLS = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'MATIC',
    'LINK', 'UNI', 'ATOM', 'LTC', 'BCH', 'NEAR', 'ARB', 'OP', 'FIL', 'APT',
]

SECTORS = [
    'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 'Communication Services',
    'Industrials', 'Consumer Staples', 'Energy', 'Utilities', 'Real Estate', 'Materials',
]

ASSET_CLASSES = ['equity', 'crypto', 'fixed_income', 'commodity']


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_all_templates(self):
    """
    Master task - generates all AI templates.
    Runs twice daily at 00:00 and 12:00 UTC.
    """
    logger.info("Starting AI template generation batch")
    start_time = timezone.now()
    
    results = {
        'started_at': start_time.isoformat(),
        'templates': {},
        'errors': [],
        'total_tokens': 0,
        'total_time_ms': 0,
    }
    
    try:
        # Market summaries
        results['templates']['market_summary'] = generate_market_summaries.delay().get()
        
        # Asset analysis (equity)
        results['templates']['asset_analysis'] = generate_asset_analysis.delay('equity', TOP_EQUITY_SYMBOLS).get()
        
        # Asset analysis (crypto)
        results['templates']['crypto_analysis'] = generate_asset_analysis.delay('crypto', TOP_CRYPTO_SYMBOLS).get()
        
        # Sector reports
        results['templates']['sector_report'] = generate_sector_reports.delay().get()
        
        # Risk commentary
        results['templates']['risk_commentary'] = generate_risk_commentary.delay().get()
        
        # Sentiment summary
        results['templates']['sentiment_summary'] = generate_sentiment_summaries.delay().get()
        
        # Volatility outlook
        results['templates']['volatility_outlook'] = generate_volatility_outlook.delay(TOP_EQUITY_SYMBOLS).get()
        
        # Options strategies
        results['templates']['options_strategy'] = generate_options_strategies.delay(TOP_EQUITY_SYMBOLS).get()
        
        # Bond market
        results['templates']['bond_market'] = generate_bond_market_analysis.delay().get()
        
        # Crypto market
        results['templates']['crypto_market'] = generate_crypto_market_analysis.delay().get()
        
        end_time = timezone.now()
        results['completed_at'] = end_time.isoformat()
        results['duration_seconds'] = (end_time - start_time).total_seconds()
        
        logger.info(f"AI template generation completed in {results['duration_seconds']:.2f}s")
        
    except Exception as e:
        logger.error(f"Template generation batch failed: {e}")
        results['errors'].append(str(e))
        raise self.retry(exc=e)
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_market_summaries(self):
    """Generate general market summary templates."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    
    # Major indices
    indices = [
        ('SPY', 'S&P 500'),
        ('QQQ', 'NASDAQ 100'),
        ('DIA', 'Dow Jones'),
        ('IWM', 'Russell 2000'),
    ]
    
    for symbol, name in indices:
        try:
            # Fetch market data
            data = fetch_market_data(symbol)
            
            # Generate content
            context = build_market_context(data, symbol)
            generator = get_content_generator()
            prompt_data = generator.generate(ContentType.MARKET_SUMMARY, context)
            
            # Call LLM (simplified)
            content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
            
            # Save template
            template, created = AITemplate.objects.update_or_create(
                template_type='market_summary',
                symbol=symbol,
                defaults={
                    'title': f"{name} Market Summary",
                    'content': content,
                    'summary': content[:200] + "...",
                    'metadata': {
                        'current_price': data.get('price'),
                        'change_pct': data.get('change_pct'),
                        'model': prompt_data.get('model_used'),
                    },
                    'last_generated_at': timezone.now(),
                    'next_refresh_at': timezone.now() + timedelta(hours=6),
                    'is_active': True,
                    'version': 1,
                }
            )
            
            template.version += 1
            template.save()
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            logger.error(f"Failed to generate market summary for {symbol}: {e}")
            results['errors'].append(f"{symbol}: {str(e)}")
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_asset_analysis(self, asset_class: str, symbols: List[str]):
    """Generate asset analysis templates for a list of symbols."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    generator = get_content_generator()
    
    for symbol in symbols:
        try:
            # Fetch asset data
            data = fetch_asset_data(symbol, asset_class)
            
            # Generate content
            context = build_asset_context(data, symbol, asset_class)
            prompt_data = generator.generate(ContentType.ASSET_ANALYSIS, context)
            
            # Call LLM
            content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
            
            # Save template
            template, created = AITemplate.objects.update_or_create(
                template_type='asset_analysis',
                symbol=symbol,
                defaults={
                    'title': f"{symbol} Analysis",
                    'content': content,
                    'summary': content[:200] + "...",
                    'asset_class': asset_class,
                    'metadata': {
                        'price': data.get('price'),
                        'change_pct': data.get('change_pct'),
                        'pe_ratio': data.get('pe_ratio'),
                        'sentiment': data.get('sentiment'),
                    },
                    'last_generated_at': timezone.now(),
                    'next_refresh_at': timezone.now() + timedelta(hours=12),
                    'is_active': True,
                    'version': 1,
                }
            )
            
            template.version += 1
            template.save()
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            logger.error(f"Failed to generate analysis for {symbol}: {e}")
            results['errors'].append(f"{symbol}: {str(e)}")
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_sector_reports(self):
    """Generate sector report templates."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    generator = get_content_generator()
    
    for sector in SECTORS:
        try:
            data = fetch_sector_data(sector)
            context = build_sector_context(data, sector)
            prompt_data = generator.generate(ContentType.SECTOR_REPORT, context)
            
            content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
            
            template, created = AITemplate.objects.update_or_create(
                template_type='sector_report',
                sector=sector,
                defaults={
                    'title': f"{sector} Sector Report",
                    'content': content,
                    'summary': content[:200] + "...",
                    'metadata': {
                        'change_pct': data.get('change_pct'),
                        'top_performers': data.get('top_performers'),
                    },
                    'last_generated_at': timezone.now(),
                    'next_refresh_at': timezone.now() + timedelta(hours=24),
                    'is_active': True,
                    'version': 1,
                }
            )
            
            template.version += 1
            template.save()
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            logger.error(f"Failed to generate sector report for {sector}: {e}")
            results['errors'].append(f"{sector}: {str(e)}")
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_risk_commentary(self):
    """Generate market risk commentary template."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    try:
        data = fetch_risk_data()
        context = build_risk_context(data)
        generator = get_content_generator()
        prompt_data = generator.generate(ContentType.RISK_COMMENTARY, context)
        
        content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
        
        template, _ = AITemplate.objects.update_or_create(
            template_type='risk_commentary',
            symbol=None,
            defaults={
                'title': 'Market Risk Commentary',
                'content': content,
                'summary': content[:200] + "...",
                'metadata': data,
                'last_generated_at': timezone.now(),
                'next_refresh_at': timezone.now() + timedelta(hours=12),
                'is_active': True,
                'version': 1,
            }
        )
        template.version += 1
        template.save()
        
        return {'created': 1, 'updated': 0, 'errors': []}
        
    except Exception as e:
        logger.error(f"Failed to generate risk commentary: {e}")
        return {'created': 0, 'updated': 0, 'errors': [str(e)]}


@shared_task(bind=True, max_retries=2)
def generate_sentiment_summaries(self):
    """Generate sentiment summary templates."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    generator = get_content_generator()
    
    targets = [
        ('MARKET', None),
        ('BTC', 'crypto'),
        ('ETH', 'crypto'),
    ]
    
    for symbol, asset_class in targets:
        try:
            data = fetch_sentiment_data(symbol, asset_class)
            context = build_sentiment_context(data, symbol)
            prompt_data = generator.generate(ContentType.SENTIMENT_SUMMARY, context)
            
            content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
            
            template, created = AITemplate.objects.update_or_create(
                template_type='sentiment_summary',
                symbol=symbol,
                defaults={
                    'title': f"{symbol} Sentiment Summary",
                    'content': content,
                    'summary': content[:200] + "...",
                    'asset_class': asset_class,
                    'metadata': data,
                    'last_generated_at': timezone.now(),
                    'next_refresh_at': timezone.now() + timedelta(hours=12),
                    'is_active': True,
                    'version': 1,
                }
            )
            
            template.version += 1
            template.save()
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            logger.error(f"Failed to generate sentiment for {symbol}: {e}")
            results['errors'].append(f"{symbol}: {str(e)}")
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_volatility_outlook(self, symbols: List[str]):
    """Generate volatility outlook templates."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    generator = get_content_generator()
    
    # Market volatility
    try:
        data = fetch_volatility_data('SPY')
        context = build_volatility_context(data, 'SPY')
        prompt_data = generator.generate(ContentType.VOLATILITY_OUTLOOK, context)
        
        content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
        
        template, created = AITemplate.objects.update_or_create(
            template_type='volatility_outlook',
            symbol='SPY',
            defaults={
                'title': 'Market Volatility Outlook',
                'content': content,
                'summary': content[:200] + "...",
                'metadata': data,
                'last_generated_at': timezone.now(),
                'next_refresh_at': timezone.now() + timedelta(hours=12),
                'is_active': True,
                'version': 1,
            }
        )
        template.version += 1
        template.save()
        results['created' if created else 'updated'] += 1
        
    except Exception as e:
        logger.error(f"Failed to generate volatility outlook: {e}")
        results['errors'].append(str(e))
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_options_strategies(self, symbols: List[str]):
    """Generate options strategy templates."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    results = {'created': 0, 'updated': 0, 'errors': []}
    generator = get_content_generator()
    
    for symbol in symbols[:20]:  # Top 20
        try:
            data = fetch_options_data(symbol)
            context = build_options_context(data, symbol)
            prompt_data = generator.generate(ContentType.OPTIONS_STRATEGY, context)
            
            content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
            
            template, created = AITemplate.objects.update_or_create(
                template_type='options_strategy',
                symbol=symbol,
                defaults={
                    'title': f"{symbol} Options Strategies",
                    'content': content,
                    'summary': content[:200] + "...",
                    'metadata': data,
                    'last_generated_at': timezone.now(),
                    'next_refresh_at': timezone.now() + timedelta(hours=6),
                    'is_active': True,
                    'version': 1,
                }
            )
            
            template.version += 1
            template.save()
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
        except Exception as e:
            logger.error(f"Failed to generate options for {symbol}: {e}")
            results['errors'].append(f"{symbol}: {str(e)}")
    
    return results


@shared_task(bind=True, max_retries=2)
def generate_bond_market_analysis(self):
    """Generate bond market analysis template."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    try:
        data = fetch_bond_data()
        context = build_bond_context(data)
        generator = get_content_generator()
        prompt_data = generator.generate(ContentType.BOND_MARKET, context)
        
        content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
        
        template, _ = AITemplate.objects.update_or_create(
            template_type='bond_market',
            symbol=None,
            defaults={
                'title': 'Bond Market Analysis',
                'content': content,
                'summary': content[:200] + "...",
                'metadata': data,
                'last_generated_at': timezone.now(),
                'next_refresh_at': timezone.now() + timedelta(hours=24),
                'is_active': True,
                'version': 1,
            }
        )
        template.version += 1
        template.save()
        
        return {'created': 1, 'updated': 0, 'errors': []}
        
    except Exception as e:
        logger.error(f"Failed to generate bond market analysis: {e}")
        return {'created': 0, 'updated': 0, 'errors': [str(e)]}


@shared_task(bind=True, max_retries=2)
def generate_crypto_market_analysis(self):
    """Generate crypto market analysis template."""
    from ai_advisor.models import AITemplate
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    try:
        data = fetch_crypto_market_data()
        context = build_crypto_context(data)
        generator = get_content_generator()
        prompt_data = generator.generate(ContentType.MARKET_SUMMARY, context)
        
        content = call_llm(prompt_data['prompt'], prompt_data['max_tokens'], prompt_data['temperature'])
        
        template, _ = AITemplate.objects.update_or_create(
            template_type='crypto_market',
            symbol=None,
            defaults={
                'title': 'Crypto Market Analysis',
                'content': content,
                'summary': content[:200] + "...",
                'asset_class': 'crypto',
                'metadata': data,
                'last_generated_at': timezone.now(),
                'next_refresh_at': timezone.now() + timedelta(hours=6),
                'is_active': True,
                'version': 1,
            }
        )
        template.version += 1
        template.save()
        
        return {'created': 1, 'updated': 0, 'errors': []}
        
    except Exception as e:
        logger.error(f"Failed to generate crypto market analysis: {e}")
        return {'created': 0, 'updated': 0, 'errors': [str(e)]}


@shared_task
def cleanup_expired_templates():
    """Mark or delete expired templates."""
    from ai_advisor.models import AITemplate
    
    expired = AITemplate.objects.filter(
        next_refresh_at__lt=timezone.now() - timedelta(hours=12)
    )
    
    count = expired.update(is_active=False)
    logger.info(f"Marked {count} templates as inactive")
    
    return {'marked_inactive': count}


@shared_task
def cleanup_old_logs():
    """Clean up old AI logs."""
    from ai_advisor.models import AITemplateLog, AIQueryLog
    
    cutoff = timezone.now() - timedelta(days=30)
    
    log_count = AITemplateLog.objects.filter(created_at__lt=cutoff).delete()
    query_count = AIQueryLog.objects.filter(created_at__lt=cutoff).delete()
    
    logger.info(f"Cleaned up {log_count[0]} template logs and {query_count[0]} query logs")
    
    return {'template_logs_deleted': log_count[0], 'query_logs_deleted': query_count[0]}


# Helper functions (implement based on your data sources)

def fetch_market_data(symbol: str) -> Dict[str, Any]:
    """Fetch market data for symbol."""
    # Implement using DataOrchestrator or cache
    return {
        'symbol': symbol,
        'price': 450.0 + hash(symbol) % 100,
        'change_pct': (hash(symbol) % 200 - 100) / 10,
        'volume': 1000000000,
        'high_52w': 500,
        'low_52w': 350,
    }


def fetch_asset_data(symbol: str, asset_class: str) -> Dict[str, Any]:
    """Fetch asset data."""
    return {
        'symbol': symbol,
        'price': 150.0 + hash(symbol) % 50,
        'change_pct': (hash(symbol) % 200 - 100) / 10,
        'pe_ratio': 20 + hash(symbol) % 15,
        'market_cap': 1000000000000,
        'dividend_yield': 1.5,
        'eps': 5.0,
        'rsi': 50 + hash(symbol) % 30 - 15,
        'iv_rank': 40 + hash(symbol) % 40,
        'sentiment': 0.5 + (hash(symbol) % 100 - 50) / 100,
    }


def fetch_sector_data(sector: str) -> Dict[str, Any]:
    """Fetch sector data."""
    return {
        'sector': sector,
        'change_pct': (hash(sector) % 200 - 100) / 10,
        'top_performers': ['AAPL', 'MSFT', 'GOOGL'],
        'underperformers': ['XOM', 'CVX'],
        'volatility': 15 + hash(sector) % 10,
        'sentiment': 0.5 + (hash(sector) % 100 - 50) / 100,
    }


def fetch_risk_data() -> Dict[str, Any]:
    """Fetch risk metrics."""
    return {
        'var_95': 12500,
        'beta': 1.15,
        'max_drawdown': -8.5,
        'correlation_sp500': 0.85,
        'volatility_annual': 18.5,
        'sentiment_label': 'Cautious',
        'sentiment_score': 0.45,
    }


def fetch_sentiment_data(symbol: str, asset_class: Optional[str]) -> Dict[str, Any]:
    """Fetch sentiment data."""
    return {
        'symbol': symbol,
        'sentiment_score': 0.5 + (hash(symbol) % 100 - 50) / 100,
        'sentiment_label': 'Neutral',
        'news_count': 50 + hash(symbol) % 100,
        'social_mentions': 10000 + hash(symbol) % 50000,
        'positive_pct': 45,
        'neutral_pct': 35,
        'negative_pct': 20,
    }


def fetch_volatility_data(symbol: str) -> Dict[str, Any]:
    """Fetch volatility data."""
    return {
        'symbol': symbol,
        'volatility_daily': 1.2,
        'volatility_annual': 19.0,
        'iv_rank': 55,
        'iv_percentile': 60,
        'hv_10': 18.0,
        'hv_30': 19.0,
        'hv_60': 18.5,
    }


def fetch_options_data(symbol: str) -> Dict[str, Any]:
    """Fetch options data."""
    return {
        'symbol': symbol,
        'current_price': 150 + hash(symbol) % 50,
        'iv_rank': 40 + hash(symbol) % 40,
        'put_call_ratio': 0.8 + (hash(symbol) % 40) / 100,
        'rsi': 50 + hash(symbol) % 30 - 15,
    }


def fetch_bond_data() -> Dict[str, Any]:
    """Fetch bond market data."""
    return {
        'yield_2y': 4.5,
        'yield_10y': 4.25,
        'yield_30y': 4.5,
        'spread_2s10s': -25,
        'duration': 6.5,
        'convexity': 0.8,
        'oas': 1.2,
        'ig_spread': 1.0,
        'hy_spread': 3.5,
    }


def fetch_crypto_market_data() -> Dict[str, Any]:
    """Fetch crypto market data."""
    return {
        'symbol': 'CRYPTO',
        'price': 45000,
        'change_pct': 2.5,
        'volatility_annual': 55.0,
        'sentiment': 0.65,
        'news_count': 150,
    }


def build_market_context(data: Dict, symbol: str):
    """Build market context for content generation."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol=symbol,
        current_price=data.get('price'),
        price_change_pct=data.get('change_pct'),
        high_52w=data.get('high_52w'),
        low_52w=data.get('low_52w'),
        volatility_daily=data.get('volatility_daily', 1.0),
        volatility_annual=data.get('volatility_annual', 16.0),
    )


def build_asset_context(data: Dict, symbol: str, asset_class: str):
    """Build asset context for content generation."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol=symbol,
        asset_class=asset_class,
        current_price=data.get('price'),
        price_change_pct=data.get('change_pct'),
        high_52w=data.get('high_52w', data.get('price') * 1.2),
        low_52w=data.get('low_52w', data.get('price') * 0.8),
        pe_ratio=data.get('pe_ratio'),
        market_cap=data.get('market_cap'),
        dividend_yield=data.get('dividend_yield'),
        eps=data.get('eps'),
        rsi=data.get('rsi'),
        iv_rank=data.get('iv_rank'),
        sentiment_score=data.get('sentiment'),
        sentiment_label='Bullish' if data.get('sentiment', 0.5) > 0.6 else 'Bearish' if data.get('sentiment', 0.5) < 0.4 else 'Neutral',
    )


def build_sector_context(data: Dict, sector: str):
    """Build sector context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        sector=sector,
        price_change_pct=data.get('change_pct'),
        volatility_annual=data.get('volatility'),
        sentiment_score=data.get('sentiment'),
        sentiment_label='Bullish' if data.get('sentiment', 0.5) > 0.6 else 'Bearish' if data.get('sentiment', 0.5) < 0.4 else 'Neutral',
    )


def build_risk_context(data: Dict):
    """Build risk context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        var_95=data.get('var_95'),
        beta=data.get('beta'),
        max_drawdown=data.get('max_drawdown'),
        correlation_sp500=data.get('correlation_sp500'),
        volatility_annual=data.get('volatility_annual'),
        price_change_pct=data.get('change_pct', 0),
        sentiment_score=data.get('sentiment_score', 0.5),
        sentiment_label=data.get('sentiment_label', 'Neutral'),
    )


def build_sentiment_context(data: Dict, symbol: str):
    """Build sentiment context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol=symbol,
        sentiment_score=data.get('sentiment_score', 0.5),
        sentiment_label=data.get('sentiment_label', 'Neutral'),
        news_count=data.get('news_count', 0),
    )


def build_volatility_context(data: Dict, symbol: str):
    """Build volatility context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol=symbol,
        volatility_daily=data.get('volatility_daily', 1.0),
        volatility_annual=data.get('volatility_annual', 16.0),
        iv_rank=data.get('iv_rank', 50),
        iv_percentile=data.get('iv_percentile', 50),
    )


def build_options_context(data: Dict, symbol: str):
    """Build options context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol=symbol,
        current_price=data.get('current_price'),
        iv_rank=data.get('iv_rank', 50),
        put_call_ratio=data.get('put_call_ratio', 1.0),
        rsi=data.get('rsi', 50),
    )


def build_bond_context(data: Dict):
    """Build bond context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        asset_class='fixed_income',
        current_price=data.get('yield_10y', 4.0) * 10,  # Approximate
        volatility_annual=data.get('duration', 6) * 2,  # Approximate
    )


def build_crypto_context(data: Dict):
    """Build crypto context."""
    from utils.services.ai_content_generator import ContentContext
    return ContentContext(
        symbol='CRYPTO',
        asset_class='crypto',
        current_price=data.get('price'),
        price_change_pct=data.get('change_pct'),
        volatility_annual=data.get('volatility_annual', 50),
        sentiment_score=data.get('sentiment', 0.5),
        sentiment_label='Bullish' if data.get('sentiment', 0.5) > 0.6 else 'Bearish' if data.get('sentiment', 0.5) < 0.4 else 'Neutral',
        news_count=data.get('news_count', 0),
    )


def call_llm(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """Call LLM through proxy."""
    # Implement using the existing LLM proxy from ai_advisor.py
    from utils.services.llm_advisor.ai_advisor import get_ai_advisor
    
    advisor = get_ai_advisor()
    
    messages = [
        {"role": "system", "content": "You are a financial analyst. Generate clear, professional content."},
        {"role": "user", "content": prompt}
    ]
    
    result = advisor._call_llm(messages, max_tokens=max_tokens, temperature=temperature)
    return result.text
