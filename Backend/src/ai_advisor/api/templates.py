"""
AI Advisor API - Template Endpoints
CRUD and generation for AI templates.
"""

from typing import Optional, List
from ninja import Router, Query, Field
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime
from django.utils import timezone
from django.db.models import Q

from utils.constants.api import RATE_LIMITS, CACHE_TTL_SHORT, CACHE_TTL_LONG
from utils.api.decorators import api_endpoint
from core.exceptions import (
    ValidationException,
    BusinessLogicException,
    ServiceException,
    AuthorizationException,
)
from ai_advisor.models import AITemplate, TEMPLATE_TYPES
from ai_advisor.services.template_generator import (
    get_template_generator,
    TEMPLATE_ACCESS_TIERS,
)

router = Router(tags=["AI Templates"])

# ============================================================================
# Request/Response Models
# ============================================================================


class TemplateListRequest(BaseModel):
    """Query parameters for listing templates."""

    template_type: Optional[str] = None
    asset_class: Optional[str] = None
    symbol: Optional[str] = None
    sector: Optional[str] = None
    include_inactive: bool = Field(False, description="Include inactive templates")
    limit: int = Field(50, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class TemplateResponse(BaseModel):
    """Template response model."""

    id: str
    template_type: str
    symbol: Optional[str]
    sector: Optional[str]
    asset_class: Optional[str]
    title: str
    summary: str
    content: str
    metadata: dict
    version: int
    last_generated_at: datetime
    next_refresh_at: datetime
    is_active: bool
    is_stale: bool
    access_tier: str  # 'free' or 'premium'
    tier_badge: Optional[str] = None  # Display text for tier badge

    class Config:
        from_attributes = True


class TemplateGenerateRequest(BaseModel):
    """Request to generate a new template."""

    template_type: str = Field(..., description="Type of template to generate")
    symbol: Optional[str] = Field(None, max_length=20, description="Asset symbol")
    sector: Optional[str] = Field(None, max_length=50, description="Sector name")
    asset_class: Optional[str] = Field(None, max_length=30, description="Asset class")
    force: bool = Field(False, description="Force regeneration even if fresh")


class TemplateGenerateResponse(BaseModel):
    """Response for template generation."""

    id: str
    template_type: str
    symbol: Optional[str]
    title: str
    status: str  # 'generated' or 'queued'
    generated_at: datetime


class TemplateDetailResponse(BaseModel):
    """Detailed template response with delta update info."""

    template: TemplateResponse
    delta_update: Optional[dict] = None  # Real-time price change info
    related_templates: List[dict] = []  # Links to related templates


class TierInfoResponse(BaseModel):
    """Information about template tier access."""

    template_type: str
    free_access: bool
    premium_access: bool
    description: str


# ============================================================================
# Helper Functions
# ============================================================================


def check_tier_access(template_type: str, is_premium: bool) -> tuple[bool, str]:
    """Check if user has access to template type."""
    tier_config = TEMPLATE_ACCESS_TIERS.get(template_type, {})
    has_free = tier_config.get("free", False)
    has_premium = tier_config.get("premium", False)

    if is_premium and has_premium:
        return True, "premium"
    elif not is_premium and has_free:
        return True, "free"
    elif is_premium and has_free:
        return True, "free"  # Premium users get free tier too
    else:
        return False, "locked"


def template_to_response(
    template: AITemplate, is_premium: bool = False
) -> TemplateResponse:
    """Convert AITemplate model to response."""
    has_access, tier = check_tier_access(template.template_type, is_premium)

    if not has_access:
        tier_badge = "🔒 Premium"
    elif tier == "premium":
        tier_badge = "⭐ Premium"
    else:
        tier_badge = "Free"

    return TemplateResponse(
        id=str(template.id),
        template_type=template.template_type,
        symbol=template.symbol,
        sector=template.sector,
        asset_class=template.asset_class,
        title=template.title,
        summary=template.summary,
        content=template.content,
        metadata=template.metadata or {},
        version=template.version,
        last_generated_at=template.last_generated_at,
        next_refresh_at=template.next_refresh_at,
        is_active=template.is_active,
        is_stale=template.is_stale,
        access_tier=tier,
        tier_badge=tier_badge,
    )


def get_tier_badge(template_type: str, is_premium: bool) -> Optional[str]:
    """Get tier badge text for template type."""
    has_access, tier = check_tier_access(template_type, is_premium)

    if not has_access:
        return "🔒 Premium"
    elif tier == "premium":
        return "⭐ Premium"
    else:
        return "Free"


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/", response=TemplateListRequest)
@api_endpoint(
    ttl=CACHE_TTL_SHORT, rate=RATE_LIMITS["default"], key_prefix="ai_templates_list"
)
def list_templates(
    request,
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    asset_class: Optional[str] = Query(None, description="Filter by asset class"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    include_inactive: bool = Query(False, description="Include inactive templates"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List available AI templates.

    Public access with rate limiting. Tier-based access control applies.
    Premium users see all templates; free users see only free templates.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    queryset = AITemplate.objects.filter(is_active=True)

    if include_inactive:
        queryset = AITemplate.objects.all()

    # Apply filters
    if template_type:
        queryset = queryset.filter(template_type=template_type)
    if asset_class:
        queryset = queryset.filter(asset_class=asset_class)
    if symbol:
        queryset = queryset.filter(symbol__iexact=symbol)
    if sector:
        queryset = queryset.filter(sector__iexact=sector)

    # Filter by tier access for non-premium users
    if not is_premium:
        accessible_types = [
            t for t, cfg in TEMPLATE_ACCESS_TIERS.items() if cfg.get("free", False)
        ]
        queryset = queryset.filter(template_type__in=accessible_types)

    # Order and paginate
    templates = queryset.order_by("-last_generated_at")[offset : offset + limit]

    # Convert to response
    result = []
    for template in templates:
        has_access, tier = check_tier_access(template.template_type, is_premium)
        if has_access:
            result.append(template_to_response(template, is_premium))

    return {
        "templates": result,
        "total": queryset.count(),
        "limit": limit,
        "offset": offset,
    }


@router.get("/types", response=List[TierInfoResponse])
@api_endpoint(
    ttl=CACHE_TTL_LONG, rate=RATE_LIMITS["default"], key_prefix="ai_template_types"
)
def list_template_types(request):
    """
    List all available template types with tier information.

    Public endpoint - no authentication required.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    result = []
    for template_type, cfg in TEMPLATE_ACCESS_TIERS.items():
        display_name = dict(TEMPLATE_TYPES).get(template_type, template_type)

        result.append(
            TierInfoResponse(
                template_type=template_type,
                free_access=cfg.get("free", False),
                premium_access=cfg.get("premium", False),
                description=f"AI-generated {display_name.lower()}",
            )
        )

    return result


@router.get("/{template_id}", response=TemplateDetailResponse)
@api_endpoint(
    ttl=CACHE_TTL_SHORT, rate=RATE_LIMITS["default"], key_prefix="ai_template_detail"
)
def get_template(request, template_id: str):
    """
    Get detailed template information.

    Includes related templates and delta updates for stale templates.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    try:
        template = AITemplate.objects.get(id=template_id, is_active=True)
    except AITemplate.DoesNotExist:
        raise ValidationException(f"Template not found: {template_id}")

    has_access, tier = check_tier_access(template.template_type, is_premium)
    if not has_access:
        raise AuthorizationException(
            "This template requires a premium subscription",
            {"template_type": template.template_type, "upgrade_url": "/pricing"},
        )

    # Check for delta update (real-time change)
    delta_update = None
    if template.is_stale:
        delta_update = _check_delta_update(template)

    # Get related templates
    related = []
    if template.symbol:
        related_templates = AITemplate.objects.filter(
            symbol=template.symbol,
            template_type__in=[
                "asset_analysis",
                "sentiment_summary",
                "volatility_outlook",
            ],
            is_active=True,
        ).exclude(id=template_id)[:3]

        for rt in related_templates:
            has_access_rt, _ = check_tier_access(rt.template_type, is_premium)
            if has_access_rt:
                related.append(
                    {
                        "id": str(rt.id),
                        "type": rt.template_type,
                        "title": rt.title,
                        "summary": rt.summary[:100],
                    }
                )

    return TemplateDetailResponse(
        template=template_to_response(template, is_premium),
        delta_update=delta_update,
        related_templates=related,
    )


@router.get("/type/{template_type}", response=List[TemplateResponse])
@api_endpoint(
    ttl=CACHE_TTL_SHORT, rate=RATE_LIMITS["default"], key_prefix="ai_templates_by_type"
)
def get_templates_by_type(
    request,
    template_type: str,
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(20, ge=1, le=50),
):
    """
    Get templates of a specific type.

    Useful for browsing all templates of a category.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    # Validate template type
    valid_types = [t[0] for t in TEMPLATE_TYPES]
    if template_type not in valid_types:
        raise ValidationException(
            f"Invalid template type: {template_type}", {"valid_types": valid_types}
        )

    queryset = AITemplate.objects.filter(template_type=template_type, is_active=True)

    if symbol:
        queryset = queryset.filter(symbol__iexact=symbol)

    # Filter by tier access
    if not is_premium:
        if not TEMPLATE_ACCESS_TIERS.get(template_type, {}).get("free", False):
            raise AuthorizationException(
                "This template type requires a premium subscription",
                {"upgrade_url": "/pricing"},
            )

    templates = queryset.order_by("-last_generated_at")[:limit]

    return [template_to_response(t, is_premium) for t in templates]


@router.get("/stale")
@api_endpoint(ttl=60, rate=RATE_LIMITS["premium"], key_prefix="ai_templates_stale")
def get_stale_templates(request, limit: int = Query(20, ge=1, le=100)):
    """
    Get templates that need refresh.

    Premium feature - shows templates marked as stale.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    if not is_premium:
        raise AuthorizationException(
            "This feature requires a premium subscription", {"upgrade_url": "/pricing"}
        )

    stale_templates = AITemplate.objects.filter(
        is_active=True, next_refresh_at__lte=timezone.now()
    ).order_by("next_refresh_at")[:limit]

    return {
        "count": stale_templates.count(),
        "templates": [
            {
                "id": str(t.id),
                "template_type": t.template_type,
                "symbol": t.symbol,
                "sector": t.sector,
                "last_generated": t.last_generated_at.isoformat(),
                "next_refresh": t.next_refresh_at.isoformat(),
                "age_hours": t.age_hours,
            }
            for t in stale_templates
        ],
    }


@router.post("/generate", response=TemplateGenerateResponse)
@api_endpoint(ttl=0, rate=RATE_LIMITS["premium"], key_prefix="ai_template_generate")
def generate_template(request, data: TemplateGenerateRequest):
    """
    Manually trigger template generation.

    Premium feature with rate limiting (2 requests/hour for free, 10 for premium).
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    # Validate template type
    valid_types = [t[0] for t in TEMPLATE_TYPES]
    if data.template_type not in valid_types:
        raise ValidationException(
            f"Invalid template type: {data.template_type}", {"valid_types": valid_types}
        )

    # Check tier access
    has_access, tier = check_tier_access(data.template_type, is_premium)
    if not has_access:
        raise AuthorizationException(
            "This template type requires a premium subscription",
            {"template_type": data.template_type, "upgrade_url": "/pricing"},
        )

    # Validate required fields based on template type
    if data.template_type in ["asset_analysis", "volatility_outlook"]:
        if not data.symbol:
            raise ValidationException(
                f"Symbol required for {data.template_type}",
                {"required_field": "symbol"},
            )
    elif data.template_type == "sector_report":
        if not data.sector:
            raise ValidationException(
                f"Sector required for {data.template_type}",
                {"required_field": "sector"},
            )

    # Generate template
    try:
        generator = get_template_generator()

        generation_map = {
            "market_summary": generator.generate_market_summary,
            "asset_analysis": lambda f=False: generator.generate_asset_analysis(
                data.symbol, f
            ),
            "sector_report": lambda f=False: generator.generate_sector_report(
                data.sector, f
            ),
            "risk_commentary": generator.generate_risk_commentary,
            "sentiment_summary": generator.generate_sentiment_summary,
            "volatility_outlook": lambda f=False: generator.generate_volatility_outlook(
                data.symbol, f
            ),
            "crypto_market": generator.generate_crypto_market,
            "bond_market": generator.generate_bond_market,
        }

        gen_func = generation_map.get(data.template_type)
        if gen_func:
            template = gen_func(force=data.force)
        else:
            raise ValidationException(
                f"Template generation not implemented: {data.template_type}"
            )

        return TemplateGenerateResponse(
            id=str(template.id),
            template_type=template.template_type,
            symbol=template.symbol,
            title=template.title,
            status="generated",
            generated_at=template.last_generated_at,
        )

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Template generation failed: {e}")
        raise ServiceException(f"Failed to generate template: {str(e)}")


@router.get("/refresh-all")
@api_endpoint(ttl=0, rate=RATE_LIMITS["premium"], key_prefix="ai_templates_refresh_all")
def refresh_all_stale(request):
    """
    Trigger refresh for all stale templates.

    Admin/premium feature. Returns count of templates to refresh.
    """
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    if not is_premium:
        raise AuthorizationException(
            "This feature requires a premium subscription", {"upgrade_url": "/pricing"}
        )

    stale_count = AITemplate.objects.filter(
        is_active=True, next_refresh_at__lte=timezone.now()
    ).count()

    # Queue refresh task
    from ai_advisor.tasks.template_refresh import refresh_all_templates

    refresh_all_templates.delay()

    return {
        "status": "queued",
        "message": f"Refreshing {stale_count} stale templates",
        "estimated_time": f"{max(1, stale_count // 10)} minutes",
    }


# ============================================================================
# Helper Functions
# ============================================================================


def _check_delta_update(template: AITemplate) -> Optional[dict]:
    """
    Check if there's significant real-time change since template generation.

    Returns delta info if price moved > 2%, None otherwise.
    """
    if not template.symbol:
        return None

    try:
        from utils.services.cache_manager import get_cache_manager

        cache = get_cache_manager()

        # Get current price
        cache_key = f"asset:{template.symbol}:price"
        current_price_data = cache.get(cache_key)

        if not current_price_data:
            return None

        current_price = current_price_data.get("price")
        if not current_price:
            return None

        # Get template's stored price
        template_metadata = template.metadata or {}
        template_price = template_metadata.get("current_price")

        if not template_price:
            return None

        # Calculate change
        price_change_pct = ((current_price - template_price) / template_price) * 100

        if abs(price_change_pct) >= 2.0:
            return {
                "type": "price_change",
                "symbol": template.symbol,
                "template_price": template_price,
                "current_price": current_price,
                "change_pct": round(price_change_pct, 2),
                "direction": "up" if price_change_pct > 0 else "down",
                "message": f"Price moved {'+' if price_change_pct > 0 else ''}{price_change_pct:.2f}% since analysis",
            }

        return None

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Delta check failed: {e}")
        return None


import logging

logger = logging.getLogger(__name__)
