"""
Celery Tasks for User AI Reports
Background tasks for generating user-specific reports.
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_portfolio_report(
    self, user_id: str, portfolio_id: str, report_type: str = "portfolio_report"
):
    """
    Generate AI report for a specific portfolio.

    Called when user requests portfolio report or when nightly job runs.
    """
    from ai_advisor.models import UserAIReport, REPORT_TYPES
    from ai_advisor.services.template_generator import get_template_generator
    from django.contrib.auth import get_user_model
    from portfolios.models import Portfolio

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        portfolio = Portfolio.objects.get(id=portfolio_id)
    except (User.DoesNotExist, Portfolio.DoesNotExist) as e:
        logger.error(f"Failed to find user or portfolio: {e}")
        return {"status": "error", "message": "User or portfolio not found"}

    generator = get_template_generator()
    llm = generator.llm

    # Build portfolio data
    holdings = portfolio.holdings.filter(is_deleted=False).select_related("asset")
    holdings_data = []

    for holding in holdings:
        holdings_data.append(
            {
                "symbol": holding.asset.ticker,
                "name": holding.asset.name,
                "shares": holding.shares,
                "avg_cost": float(holding.avg_cost),
                "current_price": float(holding.asset.last_price)
                if holding.asset.last_price
                else 0,
                "market_value": float(holding.market_value)
                if hasattr(holding, "market_value")
                else 0,
                "weight": 0,  # Calculate below
            }
        )

    # Calculate weights
    total_value = sum(h["market_value"] for h in holdings_data) or 1
    for h in holdings_data:
        h["weight"] = round((h["market_value"] / total_value) * 100, 2)

    # Generate content based on report type
    report_config = {
        "portfolio_report": {
            "prompt": f"""Generate a comprehensive portfolio report for {user.email}.

Portfolio: {portfolio.name}
Holdings: {holdings_data}

Provide:
1. Portfolio overview and current value
2. Top holdings analysis
3. Sector allocation breakdown
4. Performance summary (if data available)
5. Risk assessment
6. Recommendations for improvement

Be concise but thorough. Use markdown formatting.
""",
            "title": f"Portfolio Report - {portfolio.name}",
        },
        "holdings_analysis": {
            "prompt": f"""Analyze each holding in this portfolio:

{holdings_data}

For each holding provide:
1. Brief assessment
2. Current position outlook
3. Any concerns
4. Suggested action (HOLD, REDUCE, INCREASE)

Format as a table or list.
""",
            "title": f"Holdings Analysis - {portfolio.name}",
        },
        "performance_attribution": {
            "prompt": f"""Analyze portfolio performance attribution:

{holdings_data}

Based on the holdings and their performance:
1. Identify top contributors
2. Identify laggards
3. Sector attribution
4. Recommendations for rebalancing

Be analytical and data-driven.
""",
            "title": f"Performance Attribution - {portfolio.name}",
        },
        "risk_assessment": {
            "prompt": f"""Provide portfolio risk assessment:

{holdings_data}

Analyze:
1. Overall risk level
2. Concentration risk (single positions > 10%)
3. Sector concentration
4. Volatility exposure
5. Drawdown potential
6. Risk-adjusted return assessment

Use clear risk metrics.
""",
            "title": f"Risk Assessment - {portfolio.name}",
        },
        "rebalancing_suggestion": {
            "prompt": f"""Suggest portfolio rebalancing:

{holdings_data}

Current weights: {[h["weight"] for h in holdings_data]}

Provide:
1. Current allocation vs target (if known)
2. Overweight positions to reduce
3. Underweight positions to increase
4. Tax-efficient rebalancing suggestions
5. Implementation priority

Be specific with numbers.
""",
            "title": f"Rebalancing Suggestions - {portfolio.name}",
        },
        "tax_efficiency": {
            "prompt": f"""Analyze tax efficiency of this portfolio:

{holdings_data}

Look at:
1. Unrealized gains/losses
2. Tax-loss harvesting opportunities
3. Dividend exposure
4. Long-term vs short-term holdings
5. Recommendations for tax optimization

Be specific about amounts and actions.
""",
            "title": f"Tax Efficiency Analysis - {portfolio.name}",
        },
    }

    config = report_config.get(report_type, report_config["portfolio_report"])

    start_time = timezone.now()

    try:
        # Generate content
        result = await llm._call_llm(
            [
                {
                    "role": "system",
                    "content": "You are a senior financial advisor providing personalized portfolio analysis.",
                },
                {"role": "user", "content": config["prompt"]},
            ],
            max_tokens=2500,
            temperature=0.7,
        )

        # Parse response
        content = result.text
        summary = _extract_summary(content)

        # Calculate metadata
        metadata = {
            "holdings_count": len(holdings_data),
            "total_value": total_value,
            "report_type": report_type,
            "model_used": result.model_used,
            "tokens_used": result.tokens_used,
        }

        # Calculate expiration (24 hours for most reports)
        expires_at = start_time + timedelta(hours=24)

        # Create or update report
        report, created = UserAIReport.objects.update_or_create(
            user=user,
            report_type=report_type,
            portfolio=portfolio,
            defaults={
                "title": config["title"],
                "content": content,
                "summary": summary,
                "metadata": metadata,
                "version": 1,
                "generated_at": start_time,
                "expires_at": expires_at,
                "is_stale": False,
                "generation_error": None,
            },
        )

        if not created:
            report.version += 1
            report.save()

        logger.info(f"Generated {report_type} for portfolio {portfolio_id}")
        return {
            "status": "success",
            "report_id": str(report.id),
            "report_type": report_type,
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Report generation failed: {e}")

        # Create failed report record
        UserAIReport.objects.create(
            user=user,
            report_type=report_type,
            portfolio=portfolio,
            title=config["title"],
            content=f"Failed to generate: {str(e)}",
            summary="Generation failed",
            metadata={},
            generated_at=start_time,
            expires_at=start_time,
            is_stale=True,
            generation_error=str(e),
        )

        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_all_user_reports(self):
    """
    Generate nightly reports for all premium users.

    Runs daily at 2 AM. Generates portfolio reports for all premium users.
    """
    from django.contrib.auth import get_user_model
    from portfolios.models import Portfolio
    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    User = get_user_model()
    advisor = get_ai_advisor()

    # Get all premium users
    premium_users = []
    for user in User.objects.filter(is_active=True):
        access = advisor.check_feature_access(user)
        if access.get("is_paid", False):
            premium_users.append(user)

    generated = 0
    failed = 0

    for user in premium_users:
        # Get user's portfolios
        portfolios = Portfolio.objects.filter(user=user, is_deleted=False)

        for portfolio in portfolios:
            try:
                # Generate basic portfolio report
                generate_portfolio_report.delay(
                    user_id=str(user.id),
                    portfolio_id=str(portfolio.id),
                    report_type="portfolio_report",
                )
                generated += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                failed += 1
                logger.error(
                    f"Failed to queue report for portfolio {portfolio.id}: {e}"
                )

    return {
        "status": "completed",
        "users_processed": len(premium_users),
        "reports_queued": generated,
        "failed": failed,
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_watchlist_report(self, user_id: str, watchlist_id: str):
    """
    Generate AI report for a watchlist.

    Called when user requests watchlist analysis.
    """
    from ai_advisor.models import UserAIReport
    from ai_advisor.services.template_generator import get_template_generator
    from django.contrib.auth import get_user_model
    from investments.models import Watchlist

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        watchlist = Watchlist.objects.get(id=watchlist_id)
    except (User.DoesNotExist, Watchlist.DoesNotExist) as e:
        logger.error(f"Failed to find user or watchlist: {e}")
        return {"status": "error", "message": "User or watchlist not found"}

    generator = get_template_generator()
    llm = generator.llm

    # Get watchlist assets
    assets = watchlist.assets.all()[:20]  # Limit to 20
    assets_data = []

    for asset in assets:
        assets_data.append(
            {
                "symbol": asset.ticker,
                "name": asset.name,
                "price": float(asset.last_price) if asset.last_price else 0,
                "change_24h": asset.price_change_24h or 0,
            }
        )

    start_time = timezone.now()

    try:
        result = await llm._call_llm(
            [
                {
                    "role": "system",
                    "content": "You are a financial analyst providing watchlist analysis.",
                },
                {
                    "role": "user",
                    "content": f"""Analyze this watchlist:

Watchlist: {watchlist.name}
Assets: {assets_data}

Provide:
1. Overall market sentiment based on watchlist
2. Notable movers (positive and negative)
3. Technical outlook summary
4. Opportunities and risks
5. Suggested additions/removals

Be concise and actionable.
""",
                },
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        content = result.text
        summary = _extract_summary(content)

        # Create report
        report = UserAIReport.objects.create(
            user=user,
            report_type="watchlist_analysis",
            watchlist=watchlist,
            title=f"Watchlist Analysis - {watchlist.name}",
            content=content,
            summary=summary,
            metadata={"assets_count": len(assets_data)},
            generated_at=start_time,
            expires_at=start_time + timedelta(hours=24),
        )

        logger.info(f"Generated watchlist report for {watchlist_id}")
        return {"status": "success", "report_id": str(report.id)}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Watchlist report generation failed: {e}")
        raise self.retry(exc=e)


def _extract_summary(content: str) -> str:
    """Extract summary from generated content."""
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:200]
    return content[:200]


async def _async_call_wrapper():
    """Wrapper to make async calls in sync context."""
    import asyncio

    # This is a workaround for Celery's sync context
    # In production, use proper async Celery setup
    pass
