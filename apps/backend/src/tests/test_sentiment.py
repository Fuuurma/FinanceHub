"""
Tests for Social Sentiment Analysis Module
"""

from decimal import Decimal
from django.test import TestCase
from ninja.testing import TestClient
from social_sentiment.services.sentiment_analysis import (
    SentimentAnalyzer,
    TickerDetector,
    AggregatedSentiment,
    SentimentResult,
)
from social_sentiment.api import router


class TickerDetectorTest(TestCase):
    def test_extract_single_ticker(self):
        text = "I think $AAPL is going to moon!"
        result = TickerDetector.extract_tickers(text)
        self.assertIn("AAPL", result)

    def test_extract_multiple_tickers(self):
        text = "$AAPL and $MSFT both look good today"
        result = TickerDetector.extract_tickers(text)
        self.assertIn("AAPL", result)
        self.assertIn("MSFT", result)

    def test_extract_crypto_tickers(self):
        text = "Bitcoin is up! $BTC to the moon"
        result = TickerDetector.extract_tickers(text)
        self.assertIn("BTC", result)

    def test_extract_no_tickers(self):
        text = "The market is looking volatile today"
        result = TickerDetector.extract_tickers(text)
        self.assertEqual(len(result), 0)

    def test_is_crypto(self):
        self.assertTrue(TickerDetector.is_crypto("BTC"))
        self.assertTrue(TickerDetector.is_crypto("ETH"))
        self.assertFalse(TickerDetector.is_crypto("AAPL"))
        self.assertFalse(TickerDetector.is_crypto("MSFT"))


class SentimentAnalyzerTest(TestCase):
    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_returns_result(self):
        text = "I think $AAPL is going to moon!"
        result = self.analyzer.analyze(text)
        self.assertIsInstance(result, SentimentResult)
        self.assertIsNotNone(result.sentiment)
        self.assertIsNotNone(result.vader_compound)

    def test_analyze_text_method(self):
        text = "Bullish on $NVDA! Great AI news!"
        result = self.analyzer.analyze_text(text)
        self.assertIn("vader", result)
        self.assertIn("textblob", result)
        self.assertIn("combined_score", result)
        self.assertIn("sentiment_label", result)
        self.assertIn("detected_symbols", result)

    def test_analyze_batch(self):
        texts = [
            "Great day for $AAPL!",
            "Terrible day for $AAPL!",
            "Just a normal day for the market.",
        ]
        results = self.analyzer.analyze_batch(texts)
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], SentimentResult)

    def test_detect_tickers(self):
        text = "Check out $AAPL and $GOOGL"
        result = self.analyzer.detect_tickers(text)
        self.assertIn("AAPL", result)
        self.assertIn("GOOGL", result)


class AggregatedSentimentTest(TestCase):
    def test_aggregate_empty_results(self):
        result = AggregatedSentiment.aggregate([])
        self.assertEqual(result["sentiment"], "neutral")
        self.assertEqual(result["post_count"], 0)

    def test_aggregate_single_result(self):
        single_result = SentimentResult(
            sentiment="positive",
            vader_positive=Decimal("0.5"),
            vader_negative=Decimal("0.1"),
            vader_neutral=Decimal("0.4"),
            vader_compound=Decimal("0.4"),
            textblob_polarity=Decimal("0.3"),
            textblob_subjectivity=Decimal("0.5"),
            confidence=Decimal("0.8"),
            mentions=["AAPL"],
            hashtags=["stocks"],
        )
        result = AggregatedSentiment.aggregate([single_result])
        self.assertEqual(result["sentiment"], "positive")
        self.assertEqual(result["post_count"], 1)

    def test_aggregate_multiple_results(self):
        results = [
            SentimentResult(
                sentiment="positive",
                vader_positive=Decimal("0.5"),
                vader_negative=Decimal("0.1"),
                vader_neutral=Decimal("0.4"),
                vader_compound=Decimal("0.4"),
                textblob_polarity=Decimal("0.3"),
                textblob_subjectivity=Decimal("0.5"),
                confidence=Decimal("0.8"),
                mentions=["AAPL"],
                hashtags=["moon"],
            ),
            SentimentResult(
                sentiment="negative",
                vader_positive=Decimal("0.1"),
                vader_negative=Decimal("0.5"),
                vader_neutral=Decimal("0.4"),
                vader_compound=Decimal("-0.4"),
                textblob_polarity=Decimal("-0.3"),
                textblob_subjectivity=Decimal("0.5"),
                confidence=Decimal("0.7"),
                mentions=["AAPL"],
                hashtags=["crash"],
            ),
        ]
        result = AggregatedSentiment.aggregate(results)
        self.assertEqual(result["post_count"], 2)
        self.assertIn(result["sentiment"], ["positive", "negative", "mixed"])

    def test_calculate_weight(self):
        normal_post = {
            "followers_count": 500,
            "engagement_score": 50,
            "is_retweet": False,
        }
        high_influence_post = {
            "followers_count": 15000,
            "engagement_score": 2000,
            "is_retweet": False,
        }
        retweet_post = {
            "followers_count": 500,
            "engagement_score": 50,
            "is_retweet": True,
        }

        self.assertEqual(AggregatedSentiment.calculate_weight(normal_post), 1.0)
        self.assertEqual(
            AggregatedSentiment.calculate_weight(high_influence_post), 2.25
        )
        self.assertEqual(AggregatedSentiment.calculate_weight(retweet_post), 0.8)


class SentimentEdgeCasesTest(TestCase):
    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_empty_text(self):
        result = self.analyzer.analyze("")
        self.assertIsNotNone(result.sentiment)
        self.assertIsNotNone(result.vader_compound)

    def test_very_long_text(self):
        long_text = "This is great " * 1000 + " $AAPL"
        result = self.analyzer.analyze(long_text)
        self.assertIn("AAPL", result.mentions)

    def test_special_characters(self):
        text = "Check this out!!! $GME to the moon"
        result = self.analyzer.analyze(text)
        self.assertIsNotNone(result.sentiment)

    def test_ticker_only(self):
        text = "$AAPL"
        result = self.analyzer.analyze(text)
        self.assertIn("AAPL", result.mentions)
