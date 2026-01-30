"""
Tests for AI Advisor API models and validators.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta

from api.ai_enhanced import (
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    PortfolioReportRequest,
    PortfolioReportResponse,
    TemplateListResponse,
    OnDemandAnalysisRequest,
    OnDemandAnalysisResponse,
    AIStatusResponse,
)
from ai_advisor.models.ai_template import (
    AITemplate,
    TEMPLATE_TYPES,
    REPORT_TYPES,
)


pytestmark = pytest.mark.django_db


class TestRequestModels:
    """Tests for API request models."""

    def test_market_analysis_request_defaults(self):
        """Test MarketAnalysisRequest default values."""
        req = MarketAnalysisRequest(symbol="AAPL")
        assert req.symbol == "AAPL"
        assert req.include_forecast is True
        assert req.include_sentiment is True
        assert req.include_options is False

    def test_market_analysis_request_custom(self):
        """Test MarketAnalysisRequest with custom values."""
        req = MarketAnalysisRequest(
            symbol="AAPL",
            include_forecast=False,
            include_sentiment=False,
            include_options=True,
        )
        assert req.include_forecast is False
        assert req.include_sentiment is False
        assert req.include_options is True

    def test_portfolio_report_request_defaults(self):
        """Test PortfolioReportRequest default values."""
        req = PortfolioReportRequest(portfolio_id="123")
        assert req.portfolio_id == "123"
        assert req.report_type == "portfolio_report"
        assert req.include_recommendations is True

    def test_on_demand_analysis_request(self):
        """Test OnDemandAnalysisRequest validation."""
        req = OnDemandAnalysisRequest(
            query="Analyze my portfolio",
            context_type="portfolio",
            context_id="123",
        )
        assert req.query == "Analyze my portfolio"
        assert req.context_type == "portfolio"
        assert req.context_id == "123"

    def test_on_demand_analysis_request_optional_context(self):
        """Test OnDemandAnalysisRequest with optional context."""
        req = OnDemandAnalysisRequest(query="Market outlook")
        assert req.query == "Market outlook"
        assert req.context_type is None
        assert req.context_id is None


class TestResponseModels:
    """Tests for API response models."""

    def test_market_analysis_response(self):
        """Test MarketAnalysisResponse model."""
        now = timezone.now()
        resp = MarketAnalysisResponse(
            symbol="AAPL",
            title="Apple Analysis",
            content="Apple stock analysis...",
            summary="Bullish",
            last_updated=now,
            version=1,
            next_refresh=now + timedelta(hours=12),
            is_premium_content=False,
        )
        assert resp.symbol == "AAPL"
        assert resp.version == 1
        assert resp.is_premium_content is False

    def test_portfolio_report_response(self):
        """Test PortfolioReportResponse model."""
        now = timezone.now()
        resp = PortfolioReportResponse(
            portfolio_id="123",
            title="Portfolio Report",
            content="Your portfolio analysis...",
            summary="Well-balanced",
            metadata={"return": 5.2},
            generated_at=now,
            expires_at=now + timedelta(hours=24),
            version=1,
            status="fresh",
        )
        assert resp.portfolio_id == "123"
        assert resp.status == "fresh"
        assert resp.metadata["return"] == 5.2

    def test_on_demand_analysis_response(self):
        """Test OnDemandAnalysisResponse model."""
        resp = OnDemandAnalysisResponse(
            query="What stocks to buy?",
            response="Consider Apple and Microsoft...",
            model_used="gpt-4",
            tokens_used=1500,
            compute_time_ms=2000.5,
        )
        assert resp.query == "What stocks to buy?"
        assert resp.model_used == "gpt-4"
        assert resp.tokens_used == 1500

    def test_ai_status_response(self):
        """Test AIStatusResponse model."""
        now = timezone.now()
        resp = AIStatusResponse(
            has_access=True,
            is_premium=True,
            template_access=True,
            on_demand_access=True,
            portfolio_reports=True,
            daily_requests_remaining=95,
            next_template_refresh=now + timedelta(hours=6),
        )
        assert resp.has_access is True
        assert resp.is_premium is True
        assert resp.daily_requests_remaining == 95


class TestTemplateTypeValidation:
    """Tests for template type validation."""

    def test_valid_template_types(self):
        """Test all valid template types are recognized."""
        types = dict(TEMPLATE_TYPES)
        expected_types = [
            "market_summary",
            "asset_analysis",
            "sector_report",
            "risk_commentary",
            "sentiment_summary",
            "volatility_outlook",
            "options_strategy",
            "bond_market",
            "crypto_market",
            "earnings_preview",
            "macro_outlook",
        ]
        for t in expected_types:
            assert t in types

    def test_valid_report_types(self):
        """Test all valid report types are recognized."""
        types = dict(REPORT_TYPES)
        expected_types = [
            "portfolio_report",
            "holdings_analysis",
            "performance_attribution",
            "risk_assessment",
            "rebalancing_suggestion",
            "tax_efficiency",
        ]
        for t in expected_types:
            assert t in types


class TestTemplateModelIntegration:
    """Integration tests for template model with API."""

    def test_template_for_market_analysis_response(self):
        """Test creating MarketAnalysisResponse from template."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Market Analysis",
            content="Detailed market analysis...",
            summary="Market up 2%",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            version=2,
        )

        resp = MarketAnalysisResponse(
            symbol="",
            title=template.title,
            content=template.content,
            summary=template.summary,
            last_updated=template.last_generated_at,
            version=template.version,
            next_refresh=template.next_refresh_at,
        )

        assert resp.title == "Market Analysis"
        assert resp.version == 2
        assert resp.summary == "Market up 2%"

    def test_template_for_asset_analysis_response(self):
        """Test creating response from asset analysis template."""
        template = AITemplate.objects.create(
            template_type="asset_analysis",
            symbol="AAPL",
            title="Apple Stock Analysis",
            content="Apple shows strong fundamentals...",
            summary="Buy rating, $200 target",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=12),
        )

        resp = MarketAnalysisResponse(
            symbol=template.symbol,
            title=template.title,
            content=template.content,
            summary=template.summary,
            last_updated=template.last_generated_at,
            version=template.version,
            next_refresh=template.next_refresh_at,
        )

        assert resp.symbol == "AAPL"
        assert resp.is_premium_content is False

    def test_stale_template_status(self):
        """Test stale template detection."""
        fresh_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Fresh",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )

        stale_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Stale",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now() - timedelta(hours=12),
            next_refresh_at=timezone.now() - timedelta(hours=6),
        )

        assert fresh_template.is_stale is False
        assert stale_template.is_stale is True

    def test_template_expiration_for_report(self):
        """Test template expiration handling."""
        now = timezone.now()
        fresh_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Fresh Report",
            content="Content",
            summary="Summary",
            last_generated_at=now,
            next_refresh_at=now + timedelta(hours=12),
        )

        expired_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Expired Report",
            content="Content",
            summary="Summary",
            last_generated_at=now - timedelta(hours=25),
            next_refresh_at=now - timedelta(hours=1),
        )

        fresh_resp = PortfolioReportResponse(
            portfolio_id="123",
            title=fresh_template.title,
            content=fresh_template.content,
            summary=fresh_template.summary,
            metadata={},
            generated_at=fresh_template.last_generated_at,
            expires_at=fresh_template.next_refresh_at,
            version=fresh_template.version,
            status="fresh",
        )

        stale_resp = PortfolioReportResponse(
            portfolio_id="123",
            title=expired_template.title,
            content=expired_template.content,
            summary=expired_template.summary,
            metadata={},
            generated_at=expired_template.last_generated_at,
            expires_at=expired_template.next_refresh_at,
            version=expired_template.version,
            status="stale",
        )

        assert fresh_resp.status == "fresh"
        assert stale_resp.status == "stale"


class TestTokenUsageTracking:
    """Tests for token usage tracking models."""

    def test_on_demand_response_token_fields(self):
        """Test OnDemandAnalysisResponse has all token fields."""
        resp = OnDemandAnalysisResponse(
            query="Test query",
            response="Test response",
            model_used="gpt-4-turbo",
            tokens_used=2500,
            compute_time_ms=3500.0,
        )
        assert resp.tokens_used == 2500
        assert resp.compute_time_ms == 3500.0
        assert resp.model_used == "gpt-4-turbo"
