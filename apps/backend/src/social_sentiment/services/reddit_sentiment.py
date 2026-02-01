"""
Reddit Sentiment Analysis Service
Fetches Reddit posts and analyzes sentiment using VADER
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import praw

    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    logger.warning("PRAW not installed. Install with: pip install praw")


class RedditSentimentAnalyzer:
    """Fetch and analyze Reddit sentiment for stocks."""

    SUBREDDITS = ["wallstreetbets", "stocks", "investing", "stockmarket", "options"]

    def __init__(self):
        if not REDDIT_AVAILABLE:
            self.reddit = None
            logger.warning("Reddit API not available - praw not installed")
            return

        from django.conf import settings

        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent="FinanceHub/1.0",
        )

    def fetch_posts(self, symbol: str, limit: int = 100, hours: int = 24) -> List[Dict]:
        """
        Fetch recent posts mentioning stock symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            limit: Number of posts to fetch
            hours: Lookback period in hours

        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API client not initialized")
            return []

        start_time = datetime.utcnow() - timedelta(hours=hours)
        start_timestamp = start_time.timestamp()

        posts = []

        try:
            for subreddit_name in self.SUBREDDITS:
                subreddit = self.reddit.subreddit(subreddit_name)

                for post in subreddit.search(symbol, limit=limit):
                    if post.created_utc >= start_timestamp:
                        posts.append(
                            {
                                "id": post.id,
                                "title": post.title,
                                "text": post.selftext,
                                "author": str(post.author)
                                if post.author
                                else "[deleted]",
                                "created_at": datetime.fromtimestamp(post.created_utc),
                                "score": post.score,
                                "upvotes": post.score,
                                "downvotes": 0,
                                "num_comments": post.num_comments,
                                "url": post.url,
                                "source": "reddit",
                                "subreddit": subreddit_name,
                            }
                        )

            return posts[:limit]

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return []

    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """
        Analyze sentiment of posts using VADER.

        Args:
            posts: List of post dictionaries

        Returns:
            Aggregated sentiment analysis results
        """
        from social_sentiment.services.sentiment_analysis import SentimentAnalyzer

        if not posts:
            return {
                "score": 0.0,
                "label": "neutral",
                "mention_count": 0,
                "posts": [],
                "source": "reddit",
            }

        analyzer = SentimentAnalyzer()
        analyzed_posts = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for post in posts:
            text = f"{post.get('title', '')} {post.get('text', '')}"
            result = analyzer.analyze(text)

            engagement = post.get("score", 0) + post.get("num_comments", 0)
            weight = max(1.0, engagement / 10)

            total_weighted_score += float(result.vader_compound) * weight
            total_weight += weight

            analyzed_posts.append(
                {
                    **post,
                    "sentiment_score": float(result.vader_compound),
                    "sentiment_label": result.sentiment,
                    "weight": weight,
                }
            )

        avg_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        return {
            "score": round(avg_score, 4),
            "label": self._get_label(avg_score),
            "mention_count": len(posts),
            "posts": analyzed_posts,
            "source": "reddit",
        }

    def calculate_sentiment(
        self, symbol: str, limit: int = 100, hours: int = 24
    ) -> Dict:
        """
        Fetch posts and calculate sentiment.

        Args:
            symbol: Stock symbol
            limit: Number of posts to fetch
            hours: Lookback period

        Returns:
            Sentiment analysis results for symbol
        """
        posts = self.fetch_posts(symbol, limit, hours)
        result = self.analyze_posts(posts)
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
        Get trending tickers from Reddit by analyzing post frequency.

        Returns:
            List of trending tickers with mention counts
        """
        if not self.reddit:
            return []

        trending = {}
        cutoff = datetime.utcnow() - timedelta(hours=24)

        try:
            for subreddit_name in self.SUBREDDITS:
                subreddit = self.reddit.subreddit(subreddit_name)

                for post in subreddit.new(limit=100):
                    if post.created_utc >= cutoff.timestamp():
                        from social_sentiment.services.sentiment_analysis import (
                            TickerDetector,
                        )

                        tickers = TickerDetector.extract_tickers(
                            f"{post.title} {post.selftext}"
                        )

                        for ticker in tickers:
                            if ticker not in trending:
                                trending[ticker] = {
                                    "symbol": ticker,
                                    "mention_count": 0,
                                    "subreddits": set(),
                                }
                            trending[ticker]["mention_count"] += 1
                            trending[ticker]["subreddits"].add(subreddit_name)

            result = [
                {
                    "symbol": data["symbol"],
                    "mention_count": data["mention_count"],
                    "subreddits": list(data["subreddits"]),
                }
                for data in trending.values()
            ]

            return sorted(result, key=lambda x: x["mention_count"], reverse=True)[
                :limit
            ]

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error getting Reddit trending: {e}")
            return []
