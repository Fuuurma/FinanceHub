"""
Twitter/X Sentiment Analysis Service
Fetches tweets and analyzes sentiment using VADER
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

try:
    import tweepy

    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    logger.warning("Tweepy not installed. Install with: pip install tweepy")


class TwitterSentimentAnalyzer:
    """Fetch and analyze Twitter/X sentiment for stocks."""

    SUBREDDITS = ["wallstreetbets", "stocks", "investing", "stockmarket"]

    def __init__(self):
        if not TWITTER_AVAILABLE:
            self.client = None
            logger.warning("Twitter API not available - tweepy not installed")
            return

        from django.conf import settings

        self.client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True,
        )

    def fetch_tweets(
        self, symbol: str, count: int = 100, hours: int = 24
    ) -> List[Dict]:
        """
        Fetch recent tweets mentioning stock symbol (cashtag).

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            count: Number of tweets to fetch
            hours: Lookback period in hours

        Returns:
            List of tweet dictionaries
        """
        if not self.client:
            logger.warning("Twitter API client not initialized")
            return []

        cashtag = f"${symbol}"
        start_time = datetime.utcnow() - timedelta(hours=hours)

        try:
            tweets = self.client.search_recent_tweets(
                query=cashtag,
                max_results=min(count, 100),
                start_time=start_time,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                expansions=["author_id"],
            )

            if not tweets.data:
                return []

            processed_tweets = []
            for tweet in tweets.data:
                metrics = tweet.public_metrics
                processed_tweets.append(
                    {
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "like_count": metrics.get("like_count", 0),
                        "retweet_count": metrics.get("retweet_count", 0),
                        "reply_count": metrics.get("reply_count", 0),
                        "quote_count": metrics.get("quote_count", 0),
                        "source": "twitter",
                    }
                )

            return processed_tweets

        except tweepy.errors.TooManyRequests:
            logger.warning("Twitter API rate limit exceeded")
            return []
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching tweets: {e}")
            return []

    def analyze_tweets(self, tweets: List[Dict]) -> Dict:
        """
        Analyze sentiment of tweets using VADER.

        Args:
            tweets: List of tweet dictionaries

        Returns:
            Aggregated sentiment analysis results
        """
        from social_sentiment.services.sentiment_analysis import (
            SentimentAnalyzer,
            TickerDetector,
        )

        if not tweets:
            return {
                "score": 0.0,
                "label": "neutral",
                "mention_count": 0,
                "tweets": [],
                "source": "twitter",
            }

        analyzer = SentimentAnalyzer()
        analyzed_tweets = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for tweet in tweets:
            result = analyzer.analyze(tweet["text"])
            engagement = (
                tweet.get("like_count", 0)
                + tweet.get("retweet_count", 0)
                + tweet.get("reply_count", 0)
            )
            weight = max(1.0, engagement / 10)

            total_weighted_score += float(result.vader_compound) * weight
            total_weight += weight

            analyzed_tweets.append(
                {
                    **tweet,
                    "sentiment_score": float(result.vader_compound),
                    "sentiment_label": result.sentiment,
                    "weight": weight,
                }
            )

        avg_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        return {
            "score": round(avg_score, 4),
            "label": self._get_label(avg_score),
            "mention_count": len(tweets),
            "tweets": analyzed_tweets,
            "source": "twitter",
        }

    def calculate_sentiment(
        self, symbol: str, count: int = 100, hours: int = 24
    ) -> Dict:
        """
        Fetch tweets and calculate sentiment.

        Args:
            symbol: Stock symbol
            count: Number of tweets to fetch
            hours: Lookback period

        Returns:
            Sentiment analysis results for symbol
        """
        tweets = self.fetch_tweets(symbol, count, hours)
        result = self.analyze_tweets(tweets)
        result["symbol"] = symbol
        return result

    def _get_label(self, score: float) -> str:
        """Convert score to sentiment label."""
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"

    def get_trending_tickers(self, limit: int = 20) -> List[Dict]:
        """
        Get trending tickers from Twitter.

        Note: This is a placeholder - Twitter API v2 requires
        expensive Enterprise API access for true trending.
        """
        logger.info("Twitter trending not implemented - requires Enterprise API")
        return []
