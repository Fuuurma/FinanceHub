"""
AI Advisor API Package
Template and report endpoints.
"""

from ai_advisor.api.templates import router as templates_router
from ai_advisor.api.reports import router as reports_router

__all__ = ["templates_router", "reports_router"]
