# 📋 Task Assignment: C-037 Social Sentiment Analysis

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Guido (Backend Coder)
**Priority:** HIGH - Phase 1 Core Feature
**Estimated Effort:** 10-14 hours backend
**Timeline:** Start immediately, quality-driven (no deadline)

---

## 🎯 OVERVIEW

You are assigned to **C-037: Social Sentiment Analysis** - backend development (lead).

**Collaborators:**
- **Turing (Frontend Coder):** Building sentiment visualization, social feed UI
- **GRACE (QA):** Creating test cases, validating sentiment accuracy
- **Charo (Security):** Social data privacy, rate limiting, API security
- **MIES (UI/UX):** Design mockups for sentiment interface
- **HADI (Accessibility):** WCAG 2.1 Level AA compliance

**Your Role:** Lead backend development for social sentiment analysis. Integrate Twitter & Reddit APIs, implement NLP sentiment analysis.

---

## 📋 YOUR TASKS

### Task 1: Sentiment Data Model (2h)
**File:** `apps/backend/src/social/models/sentiment.py`

**Requirements:**
```python
from django.db import models
from django.conf import settings
from assets.models import Asset

class SentimentData(models.Model):
    """Aggregated sentiment data for an asset"""
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='sentiment_data'
    )
    source = models.CharField(
        max_length=20,
        choices=[
            ('twitter', 'Twitter'),
            ('reddit', 'Reddit'),
            ('news', 'News'),
            ('aggregated', 'Aggregated')
        ]
    )
    sentiment_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="-1.0 (bearish) to 1.0 (bullish)"
    )
    sentiment_label = models.CharField(
        max_length=10,
        choices=[
            ('bullish', 'Bullish'),
            ('bearish', 'Bearish'),
            ('neutral', 'Neutral')
        ]
    )
    mention_count = models.IntegerField(
        default=0,
        help_text="Number of mentions in this period"
    )
    volume_change = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Change vs previous period (as percentage)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sentiment_data'
        verbose_name = 'Sentiment Data'
        verbose_name_plural = 'Sentiment Data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['source', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        unique_together = [['asset', 'source', 'timestamp']]
    
    def __str__(self):
        return f"{self.asset.symbol} {self.source}: {self.sentiment_label} ({self.sentiment_score})"
    
    def calculate_label(self):
        """Determine sentiment label from score"""
        if self.sentiment_score >= 0.3:
            self.sentiment_label = 'bullish'
        elif self.sentiment_score <= -0.3:
            self.sentiment_label = 'bearish'
        else:
            self.sentiment_label = 'neutral'
        self.save()
```

**Tasks:**
- [ ] Create `SentimentData` model
- [ ] Add indexes for fast queries
- [ ] Add `calculate_label()` method
- [ ] Create database migration
- [ ] Run migration

---

### Task 2: Twitter Sentiment Integration (3h)
**File:** `apps/backend/src/social/services/twitter_sentiment.py`

**Requirements:**
```python
import tweepy
from datetime import datetime, timedelta
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.conf import settings

class TwitterSentimentAnalyzer:
    """Fetch and analyze Twitter sentiment for stocks"""
    
    def __init__(self):
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Initialize sentiment analyzer
        self.analyzer = SentimentIntensityAnalyzer()
    
    def fetch_tweets(self, symbol, count=100, hours=24):
        """
        Fetch recent tweets mentioning stock symbol (cashtag)
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            count: Number of tweets to fetch
            hours: Lookback period in hours
            
        Returns:
            List of tweet objects
        """
        cashtag = f"${symbol}"
        
        # Calculate start time
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            # Search for tweets with cashtag
            tweets = self.client.search_recent_tweets(
                query=cashtag,
                max_results=min(count, 100),
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                return []
            
            # Process tweets
            processed_tweets = []
            for tweet in tweets.data:
                processed_tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'metrics': tweet.public_metrics,
                    'source': 'twitter'
                })
            
            return processed_tweets
            
        except tweepy.Errors.TooManyRequests:
            # Rate limit exceeded
            print("Twitter API rate limit exceeded. Waiting...")
            return []
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def analyze_sentiment(self, tweets):
        """
        Analyze sentiment of tweets using VADER
        
        Args:
            tweets: List of tweet objects
            
        Returns:
            Aggregated sentiment score and label
        """
        if not tweets:
            return {
                'score': 0.0,
                'label': 'neutral',
                'mention_count': 0,
                'tweets': []
            }
        
        # Analyze each tweet
        analyzed_tweets = []
        total_score = 0.0
        
        for tweet in tweets:
            # Get sentiment score using VADER
            # VADER returns compound score: -1 (negative) to 1 (positive)
            scores = self.analyzer.polarity_scores(tweet['text'])
            compound_score = scores['compound']
            
            # Weight by engagement (likes + retweets)
            engagement = tweet['metrics']['like_count'] + tweet['metrics']['retweet_count']
            weight = max(1, engagement / 10)  # Minimum weight of 1
            
            weighted_score = compound_score * weight
            total_score += weighted_score
            
            analyzed_tweets.append({
                **tweet,
                'sentiment_score': compound_score,
                'sentiment_label': self._get_label(compound_score),
                'weight': weight
            })
        
        # Calculate weighted average
        avg_score = total_score / len(tweets) if tweets else 0.0
        
        return {
            'score': avg_score,
            'label': self._get_label(avg_score),
            'mention_count': len(tweets),
            'tweets': analyzed_tweets
        }
    
    def _get_label(self, score):
        """Convert score to label"""
        if score >= 0.3:
            return 'bullish'
        elif score <= -0.3:
            return 'bearish'
        else:
            return 'neutral'
    
    def calculate_sentiment(self, symbol, count=100, hours=24):
        """
        Fetch tweets and calculate sentiment
        
        Returns:
            {
                'symbol': 'AAPL',
                'source': 'twitter',
                'sentiment_score': 0.45,
                'sentiment_label': 'bullish',
                'mention_count': 87,
                'tweets': [...]
            }
        """
        tweets = self.fetch_tweets(symbol, count, hours)
        return {
            'symbol': symbol,
            'source': 'twitter',
            **self.analyze_sentiment(tweets)
        }
```

**Tasks:**
- [ ] Set up Twitter API credentials (request from user)
- [ ] Install dependencies: `tweepy`, `vaderSentiment`
- [ ] Create `TwitterSentimentAnalyzer` class
- [ ] Implement `fetch_tweets()` method
- [ ] Implement `analyze_sentiment()` method with VADER
- [ ] Add engagement weighting (likes + retweets)
- [ ] Handle rate limiting gracefully
- [ ] Test with real Twitter data
- [ ] Document API limits and costs

**Twitter API Cost:**
- Free tier: 500,000 tweets/month (approximately)
- Paid tier: $100/month for 10,000 tweets/month
- Rate limiting: 300 requests per 15 minutes (v2)

---

### Task 3: Reddit Sentiment Integration (3h)
**File:** `apps/backend/src/social/services/reddit_sentiment.py`

**Requirements:**
```python
import praw
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.conf import settings

class RedditSentimentAnalyzer:
    """Fetch and analyze Reddit sentiment for stocks"""
    
    def __init__(self):
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.user_agent = 'FinanceHub/1.0'
        
        # Initialize Reddit API
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
        # Initialize sentiment analyzer
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Subreddits to monitor
        self.subreddets = ['wallstreetbets', 'stocks', 'investing', 'stockmarket']
    
    def fetch_posts(self, symbol, limit=100, hours=24):
        """
        Fetch recent posts mentioning stock symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            limit: Number of posts to fetch
            hours: Lookback period in hours
            
        Returns:
            List of post objects
        """
        # Calculate start time
        start_time = datetime.utcnow() - timedelta(hours=hours)
        start_timestamp = start_time.timestamp()
        
        posts = []
        
        try:
            # Search in each subreddit
            for subreddit_name in self.subreddets:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for symbol
                for post in subreddit.search(symbol, limit=limit):
                    # Check if post is within time window
                    if post.created_utc >= start_timestamp:
                        posts.append({
                            'id': post.id,
                            'title': post.title,
                            'text': post.selftext,
                            'author': str(post.author),
                            'created_at': datetime.fromtimestamp(post.created_utc),
                            'score': post.score,  # Upvotes - downvotes
                            'num_comments': post.num_comments,
                            'url': post.url,
                            'source': 'reddit',
                            'subreddit': subreddit_name
                        })
            
            return posts[:limit]  # Limit to requested count
            
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            return []
    
    def analyze_sentiment(self, posts):
        """
        Analyze sentiment of posts using VADER
        
        Args:
            posts: List of post objects
            
        Returns:
            Aggregated sentiment score and label
        """
        if not posts:
            return {
                'score': 0.0,
                'label': 'neutral',
                'mention_count': 0,
                'posts': []
            }
        
        # Analyze each post (title + text)
        analyzed_posts = []
        total_score = 0.0
        
        for post in posts:
            # Combine title and text for analysis
            text = f"{post['title']} {post['text']}"
            
            # Get sentiment score using VADER
            scores = self.analyzer.polarity_scores(text)
            compound_score = scores['compound']
            
            # Weight by upvotes and comments
            engagement = post['score'] + post['num_comments']
            weight = max(1, engagement / 10)  # Minimum weight of 1
            
            weighted_score = compound_score * weight
            total_score += weighted_score
            
            analyzed_posts.append({
                **post,
                'sentiment_score': compound_score,
                'sentiment_label': self._get_label(compound_score),
                'weight': weight
            })
        
        # Calculate weighted average
        avg_score = total_score / len(posts) if posts else 0.0
        
        return {
            'score': avg_score,
            'label': self._get_label(avg_score),
            'mention_count': len(posts),
            'posts': analyzed_posts
        }
    
    def _get_label(self, score):
        """Convert score to label"""
        if score >= 0.3:
            return 'bullish'
        elif score <= -0.3:
            return 'bearish'
        else:
            return 'neutral'
    
    def calculate_sentiment(self, symbol, limit=100, hours=24):
        """
        Fetch posts and calculate sentiment
        
        Returns:
            {
                'symbol': 'AAPL',
                'source': 'reddit',
                'sentiment_score': 0.32,
                'sentiment_label': 'bullish',
                'mention_count': 45,
                'posts': [...]
            }
        """
        posts = self.fetch_posts(symbol, limit, hours)
        return {
            'symbol': symbol,
            'source': 'reddit',
            **self.analyze_sentiment(posts)
        }
```

**Tasks:**
- [ ] Set up Reddit API credentials (create app at reddit.com/prefs/apps)
- [ ] Install dependencies: `praw`, `vaderSentiment`
- [ ] Create `RedditSentimentAnalyzer` class
- [ ] Implement `fetch_posts()` method
- [ ] Implement `analyze_sentiment()` method with VADER
- [ ] Add engagement weighting (upvotes + comments)
- [ ] Test with real Reddit data
- [ ] Document API limits and costs

**Reddit API Cost:**
- Free tier: 60 requests per minute
- No monthly limit
- Requires API key (free)

---

### Task 4: Sentiment Aggregation Service (2h)
**File:** `apps/backend/src/social/services/sentiment_aggregator.py`

**Requirements:**
```python
from typing import Dict, List
from .twitter_sentiment import TwitterSentimentAnalyzer
from .reddit_sentiment import RedditSentimentAnalyzer

class SentimentAggregator:
    """Aggregate sentiment from multiple sources"""
    
    def __init__(self):
        self.twitter_analyzer = TwitterSentimentAnalyzer()
        self.reddit_analyzer = RedditSentimentAnalyzer()
        
        # Source weights (must sum to 1.0)
        self.source_weights = {
            'twitter': 0.40,
            'reddit': 0.40,
            'news': 0.20  # Future: news sentiment
        }
    
    def aggregate_sentiment(self, symbol, hours=24):
        """
        Aggregate sentiment from all sources
        
        Args:
            symbol: Stock symbol
            hours: Lookback period
            
        Returns:
            {
                'symbol': 'AAPL',
                'sentiment_score': 0.38,
                'sentiment_label': 'bullish',
                'mention_count': 132,
                'sources': {
                    'twitter': {'score': 0.45, 'label': 'bullish', 'count': 87},
                    'reddit': {'score': 0.32, 'label': 'bullish', 'count': 45}
                },
                'trend': 'improving'  # vs previous period
            }
        """
        # Fetch sentiment from all sources
        sources = {}
        total_weighted_score = 0.0
        total_mention_count = 0
        
        # Twitter
        twitter_sentiment = self.twitter_analyzer.calculate_sentiment(symbol, count=100, hours=hours)
        sources['twitter'] = {
            'score': twitter_sentiment['score'],
            'label': twitter_sentiment['label'],
            'count': twitter_sentiment['mention_count']
        }
        total_weighted_score += twitter_sentiment['score'] * self.source_weights['twitter']
        total_mention_count += twitter_sentiment['mention_count']
        
        # Reddit
        reddit_sentiment = self.reddit_analyzer.calculate_sentiment(symbol, limit=100, hours=hours)
        sources['reddit'] = {
            'score': reddit_sentiment['score'],
            'label': reddit_sentiment['label'],
            'count': reddit_sentiment['mention_count']
        }
        total_weighted_score += reddit_sentiment['score'] * self.source_weights['reddit']
        total_mention_count += reddit_sentiment['mention_count']
        
        # Calculate aggregated sentiment
        aggregated_score = total_weighted_score / (self.source_weights['twitter'] + self.source_weights['reddit'])
        aggregated_label = self._get_label(aggregated_score)
        
        # Calculate trend (vs previous period)
        trend = self._calculate_trend(symbol, hours)
        
        # Calculate volume change (vs previous period)
        volume_change = self._calculate_volume_change(symbol, hours, total_mention_count)
        
        return {
            'symbol': symbol,
            'sentiment_score': aggregated_score,
            'sentiment_label': aggregated_label,
            'mention_count': total_mention_count,
            'volume_change': volume_change,
            'sources': sources,
            'trend': trend
        }
    
    def _get_label(self, score):
        """Convert score to label"""
        if score >= 0.3:
            return 'bullish'
        elif score <= -0.3:
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_trend(self, symbol, current_hours):
        """
        Calculate sentiment trend (improving/worsening/stable)
        by comparing current period to previous period
        """
        from ..models import SentimentData
        
        # Get current sentiment (already calculated)
        current_data = SentimentData.objects.filter(
            asset__symbol__iexact=symbol,
            source='aggregated'
        ).order_by('-timestamp').first()
        
        if not current_data:
            return 'stable'
        
        # Get previous period sentiment
        previous_data = SentimentData.objects.filter(
            asset__symbol__iexact=symbol,
            source='aggregated',
            timestamp__lt=current_data.timestamp
        ).order_by('-timestamp').first()
        
        if not previous_data:
            return 'stable'
        
        # Compare scores
        if current_data.sentiment_score > previous_data.sentiment_score + 0.1:
            return 'improving'
        elif current_data.sentiment_score < previous_data.sentiment_score - 0.1:
            return 'worsening'
        else:
            return 'stable'
    
    def _calculate_volume_change(self, symbol, hours, current_count):
        """Calculate mention volume change vs previous period"""
        from ..models import SentimentData
        
        # Get previous period data
        previous_data = SentimentData.objects.filter(
            asset__symbol__iexact=symbol,
            source='aggregated'
        ).order_by('-timestamp')[1:2]  # Second-most recent
        
        if not previous_data:
            return None
        
        previous_count = previous_data[0].mention_count
        
        if previous_count == 0:
            return None
        
        # Calculate percentage change
        change = ((current_count - previous_count) / previous_count) * 100
        return change
```

**Tasks:**
- [ ] Create `SentimentAggregator` class
- [ ] Implement `aggregate_sentiment()` method
- [ ] Add source weighting (Twitter: 40%, Reddit: 40%, News: 20%)
- [ ] Implement `_calculate_trend()` method
- [ ] Implement `_calculate_volume_change()` method
- [ ] Add caching (5-minute TTL)
- [ ] Test aggregation logic

---

### Task 5: API Endpoints (2h)
**File:** `apps/backend/src/social/api/sentiment.py`

**Requirements:**
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from assets.models import Asset

from ..services.sentiment_aggregator import SentimentAggregator
from ..models import SentimentData
from ..serializers import SentimentDataSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sentiment(request, symbol):
    """
    Get current sentiment for asset
    
    GET /api/sentiment/AAPL/
    """
    asset = get_object_or_404(Asset, symbol__iexact=symbol)
    aggregator = SentimentAggregator()
    
    # Get aggregated sentiment
    sentiment = aggregator.aggregate_sentiment(symbol)
    
    return Response(sentiment)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sentiment_history(request, symbol):
    """
    Get sentiment history for asset
    
    GET /api/sentiment/AAPL/history/?period=24h
    
    Periods: 24h, 7d, 30d
    """
    asset = get_object_or_404(Asset, symbol__iexact=symbol)
    
    # Get period from query params
    period = request.query_params.get('period', '24h')
    
    # Calculate time range
    from datetime import datetime, timedelta
    if period == '24h':
        start_time = datetime.now() - timedelta(hours=24)
        interval_minutes = 30  # 30-minute intervals
    elif period == '7d':
        start_time = datetime.now() - timedelta(days=7)
        interval_minutes = 240  # 4-hour intervals
    elif period == '30d':
        start_time = datetime.now() - timedelta(days=30)
        interval_minutes = 1440  # Daily intervals
    else:
        return Response({'error': 'Invalid period'}, status=400)
    
    # Get sentiment data
    sentiment_data = SentimentData.objects.filter(
        asset=asset,
        timestamp__gte=start_time
    ).order_by('timestamp')
    
    # Format response
    history = []
    for data in sentiment_data:
        history.append({
            'timestamp': data.timestamp,
            'sentiment_score': float(data.sentiment_score),
            'sentiment_label': data.sentiment_label,
            'mention_count': data.mention_count
        })
    
    return Response({
        'symbol': symbol,
        'period': period,
        'history': history
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trending_assets(request):
    """
    Get trending assets by mention volume
    
    GET /api/sentiment/trending/?limit=20
    """
    limit = int(request.query_params.get('limit', 20))
    
    # Get most mentioned assets in last 24 hours
    from datetime import datetime, timedelta
    start_time = datetime.now() - timedelta(hours=24)
    
    trending = SentimentData.objects.filter(
        source='aggregated',
        timestamp__gte=start_time
    ).order_by('-mention_count')[:limit]
    
    # Format response
    assets = []
    for data in trending:
        assets.append({
            'symbol': data.asset.symbol,
            'sentiment_score': float(data.sentiment_score),
            'sentiment_label': data.sentiment_label,
            'mention_count': data.mention_count,
            'volume_change': float(data.volume_change) if data.volume_change else None
        })
    
    return Response({
        'trending': assets,
        'timestamp': datetime.now()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_social_feed(request, symbol):
    """
    Get social feed (tweets, Reddit posts) for asset
    
    GET /api/sentiment/AAPL/feed/?source=all&limit=50
    
    Sources: all, twitter, reddit
    """
    asset = get_object_or_404(Asset, symbol__iexact=symbol)
    
    # Get source filter
    source = request.query_params.get('source', 'all')
    limit = int(request.query_params.get('limit', 50))
    
    aggregator = SentimentAggregator()
    sentiment = aggregator.aggregate_sentiment(symbol)
    
    # Filter feed items
    feed_items = []
    
    if source in ['all', 'twitter']:
        twitter_data = sentiment['sources'].get('twitter', {})
        if 'tweets' in twitter_data:
            for tweet in twitter_data['tweets'][:limit]:
                feed_items.append({
                    'id': f"twitter_{tweet['id']}",
                    'source': 'twitter',
                    'author': tweet.get('author', 'Unknown'),
                    'content': tweet['text'],
                    'timestamp': tweet['created_at'],
                    'sentiment_score': tweet['sentiment_score'],
                    'sentiment_label': tweet['sentiment_label'],
                    'url': tweet.get('url', f"https://twitter.com/i/status/{tweet['id']}")
                })
    
    if source in ['all', 'reddit']:
        reddit_data = sentiment['sources'].get('reddit', {})
        if 'posts' in reddit_data:
            for post in reddit_data['posts'][:limit]:
                feed_items.append({
                    'id': f"reddit_{post['id']}",
                    'source': 'reddit',
                    'author': post['author'],
                    'content': f"{post['title']}\n\n{post['text']}",
                    'timestamp': post['created_at'],
                    'sentiment_score': post['sentiment_score'],
                    'sentiment_label': post['sentiment_label'],
                    'url': post['url']
                })
    
    # Sort by timestamp
    feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response({
        'symbol': symbol,
        'feed': feed_items[:limit]
    })
```

**Tasks:**
- [ ] Create `/api/sentiment/{symbol}/` endpoint
- [ ] Create `/api/sentiment/{symbol}/history/` endpoint
- [ ] Create `/api/sentiment/trending/` endpoint
- [ ] Create `/api/sentiment/{symbol}/feed/` endpoint
- [ ] Add permission classes
- [ ] Add caching headers (5-minute cache)
- [ ] Add URL routing
- [ ] Test all endpoints

---

### Task 6: Background Tasks (2h)
**File:** `apps/backend/src/social/tasks/sentiment_tasks.py`

**Requirements:**
```python
from celery import shared_task
from datetime import datetime, timedelta
from assets.models import Asset

from ..services.sentiment_aggregator import SentimentAggregator
from ..models import SentimentData

@shared_task
def update_sentiment_data():
    """
    Update sentiment data for all tracked assets
    Runs every 5 minutes
    """
    aggregator = SentimentAggregator()
    
    # Get all assets (or limit to most popular)
    assets = Asset.objects.filter(
        is_active=True
    )[:100]  # Limit to top 100 assets
    
    for asset in assets:
        try:
            # Get aggregated sentiment
            sentiment = aggregator.aggregate_sentiment(asset.symbol, hours=24)
            
            # Save to database
            SentimentData.objects.create(
                asset=asset,
                source='aggregated',
                sentiment_score=sentiment['sentiment_score'],
                sentiment_label=sentiment['sentiment_label'],
                mention_count=sentiment['mention_count'],
                volume_change=sentiment.get('volume_change')
            )
            
            print(f"Updated sentiment for {asset.symbol}")
            
        except Exception as e:
            print(f"Error updating sentiment for {asset.symbol}: {e}")
    
    return f"Updated sentiment for {len(assets)} assets"

@shared_task
def calculate_trending_assets():
    """
    Calculate most mentioned assets
    Runs every 15 minutes
    """
    from datetime import datetime, timedelta
    
    # Get assets with most mentions in last 24 hours
    start_time = datetime.now() - timedelta(hours=24)
    
    trending = SentimentData.objects.filter(
        source='aggregated',
        timestamp__gte=start_time
    ).order_by('-mention_count')[:20]
    
    # Cache result (using Django cache)
    from django.core.cache import cache
    cache.set('trending_assets', list(trending), 900)  # 15 minutes
    
    return f"Calculated {len(trending)} trending assets"
```

**Tasks:**
- [ ] Create `update_sentiment_data()` Celery task
- [ ] Create `calculate_trending_assets()` Celery task
- [ ] Add error handling and retry logic
- [ ] Set up periodic tasks (Celery Beat):
  - `update_sentiment_data`: every 5 minutes
  - `calculate_trending_assets`: every 15 minutes
- [ ] Test background tasks
- [ ] Monitor task execution

**Celery Configuration:**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'update-sentiment': {
        'task': 'social.tasks.update_sentiment_data',
        'schedule': 300.0,  # 5 minutes
    },
    'calculate-trending': {
        'task': 'social.tasks.calculate_trending_assets',
        'schedule': 900.0,  # 15 minutes
    },
}
```

---

## ✅ ACCEPTANCE CRITERIA

Your backend work is complete when:

- [ ] `SentimentData` model created and migrated
- [ ] `TwitterSentimentAnalyzer` implements all methods
- [ ] `RedditSentimentAnalyzer` implements all methods
- [ ] `SentimentAggregator` implements all methods
- [ ] All API endpoints working
- [ ] Celery tasks created and scheduled
- [ ] Sentiment accuracy > 75% (validated by GRACE)
- [ ] Rate limiting handled gracefully
- [ ] All methods have error handling
- [ ] API has proper caching (5-minute TTL)
- [ ] Zero security vulnerabilities (validated by Charo)
- [ ] Social data privacy compliant (validated by Charo)

---

## 📊 SUCCESS METRICS

- API response time < 500ms (p95)
- Sentiment updates every 5 minutes
- Sentiment accuracy > 75% (vs manual analysis)
- Handle 100+ assets without performance degradation
- 100% test coverage for analyzers
- Rate limit errors < 1% of requests

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Create branch:** `feature/c-037-social-sentiment-backend`
2. **Request API keys:** Twitter API, Reddit API
3. **Install dependencies:** `tweepy`, `praw`, `vaderSentiment`
4. **Create models:** SentimentData
5. **Contact Turing:** Coordinate API integration

### This Week
1. **Build analyzers:** Twitter and Reddit analyzers
2. **Build aggregator:** Combine sources
3. **Create API:** All endpoints working
4. **Set up Celery:** Background tasks scheduled
5. **Write tests:** Unit tests for analyzers
6. **Coordinate with Turing:** Frontend integration

### Next Week
1. **Security review:** Charo will audit code
2. **Accuracy testing:** GRACE will validate sentiment accuracy
3. **Performance optimization:** Cache tuning
4. **Bug fixes:** Address issues from QA
5. **Documentation:** Document API endpoints

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- Turing: Frontend progress, API questions
- GRACE: Testing status, accuracy validation
- Charo: Security review feedback

**Weekly Updates:**
- Report progress to GAUDÍ (Architect)
- Flag blockers immediately

**Ask for help:**
- Twitter API setup → ARIA (coordination)
- Reddit API setup → ARIA (coordination)
- Security questions → Charo
- Performance issues → ARIA
- Testing failures → GRACE

---

## 🔄 COORDINATION WITH TURING

**Turing needs:**
1. API endpoints (provide URL documentation)
2. Request/response formats (provide examples)
3. Update frequency (5 minutes)
4. WebSocket (not needed for sentiment, polling is fine)

**Before Turing starts:**
- [ ] All API endpoints working
- [ ] API documentation complete
- [ ] Test data available
- [ ] Background tasks running

**During development:**
- Daily sync with Turing
- Provide API updates immediately
- Fix API bugs quickly

---

## 🔐 SECURITY CONSIDERATIONS

**API Keys:**
- Store Twitter API keys in environment variables
- Store Reddit API keys in environment variables
- Never commit keys to repository
- Use Django's `django-environ` for secrets management

**Data Privacy:**
- Don't store PII from social media
- Don't store user handles/usernames (anonymize)
- Comply with Twitter/Reddit ToS
- Implement rate limiting to prevent abuse

**Rate Limiting:**
- Twitter: 300 requests per 15 minutes
- Reddit: 60 requests per minute
- Implement backoff logic
- Cache results aggressively

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, quality-driven
**Collaborators:** Turing (FE), GRACE (QA), Charo (Security)

---

🐦 *Guido - Backend Coder*

📊 *Focus: C-037 Social Sentiment Analysis*

*"Quality over speed. The details matter."*
