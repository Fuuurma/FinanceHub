"""
Tests for AI Advisor API (Premium Feature)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from ninja.testing import TestAsyncClient
import asyncio

from api.ai_advisor import router
from utils.services.llm_advisor.ai_advisor import (
    AIAdvisorService,
    AIResponse,
    UsageStats,
)


def is_redis_available():
    """Check if Redis is available."""
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, db=0)
        r.ping()
        return True
    except Exception:
        return False


REDIS_AVAILABLE = is_redis_available()


class MockUser:
    """Mock user for testing."""

    def __init__(self, is_authenticated=True, is_paid=False, has_feature=False):
        self.id = "test-user-id"
        self.is_authenticated = is_authenticated
        self._is_subscription_active = is_paid
        self._is_trial_active = False
        self._account_type = Mock()
        self._account_type.name = "Free" if not is_paid else "Premium"
        self._account_type.features = {"ai_advisor": has_feature} if has_feature else {}

    @property
    def is_subscription_active(self):
        return self._is_subscription_active

    @property
    def is_trial_active(self):
        return self._is_trial_active

    @property
    def account_type(self):
        return self._account_type


class MockRequest:
    """Mock request object."""

    def __init__(self, user):
        self.user = user


@pytest.fixture
def mock_paid_user():
    """Create a paid user mock."""
    return MockUser(is_authenticated=True, is_paid=True)


@pytest.fixture
def mock_free_user():
    """Create a free user mock."""
    return MockUser(is_authenticated=True, is_paid=False)


@pytest.fixture
def mock_unauthenticated_user():
    """Create an unauthenticated user mock."""
    return MockUser(is_authenticated=False)


@pytest.fixture
def advisor_service():
    """Create AI advisor service instance."""
    return AIAdvisorService()


class TestAIFeatureAccess:
    """Tests for AI feature access checking."""

    def test_paid_user_has_access(self, advisor_service, mock_paid_user):
        """Test that paid users have access to AI features."""
        access = advisor_service.check_feature_access(mock_paid_user)

        assert access["has_access"] is True
        assert access["is_paid"] is True
        assert access["max_requests"] == 100

    def test_free_user_no_access(self, advisor_service, mock_free_user):
        """Test that free users without feature flag don't have access."""
        access = advisor_service.check_feature_access(mock_free_user)

        assert access["has_access"] is False
        assert access["is_paid"] is False

    def test_free_user_with_feature_flag(self, advisor_service):
        """Test that free users with feature flag have access."""
        user = MockUser(is_authenticated=True, is_paid=False, has_feature=True)
        access = advisor_service.check_feature_access(user)

        assert access["has_access"] is True
        # With feature flag, user has paid-level access
        assert access["is_paid"] is True
        assert access["max_requests"] == 100


class TestUsageStats:
    """Tests for usage tracking."""

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    def test_get_usage_stats(self, advisor_service):
        """Test getting usage statistics."""
        stats = advisor_service.get_usage_stats("test-user-id")

        assert isinstance(stats, UsageStats)
        assert stats.requests_today >= 0
        assert stats.remaining_today >= 0


class TestAIResponseGeneration:
    """Tests for AI response generation (mocked)."""

    @patch.object(AIAdvisorService, "_call_llm")
    def test_explain_options_strategy(
        self, mock_call_llm, advisor_service, mock_paid_user
    ):
        """Test options strategy explanation."""
        mock_call_llm.return_value = AIResponse(
            text="A covered call involves owning 100 shares and selling a call option...",
            model_used="glm-4.7",
            tokens_used=150,
            compute_time_ms=500.0,
        )

        result = advisor_service.explain_options_strategy(
            strategy_type="covered_call",
            underlying="AAPL",
            strike=150.0,
            expiry="2024-03-15",
            premium=2.50,
            direction="long",
        )

        assert isinstance(result, AIResponse)
        assert "covered call" in result.text.lower()
        assert result.tokens_used > 0

    @patch.object(AIAdvisorService, "_call_llm")
    def test_suggest_options_strategy(
        self, mock_call_llm, advisor_service, mock_paid_user
    ):
        """Test options strategy suggestion."""
        mock_call_llm.return_value = AIResponse(
            text="1. Bull Call Spread: Buy $100 call, sell $105 call...",
            model_used="glm-4.7",
            tokens_used=200,
            compute_time_ms=600.0,
        )

        result = advisor_service.suggest_options_strategy(
            market_outlook="bullish",
            risk_tolerance="medium",
            underlying="SPY",
            current_price=450.0,
            time_horizon="weeks",
        )

        assert isinstance(result, AIResponse)
        assert result.tokens_used > 0

    @patch.object(AIAdvisorService, "_call_llm")
    def test_generate_forecast_narrative_arima(
        self, mock_call_llm, advisor_service, mock_paid_user
    ):
        """Test ARIMA forecast narrative generation."""
        mock_call_llm.return_value = AIResponse(
            text="The ARIMA model forecasts a slight increase in price...",
            model_used="glm-4.7",
            tokens_used=180,
            compute_time_ms=550.0,
        )

        forecast_data = {
            "forecast": {"day_1": 150.25, "day_5": 152.10, "day_10": 153.50},
            "order": (1, 0, 1),
            "aic": 245.5,
        }

        result = advisor_service.generate_forecast_narrative(
            symbol="AAPL",
            current_price=150.0,
            forecast_data=forecast_data,
            model_type="ARIMA",
            confidence_level=0.95,
        )

        assert isinstance(result, AIResponse)
        assert result.tokens_used > 0

    @patch.object(AIAdvisorService, "_call_llm")
    def test_generate_forecast_narrative_garch(
        self, mock_call_llm, advisor_service, mock_paid_user
    ):
        """Test GARCH forecast narrative generation."""
        mock_call_llm.return_value = AIResponse(
            text="The GARCH model indicates volatility will increase...",
            model_used="glm-4.7",
            tokens_used=180,
            compute_time_ms=550.0,
        )

        forecast_data = {
            "current_volatility": 0.20,
            "forecast_volatility": 0.25,
            "omega": 0.0001,
            "alpha": 0.05,
            "beta": 0.90,
        }

        result = advisor_service.generate_forecast_narrative(
            symbol="AAPL",
            current_price=150.0,
            forecast_data=forecast_data,
            model_type="GARCH",
            confidence_level=0.95,
        )

        assert isinstance(result, AIResponse)
        assert result.tokens_used > 0

    @patch.object(AIAdvisorService, "_call_llm")
    def test_explain_risk_metric(self, mock_call_llm, advisor_service, mock_paid_user):
        """Test risk metric explanation."""
        mock_call_llm.return_value = AIResponse(
            text="VaR of $10,000 means you're 95% confident...",
            model_used="glm-4.7",
            tokens_used=120,
            compute_time_ms=400.0,
        )

        result = advisor_service.explain_risk_metric(
            metric_name="VaR",
            value=10000.0,
            context={"confidence_level": 0.95},
            asset_type="portfolio",
        )

        assert isinstance(result, AIResponse)
        assert "VaR" in result.text or "var" in result.text.lower()


class TestAPIEndpoints:
    """Tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create async test client."""
        return TestAsyncClient(router)

    @pytest.mark.skip(reason="API endpoint tests require full async setup")
    @pytest.mark.asyncio
    async def test_access_status_unauthenticated(self, client):
        """Test access check for unauthenticated user."""
        response = await client.get("/access")

        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] is False

    @pytest.mark.skip(reason="API endpoint tests require full async setup")
    @pytest.mark.asyncio
    async def test_explain_strategy_requires_auth(self, client):
        """Test that strategy explanation requires authentication."""
        response = await client.post(
            "/explain-strategy",
            {
                "strategy_type": "call",
                "underlying": "AAPL",
                "strike": 150.0,
                "expiry": "2024-03-15",
                "premium": 2.50,
                "direction": "long",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_strategy_type(self, client, mock_paid_user):
        """Test validation for invalid strategy type."""
        with patch("api.ai_advisor.check_ai_access") as mock_check:
            mock_check.return_value = None

            response = await client.post(
                "/explain-strategy",
                {
                    "strategy_type": "invalid_strategy",
                    "underlying": "AAPL",
                    "strike": 150.0,
                    "expiry": "2024-03-15",
                    "premium": 2.50,
                    "direction": "long",
                },
            )

            assert response.status_code == 422

    @pytest.mark.skip(reason="API endpoint tests require full async setup")
    @pytest.mark.asyncio
    async def test_invalid_model_type(self, client, mock_paid_user):
        """Test validation for invalid model type."""
        with patch("api.ai_advisor.check_ai_access") as mock_check:
            mock_check.return_value = None

            response = await client.post(
                "/forecast-narrative",
                {
                    "symbol": "AAPL",
                    "current_price": 150.0,
                    "forecast_data": {},
                    "model_type": "INVALID",
                    "confidence_level": 0.95,
                },
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_model_type(self, client, mock_paid_user):
        """Test validation for invalid model type."""
        with patch("api.ai_advisor.check_ai_access") as mock_check:
            mock_check.return_value = None

            response = await client.post(
                "/forecast-narrative",
                {
                    "symbol": "AAPL",
                    "current_price": 150.0,
                    "forecast_data": {},
                    "model_type": "INVALID",
                    "confidence_level": 0.95,
                },
            )

            assert response.status_code == 422


class TestUsageRecording:
    """Tests for usage recording."""

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    def test_record_usage(self, advisor_service):
        """Test recording AI usage."""
        advisor_service.record_usage("test-user-id", tokens=500)

        stats = advisor_service.get_usage_stats("test-user-id")
        assert stats.requests_today >= 1


class TestAIAdvisorError:
    """Tests for error handling."""

    @patch.object(AIAdvisorService, "_call_llm")
    def test_llm_error_handling(self, mock_call_llm, advisor_service):
        """Test that LLM errors are handled properly."""
        import requests

        mock_call_llm.side_effect = requests.exceptions.ConnectionError(
            "Proxy unavailable"
        )

        with pytest.raises(Exception) as exc_info:
            advisor_service.explain_options_strategy(
                strategy_type="call",
                underlying="AAPL",
                strike=150.0,
                expiry="2024-03-15",
                premium=2.50,
            )

        assert "unavailable" in str(exc_info.value).lower()
