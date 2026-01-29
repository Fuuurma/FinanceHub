"""
AI User Report Generation Celery Tasks
Nightly reports for premium users.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def generate_user_portfolio_reports(self):
    """
    Generate portfolio reports for all premium users.
    Runs nightly at 02:00 UTC.
    """
    from ai_advisor.models import UserAIReport
    from users.models import User
    
    logger.info("Starting user portfolio report generation")
    start_time = timezone.now()
    
    # Get premium users with active subscriptions
    premium_users = User.objects.filter(
        is_active=True,
        subscription_expires_at__gt=timezone.now(),
    ).exclude(
        account_type__features__ai_advisor=False
    )
    
    results = {
        'started_at': start_time.isoformat(),
        'users_processed': 0,
        'reports_generated': 0,
        'errors': [],
        'total_tokens': 0,
    }
    
    for user in premium_users:
        try:
            # Get user's primary portfolio
            from portfolios.models import Portfolio
            portfolios = Portfolio.objects.filter(
                user=user,
                is_deleted=False
            ).prefetch_related('holdings__asset')
            
            if not portfolios:
                continue
            
            # Generate report for each portfolio
            for portfolio in portfolios:
                report = generate_single_portfolio_report(user, portfolio)
                if report:
                    results['reports_generated'] += 1
                    results['total_tokens'] += report.get('tokens', 0)
            
            results['users_processed'] += 1
            
        except Exception as e:
            logger.error(f"Failed to generate reports for user {user.id}: {e}")
            results['errors'].append(f"User {user.id}: {str(e)}")
    
    results['completed_at'] = timezone.now().isoformat()
    logger.info(f"User portfolio reports completed: {results}")
    
    return results


@shared_task(bind=True, max_retries=3)
def generate_single_portfolio_report(self, user_id: str, portfolio_id: str) -> Dict[str, Any]:
    """Generate report for a specific user's portfolio."""
    from ai_advisor.models import UserAIReport
    from users.models import User
    from portfolios.models import Portfolio
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    try:
        user = User.objects.get(id=user_id)
        portfolio = Portfolio.objects.get(id=portfolio_id, user=user)
        
        # Aggregate portfolio data
        data = aggregate_portfolio_data(portfolio)
        
        # Generate content
        context = build_portfolio_context(data, portfolio)
        generator = get_content_generator()
        prompt_data = generator.generate(ContentType.PORTFOLIO_REPORT, context)
        
        # Call LLM
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor
        advisor = get_ai_advisor()
        
        messages = [
            {"role": "system", "content": "You are a senior portfolio analyst. Generate comprehensive, actionable reports."},
            {"role": "user", "content": prompt_data['prompt']}
        ]
        
        llm_result = advisor._call_llm(
            messages,
            max_tokens=prompt_data['max_tokens'],
            temperature=prompt_data['temperature']
        )
        
        content = llm_result.text
        
        # Save report
        with transaction.atomic():
            # Mark old reports as stale
            UserAIReport.objects.filter(
                user=user,
                report_type='portfolio_report',
                portfolio=portfolio,
            ).update(is_stale=True)
            
            report = UserAIReport.objects.create(
                user=user,
                report_type='portfolio_report',
                portfolio=portfolio,
                title=f"Portfolio Report - {portfolio.name}",
                content=content,
                summary=content[:300] + "...",
                metadata={
                    'total_value': data.get('total_value'),
                    'total_return': data.get('total_return'),
                    'sharpe_ratio': data.get('sharpe_ratio'),
                    'var_95': data.get('var_95'),
                    'top_holdings': data.get('top_holdings', [])[:5],
                    'sector_allocation': data.get('sector_allocation', {}),
                    'model_used': llm_result.model_used,
                    'tokens_used': llm_result.tokens_used,
                },
                generated_at=timezone.now(),
                expires_at=timezone.now() + timedelta(hours=24),
                is_stale=False,
                version=1,
            )
        
        logger.info(f"Generated portfolio report for user {user_id}, portfolio {portfolio_id}")
        
        return {
            'report_id': str(report.id),
            'tokens': llm_result.tokens_used,
            'content_length': len(content),
        }
        
    except Exception as e:
        logger.error(f"Failed to generate portfolio report: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2)
def generate_user_holdings_analysis(self, user_id: str, portfolio_id: str) -> Dict[str, Any]:
    """Generate holdings analysis for a user's portfolio."""
    from ai_advisor.models import UserAIReport
    from users.models import User
    from portfolios.models import Portfolio
    from utils.services.ai_content_generator import get_content_generator, ContentType
    
    try:
        user = User.objects.get(id=user_id)
        portfolio = Portfolio.objects.get(id=portfolio_id, user=user)
        
        data = aggregate_portfolio_data(portfolio)
        context = build_holdings_context(data)
        generator = get_content_generator()
        prompt_data = generator.generate(ContentType.HOLDINGS_ANALYSIS, context)
        
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor
        advisor = get_ai_advisor()
        
        messages = [
            {"role": "system", "content": "You are a holdings analyst. Analyze portfolio composition and suggest improvements."},
            {"role": "user", "content": prompt_data['prompt']}
        ]
        
        llm_result = advisor._call_llm(
            messages,
            max_tokens=prompt_data['max_tokens'],
            temperature=prompt_data['temperature']
        )
        
        # Save report
        report = UserAIReport.objects.create(
            user=user,
            report_type='holdings_analysis',
            portfolio=portfolio,
            title=f"Holdings Analysis - {portfolio.name}",
            content=llm_result.text,
            summary=llm_result.text[:300] + "...",
            metadata={
                'holdings_count': len(data.get('holdings', [])),
                'sectors_covered': list(data.get('sector_allocation', {}).keys()),
            },
            generated_at=timezone.now(),
            expires_at=timezone.now() + timedelta(hours=24),
            is_stale=False,
        )
        
        return {'report_id': str(report.id)}
        
    except Exception as e:
        logger.error(f"Failed to generate holdings analysis: {e}")
        return {'error': str(e)}


@shared_task(bind=True, max_retries=2)
def regenerate_stale_reports(self):
    """Regenerate reports marked as stale."""
    from ai_advisor.models import UserAIReport
    
    stale_reports = UserAIReport.objects.filter(
        is_stale=True,
        expires_at__gt=timezone.now()
    ).select_related('user', 'portfolio')[:50]  # Process in batches
    
    regenerated = 0
    errors = []
    
    for report in stale_reports:
        try:
            if report.portfolio:
                result = generate_single_portfolio_report.delay(
                    user_id=str(report.user_id),
                    portfolio_id=str(report.portfolio_id)
                )
                regenerated += 1
        except Exception as e:
            errors.append(f"Report {report.id}: {str(e)}")
    
    return {'regenerated': regenerated, 'errors': errors}


def aggregate_portfolio_data(portfolio) -> Dict[str, Any]:
    """Aggregate all data needed for portfolio report."""
    from django.db.models import Sum, Avg
    from portfolios.models import Holding
    from assets.models import Asset
    
    holdings = portfolio.holdings.filter(is_deleted=False).select_related('asset')
    
    # Basic metrics
    total_value = sum(h.current_value for h in holdings if h.current_value)
    total_invested = sum(h.purchase_price * h.quantity for h in holdings if h.purchase_price and h.quantity)
    total_return = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    # Holdings breakdown
    holdings_data = []
    sector_allocation = {}
    
    for holding in holdings:
        asset = holding.asset
        current_value = holding.current_value or 0
        weight = (current_value / total_value * 100) if total_value > 0 else 0
        
        # Calculate return for this holding
        invested = holding.purchase_price * holding.quantity if holding.purchase_price else 0
        holding_return = ((current_value - invested) / invested * 100) if invested > 0 else 0
        
        holdings_data.append({
            'symbol': asset.symbol,
            'name': asset.name,
            'current_value': float(current_value),
            'weight': round(weight, 2),
            'return': round(holding_return, 2),
            'quantity': holding.quantity,
            'sector': getattr(asset.sector, 'name', 'Other') if hasattr(asset, 'sector') else 'Other',
            'asset_type': asset.asset_type.name if hasattr(asset, 'asset_type') else 'Equity',
        })
        
        # Aggregate by sector
        sector = getattr(asset.sector, 'name', 'Other') if hasattr(asset, 'sector') else 'Other'
        sector_allocation[sector] = sector_allocation.get(sector, 0) + weight
    
    # Top/bottom performers
    sorted_holdings = sorted(holdings_data, key=lambda x: x['return'], reverse=True)
    top_holdings = sorted_holdings[:5]
    bottom_holdings = sorted_holdings[-5:]
    
    # Risk metrics (simplified - use actual calculations in production)
    var_95 = total_value * 0.02  # Simplified 2% VaR
    beta = 1.1  # Placeholder - calculate from returns
    sharpe_ratio = 1.5  # Placeholder
    max_drawdown = -8.5  # Placeholder
    
    return {
        'portfolio_name': portfolio.name,
        'total_value': float(total_value),
        'total_invested': float(total_invested),
        'total_return': round(total_return, 2),
        'holdings': holdings_data,
        'top_holdings': top_holdings,
        'bottom_holdings': bottom_holdings,
        'sector_allocation': sector_allocation,
        'var_95': round(var_95, 2),
        'beta': beta,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'holdings_count': len(holdings_data),
    }


def build_portfolio_context(data: Dict, portfolio) -> Dict:
    """Build context for portfolio report."""
    from utils.services.ai_content_generator import ContentContext
    
    # Format holdings table
    holdings_table = "| Symbol | Weight | Return | Risk |"
    holdings_table += "\n|-------|--------|--------|------|"
    for h in data.get('holdings', [])[:10]:
        risk = 'H' if h['weight'] > 15 else 'M' if h['weight'] > 5 else 'L'
        holdings_table += f"\n| {h['symbol']} | {h['weight']:.1f}% | {h['return']:+.2f}% | {risk} |"
    
    # Format sector allocation
    sector_lines = []
    for sector, weight in sorted(data.get('sector_allocation', {}).items(), key=lambda x: -x[1]):
        sector_lines.append(f"- {sector}: {weight:.1f}%")
    sector_allocation_str = "\n".join(sector_lines)
    
    # Top/bottom performers
    top_str = "\n".join([f"- {h['symbol']}: {h['return']:+.2f}%" for h in data.get('top_holdings', [])])
    bottom_str = "\n".join([f"- {h['symbol']}: {h['return']:+.2f}%" for h in data.get('bottom_holdings', [])])
    
    return {
        'portfolio_name': data.get('portfolio_name', 'Portfolio'),
        'total_value': data.get('total_value', 0),
        'total_return': data.get('total_return', 0),
        'sharpe_ratio': data.get('sharpe_ratio', 0),
        'max_drawdown': data.get('max_drawdown', 0),
        'var_95': data.get('var_95', 0),
        'beta': data.get('beta', 1.0),
        'correlation_sp500': 0.85,
        'holdings_table': holdings_table,
        'sector_allocation': sector_allocation_str,
        'top_performers': top_str,
        'bottom_performers': bottom_str,
        'performance_attribution': "Tech +2.1%, Energy -0.5%, Financials +0.8%",
        'risk_factors': f"Concentration in top 5: {sum(h['weight'] for h in data.get('holdings', [])[:5]):.1f}%",
    }


def build_holdings_context(data: Dict) -> Dict:
    """Build context for holdings analysis."""
    return {
        'holdings': data.get('holdings', []),
        'sector_allocation': data.get('sector_allocation', {}),
        'top_holdings': data.get('top_holdings', []),
        'total_value': data.get('total_value', 0),
        'total_return': data.get('total_return', 0),
    }


@shared_task
def cleanup_expired_user_reports():
    """Delete or archive expired user reports."""
    from ai_advisor.models import UserAIReport
    
    expired = UserAIReport.objects.filter(expires_at__lt=timezone.now())
    count = expired.delete()
    
    logger.info(f"Cleaned up {count[0]} expired user reports")
    
    return {'deleted': count[0]}
