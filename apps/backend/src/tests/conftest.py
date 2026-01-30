"""
Pytest configuration and fixtures for FinanceHub tests.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock
from datetime import datetime

# Add Backend/src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure test database."""
    pass


@pytest.fixture
def api_client():
    """Create a test API client."""
    from ninja.testing import TestClient
    from api.ai_enhanced import router

    return TestClient(router)


@pytest.fixture
def user(db):
    """Create a test user."""
    from users.models import User, AccountType

    premium_type = AccountType.objects.get(name="Premium")
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        account_type=premium_type,
    )
    return user


@pytest.fixture
def non_premium_user(db):
    """Create a non-premium test user."""
    from users.models import User, AccountType

    free_type = AccountType.objects.get(name="Free")
    user = User.objects.create_user(
        email="regular@example.com",
        password="testpass123",
        first_name="Regular",
        last_name="User",
        account_type=free_type,
    )
    return user


@pytest.fixture
def non_premium_user(db):
    """Create a non-premium test user."""
    from users.models import User

    user = User.objects.create_user(
        email="regular@example.com",
        password="testpass123",
        first_name="Regular",
        last_name="User",
        is_premium=False,
    )
    return user


@pytest.fixture
def portfolio(db, user):
    """Create a test portfolio."""
    from portfolios.models import Portfolio

    portfolio = Portfolio.objects.create(
        user=user,
        name="Test Portfolio",
        portfolio_type=Portfolio.PortfolioType.INDEX_FUND,
        currency="USD",
        status=Portfolio.Status.ACTIVE,
    )
    return portfolio


@pytest.fixture
def asset(db):
    """Create a test asset."""
    from assets.models.asset import Asset
    from assets.models.asset_type import AssetType
    from assets.models.asset_class import AssetClass

    equity_class = AssetClass.objects.create(
        name="Equity",
        description="Stock investments",
        risk_level=5,
    )
    stock_type = AssetType.objects.create(
        name="Stock",
        asset_class=equity_class,
        symbol_pattern="^[A-Z]{1,5}$",
    )
    asset = Asset.objects.create(
        ticker="AAPL",
        name="Apple Inc.",
        asset_type=stock_type,
        asset_class=equity_class,
        currency="USD",
        status=Asset.Status.ACTIVE,
    )
    return asset


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock AI response for testing purposes.",
                    "role": "assistant",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
        },
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "indices": [
            {"symbol": "SPX", "value": 4780.25, "change": 1.2},
            {"symbol": "DJI", "value": 37500.50, "change": 0.8},
            {"symbol": "IXIC", "value": 15000.75, "change": 1.5},
        ],
        "sectors": [
            {"name": "Technology", "change": 2.1},
            {"name": "Healthcare", "change": 0.5},
            {"name": "Financials", "change": 1.3},
        ],
        "fear_greed_index": 65,
        "vix": 18.5,
    }


@pytest.fixture
def sample_portfolio_data(portfolio, asset):
    """Sample portfolio data for portfolios testing."""
    from portfolios.models import Holding

    holding = Holding.objects.create(
        portfolio=portfolio,
        asset=asset,
        quantity=10,
        average_cost=150.00,
    )

    return {
        "portfolio_id": portfolio.id,
        "total_value": 2000.00,
        "total_cost": 1500.00,
        "holdings": [
            {
                "asset": "AAPL",
                "quantity": 10,
                "current_price": 200.00,
                "value": 2000.00,
                "gain_loss": 500.00,
                "gain_loss_pct": 33.33,
            }
        ],
        "allocation": {
            "Technology": 100.0,
        },
    }


@pytest.fixture
def sample_crypto_data():
    """Sample cryptocurrency data for testing."""
    return {
        "bitcoin": {
            "price": 45000.00,
            "change_24h": 3.5,
            "market_cap": 850000000000,
            "volume": 35000000000,
        },
        "ethereum": {
            "price": 2500.00,
            "change_24h": 2.8,
            "market_cap": 300000000000,
            "volume": 15000000000,
        },
        "market_sentiment": "bullish",
    }
