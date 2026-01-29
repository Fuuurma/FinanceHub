"""
FilterSchema examples for FinanceHub.

IMPORTANT: REFERENCE only - do not modify existing code.
"""

from ninja import FilterSchema
from pydantic import Field
from typing import Optional
from datetime import datetime


class PortfolioFilter(FilterSchema):
    """Filter for portfolio listings."""
    status: Optional[str] = None
    search: Optional[str] = Field(None, q="name__icontains,description__icontains")
    order_by: Optional[str] = Field(None, order_by="created_at,-created_at,name,-name")


class TransactionFilter(FilterSchema):
    """Filter for transaction listings."""
    portfolio_id: Optional[int] = None
    transaction_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    order_by: Optional[str] = Field(default="-date", order_by="date,-date")


class ChartFilter(FilterSchema):
    """Filter for chart data."""
    portfolio_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    interval: Optional[str] = None  # daily, weekly, monthly
    order_by: Optional[str] = Field(default="-date", order_by="date,-date")


# Usage:
# from .filters import PortfolioFilter
# from core import CustomPageNumberPagination
#
# @router.get("/portfolios")
# def list_portfolios(request, filters: PortfolioFilter = Query(...)):
#     queryset = Portfolio.objects.all()
#     return pagination.paginate_queryset(queryset, request, params=filters.dict(exclude_unset=True))
