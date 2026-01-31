# Task C-037: Social Sentiment Analysis

**Priority:** P1 HIGH  
**Estimated Time:** 18-24 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Setup (Step 1):** Get API keys (30m) - Twitter, Reddit, StockTwits
2. **Backend (Step 2):** Create models (2h) - SentimentScore, SocialMention
3. **Backend (Step 3):** Create sentiment analyzer (3h) - VADER + TextBlob
4. **Backend (Step 4):** Create Twitter scraper (3h) - API v2 integration
5. **Backend (Step 5):** Create Reddit scraper (2h) - PRAW integration
6. **Backend (Step 6):** Create aggregation service (2h) - Combine sources
7. **Backend (Step 7):** Create API endpoints (2h) - 5 REST endpoints
8. **Frontend (Step 8):** Create sentiment gauge (1h) - Visual indicator
9. **Frontend (Step 9):** Create sentiment chart (1h) - Historical trend
10. **Frontend (Step 10):** Create sentiment dashboard (1h) - Aggregation page

**Total: 17.5 hours (estimate)**

---

## Overview
Implement social sentiment analysis by aggregating and analyzing data from Twitter, Reddit, and other social platforms to provide trading insights based on public sentiment.

## User Story
As a trader, I want to see social sentiment indicators for assets so I can gauge market sentiment and make more informed trading decisions based on public opinion.

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Get API Keys (30 minutes) ⚠️ REQUIRED FIRST

**Twitter API v2:**
1. Go to: https://developer.twitter.com/
2. Create developer account
3. Create new app
4. Get Bearer Token
5. Add to `.env`: `TWITTER_BEARER_TOKEN=your_token_here`

**Reddit API:**
1. Go to: https://www.reddit.com/prefs/apps
2. Create new app (script type)
3. Get Client ID and Secret
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=finance-hub/1.0
   ```

**StockTwits API:**
1. Go to: https://stocktwits.com/developers
2. Create new app
3. Get API Key
4. Add to `.env`: `STOCKTWITS_API_KEY=your_key_here`

---

### STEP 2: Create Database Models (2 hours)

**File:** `apps/backend/src/sentiment/models/__init__.py`

```python
from .sentiment import SentimentScore, SocialMention

__all__ = ['SentimentScore', 'SocialMention']
```

**File:** `apps/backend/src/sentiment/models/sentiment.py`

```python
from django.db import models
from django.conf import settings
from apps.common.models import UUIDModel, TimestampedModel, SoftDeleteModel
from apps.investments.models import Asset

class SentimentScore(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Aggregated sentiment score for an asset on a specific date.
    
    sentiment_score: -1.0 (extremely bearish) to +1.0 (extremely bullish)
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='sentiment_scores'
    )
    
    date = models.DateField()
    
    sentiment_score = models.FloatField(
        help_text="Aggregate sentiment from -1 (bearish) to +1 (bullish)"
    )
    
    mention_count = models.IntegerField(
        default=0,
        help_text="Total number of mentions"
    )
    
    bullish_count = models.IntegerField(
        default=0,
        help_text="Number of bullish mentions"
    )
    
    bearish_count = models.IntegerField(
        default=0,
        help_text="Number of bearish mentions"
    )
    
    neutral_count = models.IntegerField(
        default=0,
        help_text="Number of neutral mentions"
    )
    
    source = models.CharField(
        max_length=50,
        choices=[
            ('TWITTER', 'Twitter'),
            ('REDDIT', 'Reddit'),
            ('STOCKTWITS', 'StockTwits'),
            ('ALL', 'All Sources')
        ],
        default='ALL'
    )
    
    # Metrics for trend analysis
    avg_sentiment_7d = models.FloatField(
        null=True,
        blank=True,
        help_text="7-day moving average"
    )
    
    sentiment_velocity = models.FloatField(
        null=True,
        blank=True,
        help_text="Rate of change (sentiment_today - sentiment_yesterday)"
    )
    
    is_outlier = models.BooleanField(
        default=False,
        help_text="Unusual sentiment spike (> 2 std dev)"
    )
    
    class Meta:
        db_table = 'sentiment_scores'
        unique_together = [['asset', 'date', 'source']]
        indexes = [
            models.Index(fields=['asset', 'date']),
            models.Index(fields=['date', 'sentiment_score']),
        ]
    
    def __str__(self):
        return f"{self.asset.symbol} - {self.date}: {self.sentiment_score:.2f}"


class SocialMention(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Individual social media mention about an asset.
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='social_mentions'
    )
    
    platform = models.CharField(
        max_length=50,
        choices=[
            ('TWITTER', 'Twitter'),
            ('REDDIT', 'Reddit'),
            ('STOCKTWITS', 'StockTwits')
        ]
    )
    
    # Author info
    username = models.CharField(max_length=255)
    author_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Content
    content = models.TextField()
    
    # Sentiment analysis
    sentiment_score = models.FloatField(
        help_text="Sentiment from -1 (bearish) to +1 (bullish)"
    )
    
    sentiment_label = models.CharField(
        max_length=20,
        choices=[
            ('BULLISH', 'Bullish'),
            ('BEARISH', 'Bearish'),
            ('NEUTRAL', 'Neutral')
        ]
    )
    
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Confidence in sentiment classification (0-1)"
    )
    
    # Engagement metrics
    posted_at = models.DateTimeField()
    
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    
    # URLs
    url = models.URLField(max_length=1000)
    
    # Additional metadata (JSON)
    metadata = models.JSONField(
        default=dict,
        help_text="Store platform-specific data (hashtags, emojis, etc.)"
    )
    
    class Meta:
        db_table = 'social_mentions'
        indexes = [
            models.Index(fields=['asset', 'posted_at']),
            models.Index(fields=['platform', 'posted_at']),
            models.Index(fields=['sentiment_score']),
        ]
    
    def __str__(self):
        return f"{self.platform} - {self.username}: {self.sentiment_score:.2f}"
```

**CREATE MIGRATION:**
```bash
python manage.py makemigrations sentiment
python manage.py migrate sentiment
```

---

### STEP 3: Create Sentiment Analyzer (3 hours) ⭐ CRITICAL

**File:** `apps/backend/src/sentiment/services/sentiment_analyzer.py`

```python
import re
from typing import Dict, List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

class SentimentAnalyzer:
    """
    Analyze sentiment of text using multiple NLP approaches.
    
    Combines:
    1. VADER (Valence Aware Dictionary and sEntiment Reasoner)
       - Optimized for social media text
       - Handles emojis, slang, capitalization
       - Fast and accurate for short text
    
    2. TextBlob
       - General-purpose sentiment analysis
       - Good for longer text
       - Provides subjectivity scores
    
    3. Custom ticker detection
       - Identify asset tickers in text
       - Handle cashtag syntax ($TSLA)
    """
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.ticker_pattern = re.compile(
            r'\$([A-Z]{1,5})\b|\b\$([A-Z]{1,5})|([A-Z]{2,5})\b',
            re.IGNORECASE
        )
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text using VADER and TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with:
            - sentiment_score: -1 to +1 (combined score)
            - sentiment_label: 'BULLISH', 'BEARISH', 'NEUTRAL'
            - vader_score: VADER compound score
            - textblob_score: TextBlob polarity
            - confidence: Confidence in classification
        """
        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combine scores (weighted average: VADER 70%, TextBlob 30%)
        combined_score = (vader_compound * 0.7) + (textblob_polarity * 0.3)
        
        # Determine label
        if combined_score >= 0.05:
            label = 'BULLISH'
        elif combined_score <= -0.05:
            label = 'BEARISH'
        else:
            label = 'NEUTRAL'
        
        # Calculate confidence (based on score magnitude)
        confidence = abs(combined_score)
        if confidence < 0.1:
            confidence = 0.3  # Low confidence for near-neutral
        elif confidence < 0.3:
            confidence = 0.6  # Medium confidence
        else:
            confidence = 0.9  # High confidence for strong sentiment
        
        return {
            'sentiment_score': combined_score,
            'sentiment_label': label,
            'vader_score': vader_compound,
            'textblob_score': textblob_polarity,
            'confidence': confidence,
            'vader_details': vader_scores
        }
    
    def detect_tickers(self, text: str) -> List[str]:
        """
        Detect stock ticker symbols in text.
        
        Handles:
        - Cashtags: $TSLA, $AAPL
        - Ticker pattern: TSLA, AAPL, MSFT (2-5 uppercase letters)
        - Common tickers only (filter out words like "THE", "ARE")
        
        Args:
            text: Text to search
            
        Returns:
            List of detected ticker symbols
        """
        # Common English words to exclude
        exclude_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'YOU', 'ALL', 'CAN', 'HAD',
            'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'NOT', 'NOW'
        }
        
        matches = self.ticker_pattern.findall(text)
        tickers = set()
        
        for match in matches:
            # match is a tuple: (group1, group2, group3)
            ticker = None
            if match[0]:  # $TSLA format
                ticker = match[0]
            elif match[1]:  # $TSLA format (alt)
                ticker = match[1]
            elif match[2]:  # TSLA format
                ticker = match[2]
            
            if ticker and len(ticker) >= 2 and len(ticker) <= 5:
                ticker_upper = ticker.upper()
                if ticker_upper not in exclude_words:
                    tickers.add(ticker_upper)
        
        return list(tickers)
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        return [self.analyze_sentiment(text) for text in texts]


# QUICK TEST
if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    
    # Test cases
    test_texts = [
        "🚀🚀 TSLA to the moon! Elon is a genius! $TSLA #Tesla",
        "Bearish on $AAPL, iPhone sales declining 📉",
        "Just bought more NVDA, looks solid",
        "Market is looking weak today, might be time to sell"
    ]
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        tickers = analyzer.detect_tickers(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.2f})")
        print(f"Tickers: {tickers}")
```

**INSTALL DEPENDENCIES:**
```bash
pip install vaderSentiment textblob
python -m textblob.download_corpora  # Download TextBlob data
```

---

### STEP 4: Create Twitter Scraper (3 hours) ⭐ TWITTER API v2

**File:** `apps/backend/src/sentiment/scrapers/twitter_scraper.py`

```python
import os
import tweepy
from datetime import datetime, timedelta
from typing import List, Dict
from ..services.sentiment_analyzer import SentimentAnalyzer

class TwitterScraper:
    """
    Twitter/X API v2 scraper for financial sentiment.
    
    Requires Twitter API v2 Bearer Token.
    Free tier: 500,000 tweets/month (enough for development)
    """
    
    def __init__(self):
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not set in environment")
        
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.analyzer = SentimentAnalyzer()
    
    def search_tweets_by_ticker(
        self,
        ticker: str,
        max_results: int = 100,
        days_back: int = 1
    ) -> List[Dict]:
        """
        Search for tweets mentioning a specific ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'TSLA')
            max_results: Number of tweets to fetch (max 100 per request)
            days_back: How many days back to search
            
        Returns:
            List of tweet data with sentiment analysis
        """
        # Build query
        query = f'${ticker} OR {ticker} lang:en -is:retweet'
        
        # Calculate date range
        start_time = datetime.utcnow() - timedelta(days=days_back)
        
        try:
            # Search tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id']
            )
            
            if not response.data:
                return []
            
            tweets = []
            for tweet in response.data:
                # Analyze sentiment
                sentiment_result = self.analyzer.analyze_sentiment(tweet.text)
                
                tweets.append({
                    'platform': 'TWITTER',
                    'username': f"@{tweet.author_id}",  # Would need user lookup for actual username
                    'author_id': tweet.author_id,
                    'content': tweet.text,
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_label': sentiment_result['sentiment_label'],
                    'confidence': sentiment_result['confidence'],
                    'posted_at': tweet.created_at,
                    'likes_count': tweet.public_metrics['like_count'],
                    'comments_count': tweet.public_metrics['reply_count'],
                    'shares_count': tweet.public_metrics['retweet_count'],
                    'url': f"https://twitter.com/i/web/status/{tweet.id}",
                    'metadata': {
                        'tweet_id': tweet.id,
                        'query_used': query
                    }
                })
            
            return tweets
            
        except tweepy.Errors.TooManyRequests:
            print("Twitter API rate limit exceeded")
            return []
        except tweepy.Errors.Forbidden:
            print("Twitter API access forbidden - check credentials")
            return []
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def get_trending_tickers(self, limit: int = 10) -> List[str]:
        """
        Get trending stock tickers from Twitter.
        
        This is a simplified version - you'd need to:
        1. Search for common financial cashtags
        2. Aggregate mentions over last hour
        3. Sort by mention count
        
        Args:
            limit: Number of trending tickers to return
            
        Returns:
            List of trending ticker symbols
        """
        # For now, return hardcoded list
        # In production, implement aggregation from recent tweets
        return ['TSLA', 'AAPL', 'NVDA', 'AMD', 'SPY', 'QQQ', 'AMC', 'GME'][:limit]


# USAGE EXAMPLE
if __name__ == '__main__':
    scraper = TwitterScraper()
    
    # Search Tesla tweets
    tweets = scraper.search_tweets_by_ticker('TSLA', max_results=10)
    
    for tweet in tweets[:3]:
        print(f"\n{tweet['sentiment_label']}: {tweet['sentiment_score']:.2f}")
        print(f"Content: {tweet['content'][:100]}")
        print(f"Likes: {tweet['likes_count']}")
```

**INSTALL Tweepy:**
```bash
pip install tweepy
```

---

### STEP 5: Create Reddit Scraper (2 hours) ⭐ PRAW

**File:** `apps/backend/src/sentiment/scrapers/reddit_scraper.py`

```python
import os
import praw
from datetime import datetime, timedelta
from typing import List, Dict
from ..services.sentiment_analyzer import SentimentAnalyzer

class RedditScraper:
    """
    Reddit scraper using PRAW (Python Reddit API Wrapper).
    
    Focuses on financial subreddits:
    - r/wallstreetbets (2.8M members)
    - r/stocks (2.5M members)
    - r/investing (1.8M members)
    - r/options (500K members)
    """
    
    FINANCIAL_SUBREDDITS = [
        'wallstreetbets',
        'stocks',
        'investing',
        'options',
        'stockmarket',
        'pennystocks'
    ]
    
    def __init__(self):
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'finance-hub/1.0')
        
        if not client_id or not client_secret:
            raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        self.analyzer = SentimentAnalyzer()
    
    def search_posts_by_ticker(
        self,
        ticker: str,
        subreddits: List[str] = None,
        limit: int = 100,
        time_filter: str = 'day'
    ) -> List[Dict]:
        """
        Search Reddit posts mentioning a ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'TSLA')
            subreddits: List of subreddits to search (default: financial)
            limit: Number of posts to fetch
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            
        Returns:
            List of post data with sentiment analysis
        """
        if subreddits is None:
            subreddits = self.FINANCIAL_SUBREDDITS
        
        posts = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for ticker in posts
                search_query = f'title:{ticker} OR self:{ticker}'
                
                for submission in subreddit.search(
                    search_query,
                    limit=limit // len(subreddits),
                    time_filter=time_filter
                ):
                    # Combine title and text
                    text = f"{submission.title}\n\n{submission.selftext}"
                    
                    # Analyze sentiment
                    sentiment_result = self.analyzer.analyze_sentiment(text)
                    
                    posts.append({
                        'platform': 'REDDIT',
                        'username': str(submission.author),
                        'author_id': submission.author.id if submission.author else None,
                        'content': text,
                        'sentiment_score': sentiment_result['sentiment_score'],
                        'sentiment_label': sentiment_result['sentiment_label'],
                        'confidence': sentiment_result['confidence'],
                        'posted_at': datetime.fromtimestamp(submission.created_utc),
                        'likes_count': submission.score,
                        'comments_count': submission.num_comments,
                        'shares_count': 0,  # Reddit doesn't have shares
                        'url': f"https://reddit.com{submission.permalink}",
                        'metadata': {
                            'subreddit': subreddit_name,
                            'post_id': submission.id,
                            'upvote_ratio': submission.upvote_ratio
                        }
                    })
                
            except Exception as e:
                print(f"Error searching r/{subreddit_name}: {e}")
                continue
        
        return posts
    
    def get_hot_posts(
        self,
        subreddit: str = 'wallstreetbets',
        limit: int = 50
    ) -> List[Dict]:
        """
        Get hot posts from a subreddit.
        
        Args:
            subreddit: Subreddit name
            limit: Number of posts to fetch
            
        Returns:
            List of hot posts with sentiment analysis
        """
        posts = []
        
        try:
            for submission in self.reddit.subreddit(subreddit).hot(limit=limit):
                text = f"{submission.title}\n\n{submission.selftext}"
                
                # Detect tickers
                tickers = self.analyzer.detect_tickers(text)
                
                if not tickers:
                    continue  # Skip posts without tickers
                
                sentiment_result = self.analyzer.analyze_sentiment(text)
                
                posts.append({
                    'platform': 'REDDIT',
                    'username': str(submission.author),
                    'content': text,
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_label': sentiment_result['sentiment_label'],
                    'confidence': sentiment_result['confidence'],
                    'posted_at': datetime.fromtimestamp(submission.created_utc),
                    'likes_count': submission.score,
                    'comments_count': submission.num_comments,
                    'url': f"https://reddit.com{submission.permalink}",
                    'metadata': {
                        'subreddit': subreddit,
                        'tickers_detected': tickers,
                        'upvote_ratio': submission.upvote_ratio
                    }
                })
        
        except Exception as e:
            print(f"Error fetching hot posts from r/{subreddit}: {e}")
        
        return posts


# USAGE EXAMPLE
if __name__ == '__main__':
    scraper = RedditScraper()
    
    # Search r/wallstreetbets for TSLA
    posts = scraper.search_posts_by_ticker('TSLA', subreddits=['wallstreetbets'], limit=10)
    
    for post in posts[:3]:
        print(f"\n{post['sentiment_label']}: {post['sentiment_score']:.2f}")
        print(f"Content: {post['content'][:100]}")
        print(f"Likes: {post['likes_count']}")
```

**INSTALL PRAW:**
```bash
pip install praw
```

---

### STEP 6: Create Aggregation Service (2 hours)

**File:** `apps/backend/src/sentiment/services/aggregation_service.py`

```python
from typing import Dict, List
from datetime import date, timedelta
from django.db.models import Avg, Count, Q
from apps.investments.models import Asset
from ..models import SentimentScore, SocialMention

class SentimentAggregationService:
    """
    Aggregate sentiment data from multiple sources.
    """
    
    def calculate_daily_sentiment(
        self,
        asset_id: str,
        date: date,
        source: str = 'ALL'
    ) -> Dict:
        """
        Calculate aggregate sentiment score for an asset on a specific date.
        
        Aggregates all mentions from the day and calculates:
        - Average sentiment score
        - Bullish/bearish/neutral counts
        - Sentiment velocity (change from previous day)
        
        Args:
            asset_id: Asset ID
            date: Date to calculate sentiment for
            source: Source filter (TWITTER, REDDIT, STOCKTWITS, ALL)
            
        Returns:
            Dictionary with aggregated sentiment data
        """
        # Get mentions for the day
        mentions = SocialMention.objects.filter(
            asset_id=asset_id,
            posted_at__date=date
        )
        
        if source != 'ALL':
            mentions = mentions.filter(platform=source)
        
        if not mentions.exists():
            return None
        
        # Calculate aggregates
        mention_count = mentions.count()
        bullish_count = mentions.filter(sentiment_label='BULLISH').count()
        bearish_count = mentions.filter(sentiment_label='BEARISH').count()
        neutral_count = mentions.filter(sentiment_label='NEUTRAL').count()
        
        # Weighted sentiment score (weighted by engagement)
        total_engagement = sum(
            m.likes_count + m.comments_count + m.shares_count
            for m in mentions
        ) or 1
        
        weighted_score = sum(
            m.sentiment_score * (m.likes_count + m.comments_count + m.shares_count + 1)
            for m in mentions
        ) / total_engagement
        
        # Calculate sentiment velocity
        yesterday = date - timedelta(days=1)
        yesterday_sentiment = SentimentScore.objects.filter(
            asset_id=asset_id,
            date=yesterday,
            source=source
        ).first()
        
        sentiment_velocity = None
        if yesterday_sentiment:
            sentiment_velocity = weighted_score - yesterday_sentiment.sentiment_score
        
        return {
            'sentiment_score': weighted_score,
            'mention_count': mention_count,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'sentiment_velocity': sentiment_velocity
        }
    
    def get_trending_assets(
        self,
        hours: int = 24,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get assets with highest mention volume in the last N hours.
        
        Args:
            hours: Number of hours to look back
            limit: Number of assets to return
            
        Returns:
            List of trending assets
        """
        since = date.today() - timedelta(hours=hours)
        
        # Get assets with most mentions
        trending = SocialMention.objects.filter(
            posted_at__gte=since
        ).values('asset__symbol', 'asset__name').annotate(
            mention_count=Count('id'),
            avg_sentiment=Avg('sentiment_score')
        ).order_by('-mention_count')[:limit]
        
        return list(trending)
    
    def get_highest_bullish_sentiment(self, limit: int = 10) -> List[Dict]:
        """
        Get assets with highest bullish sentiment.
        
        Args:
            limit: Number of assets to return
            
        Returns:
            List of assets with highest sentiment scores
        """
        today = date.today()
        
        bullish = SentimentScore.objects.filter(
            date=today,
            sentiment_score__gt=0
        ).select_related('asset').order_by('-sentiment_score')[:limit]
        
        return [
            {
                'symbol': s.asset.symbol,
                'sentiment_score': s.sentiment_score,
                'mention_count': s.mention_count
            }
            for s in bullish
        ]
```

---

### STEP 7: Create API Endpoints (2 hours)

**File:** `apps/backend/src/sentiment/api/sentiment.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import SentimentScore, SocialMention
from ..services.aggregation_service import SentimentAggregationService

class SentimentViewSet(viewsets.ViewSet):
    """
    Sentiment analysis API endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregation_service = SentimentAggregationService()
    
    def retrieve(self, request, pk=None):
        """
        GET /api/sentiment/{asset_id}
        Get current sentiment for an asset.
        """
        from apps.investments.models import Asset
        
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get latest sentiment score
        latest_sentiment = SentimentScore.objects.filter(
            asset=asset
        ).order_by('-date').first()
        
        if not latest_sentiment:
            return Response({'error': 'No sentiment data available'})
        
        return Response({
            'symbol': asset.symbol,
            'sentiment_score': latest_sentiment.sentiment_score,
            'sentiment_label': self._get_sentiment_label(latest_sentiment.sentiment_score),
            'mention_count': latest_sentiment.mention_count,
            'bullish_count': latest_sentiment.bullish_count,
            'bearish_count': latest_sentiment.bearish_count,
            'date': latest_sentiment.date
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        GET /api/sentiment/{asset_id}/history
        Get historical sentiment for an asset.
        """
        from apps.investments.models import Asset
        
        days = int(request.query_params.get('days', 30))
        
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get historical sentiment
        since = date.today() - timedelta(days=days)
        history = SentimentScore.objects.filter(
            asset=asset,
            date__gte=since
        ).order_by('date')
        
        return Response({
            'symbol': asset.symbol,
            'history': [
                {
                    'date': h.date,
                    'sentiment_score': h.sentiment_score,
                    'mention_count': h.mention_count
                }
                for h in history
            ]
        })
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        GET /api/sentiment/trending
        Get most mentioned assets.
        """
        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 10))
        
        trending = self.aggregation_service.get_trending_assets(hours, limit)
        
        return Response({'trending': trending})
    
    @action(detail=False, methods=['get'])
    def hottest(self, request):
        """
        GET /api/sentiment/hottest
        Get assets with highest bullish sentiment.
        """
        limit = int(request.query_params.get('limit', 10))
        
        hottest = self.aggregation_service.get_highest_bullish_sentiment(limit)
        
        return Response({'hottest': hottest})
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score >= 0.3:
            return 'Very Bullish'
        elif score >= 0.1:
            return 'Bullish'
        elif score <= -0.3:
            return 'Very Bearish'
        elif score <= -0.1:
            return 'Bearish'
        else:
            return 'Neutral'
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Not Handling Twitter Rate Limits
```python
# WRONG - Will hit rate limits immediately
for ticker in tickers:
    tweets = scraper.search_tweets_by_ticker(ticker)

# CORRECT - Implement rate limiting
import time
for ticker in tickers:
    tweets = scraper.search_tweets_by_ticker(ticker)
    time.sleep(1)  # Wait 1 second between requests
```

### ❌ Mistake 2: Not Filtering Retweets
```python
# WRONG - Includes retweets (duplicate content)
query = f'${ticker}'

# CORRECT - Exclude retweets for unique sentiment
query = f'${ticker} OR {ticker} lang:en -is:retweet'
```

### ❌ Mistake 3: Not Handling Emoji Sentiment
```python
# WRONG - Ignores emojis (lots of sentiment in emojis!)
text = "TSLA to the moon 🚀🚀"

# CORRECT - VADER automatically handles emojis
# 🚀 = positive, 📉 = negative, 💀 = very negative
# VADER score for "TSLA to the moon 🚀🚀" = 0.698 (very bullish)
```

### ❌ Mistake 4: Detecting False Tickers
```python
# WRONG - Detects "THE", "AND", "FOR" as tickers
ticker_pattern = re.compile(r'\b([A-Z]{2,5})\b')

# CORRECT - Exclude common English words
exclude_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'YOU', 'ALL'}
# Only keep tickers not in exclude_words
```

### ❌ Mistake 5: Not Weighting by Engagement
```python
# WRONG - All mentions treated equally
avg_sentiment = sum(m.sentiment_score for m in mentions) / len(mentions)

# CORRECT - Weight by engagement (likes + comments)
weighted_score = sum(
    m.sentiment_score * (m.likes_count + m.comments_count + 1)
    for m in mentions
) / sum(m.likes_count + m.comments_count + 1 for m in mentions)
```

---

## ❓ FAQ

**Q: Which sentiment library should I use?**  
A: Start with VADER. It's specifically designed for social media text, handles emojis, and is very fast. Add TextBlob for longer text analysis.

**Q: How do I handle Twitter API rate limits?**  
A: Free tier = 450 tweets/15 min window. Implement exponential backoff and cache results. Use Redis for hot assets.

**Q: Should I include retweets in sentiment analysis?**  
A: NO. Retweets are duplicates and skew sentiment. Always use `-is:retweet` in queries.

**Q: How accurate is social sentiment for predicting price?**  
A: It's a contrarian indicator. Extreme bullish sentiment often precedes a pullback. Use with technical indicators, not alone.

**Q: Which Reddit subreddits have the best signal?**  
A: r/wallstreetbets (high volume, high noise), r/stocks (more thoughtful), r/investing (fundamental focus).

**Q: How do I handle cashtags vs regular ticker mentions?**  
A: Cashtags ($TSLA) are more intentional. Give them 2x weight compared to regular mentions.

**Q: Should I analyze comments or just post titles?**  
A: Both! Post titles are shorter but higher signal. Comments add volume but more noise. Weight titles 2x.

---

## 📦 FRONTEND IMPLEMENTATION GUIDE

### File: `apps/frontend/src/components/sentiment/SentimentGauge.tsx`

```typescript
'use client';

import { useMemo } from 'react';

interface SentimentGaugeProps {
  score: number; // -1 to +1
  size?: number;
}

export function SentimentGauge({ score, size = 120 }: SentimentGaugeProps) {
  const percentage = useMemo(() => {
    // Convert -1 to +1 range to 0-100 percentage
    return ((score + 1) / 2) * 100;
  }, [score]);
  
  const color = useMemo(() => {
    if (score >= 0.3) return '#10b981';  // green
    if (score >= 0.1) return '#34d399';  // light green
    if (score <= -0.3) return '#ef4444'; // red
    if (score <= -0.1) return '#f87171'; // light red
    return '#9ca3af';  // gray
  }, [score]);
  
  const label = useMemo(() => {
    if (score >= 0.3) return 'Very Bullish';
    if (score >= 0.1) return 'Bullish';
    if (score <= -0.3) return 'Very Bearish';
    if (score <= -0.1) return 'Bearish';
    return 'Neutral';
  }, [score]);
  
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2} className="overflow-visible">
        {/* Background arc */}
        <path
          d="M 10 100 A 80 80 0 0 1 190 100"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="20"
          strokeLinecap="round"
        />
        
        {/* Colored arc */}
        <path
          d="M 10 100 A 80 80 0 0 1 190 100"
          fill="none"
          stroke={color}
          strokeWidth="20"
          strokeLinecap="round"
          strokeDasharray={`${percentage * 2.51} 251`}  // 251 is circumference
          transform="rotate(-90 100 100)"
        />
        
        {/* Needle */}
        <line
          x1="100"
          y1="100"
          x2={100 + 60 * Math.cos((percentage / 100) * Math.PI)}
          y2={100 + 60 * Math.sin((percentage / 100) * Math.PI)}
          stroke="#374151"
          strokeWidth="3"
          transform="rotate(-90 100 100)"
        />
      </svg>
      
      <div className="mt-2 text-center">
        <div className="text-2xl font-bold" style={{ color }}>
          {score.toFixed(2)}
        </div>
        <div className="text-sm text-gray-600">{label}</div>
      </div>
    </div>
  );
}
```

---

## 📊 SENTIMENT CHART

**File:** `apps/frontend/src/components/sentiment/SentimentChart.tsx`

```typescript
'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SentimentChartProps {
  data: Array<{
    date: string;
    sentiment_score: number;
    mention_count: number;
  }>;
}

export function SentimentChart({ data }: SentimentChartProps) {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(date) => new Date(date).toLocaleDateString()}
          />
          <YAxis
            domain={[-1, 1]}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip
            formatter={(value: number) => value.toFixed(2)}
            labelFormatter={(date) => new Date(date).toLocaleDateString()}
          />
          <Line
            type="monotone"
            dataKey="sentiment_score"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] API keys added to `.env` (Twitter, Reddit, StockTwits)
- [ ] All models created with base classes
- [ ] Migration created and applied
- [ ] VADER sentiment analyzer working
- [ ] TextBlob installed and corpora downloaded
- [ ] Twitter scraper handles rate limits
- [ ] Reddit scraper filters by subreddits
- [ ] Ticker detection excludes common words
- [ ] Sentiment is weighted by engagement
- [ ] API endpoints have authentication
- [ ] Frontend gauge shows correct colors
- [ ] Sentiment chart renders historical data
- [ ] Tests for sentiment accuracy
- [ ] Performance tested (API < 5 seconds)

---

## 🎯 SUCCESS CRITERIA

1. ✅ Sentiment scores update every hour
2. ✅ Twitter/Reddit scrapers work without errors
3. ✅ Ticker detection is accurate (>90%)
4. ✅ Sentiment gauge renders correctly
5. ✅ API returns trending assets
6. ✅ No rate limit errors (429)
7. ✅ Frontend shows real-time updates

---

**Start with Step 1 (get API keys) and work through each step sequentially.**
