"""
Example endpoints for FinanceHub.

IMPORTANT: REFERENCE only - do not modify existing code.
"""

from ninja import Router, Query
from typing import Optional

# Recommended imports:
# from core import (
#     create_success_response,
#     create_error_response,
#     ErrorCode,
#     NotFoundException,
#     ValidationException,
#     get_logger,
#     LogCategory,
#     CustomPageNumberPagination,
# )
# from .filters import PortfolioFilter, TransactionFilter

router = Router()
logger = get_logger("finance", category=LogCategory.API)


# =============================================================================
# EXAMPLE 1: FilterSchema with pagination
# =============================================================================

# @router.get("/portfolios")
# def list_portfolios(request, filters: PortfolioFilter = Query(...)):
#     '''
#     List portfolios with filtering and pagination.
#     '''
#     logger.info("Listing portfolios", extra={"filters": filters.dict(exclude_unset=True)})
#
#     queryset = Portfolio.objects.all()
#     filter_params = filters.dict(exclude_unset=True)
#
#     if filter_params:
#         queryset = queryset.filter(**filter_params)
#
#     pagination = CustomPageNumberPagination()
#     pagination.page_size = 20
#
#     return pagination.paginate_queryset(queryset, request)


# =============================================================================
# EXAMPLE 2: Error handling
# =============================================================================

# @router.get("/portfolios/{portfolio_id}")
# def get_portfolio(request, portfolio_id: int):
#     '''
#     Get a single portfolio.
#     '''
#     try:
#         portfolio = Portfolio.objects.get(id=portfolio_id)
#         return create_success_response(
#             data=portfolio.to_dict(),
#             message="Portfolio retrieved successfully"
#         )
#     except Portfolio.DoesNotExist:
#         raise NotFoundException("Portfolio", portfolio_id)


# =============================================================================
# EXAMPLE 3: Validation
# =============================================================================

# @router.post("/transactions")
# def create_transaction(request, data: TransactionCreateSchema):
#     '''
#     Create a new transaction.
#     '''
#     if not data.amount or data.amount <= 0:
#         raise ValidationException(
#             message="Amount must be positive",
#             field="amount"
#         )
#
#     transaction = Transaction.objects.create(**data.dict())
#
#     return create_success_response(
#         data=transaction.to_dict(),
#         message="Transaction created successfully",
#         status_code=201
#     )


# =============================================================================
# SUMMARY
# =============================================================================
#
# 1. Use FilterSchema for filtering
# 2. Return create_success_response() / create_error_response()
# 3. Raise NotFoundException, ValidationException, etc.
# 4. Add structured logging with get_logger()
# 5. Use CustomPageNumberPagination for lists
#
# See /Users/sergi/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md
