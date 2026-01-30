"""
Rate Limit Admin API

Admin dashboard endpoint for monitoring rate limiting and violations.
"""

from ninja import Router
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from utils.services.rate_limit_monitor import get_rate_limit_monitor

router = Router()


@router.get("/admin/rate-limits/stats")
@staff_member_required
def rate_limits_stats(request):
    """Get rate limiting statistics"""
    monitor = get_rate_limit_monitor()
    stats = monitor.get_stats()
    return JsonResponse(stats)


@router.get("/admin/rate-limits/violations")
@staff_member_required
def rate_limits_violations(request):
    """Get recent rate limit violations"""
    limit = int(request.GET.get("limit", 100))
    monitor = get_rate_limit_monitor()
    violations = monitor.get_violations(limit=limit)
    return JsonResponse({"violations": violations})


@router.get("/admin/rate-limits/check-banned/{identifier}")
@staff_member_required
def check_banned(request, identifier: str):
    """Check if an identifier is banned"""
    monitor = get_rate_limit_monitor()
    is_banned = monitor.is_banned(identifier)
    return JsonResponse({"identifier": identifier, "is_banned": is_banned})


@router.post("/admin/rate-limits/cleanup")
@staff_member_required
def cleanup_violations(request):
    """Clean up old violation records"""
    monitor = get_rate_limit_monitor()
    cleaned = monitor.cleanup_old_violations()
    return JsonResponse({"cleaned": cleaned})
