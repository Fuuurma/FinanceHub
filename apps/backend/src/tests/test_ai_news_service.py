"""
Unit tests for the AINewsService and NewsAggregatorService.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from investments.services.ai_news_service import (
    AINewsService,
    NewsAggregatorService,
    AIServiceError,
)


class TestAINewsServiceUnit:
    """Unit tests for AINewsService."""

    def test_service_initialization_without_api_key(self):
        """Test service initialization without API key."""
        with patch("investments.services.ai_news_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            service = AINewsService(api_key=None)
            assert service.client is None

    def test_service_initialization_with_api_key(self):
        """Test service initialization with API key."""
        with patch("investments.services.ai_news_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            with patch("builtins.__import__") as mock_import:
                mock_import.return_value = None
                service = AINewsService(api_key="test-api-key")
                assert service.client is None

    def test_mock_summarize_format(self):
        """Test mock summarization returns expected format."""
        service = AINewsService()
        result = service._mock_summarize("Test Title", "Test content here.")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Test Title" in result

    def test_mock_sentiment_positive_keywords(self):
        """Test mock sentiment detection with positive keywords."""
        service = AINewsService()
        result = service._mock_sentiment(
            "Stock surges to record high after earnings beat",
            "The company reported record profits and revenue growth.",
        )
        assert "score" in result
        assert "label" in result
        assert "key_points" in result
        assert result["label"] == "POSITIVE"
        assert result["score"] > 0

    def test_mock_sentiment_negative_keywords(self):
        """Test mock sentiment detection with negative keywords."""
        service = AINewsService()
        result = service._mock_sentiment(
            "Stock plunges after warning",
            "The company reported losses and declining revenue.",
        )
        assert result["label"] == "NEGATIVE"
        assert result["score"] < 0

    def test_mock_sentiment_neutral(self):
        """Test mock sentiment detection for neutral content."""
        service = AINewsService()
        result = service._mock_sentiment(
            "Company announces quarterly meeting",
            "The board will meet to discuss regular business.",
        )
        assert result["label"] == "NEUTRAL"
        assert -0.2 <= result["score"] <= 0.2

    def test_mock_extract_assets_basic(self):
        """Test mock asset extraction finds uppercase symbols."""
        service = AINewsService()
        result = service._mock_extract_assets(
            "AAPL and MSFT lead market higher",
            "Apple Inc. and Microsoft Corp. both gained today.",
        )
        assert isinstance(result, list)
        assert "AAPL" in result or "MSFT" in result

    def test_mock_extract_assets_filters_common_words(self):
        """Test mock asset extraction filters common words."""
        service = AINewsService()
        result = service._mock_extract_assets(
            "THE STOCK AND FOR THE COMPANY", "This is a test article about THE market."
        )
        assert "THE" not in result
        assert "AND" not in result
        assert "FOR" not in result

    def test_mock_extract_assets_limit(self):
        """Test mock asset extraction respects limit."""
        service = AINewsService()
        text = "AAPL MSFT GOOGL AMZN META NVDA TSLA AMD INTC QCOM AAPL GOOGL"
        result = service._mock_extract_assets(text, text * 10)
        assert len(result) <= 10

    def test_mock_impact_score_base(self):
        """Test mock impact score calculation."""
        service = AINewsService()
        result = service._mock_impact_score("Test Title", "Test content", 0.0, [])
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

    def test_mock_impact_score_with_keywords(self):
        """Test mock impact score with impact keywords."""
        service = AINewsService()
        base_result = service._mock_impact_score("Title", "Content", 0.0, [])
        earnings_result = service._mock_impact_score(
            "Earnings Report", "Quarterly earnings report shows profit", 0.0, []
        )
        assert earnings_result > base_result

    def test_mock_impact_score_with_sentiment(self):
        """Test mock impact score incorporates sentiment."""
        service = AINewsService()
        neutral_result = service._mock_impact_score("Title", "Content", 0.0, [])
        positive_result = service._mock_impact_score("Title", "Content", 0.8, [])
        assert positive_result > neutral_result

    def test_mock_impact_score_with_assets(self):
        """Test mock impact score with asset mentions."""
        service = AINewsService()
        no_assets = service._mock_impact_score("Title", "Content", 0.0, [])
        with_assets = service._mock_impact_score(
            "Title", "Content", 0.0, ["AAPL", "MSFT"]
        )
        assert with_assets > no_assets

    def test_mock_impact_score_max_limit(self):
        """Test mock impact score doesn't exceed 100."""
        service = AINewsService()
        result = service._mock_impact_score(
            "BREAKING: IPO and acquisition announcement!",
            "Breaking news about major acquisition and ipo",
            1.0,
            ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
        )
        assert result <= 100


class TestAINewsServiceAsync:
    """Async tests for AINewsService."""

    @pytest.mark.asyncio
    async def test_summarize_article_mock_mode(self):
        """Test article summarization in mock mode."""
        service = AINewsService()
        result = await service.summarize_article("Test Title", "Test content.")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_analyze_sentiment_mock_mode(self):
        """Test sentiment analysis in mock mode."""
        service = AINewsService()
        result = await service.analyze_sentiment("Test Title", "Test content.")
        assert "score" in result
        assert "label" in result
        assert "key_points" in result

    @pytest.mark.asyncio
    async def test_extract_asset_mentions_mock_mode(self):
        """Test asset extraction in mock mode."""
        service = AINewsService()
        result = await service.extract_asset_mentions("AAPL rises", "AAPL stock up")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_calculate_impact_score_mock_mode(self):
        """Test impact score calculation in mock mode."""
        service = AINewsService()
        result = await service.calculate_impact_score("Title", "Content", 0.5, ["AAPL"])
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

    @pytest.mark.asyncio
    async def test_analyze_article_full_structure(self):
        """Test full article analysis returns correct structure."""
        service = AINewsService()
        result = await service.analyze_article_full(
            "Test Title", "Test content.", "test_source"
        )

        assert "summary" in result
        assert "sentiment" in result
        assert "asset_mentions" in result
        assert "impact_score" in result
        assert "analyzed_at" in result

        assert isinstance(result["summary"], str)
        assert isinstance(result["sentiment"], dict)
        assert isinstance(result["asset_mentions"], list)
        assert isinstance(result["impact_score"], (int, float))


class TestNewsAggregatorService:
    """Tests for NewsAggregatorService."""

    def test_aggregator_initialization(self):
        """Test aggregator service initialization."""
        with patch("investments.services.ai_news_service.AINewsService"):
            service = NewsAggregatorService()
            assert hasattr(service, "ai_service")

    @pytest.mark.asyncio
    async def test_process_article_structure(self):
        """Test article processing returns correct structure."""
        service = NewsAggregatorService()

        result = await service.process_article(
            title="Test Article",
            content="Test content",
            url="https://example.com/article",
            source="Test Source",
            published_at=datetime.now(),
            description="Test description",
            author="Test Author",
            image_url="https://example.com/image.jpg",
            category="Technology",
        )

        assert "title" in result
        assert "url" in result
        assert "source" in result
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "related_symbols" in result
        assert "summary" in result
        assert "impact_score" in result

    @pytest.mark.asyncio
    async def test_process_article_with_minimal_data(self):
        """Test article processing with minimal data."""
        service = NewsAggregatorService()

        result = await service.process_article(
            title="Test Article",
            content="Test content",
            url="https://example.com/article",
            source="Test Source",
            published_at=datetime.now(),
        )

        assert result["title"] == "Test Article"
        assert result["sentiment"] in ["positive", "negative", "neutral"]

    @pytest.mark.asyncio
    async def test_batch_process_structure(self):
        """Test batch processing returns list of results."""
        service = NewsAggregatorService()

        articles = [
            {
                "title": "Article 1",
                "content": "Content 1",
                "url": "https://example.com/1",
                "source": "Source 1",
                "published_at": datetime.now(),
            },
            {
                "title": "Article 2",
                "content": "Content 2",
                "url": "https://example.com/2",
                "source": "Source 2",
                "published_at": datetime.now(),
            },
        ]

        results = await service.batch_process(articles)

        assert isinstance(results, list)
        assert len(results) == 2
        assert "title" in results[0]
        assert "title" in results[1]

    @pytest.mark.asyncio
    async def test_batch_process_handles_errors(self):
        """Test batch processing handles errors gracefully."""
        service = NewsAggregatorService()

        articles = [
            {
                "title": "Valid Article",
                "content": "Content",
                "url": "https://example.com/1",
                "source": "Source",
                "published_at": datetime.now(),
            },
            {
                "title": "Invalid Article",
                "content": "Content",
                "url": "https://example.com/2",
                "source": "Source",
                "published_at": "not-a-datetime",
            },
        ]

        results = await service.batch_process(articles)
        assert len(results) == 2


class TestSentimentScoring:
    """Tests for sentiment scoring logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AINewsService()

    def test_sentiment_score_range(self):
        """Test that sentiment scores stay within bounds."""
        for _ in range(10):
            result = self.service._mock_sentiment("Title", "Content")
            assert -1.0 <= result["score"] <= 1.0

    def test_positive_keywords_accumulate(self):
        """Test that multiple positive keywords increase score."""
        single = self.service._mock_sentiment("Surge", "Gain growth profit")
        multi = self.service._mock_sentiment(
            "Surge soar jump", "Gain growth profit beat record"
        )
        assert multi["score"] > single["score"]

    def test_negative_keywords_accumulate(self):
        """Test that multiple negative keywords decrease score."""
        single = self.service._mock_sentiment("Fall", "Loss decline")
        multi = self.service._mock_sentiment(
            "Fall plunge drop", "Loss decline miss warning cut"
        )
        assert multi["score"] < single["score"]


class TestImpactKeywords:
    """Tests for impact keyword scoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AINewsService()

    @pytest.mark.parametrize(
        "keyword,expected_bonus",
        [
            ("ipo", 15),
            ("breaking", 15),
            ("acquisition", 12),
            ("merger", 12),
            ("lawsuit", 10),
            ("fed", 10),
            ("recession", 10),
            ("earnings", 10),
        ],
    )
    def test_impact_keywords_add_score(self, keyword, expected_bonus):
        """Test that impact keywords add expected bonus."""
        base = self.service._mock_impact_score("Title", "Content", 0.0, [])
        with_keyword = self.service._mock_impact_score(
            f"News about {keyword}", f"This is about {keyword}", 0.0, []
        )
        assert with_keyword >= base + expected_bonus - 1


class TestAssetExtractionEdgeCases:
    """Tests for asset extraction edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AINewsService()

    def test_empty_content(self):
        """Test asset extraction with empty content."""
        result = self.service._mock_extract_assets("Title", "")
        assert isinstance(result, list)

    def test_no_symbols(self):
        """Test asset extraction when no symbols present."""
        result = self.service._mock_extract_assets(
            "Market shows mixed signals", "The overall market was mixed today."
        )
        assert isinstance(result, list)

    def test_numeric_tickers_filtered(self):
        """Test that pure numeric tickers are handled."""
        result = self.service._mock_extract_assets(
            "1234 Stock up", "Company 1234 reported earnings."
        )
        assert "1234" not in result

    def test_chinese_characters_no_symbols(self):
        """Test Chinese content doesn't produce false symbols."""
        result = self.service._mock_extract_assets(
            "苹果公司股票上涨", "苹果公司今天发布了最新财报。"
        )
        assert len(result) == 0 or all(not s.isdigit() for s in result)
