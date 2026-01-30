"""
Example tests for FinanceHub.

IMPORTANT: REFERENCE only - do not modify existing tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# =============================================================================
# TEST ERROR RESPONSES
# =============================================================================

# from core import (
#     create_success_response,
#     create_error_response,
#     ErrorCode,
#     NotFoundException,
#     ValidationException,
# )
#
# def test_create_success_response():
#     response = create_success_response(data={"id": 1}, message="OK")
#     assert response["success"] is True
#     assert response["data"] == {"id": 1}
#
# def test_create_error_response():
#     response = create_error_response(
#         error="Not found",
#         code=ErrorCode.NOT_FOUND,
#         status_code=404
#     )
#     assert response["success"] is False
#     assert response["code"] == "NOT_FOUND"
#
# def test_not_found_exception():
#     with pytest.raises(NotFoundException) as exc_info:
#         raise NotFoundException("Portfolio", 123)
#     assert exc_info.value.resource == "Portfolio"


# =============================================================================
# TEST FILTERSCHEMA
# =============================================================================

# from .filters import PortfolioFilter, TransactionFilter
#
# def test_portfolio_filter():
#     filters = PortfolioFilter(status="active", search="tech")
#     assert filters.status == "active"
#     assert filters.search == "tech"
#
# def test_transaction_filter():
#     filters = TransactionFilter(transaction_type="buy")
#     assert filters.transaction_type == "buy"


# =============================================================================
# TEST PAGINATION
# =============================================================================

# from core import CustomPageNumberPagination
#
# @pytest.fixture
# def mock_queryset():
#     mock = MagicMock()
#     mock.filter.return_value = mock
#     mock.order_by.return_value = mock
#     mock.__getitem__ = Mock(side_effect=lambda s: list(mock) if isinstance(s, slice) else mock)
#     return mock
#
# def test_pagination(mock_queryset):
#     pagination = CustomPageNumberPagination()
#     pagination.page_size = 10
#     request = Mock()
#     request.GET = {"page": "1"}
#     pagination.paginate_queryset(mock_queryset, request)
#     mock.__getitem__.assert_called()


# =============================================================================
# TEST UTILITIES
# =============================================================================

def create_mock_request(get_params=None, post_data=None):
    request = Mock()
    request.GET = get_params or {}
    request.POST = post_data or {}
    request.data = post_data or {}
    return request


# =============================================================================
# RUNNING TESTS
# =============================================================================
#
# pytest src/core/api/examples/tests.py -v
#
# =============================================================================
