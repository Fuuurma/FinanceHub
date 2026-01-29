"""
Celery Tasks for AI Template Refresh
Background tasks for refreshing stale templates.
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_stale_templates(self):
    """
    Refresh all templates that are marked as stale.

    Runs hourly via Celery beat.
    """
    from ai_advisor.models import AITemplate
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    # Get all stale templates
    stale_templates = AITemplate.objects.filter(
        is_active=True, next_refresh_at__lte=timezone.now()
    )

    refreshed = 0
    failed = 0

    for template in stale_templates:
        try:
            # Map template type to generator method
            gen_map = {
                "market_summary": generator.generate_market_summary,
                "asset_analysis": lambda f=False: generator.generate_asset_analysis(
                    template.symbol, f
                ),
                "sector_report": lambda f=False: generator.generate_sector_report(
                    template.sector, f
                ),
                "risk_commentary": generator.generate_risk_commentary,
                "sentiment_summary": generator.generate_sentiment_summary,
                "volatility_outlook": lambda f=False: generator.generate_volatility_outlook(
                    template.symbol, f
                ),
                "crypto_market": generator.generate_crypto_market,
                "bond_market": generator.generate_bond_market,
            }

            gen_func = gen_map.get(template.template_type)
            if gen_func:
                gen_func(force=True)
                refreshed += 1
                logger.info(
                    f"Refreshed {template.template_type} for {template.symbol or template.sector}"
                )

        except Exception as e:
            failed += 1
            logger.error(f"Failed to refresh {template.template_type}: {e}")

    return {
        "refreshed": refreshed,
        "failed": failed,
        "total": stale_templates.count(),
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_market_summary_task(self):
    """
    Generate market summary template.

    Runs twice daily (6 AM, 6 PM).
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_market_summary()
        logger.info(f"Generated market summary: {template.id}")
        return {"status": "success", "template_id": str(template.id)}
    except Exception as e:
        logger.error(f"Market summary generation failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_crypto_market_task(self):
    """
    Generate crypto market analysis.

    Runs every 6 hours.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_crypto_market()
        logger.info(f"Generated crypto market analysis: {template.id}")
        return {"status": "success", "template_id": str(template.id)}
    except Exception as e:
        logger.error(f"Crypto market generation failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_asset_analysis_task(self, symbol: str):
    """
    Generate asset analysis for a specific symbol.

    Called when user requests analysis for an asset.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_asset_analysis(symbol.upper())
        logger.info(f"Generated asset analysis for {symbol}: {template.id}")
        return {"status": "success", "template_id": str(template.id), "symbol": symbol}
    except Exception as e:
        logger.error(f"Asset analysis generation failed for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_sector_report_task(self, sector: str):
    """
    Generate sector report for a specific sector.

    Called when user requests sector analysis.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_sector_report(sector)
        logger.info(f"Generated sector report for {sector}: {template.id}")
        return {"status": "success", "template_id": str(template.id), "sector": sector}
    except Exception as e:
        logger.error(f"Sector report generation failed for {sector}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_risk_commentary_task(self):
    """
    Generate market risk commentary.

    Runs twice daily.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_risk_commentary()
        logger.info(f"Generated risk commentary: {template.id}")
        return {"status": "success", "template_id": str(template.id)}
    except Exception as e:
        logger.error(f"Risk commentary generation failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_sentiment_summary_task(self):
    """
    Generate market sentiment summary.

    Runs twice daily.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_sentiment_summary()
        logger.info(f"Generated sentiment summary: {template.id}")
        return {"status": "success", "template_id": str(template.id)}
    except Exception as e:
        logger.error(f"Sentiment summary generation failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_volatility_outlook_task(self, symbol: str = "SPY"):
    """
    Generate volatility outlook for a symbol.

    Runs twice daily per symbol.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_volatility_outlook(symbol.upper())
        logger.info(f"Generated volatility outlook for {symbol}: {template.id}")
        return {"status": "success", "template_id": str(template.id), "symbol": symbol}
    except Exception as e:
        logger.error(f"Volatility outlook generation failed for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_bond_market_task(self):
    """
    Generate bond market analysis.

    Runs daily.
    """
    from ai_advisor.services.template_generator import get_template_generator

    generator = get_template_generator()

    try:
        template = generator.generate_bond_market()
        logger.info(f"Generated bond market analysis: {template.id}")
        return {"status": "success", "template_id": str(template.id)}
    except Exception as e:
        logger.error(f"Bond market generation failed: {e}")
        raise self.retry(exc=e)


@shared_task
def cleanup_old_template_logs(days: int = 30):
    """
    Clean up old template generation logs.

    Runs weekly to prevent log bloat.
    """
    from ai_advisor.models import AITemplateLog
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=days)

    deleted = AITemplateLog.objects.filter(created_at__lt=cutoff).delete()

    logger.info(f"Cleaned up {deleted[0]} old template logs")
    return {"deleted_logs": deleted[0]}
