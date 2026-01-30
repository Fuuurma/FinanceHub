"""
AI Advisor API - User Reports Endpoints
User-specific AI report generation and retrieval.
"""

from typing import Optional
from ninja import Router, Query
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime
from django.utils import timezone

from utils.constants.api import RATE_LIMITS, CACHE_TTL_SHORT, CACHE_TTL_LONG, CACHE_TTL_MEDIUM
from utils.api.decorators import api_endpoint
from core.exceptions import (
    ValidationException,
    BusinessLogicException,
    AuthorizationException,
)
from ai_advisor.models import UserAIReport, REPORT_TYPES

router = Router(tags=["AI User Reports"])

# ============================================================================
# Request/Response Models
# ============================================================================


class ReportResponse(BaseModel):
    """User report response model."""

    id: str
    report_type: str
    portfolio_id: Optional[str]
    watchlist_id: Optional[str]
    title: str
    summary: str
    content: str
    metadata: dict
    version: int
    generated_at: datetime
    expires_at: datetime
    is_stale: bool
    is_expired: bool
    status: str  # 'fresh', 'stale', 'generating', 'expired'

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response for listing user reports."""

    reports: list
    total: int
    premium_reports: int  # Reports requiring premium
    free_reports: int


class RegenerateResponse(BaseModel):
    """Response for report regeneration."""

    status: str  # 'queued', 'generating', 'ready'
    report_id: str
    estimated_time: str  # e.g., "30-60 seconds"


# ============================================================================
# Helper Functions
# ============================================================================


def check_report_access(request, report_type: str) -> tuple[bool, str]:
    """Check if user has access to report type."""
    is_premium = False
    if request.user.is_authenticated:
        from utils.services.llm_advisor.ai_advisor import get_ai_advisor

        advisor = get_ai_advisor()
        access = advisor.check_feature_access(request.user)
        is_premium = access.get("is_paid", False)

    # All reports require premium
    if is_premium:
        return True, "premium"
    else:
        return False, "locked"


def report_to_response(report: UserAIReport) -> ReportResponse:
    """Convert UserAIReport model to response."""
    is_expired = report.is_expired

    if is_expired:
        status = "expired"
    elif report.is_stale:
        status = "stale"
    else:
        status = "fresh"

    return ReportResponse(
        id=str(report.id),
        report_type=report.report_type,
        portfolio_id=str(report.portfolio.id) if report.portfolio else None,
        watchlist_id=str(report.watchlist.id) if report.watchlist else None,
        title=report.title,
        summary=report.summary,
        content=report.content,
        metadata=report.metadata or {},
        version=report.version,
        generated_at=report.generated_at,
        expires_at=report.expires_at,
        is_stale=report.is_stale,
        is_expired=is_expired,
        status=status,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/", response=ReportListResponse)
@api_endpoint(
    ttl=CACHE_TTL_SHORT, rate=RATE_LIMITS["premium"], key_prefix="ai_reports_list"
)
def list_user_reports(
    request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
):
    """
    List user's AI reports.

    Premium feature - requires authentication.
    Returns all reports for the authenticated user.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException(
            "Authentication required to view reports", {"login_url": "/login"}
        )

    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access.get("has_access", False):
        raise AuthorizationException(
            "AI Reports require a premium subscription", {"upgrade_url": "/pricing"}
        )

    queryset = UserAIReport.objects.filter(user=request.user)

    reports = []
    for report in queryset.order_by("-generated_at")[offset : offset + limit]:
        reports.append(report_to_response(report))

    # Count by tier
    premium_reports = queryset.filter(
        report_type__in=[
            "portfolio_report",
            "holdings_analysis",
            "performance_attribution",
        ]
    ).count()

    free_reports = queryset.filter(
        report_type__in=["risk_assessment", "rebalancing_suggestion", "tax_efficiency"]
    ).count()

    return {
        "reports": reports,
        "total": queryset.count(),
        "premium_reports": premium_reports,
        "free_reports": free_reports,
    }


@router.get("/{report_id}", response=ReportResponse)
@api_endpoint(
    ttl=CACHE_TTL_MEDIUM, rate=RATE_LIMITS["premium"], key_prefix="ai_report_detail"
)
def get_report(request, report_id: str):
    """
    Get a specific user report.

    Premium feature - requires ownership of the report.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException("Authentication required", {"login_url": "/login"})

    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access.get("has_access", False):
        raise AuthorizationException(
            "AI Reports require a premium subscription", {"upgrade_url": "/pricing"}
        )

    try:
        report = UserAIReport.objects.get(id=report_id, user=request.user)
    except UserAIReport.DoesNotExist:
        raise ValidationException(f"Report not found: {report_id}")

    return report_to_response(report)


@router.get("/portfolio/{portfolio_id}", response=ReportResponse)
@api_endpoint(
    ttl=CACHE_TTL_MEDIUM, rate=RATE_LIMITS["premium"], key_prefix="ai_portfolio_report"
)
def get_portfolio_report(
    request,
    portfolio_id: str,
    report_type: str = Query("portfolio_report", description="Type of report"),
):
    """
    Get AI report for a specific portfolio.

    Premium feature. Returns cached report or triggers generation.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException("Authentication required", {"login_url": "/login"})

    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access.get("has_access", False):
        raise AuthorizationException(
            "AI Reports require a premium subscription", {"upgrade_url": "/pricing"}
        )

    # Validate report type
    valid_types = [t[0] for t in REPORT_TYPES]
    if report_type not in valid_types:
        raise ValidationException(
            f"Invalid report type: {report_type}", {"valid_types": valid_types}
        )

    # Get active report
    report = UserAIReport.get_active_report(
        user=request.user, report_type=report_type, portfolio_id=portfolio_id
    )

    if not report:
        # Trigger generation
        from ai_advisor.tasks.user_reports import generate_portfolio_report

        generate_portfolio_report.delay(
            user_id=str(request.user.id),
            portfolio_id=portfolio_id,
            report_type=report_type,
        )

        # Return generating status
        return ReportResponse(
            id="pending",
            report_type=report_type,
            portfolio_id=portfolio_id,
            watchlist_id=None,
            title="Generating Report...",
            summary="Your personalized portfolio report is being generated.",
            content="This typically takes 30-60 seconds. Please check back shortly.",
            metadata={},
            version=0,
            generated_at=timezone.now(),
            expires_at=timezone.now(),
            is_stale=False,
            is_expired=False,
            status="generating",
        )

    return report_to_response(report)


@router.post("/portfolio/{portfolio_id}/regenerate", response=RegenerateResponse)
@api_endpoint(ttl=0, rate=RATE_LIMITS["premium"], key_prefix="ai_report_regenerate")
def regenerate_portfolio_report(
    request, portfolio_id: str, report_type: str = "portfolio_report"
):
    """
    Manually trigger report regeneration.

    Premium feature. Queues async regeneration task.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException("Authentication required", {"login_url": "/login"})

    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access.get("has_access", False):
        raise AuthorizationException(
            "AI Reports require a premium subscription", {"upgrade_url": "/pricing"}
        )

    # Validate report type
    valid_types = [t[0] for t in REPORT_TYPES]
    if report_type not in valid_types:
        raise ValidationException(
            f"Invalid report type: {report_type}", {"valid_types": valid_types}
        )

    # Queue regeneration
    from ai_advisor.tasks.user_reports import generate_portfolio_report

    generate_portfolio_report.delay(
        user_id=str(request.user.id), portfolio_id=portfolio_id, report_type=report_type
    )

    return RegenerateResponse(
        status="queued",
        report_id=portfolio_id,
        estimated_time="30-60 seconds",
    )


@router.get("/latest")
@api_endpoint(
    ttl=CACHE_TTL_SHORT, rate=RATE_LIMITS["premium"], key_prefix="ai_reports_latest"
)
def get_latest_reports(request, limit: int = Query(5, ge=1, le=20)):
    """
    Get user's most recent AI reports.

    Premium feature. Quick access to latest reports.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException("Authentication required", {"login_url": "/login"})

    from utils.services.llm_advisor.ai_advisor import get_ai_advisor

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access.get("has_access", False):
        raise AuthorizationException(
            "AI Reports require a premium subscription", {"upgrade_url": "/pricing"}
        )

    reports = UserAIReport.objects.filter(
        user=request.user, expires_at__gt=timezone.now()
    ).order_by("-generated_at")[:limit]

    return {
        "reports": [report_to_response(r) for r in reports],
        "count": len(reports),
    }


@router.delete("/{report_id}")
@api_endpoint(ttl=0, rate=RATE_LIMITS["premium"], key_prefix="ai_report_delete")
def delete_report(request, report_id: str):
    """
    Delete a user report.

    Premium feature. Removes report from database.
    """
    if not request.user.is_authenticated:
        raise AuthorizationException("Authentication required", {"login_url": "/login"})

    try:
        report = UserAIReport.objects.get(id=report_id, user=request.user)
        report.delete()
        return {"status": "deleted", "report_id": report_id}
    except UserAIReport.DoesNotExist:
        raise ValidationException(f"Report not found: {report_id}")


import logging

logger = logging.getLogger(__name__)
