"""
Celery Tasks for Social Sentiment Analysis
Background tasks for periodic sentiment updates
"""

import logging
from celery import shared_task
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_sentiment_data(self):
    """
    Update sentiment data for all tracked assets.
    Runs every 5 minutes.
    """
    try:
        from social_sentiment.services.sentiment_analysis import SentimentAnalyzer
        from social_sentiment.services.twitter_sentiment import TwitterSentimentAnalyzer
        from social_sentiment.services.reddit_sentiment import RedditSentimentAnalyzer
        from social_sentiment.models import SentimentAnalysis, SocialPost, TickerMention
        from assets.models import Asset

        aggregator = SentimentAnalyzer()
        twitter_analyzer = TwitterSentimentAnalyzer()
        reddit_analyzer = RedditSentimentAnalyzer()

        assets = Asset.objects.filter(is_active=True)[:100]
        updated_count = 0

        for asset in assets:
            try:
                symbol = asset.symbol.upper()

                twitter_sentiment = twitter_analyzer.calculate_sentiment(
                    symbol, count=100, hours=24
                )
                reddit_sentiment = reddit_analyzer.calculate_sentiment(
                    symbol, limit=100, hours=24
                )

                combined_score = (
                    twitter_sentiment.get("score", 0) * 0.4
                    + reddit_sentiment.get("score", 0) * 0.4
                )

                total_mentions = twitter_sentiment.get(
                    "mention_count", 0
                ) + reddit_sentiment.get("mention_count", 0)

                TickerMention.objects.update_or_create(
                    ticker=symbol,
                    source="combined",
                    period_start=datetime.utcnow().replace(
                        minute=0, second=0, microsecond=0
                    ),
                    period_end=datetime.utcnow().replace(
                        minute=59, second=59, microsecond=999999
                    ),
                    defaults={
                        "mention_count": total_mentions,
                        "avg_sentiment": combined_score,
                        "sentiment_change": 0.0,
                        "total_engagement": 0,
                    },
                )

                updated_count += 1
                logger.info(f"Updated sentiment for {symbol}")

            except Exception as e:
                logger.error(f"Error updating sentiment for {asset.symbol}: {e}")

        return f"Updated sentiment for {updated_count} assets"

    except Exception as e:
        logger.error(f"Sentiment update task failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_trending_assets(self):
    """
    Calculate most mentioned assets.
    Runs every 15 minutes.
    """
    try:
        from social_sentiment.models import TickerMention
        from django.core.cache import cache

        cutoff = datetime.utcnow() - timedelta(hours=24)

        trending = TickerMention.objects.filter(
            period_start__gte=cutoff,
            source="combined",
        ).order_by("-mention_count")[:20]

        trending_data = [
            {
                "symbol": t.ticker,
                "mention_count": t.mention_count,
                "sentiment_score": t.avg_sentiment,
                "sentiment_change": t.sentiment_change,
            }
            for t in trending
        ]

        cache.set("trending_assets", trending_data, 900)

        return f"Calculated {len(trending_data)} trending assets"

    except Exception as e:
        logger.error(f"Trending calculation failed: {e}")
        raise self.retry(exc=e)


@shared_task
def fetch_twitter_sentiment(symbol: str):
    """
    Fetch and store Twitter sentiment for a specific symbol.
    """
    try:
        from social_sentiment.services.twitter_sentiment import TwitterSentimentAnalyzer
        from social_sentiment.models import SocialPost, SentimentAnalysis
        from social_sentiment.services.sentiment_analysis import SentimentAnalyzer

        twitter_analyzer = TwitterSentimentAnalyzer()
        sentiment_analyzer = SentimentAnalyzer()

        tweets = twitter_analyzer.fetch_tweets(symbol, count=100, hours=24)

        for tweet in tweets:
            post, created = SocialPost.objects.update_or_create(
                post_id=f"twitter_{tweet['id']}",
                defaults={
                    "source": "twitter",
                    "symbol": symbol,
                    "author": "twitter_user",
                    "content": tweet["text"],
                    "url": f"https://twitter.com/i/status/{tweet['id']}",
                    "followers_count": 0,
                    "engagement_score": tweet.get("like_count", 0)
                    + tweet.get("retweet_count", 0),
                    "posted_at": tweet["created_at"],
                    "upvotes": tweet.get("like_count", 0),
                    "downvotes": 0,
                    "comments": tweet.get("reply_count", 0),
                    "shares": tweet.get("retweet_count", 0),
                },
            )

            if created or not SentimentAnalysis.objects.filter(post=post).exists():
                result = sentiment_analyzer.analyze(tweet["text"])
                SentimentAnalysis.objects.create(
                    post=post,
                    symbol=symbol,
                    source="twitter",
                    sentiment=result.sentiment,
                    vader_compound=result.vader_compound,
                    vader_positive=result.vader_positive,
                    vader_negative=result.vader_negative,
                    vader_neutral=result.vader_neutral,
                    textblob_polarity=result.textblob_polarity,
                    textblob_subjectivity=result.textblob_subjectivity,
                    weighted_sentiment=result.confidence,
                    confidence=result.confidence,
                    mentions=result.mentions,
                    hashtags=result.hashtags,
                )

        return f"Fetched {len(tweets)} tweets for {symbol}"

    except Exception as e:
        logger.error(f"Twitter fetch failed for {symbol}: {e}")
        return f"Error: {e}"


@shared_task
def fetch_reddit_sentiment(symbol: str):
    """
    Fetch and store Reddit sentiment for a specific symbol.
    """
    try:
        from social_sentiment.services.reddit_sentiment import RedditSentimentAnalyzer
        from social_sentiment.models import SocialPost, SentimentAnalysis
        from social_sentiment.services.sentiment_analysis import SentimentAnalyzer

        reddit_analyzer = RedditSentimentAnalyzer()
        sentiment_analyzer = SentimentAnalyzer()

        posts = reddit_analyzer.fetch_posts(symbol, limit=100, hours=24)

        for post in posts:
            social_post, created = SocialPost.objects.update_or_create(
                post_id=f"reddit_{post['id']}",
                defaults={
                    "source": "reddit",
                    "symbol": symbol,
                    "author": post["author"],
                    "content": f"{post['title']}\n\n{post['text']}",
                    "url": post["url"],
                    "followers_count": 0,
                    "engagement_score": post.get("score", 0)
                    + post.get("num_comments", 0),
                    "posted_at": post["created_at"],
                    "upvotes": post.get("upvotes", 0),
                    "downvotes": 0,
                    "comments": post.get("num_comments", 0),
                    "shares": 0,
                },
            )

            if (
                created
                or not SentimentAnalysis.objects.filter(post=social_post).exists()
            ):
                text = f"{post.get('title', '')} {post.get('text', '')}"
                result = sentiment_analyzer.analyze(text)
                SentimentAnalysis.objects.create(
                    post=social_post,
                    symbol=symbol,
                    source="reddit",
                    sentiment=result.sentiment,
                    vader_compound=result.vader_compound,
                    vader_positive=result.vader_positive,
                    vader_negative=result.vader_negative,
                    vader_neutral=result.vader_neutral,
                    textblob_polarity=result.textblob_polarity,
                    textblob_subjectivity=result.textblob_subjectivity,
                    weighted_sentiment=result.confidence,
                    confidence=result.confidence,
                    mentions=result.mentions,
                    hashtags=result.hashtags,
                )

        return f"Fetched {len(posts)} posts for {symbol}"

    except Exception as e:
        logger.error(f"Reddit fetch failed for {symbol}: {e}")
        return f"Error: {e}"


@shared_task
def clean_old_sentiment_data():
    """
    Clean old sentiment data to prevent database bloat.
    Runs daily.
    """
    from social_sentiment.models import SentimentAnalysis, SocialPost, TickerMention
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=30)

    deleted_analyses = SentimentAnalysis.objects.filter(created_at__lt=cutoff).delete()

    deleted_posts = SocialPost.objects.filter(created_at__lt=cutoff).delete()

    deleted_mentions = TickerMention.objects.filter(period_start__lt=cutoff).delete()

    return f"Deleted {deleted_analyses[0]} analyses, {deleted_posts[0]} posts, {deleted_mentions[0]} mentions"


def setup_celery_beat_schedule():
    """
    Configure Celery Beat schedule for sentiment tasks.
    Call this from settings.py or apps.py
    """
    from celery import current_app

    current_app.conf.beat_schedule = {
        "update-sentiment-every-5-minutes": {
            "task": "social_sentiment.tasks.update_sentiment_data",
            "schedule": 300.0,
        },
        "calculate-trending-every-15-minutes": {
            "task": "social_sentiment.tasks.calculate_trending_assets",
            "schedule": 900.0,
        },
        "clean-old-data-daily": {
            "task": "social_sentiment.tasks.clean_old_sentiment_data",
            "schedule": 86400.0,
        },
    }

    return current_app.conf.beat_schedule
