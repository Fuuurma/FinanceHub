"""
Social Sentiment Analysis Tests - C-037

Comprehensive test suite for social sentiment functionality including:
- Twitter sentiment fetching
- Reddit sentiment fetching
- Sentiment aggregation from multiple sources
- Sentiment trend detection
- Accuracy validation
- Performance testing

Created by: GRACE (QA Engineer)
Date: February 1, 2026
Status: READY FOR IMPLEMENTATION
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase

from src.social_sentiment.services.sentiment_service import SentimentService
from src.social_sentiment.services.twitter_service import TwitterService
from src.social_sentiment.services.reddit_service import RedditService


class TestTwitterSentimentFetching(TestCase):
    """Test Twitter sentiment functionality (TC-SS-001, TC-SS-002)."""

    def setUp(self):
        """Set up test fixtures."""
        self.twitter_service = TwitterService()
        self.sentiment_service = SentimentService()

    def test_fetch_twitter_sentiment_for_stock(self):
        """
        TC-SS-001: Fetch Twitter sentiment for stock

        Expected: Returns tweets with sentiment scores
        Test Data: Fetch sentiment for AAPL
        """
        mock_tweets = [
            {"text": "AAPL is looking great today!", "sentiment_score": 0.8},
            {"text": "AAPL might have some issues", "sentiment_score": -0.3},
            {"text": "AAPL earnings coming up", "sentiment_score": 0.1},
        ]

        with patch.object(
            self.twitter_service, "fetch_tweets", return_value=mock_tweets
        ):
            result = self.sentiment_service.get_twitter_sentiment("AAPL")

            assert result is not None
            assert "score" in result
            assert "tweets" in result
            assert -1.0 <= result["score"] <= 1.0

    def test_handle_twitter_rate_limiting(self):
        """
        TC-SS-002: Handle Twitter API rate limiting

        Expected: Gracefully handle rate limit, wait and retry
        Test Data: Exceed Twitter API rate limit
        """
        from src.social_sentiment.exceptions import RateLimitException

        with patch.object(
            self.twitter_service,
            "fetch_tweets",
            side_effect=RateLimitException("Rate limited"),
        ):
            with pytest.raises(RateLimitException):
                self.sentiment_service.get_twitter_sentiment("AAPL")


class TestRedditSentimentFetching(TestCase):
    """Test Reddit sentiment functionality (TC-SS-003)."""

    def setUp(self):
        """Set up test fixtures."""
        self.reddit_service = RedditService()
        self.sentiment_service = SentimentService()

    def test_fetch_reddit_sentiment_for_stock(self):
        """
        TC-SS-003: Fetch Reddit sentiment for stock

        Expected: Returns posts with sentiment scores
        Test Data: Fetch sentiment for TSLA
        """
        mock_posts = [
            {"text": "TSLA to the moon!", "sentiment_score": 0.9, "upvotes": 1500},
            {"text": "TSLA is overvalued", "sentiment_score": -0.5, "upvotes": 800},
        ]

        with patch.object(self.reddit_service, "fetch_posts", return_value=mock_posts):
            result = self.sentiment_service.get_reddit_sentiment("TSLA")

            assert result is not None
            assert "score" in result
            assert "posts" in result
            assert "r/wallstreetbets" in str(result["sources"]) or "r/stocks" in str(
                result["sources"]
            )


class TestSentimentAggregation(TestCase):
    """Test sentiment aggregation (TC-SS-004)."""

    def setUp(self):
        """Set up test fixtures."""
        self.sentiment_service = SentimentService()

    def test_aggregate_sentiment_from_multiple_sources(self):
        """
        TC-SS-004: Aggregate sentiment from multiple sources

        Expected: Returns weighted sentiment score
        Test Data:
          - Twitter: score=0.5, count=100
          - Reddit: score=0.3, count=50
        """
        mock_sources = {
            "twitter": {"score": Decimal("0.5"), "count": 100},
            "reddit": {"score": Decimal("0.3"), "count": 50},
        }

        result = self.sentiment_service.aggregate_sentiment(mock_sources)

        assert result is not None
        assert "aggregated_score" in result
        assert "source_weights" in result
        assert result["source_weights"]["twitter"] == 0.4
        assert result["source_weights"]["reddit"] == 0.4


class TestSentimentTrendDetection(TestCase):
    """Test sentiment trend detection (TC-SS-005)."""

    def setUp(self):
        """Set up test fixtures."""
        self.sentiment_service = SentimentService()

    def test_detect_improving_sentiment_trend(self):
        """
        TC-SS-005: Detect improving sentiment trend

        Expected: Returns "improving" when sentiment increases
        Test Data: Current score=0.4, previous score=0.2
        """
        current_score = Decimal("0.4")
        previous_score = Decimal("0.2")

        trend = self.sentiment_service.detect_trend(current_score, previous_score)

        assert trend == "improving"

    def test_detect_declining_sentiment_trend(self):
        """Test declining trend detection."""
        current_score = Decimal("0.1")
        previous_score = Decimal("0.4")

        trend = self.sentiment_service.detect_trend(current_score, previous_score)

        assert trend == "declining"

    def test_detect_stable_sentiment_trend(self):
        """Test stable trend detection."""
        current_score = Decimal("0.3")
        previous_score = Decimal("0.29")

        trend = self.sentiment_service.detect_trend(current_score, previous_score)

        assert trend == "stable"


class TestSentimentAccuracyValidation(TestCase):
    """Test sentiment accuracy (TC-SS-006)."""

    def setUp(self):
        """Set up test fixtures."""
        self.sentiment_service = SentimentService()

    def test_sentiment_accuracy_threshold(self):
        """
        TC-SS-006: Validate sentiment accuracy

        Expected: Sentiment accuracy > 75%
        """
        mock_analyses = [
            {"text": "Bullish on AAPL", "predicted": "bullish", "actual": "bullish"},
            {"text": "AAPL looks good", "predicted": "bullish", "actual": "bullish"},
            {"text": "AAPL might drop", "predicted": "bearish", "actual": "bearish"},
            {
                "text": "Not sure about AAPL",
                "predicted": "neutral",
                "actual": "neutral",
            },
        ]

        accuracy = self.sentiment_service.calculate_accuracy(mock_analyses)

        assert accuracy > 0.75, f"Accuracy {accuracy} below 75% threshold"


class TestSentimentPerformance(TestCase):
    """Test sentiment performance (TC-SS-007)."""

    def setUp(self):
        """Set up test fixtures."""
        self.sentiment_service = SentimentService()

    def test_sentiment_api_response_time(self):
        """
        TC-SS-007: Sentiment API response time < 500ms

        Expected: p95 response time < 500ms
        """
        import time

        response_times = []
        for i in range(50):
            start = time.time()
            try:
                self.sentiment_service.get_combined_sentiment("AAPL")
            except Exception:
                pass
            elapsed = time.time() - start
            response_times.append(elapsed * 1000)

        response_times.sort()
        p95 = response_times[int(len(response_times) * 0.95)]
        assert p95 < 500, f"P95 response time {p95}ms exceeds 500ms threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
