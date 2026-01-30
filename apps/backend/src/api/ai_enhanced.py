"""
Enhanced AI Advisor API
Pre-generated templates + on-demand analysis for premium users.
"""
from typing import Optional, List
from ninja import Router, Query, Field
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime
from django.utils import timezone

from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import (
    ValidationException,
    BusinessLogicException,
    ServiceException,
)
from utils.services.llm_advisor.ai_advisor import get_ai_advisor, AIAdvisorError
from utils.services.ai_content_generator import get_content_generator, ContentType

router = Router(tags=["AI Advisor (Enhanced)"])

# ============================================================================
# Request/Response Models
# ============================================================================

class MarketAnalysisRequest(BaseModel):
    """Request for market/asset analysis."""
    symbol: str = PydanticField(..., description="Asset symbol")
    include_forecast: bool = PydanticField(default=True, description="Include forecast data")
    include_sentiment: bool = PydanticField(default=True, description="Include sentiment")
    include_options: bool = PydanticField(default=False, description="Include options strategies")


class MarketAnalysisResponse(BaseModel):
    """Response with market analysis."""
    symbol: str
    title: str
    content: str
    summary: str
    last_updated: datetime
    version: int
    next_refresh: datetime
    is_premium_content: bool = False


class PortfolioReportRequest(BaseModel):
    """Request for portfolio report."""
    portfolio_id: str
    report_type: str = PydanticField(default="portfolio_report", description="Type of report")
    include_recommendations: bool = PydanticField(default=True)


class PortfolioReportResponse(BaseModel):
    """Response with portfolio report."""
    portfolio_id: str
    title: str
    content: str
    summary: str
    metadata: dict
    generated_at: datetime
    expires_at: datetime
    version: int
    status: str  # "fresh" | "generating" | "stale"


class TemplateListResponse(BaseModel):
    """Response with list of available templates."""
    template_type: str
    count: int
    templates: List[dict]


class OnDemandAnalysisRequest(BaseModel):
    """Request for on-demand AI analysis."""
    query: str = PydanticField(..., description="Natural language query")
    context_type: Optional[str] = PydanticField(default=None, description="portfolio, market, asset")
    context_id: Optional[str] = PydanticField(default=None, description="Portfolio or symbol ID")


class OnDemandAnalysisResponse(BaseModel):
    """Response for on-demand analysis."""
    query: str
    response: str
    model_used: str
    tokens_used: int
    compute_time_ms: float


class AIStatusResponse(BaseModel):
    """Response with AI feature status."""
    has_access: bool
    is_premium: bool
    template_access: bool
    on_demand_access: bool
    portfolio_reports: bool
    daily_requests_remaining: int
    next_template_refresh: Optional[datetime]


# ============================================================================
# Helper Functions
# ============================================================================

def check_ai_access(request, require_premium: bool = True) -> dict:
    """Check user AI access and return status."""
    if not request.user.is_authenticated:
        raise BusinessLogicException(
            "AI features require authentication",
            {"feature": "AI Advisor"}
        )
    
    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)
    
    if require_premium and not access["has_access"]:
        raise BusinessLogicException(
            "AI Advisor requires a premium subscription",
            {
                "feature": "AI Advisor",
                "account_type": access["account_type"],
                "upgrade_url": "/pricing"
            }
        )
    
    return access


def get_template_with_real_time(symbol: str, template_type: str) -> dict:
    """Get template and add real-time data if needed."""
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type=template_type,
        symbol=symbol.upper(),
        is_active=True
    ).order_by("-last_generated_at").first()
    
    if not template:
        raise ValidationException(
            f"No analysis available for {symbol}",
            {"symbol": symbol, "template_type": template_type}
        )
    
    # Check if real-time update is needed
    real_time_update = None
    if template.is_stale:
        # Fetch current data
        current_data = fetch_current_price(symbol)
        template_data = template.metadata or {}
        
        # Compare and generate delta if significant
        price_change = abs(current_data.get('change_pct', 0) - template_data.get('change_pct', 0))
        if price_change > 2.0:  # More than 2% difference
            real_time_update = generate_delta_update(template, current_data)
    
    return {
        "template": template,
        "real_time_update": real_time_update,
    }


def fetch_current_price(symbol: str) -> dict:
    """Fetch current price data."""
    # Implement using cache/data orchestrator
    return {
        'symbol': symbol,
        'price': 150.0,
        'change_pct': 1.5,
    }


def generate_delta_update(template, current_data: dict) -> str:
    """Generate brief update based on real-time data."""
    change = current_data.get('change_pct', 0)
    price = current_data.get('price', 0)
    
    if change > 0:
        return f"**Update:** Price now ${price:.2f} (+{change:.2f}%) since analysis."
    else:
        return f"**Update:** Price now ${price:.2f} ({change:.2f}%) since analysis."


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/market/{symbol}", response=MarketAnalysisResponse)
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_market")
def get_market_analysis(request, symbol: str, include_forecast: bool = True):
    """
    Get AI market analysis for a symbol.
    
    Returns pre-generated template with optional real-time updates.
    Template refreshed twice daily.
    """
    check_ai_access(request, require_premium=False)  # Templates accessible to all
    
    # Get template
    result = get_template_with_real_time(symbol, 'asset_analysis')
    template = result['template']
    real_time_update = result['real_time_update']
    
    # Combine template content with real-time update
    content = template.content
    if real_time_update:
        content = f"{content}\n\n{real_time_update}"
    
    return MarketAnalysisResponse(
        symbol=symbol.upper(),
        title=template.title,
        content=content,
        summary=template.summary,
        last_updated=template.last_generated_at,
        version=template.version,
        next_refresh=template.next_refresh_at,
        is_premium_content=False,
    )


@router.get("/market/{symbol}/full", response=MarketAnalysisResponse)
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_market_full")
def get_full_market_analysis(request, symbol: str):
    """
    Get comprehensive market analysis for a symbol.
    
    Includes analysis, sentiment, volatility outlook, and options strategies.
    Premium feature - requires subscription.
    """
    access = check_ai_access(request, require_premium=True)
    
    from ai_advisor.models import AITemplate
    
    # Get all related templates
    templates = AITemplate.objects.filter(
        symbol=symbol.upper(),
        is_active=True,
        template_type__in=['asset_analysis', 'sentiment_summary', 'volatility_outlook', 'options_strategy']
    ).order_by('template_type')
    
    if not templates:
        raise ValidationException(f"No analysis available for {symbol}")
    
    # Combine all content
    combined_content = []
    combined_summary = []
    
    for template in templates:
        section_title = template.get_template_type_display()
        combined_content.append(f"## {section_title}\n\n{template.content}")
        combined_summary.append(f"[{section_title}]: {template.summary[:100]}...")
    
    full_content = "\n\n".join(combined_content)
    full_summary = " | ".join(combined_summary)
    
    latest_template = templates.first()
    
    return MarketAnalysisResponse(
        symbol=symbol.upper(),
        title=f"Comprehensive Analysis - {symbol.upper()}",
        content=full_content,
        summary=full_summary[:500],
        last_updated=latest_template.last_generated_at,
        version=latest_template.version,
        next_refresh=latest_template.next_refresh_at,
        is_premium_content=True,
    )


@router.get("/portfolio/{portfolio_id}/report", response=PortfolioReportResponse)
@api_endpoint(ttl=86400, rate=RATE_LIMITS['premium'], key_prefix="ai_portfolio")
def get_portfolio_report(request, portfolio_id: str, report_type: str = "portfolio_report"):
    """
    Get user's portfolio AI report.
    
    Returns pre-generated nightly report for premium users.
    Free users get a summary template.
    """
    access = check_ai_access(request, require_premium=False)
    
    if not access["has_access"]:
        # Return summary template for non-premium users
        from ai_advisor.models import AITemplate
        
        template = AITemplate.objects.filter(
            template_type='market_summary',
            symbol='SPY'
        ).first()
        
        return PortfolioReportResponse(
            portfolio_id=portfolio_id,
            title="Portfolio Summary (Upgrade for Full Report)",
            content=template.content if template else "Upgrade to premium for detailed portfolio analysis.",
            summary="Premium feature",
            metadata={},
            generated_at=timezone.now(),
            expires_at=timezone.now(),
            version=0,
            status="upgrade_required"
        )
    
    # Get latest report for premium users
    from ai_advisor.models import UserAIReport
    
    report = UserAIReport.get_active_report(
        user=request.user,
        report_type=report_type,
        portfolio_id=portfolio_id
    )
    
    if not report:
        # Trigger async generation
        from tasks.ai_user_reports import generate_single_portfolio_report
        generate_single_portfolio_report.delay(
            user_id=str(request.user.id),
            portfolio_id=portfolio_id
        )
        
        return PortfolioReportResponse(
            portfolio_id=portfolio_id,
            title="Generating Report...",
            content="Your personalized portfolio report is being generated. This typically takes 30-60 seconds.",
            summary="Generating...",
            metadata={},
            generated_at=timezone.now(),
            expires_at=timezone.now(),
            version=0,
            status="generating"
        )
    
    if report.is_expired:
        # Trigger refresh
        from tasks.ai_user_reports import generate_single_portfolio_report
        generate_single_portfolio_report.delay(
            user_id=str(request.user.id),
            portfolio_id=portfolio_id
        )
        
        return PortfolioReportResponse(
            portfolio_id=portfolio_id,
            title="Report Expired - Regenerating",
            content="Your report has expired and is being refreshed.",
            summary="Regenerating...",
            metadata=report.metadata or {},
            generated_at=report.generated_at,
            expires_at=report.expires_at,
            version=report.version,
            status="generating"
        )
    
    return PortfolioReportResponse(
        portfolio_id=portfolio_id,
        title=report.title,
        content=report.content,
        summary=report.summary,
        metadata=report.metadata or {},
        generated_at=report.generated_at,
        expires_at=report.expires_at,
        version=report.version,
        status="fresh"
    )


@router.get("/templates")
@api_endpoint(ttl=300, rate=RATE_LIMITS['default'], key_prefix="ai_templates")
def list_templates(
    request,
    template_type: Optional[str] = Query(None, description="Filter by type"),
    asset_class: Optional[str] = Query(None, description="Filter by asset class")
):
    """List available AI templates."""
    from ai_advisor.models import AITemplate
    
    check_ai_access(request, require_premium=False)
    
    queryset = AITemplate.objects.filter(is_active=True)
    
    if template_type:
        queryset = queryset.filter(template_type=template_type)
    
    if asset_class:
        queryset = queryset.filter(asset_class=asset_class)
    
    # Group by type
    templates_by_type = {}
    for template in queryset.order_by('template_type', '-last_generated_at'):
        ttype = template.template_type
        if ttype not in templates_by_type:
            templates_by_type[ttype] = []
        
        templates_by_type[ttype].append({
            'symbol': template.symbol,
            'sector': template.sector,
            'title': template.title,
            'last_updated': template.last_generated_at.isoformat(),
            'next_refresh': template.next_refresh_at.isoformat(),
        })
    
    return {
        'types': list(templates_by_type.keys()),
        'templates': templates_by_type,
        'total_count': queryset.count(),
    }


@router.get("/templates/summary")
@api_endpoint(ttl=300, rate=RATE_LIMITS['default'], key_prefix="ai_templates_summary")
def get_market_summary(request):
    """Get latest market summary template."""
    check_ai_access(request, require_premium=False)
    
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type='market_summary',
        symbol='SPY',
        is_active=True
    ).first()
    
    if not template:
        raise ValidationException("Market summary not available")
    
    return {
        'title': template.title,
        'summary': template.summary,
        'last_updated': template.last_generated_at.isoformat(),
        'content': template.content,
    }


@router.get("/status")
def get_ai_status(request):
    """Get AI feature access status for current user."""
    if not request.user.is_authenticated:
        return AIStatusResponse(
            has_access=False,
            is_premium=False,
            template_access=True,
            on_demand_access=False,
            portfolio_reports=False,
            daily_requests_remaining=0,
            next_template_refresh=None
        )
    
    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)
    
    # Get next template refresh time
    from ai_advisor.models import AITemplate
    next_refresh = AITemplate.objects.filter(
        is_active=True
    ).order_by('next_refresh_at').values_list('next_refresh_at', flat=True).first()
    
    return AIStatusResponse(
        has_access=access["has_access"],
        is_premium=access["is_paid"],
        template_access=True,
        on_demand_access=access["has_access"],
        portfolio_reports=access["has_access"],
        daily_requests_remaining=access["max_requests"] - advisor.get_usage_stats(str(request.user.id)).requests_today,
        next_refresh=next_refresh,
    )


@router.post("/analyze", response=OnDemandAnalysisResponse)
@api_endpoint(ttl=0, rate=RATE_LIMITS['premium'], key_prefix="ai_analyze")
def analyze_query(request, data: OnDemandAnalysisRequest):
    """
    On-demand AI analysis for user queries.
    
    Premium users only. Generates real-time responses.
    """
    access = check_ai_access(request, require_premium=True)
    
    try:
        advisor = get_ai_advisor()
        
        # Build context based on query type
        system_prompt = """You are a senior financial advisor. 
Answer user questions clearly and professionally. Use data when available.
Provide actionable insights while being transparent about uncertainty."""
        
        user_prompt = data.query
        
        # Add context if provided
        if data.context_type == 'portfolio' and data.context_id:
            user_prompt = f"Context: Portfolio ID {data.context_id}\n\nQuestion: {data.query}"
        elif data.context_type == 'market' and data.context_id:
            user_prompt = f"Context: Analyzing {data.context_id}\n\nQuestion: {data.query}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = advisor._call_llm(messages, max_tokens=1500, temperature=0.7)
        
        # Log query (simplified - full implementation would use AIQueryLog)
        
        return OnDemandAnalysisResponse(
            query=data.query,
            response=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            compute_time_ms=result.compute_time_ms
        )
        
    except AIAdvisorError as e:
        raise ServiceException(f"AI analysis failed: {str(e)}")


@router.post("/portfolio/{portfolio_id}/regenerate")
@api_endpoint(ttl=0, rate=RATE_LIMITS['premium'], key_prefix="ai_regenerate")
def regenerate_portfolio_report(request, portfolio_id: str):
    """
    Manually trigger portfolio report regeneration.
    Premium users only.
    """
    access = check_ai_access(request, require_premium=True)
    
    from tasks.ai_user_reports import generate_single_portfolio_report
    
    # Queue regeneration
    generate_single_portfolio_report.delay(
        user_id=str(request.user.id),
        portfolio_id=portfolio_id
    )
    
    return {
        "status": "queued",
        "message": "Report regeneration has been queued",
        "estimated_time": "30-60 seconds",
    }


@router.get("/sector/{sector_name}")
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_sector")
def get_sector_analysis(request, sector_name: str):
    """Get sector analysis template."""
    check_ai_access(request, require_premium=False)
    
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type='sector_report',
        sector__iexact=sector_name,
        is_active=True
    ).first()
    
    if not template:
        raise ValidationException(f"Sector analysis not available for {sector_name}")
    
    return {
        'sector': template.sector,
        'title': template.title,
        'content': template.content,
        'summary': template.summary,
        'last_updated': template.last_generated_at.isoformat(),
    }


@router.get("/risk-commentary")
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_risk")
def get_risk_commentary(request):
    """Get market risk commentary."""
    check_ai_access(request, require_premium=False)
    
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type='risk_commentary',
        symbol__isnull=True,
        is_active=True
    ).first()
    
    if not template:
        raise ValidationException("Risk commentary not available")
    
    return {
        'title': template.title,
        'content': template.content,
        'summary': template.summary,
        'last_updated': template.last_generated_at.isoformat(),
    }


@router.get("/volatility-outlook")
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_volatility")
def get_volatility_outlook(request, symbol: str = "SPY"):
    """Get volatility outlook for a symbol."""
    check_ai_access(request, require_premium=False)
    
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type='volatility_outlook',
        symbol__iexact=symbol,
        is_active=True
    ).first()
    
    if not template:
        # Try market-level
        template = AITemplate.objects.filter(
            template_type='volatility_outlook',
            symbol='SPY',
            is_active=True
        ).first()
    
    if not template:
        raise ValidationException(f"Volatility outlook not available for {symbol}")
    
    return {
        'symbol': template.symbol or 'MARKET',
        'title': template.title,
        'content': template.content,
        'metadata': template.metadata,
        'last_updated': template.last_generated_at.isoformat(),
    }


@router.get("/bond-market")
@api_endpoint(ttl=3600, rate=RATE_LIMITS['premium'], key_prefix="ai_bond")
def get_bond_market_analysis(request):
    """Get bond market analysis."""
    check_ai_access(request, require_premium=False)
    
    from ai_advisor.models import AITemplate
    
    template = AITemplate.objects.filter(
        template_type='bond_market',
        is_active=True
    ).first()
    
    if not template:
        raise ValidationException("Bond market analysis not available")
    
    return {
        'title': template.title,
        'content': template.content,
        'metadata': template.metadata,
        'last_updated': template.last_generated_at.isoformat(),
    }
