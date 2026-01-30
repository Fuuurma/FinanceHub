"""
Tests for AI Advisor template models.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from ai_advisor.models.ai_template import (
    AITemplate,
    AITemplateLog,
    AIQueryLog,
    UserAIReport,
    TEMPLATE_TYPES,
    REPORT_TYPES,
)


pytestmark = pytest.mark.django_db


class TestAITemplateModel:
    """Tests for AITemplate model."""

    def test_template_creation(self):
        """Test basic template creation."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Daily Market Summary",
            content="Market performed well today...",
            summary="Brief summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert template.id is not None
        assert template.template_type == "market_summary"
        assert template.is_active is True

    def test_template_with_symbol(self):
        """Test template with specific symbol."""
        template = AITemplate.objects.create(
            template_type="asset_analysis",
            symbol="AAPL",
            title="Apple Analysis",
            content="Apple stock analysis...",
            summary="Apple analysis summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=12),
        )
        assert template.symbol == "AAPL"

    def test_template_with_sector(self):
        """Test template with sector."""
        template = AITemplate.objects.create(
            template_type="sector_report",
            sector="Technology",
            title="Tech Sector Report",
            content="Technology sector analysis...",
            summary="Tech sector summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=24),
        )
        assert template.sector == "Technology"

    def test_template_with_asset_class(self):
        """Test template with asset class."""
        template = AITemplate.objects.create(
            template_type="crypto_market",
            asset_class="crypto",
            title="Crypto Market Report",
            content="Cryptocurrency market analysis...",
            summary="Crypto summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert template.asset_class == "crypto"

    def test_is_stale_property(self):
        """Test is_stale property."""
        fresh_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Fresh Template",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert fresh_template.is_stale is False

        stale_template = AITemplate.objects.create(
            template_type="market_summary",
            title="Stale Template",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now() - timedelta(hours=12),
            next_refresh_at=timezone.now() - timedelta(hours=1),
        )
        assert stale_template.is_stale is True

    def test_age_hours_property(self):
        """Test age_hours calculation."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Test Template",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now() - timedelta(hours=5),
            next_refresh_at=timezone.now() + timedelta(hours=1),
        )
        assert 4.9 <= template.age_hours <= 5.1

    def test_refresh_needed_for_market_summary(self):
        """Test refresh interval for market_summary (6 hours)."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Test",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now() - timedelta(hours=7),
            next_refresh_at=timezone.now() - timedelta(hours=1),
        )
        assert template.refresh_needed() is True

    def test_refresh_needed_for_sector_report(self):
        """Test refresh interval for sector_report (24 hours)."""
        template = AITemplate.objects.create(
            template_type="sector_report",
            sector="Technology",
            title="Tech Report",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now() - timedelta(hours=23),
            next_refresh_at=timezone.now() + timedelta(hours=1),
        )
        assert template.refresh_needed() is False

    def test_template_string_representation(self):
        """Test __str__ method."""
        template = AITemplate.objects.create(
            template_type="asset_analysis",
            symbol="AAPL",
            title="Test",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now(),
        )
        assert "Asset Analysis" in str(template)
        assert "AAPL" in str(template)

    def test_template_inactive(self):
        """Test inactive template."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Inactive",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            is_active=False,
        )
        assert template.is_active is False

    def test_template_with_metadata(self):
        """Test template with metadata."""
        metadata = {"prices": {"AAPL": 150.0}, "sentiment": "bullish"}
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Test with Meta",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            metadata=metadata,
        )
        assert template.metadata == metadata
        assert template.metadata["sentiment"] == "bullish"

    def test_template_versioning(self):
        """Test template version tracking."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Version Test",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            version=5,
        )
        assert template.version == 5

    def test_template_generation_error(self):
        """Test template with generation error."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Error Template",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            generation_error="LLM API rate limit exceeded",
        )
        assert template.generation_error == "LLM API rate limit exceeded"


class TestAITemplateLogModel:
    """Tests for AITemplateLog model."""

    def test_log_creation(self):
        """Test log entry creation."""
        log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=True,
            model_used="gpt-4",
            input_tokens=100,
            output_tokens=500,
            total_tokens=600,
            compute_time_ms=1500,
        )
        assert log.id is not None
        assert log.success is True
        assert log.total_tokens == 600

    def test_failed_log(self):
        """Test failed log entry."""
        log = AITemplateLog.objects.create(
            template_type="asset_analysis",
            symbol="INVALID",
            success=False,
            error_message="API rate limit exceeded",
            model_used="gpt-4",
        )
        assert log.success is False
        assert "rate limit" in log.error_message

    def test_log_string_representation(self):
        """Test __str__ method."""
        success_log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=True,
            model_used="gpt-4",
        )
        assert "SUCCESS" in str(success_log)

        failed_log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=False,
            model_used="gpt-4",
        )
        assert "FAILED" in str(failed_log)

    def test_log_with_symbol(self):
        """Test log entry with symbol."""
        log = AITemplateLog.objects.create(
            template_type="asset_analysis",
            symbol="AAPL",
            success=True,
            model_used="gpt-4",
            input_tokens=200,
            output_tokens=1000,
            total_tokens=1200,
        )
        assert log.symbol == "AAPL"

    def test_log_with_template(self):
        """Test log entry linked to template."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Test",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        log = AITemplateLog.objects.create(
            template_type="market_summary",
            template=template,
            success=True,
            model_used="gpt-4",
            input_tokens=100,
            output_tokens=500,
            total_tokens=600,
        )
        assert log.template == template

    def test_log_cost_tracking(self):
        """Test log cost tracking fields."""
        log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=True,
            model_used="gpt-4",
            input_tokens=1500,
            output_tokens=3000,
            total_tokens=4500,
            compute_time_ms=2500,
        )
        assert log.input_tokens == 1500
        assert log.output_tokens == 3000
        assert log.total_tokens == 4500
        assert log.compute_time_ms == 2500

    def test_log_input_data_snapshot(self):
        """Test log input data snapshot."""
        input_data = {"symbols": ["AAPL", "GOOGL"], "timeframe": "1d"}
        log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=True,
            model_used="gpt-4",
            input_data=input_data,
        )
        assert log.input_data == input_data
        assert log.input_data["symbols"] == ["AAPL", "GOOGL"]

    def test_log_failed_with_retry_info(self):
        """Test failed log with retry information."""
        log = AITemplateLog.objects.create(
            template_type="market_summary",
            success=False,
            error_message="Temporary failure, retry recommended",
            model_used="gpt-4",
            compute_time_ms=500,
        )
        assert log.success is False
        assert log.total_tokens == 0
        assert log.compute_time_ms == 500


class TestAIQueryLogModel:
    """Tests for AIQueryLog model."""

    def test_query_log_creation(self):
        """Test query log creation."""
        log = AIQueryLog.objects.create(
            session_id="session_123",
            query_type="portfolio",
            query_text="Analyze my portfolio",
            success=True,
            model_used="gpt-4",
            input_tokens=200,
            output_tokens=1000,
            total_tokens=1200,
            compute_time_ms=2000,
        )
        assert log.id is not None
        assert log.session_id == "session_123"

    def test_query_log_with_user(self):
        """Test query log for authenticated user."""
        log = AIQueryLog.objects.create(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            session_id="session_456",
            query_type="market",
            query_text="Market outlook",
            success=True,
            model_used="gpt-4",
        )
        assert log.user_id is not None
        assert log.session_id == "session_456"

    def test_query_log_failed(self):
        """Test failed query log."""
        log = AIQueryLog.objects.create(
            session_id="session_789",
            query_type="analysis",
            query_text="Analyze this stock",
            success=False,
            error_message="Model timeout",
            model_used="gpt-4",
        )
        assert log.success is False
        assert log.error_message == "Model timeout"

    def test_query_log_response_truncation(self):
        """Test query log response truncation for long responses."""
        long_response = "A" * 5000
        log = AIQueryLog.objects.create(
            session_id="session_abc",
            query_type="analysis",
            query_text="Give me a detailed analysis",
            success=True,
            response_text=long_response,
            model_used="gpt-4",
        )
        assert len(log.response_text) == 5000

    def test_query_log_query_types(self):
        """Test different query types."""
        query_types = ["portfolio", "market", "strategy", "sentiment", "risk"]
        for qtype in query_types:
            log = AIQueryLog.objects.create(
                session_id=f"session_{qtype}",
                query_type=qtype,
                query_text=f"{qtype} query",
                success=True,
                model_used="gpt-4",
            )
            assert log.query_type == qtype

    def test_query_log_cost_tracking(self):
        """Test query log cost tracking."""
        log = AIQueryLog.objects.create(
            session_id="session_cost",
            query_type="portfolio",
            query_text="Analyze portfolio",
            success=True,
            model_used="gpt-4-turbo",
            input_tokens=500,
            output_tokens=2000,
            total_tokens=2500,
            compute_time_ms=1800,
        )
        assert log.model_used == "gpt-4-turbo"
        assert log.total_tokens == 2500
        assert log.compute_time_ms == 1800

    def test_query_log_anonymous_session(self):
        """Test query log for anonymous user session."""
        log = AIQueryLog.objects.create(
            session_id="anonymous_session_xyz",
            query_type="market",
            query_text="General market question",
            success=True,
            model_used="gpt-4",
        )
        assert log.user_id is None
        assert log.session_id == "anonymous_session_xyz"


class TestTemplateTypeChoices:
    """Tests for template type choices."""

    def test_template_types_complete(self):
        """Verify all expected template types exist."""
        types = dict(TEMPLATE_TYPES)
        assert "market_summary" in types
        assert "asset_analysis" in types
        assert "sector_report" in types
        assert "crypto_market" in types
        assert "bond_market" in types
        assert "options_strategy" in types
        assert "volatility_outlook" in types
        assert "sentiment_summary" in types
        assert "risk_commentary" in types
        assert "macro_outlook" in types
        assert "earnings_preview" in types

    def test_report_types_complete(self):
        """Verify all expected report types exist."""
        types = dict(REPORT_TYPES)
        assert "portfolio_report" in types
        assert "holdings_analysis" in types
        assert "performance_attribution" in types
        assert "risk_assessment" in types
        assert "rebalancing_suggestion" in types
        assert "tax_efficiency" in types

    def test_template_type_count(self):
        """Verify minimum template types exist."""
        assert len(TEMPLATE_TYPES) >= 10

    def test_report_type_count(self):
        """Verify minimum report types exist."""
        assert len(REPORT_TYPES) >= 5


class TestAITemplateModelEdgeCases:
    """Edge case tests for AITemplate model."""

    def test_template_null_symbol(self):
        """Test template with null symbol (general templates)."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            symbol=None,
            title="General Market",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert template.symbol is None

    def test_template_null_sector(self):
        """Test template with null sector."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            sector=None,
            title="No Sector",
            content="Content",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert template.sector is None

    def test_template_empty_content(self):
        """Test template with empty content."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Empty",
            content="",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert template.content == ""

    def test_template_long_summary(self):
        """Test template with long summary (near max 500 chars)."""
        long_summary = "A" * 499
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Long Summary",
            content="Content",
            summary=long_summary,
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
        )
        assert len(template.summary) == 499

    def test_template_version_increment(self):
        """Test template version increments on update."""
        template = AITemplate.objects.create(
            template_type="market_summary",
            title="Version Test",
            content="Content v1",
            summary="Summary",
            last_generated_at=timezone.now(),
            next_refresh_at=timezone.now() + timedelta(hours=6),
            version=1,
        )
        template.version = 2
        template.save()
        template.refresh_from_db()
        assert template.version == 2
