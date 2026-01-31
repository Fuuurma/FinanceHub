# #️⃣ TASK: C-037 - Social Sentiment Analysis

**Task ID:** C-037
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Linus)
**Status:** ⏳ PENDING
**Priority:** P1 HIGH
**Estimated Time:** 18-24 hours
**Deadline:** March 5, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a social sentiment analysis system that aggregates and analyzes:
- Twitter/X sentiment for stocks
- Reddit sentiment (r/wallstreetbets, r/stocks)
- News sentiment scoring
- Social volume tracking
- Sentiment trends over time

---

## 📋 REQUIREMENTS

### 1. Sentiment Models

```python
# apps/backend/src/social_sentiment/models.py
class SentimentScore(models.Model):
    symbol = CharField()  # Stock symbol
    source = CharField()  # 'twitter', 'reddit', 'news'
    score = DecimalField(max_digits=5, decimal_places=4)  # -1 to 1
    volume = IntegerField()  # Number of mentions
    positive_count = IntegerField()
    negative_count = IntegerField()
    neutral_count = IntegerField()
    timestamp = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),
            models.Index(fields=['source', 'timestamp']),
        ]

class SentimentSummary(models.Model):
    symbol = CharField()
    date = DateField()
    avg_sentiment = DecimalField(max_digits=5, decimal_places=4)
    total_volume = IntegerField()
    twitter_sentiment = DecimalField(max_digits=5, decimal_places=4, null=True)
    reddit_sentiment = DecimalField(max_digits=5, decimal_places=4, null=True)
    news_sentiment = DecimalField(max_digits=5, decimal_places=4, null=True)
    trend = CharField()  # 'up', 'down', 'neutral'
    created_at = DateTimeField(auto_now_add=True)

class SentimentAlert(models.Model):
    user = ForeignKey(User)
    symbol = CharField()
    alert_type = CharField()  # 'spike', 'drop', 'extreme'
    threshold = DecimalField(max_digits=5, decimal_places=4)
    current_value = DecimalField(max_digits=5, decimal_places=4)
    is_active = BooleanField(default=True)
    notified = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

class SocialMention(models.Model):
    symbol = CharField()
    source = CharField()
    source_id = CharField()  # Tweet ID, Reddit post ID
    author = CharField()
    content = TextField()
    url = URLField()
    sentiment = DecimalField(max_digits=5, decimal_places=4)
    sentiment_label = CharField()  # 'positive', 'negative', 'neutral'
    created_at = DateTimeField(auto_now_add=True)
```

### 2. Sentiment Analysis Service

```python
# apps/backend/src/social_sentiment/services/sentiment_service.py
from textblob import TextBlob  # Or use more advanced NLP
import requests

class SentimentAnalysisService:
    def analyze_text(self, text: str) -> tuple:
        """
        Analyze sentiment of text
        Returns: (score: float, label: str)
        Score: -1 (very negative) to 1 (very positive)
        Label: 'positive', 'negative', 'neutral'
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1

        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return (polarity, label)

    def aggregate_sentiment(self, symbol: str, source: str,
                           hours: int = 24) -> SentimentScore:
        """
        Aggregate sentiment for symbol from source
        Calculate average score from recent mentions
        """
        mentions = SocialMention.objects.filter(
            symbol=symbol,
            source=source,
            created_at__gte=timezone.now() - timedelta(hours=hours)
        )

        if not mentions.exists():
            return None

        scores = [m.sentiment for m in mentions]
        avg_score = sum(scores) / len(scores)

        sentiment = SentimentScore.objects.create(
            symbol=symbol,
            source=source,
            score=avg_score,
            volume=mentions.count(),
            positive_count=mentions.filter(sentiment_label='positive').count(),
            negative_count=mentions.filter(sentiment_label='negative').count(),
            neutral_count=mentions.filter(sentiment_label='neutral').count()
        )

        return sentiment

    def get_sentiment_trend(self, symbol: str, days: int = 7):
        """
        Calculate sentiment trend over time
        Returns 'up', 'down', or 'neutral'
        """
        summaries = SentimentSummary.objects.filter(
            symbol=symbol,
            date__gte=timezone.now().date() - timedelta(days=days)
        ).order_by('date')

        if len(summaries) < 2:
            return 'neutral'

        recent_avg = summaries.last().avg_sentiment
        older_avg = summaries.first().avg_sentiment

        if recent_avg - older_avg > 0.1:
            return 'up'
        elif recent_avg - older_avg < -0.1:
            return 'down'
        else:
            return 'neutral'

    def check_sentiment_alerts(self, symbol: str):
        """
        Check if any sentiment alerts should trigger
        """
        alerts = SentimentAlert.objects.filter(
            symbol=symbol,
            is_active=True
        )

        for alert in alerts:
            # Get current sentiment
            current_score = self.aggregate_sentiment(symbol, 'all', 1)

            if current_score and self._should_trigger_alert(alert, current_score):
                self._send_alert(alert, current_score)
```

### 3. Data Collection Services

```python
# apps/backend/src/social_sentiment/services/twitter_service.py
import tweepy  # Twitter API v2

class TwitterSentimentService:
    def search_mentions(self, symbol: str, count: int = 100):
        """
        Search Twitter for mentions of symbol
        Uses Twitter API v2
        """
        # Requires Twitter API access
        # Search for $SYMBOL or #SYMBOL
        # Fetch tweets
        # Analyze sentiment
        # Store in SocialMention
        pass

# apps/backend/src/social_sentiment/services/reddit_service.py
import praw  # Reddit API

class RedditSentimentService:
    def search_subreddits(self, symbol: str, subreddits: List[str]):
        """
        Search Reddit for symbol mentions
        """
        reddit = praw.Reddit()

        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)

            # Search for symbol
            for post in subreddit.search(symbol, limit=100):
                # Analyze sentiment
                sentiment, label = SentimentAnalysisService().analyze_text(post.title + ' ' + post.selftext)

                # Store mention
                SocialMention.objects.create(
                    symbol=symbol,
                    source='reddit',
                    source_id=post.id,
                    author=str(post.author),
                    content=post.title + ' ' + post.selftext[:500],
                    url=post.url,
                    sentiment=sentiment,
                    sentiment_label=label
                )

# apps/backend/src/social_sentiment/services/news_sentiment_service.py
class NewsSentimentService:
    def analyze_news(self, symbol: str):
        """
        Analyze sentiment from news articles
        Uses existing news API
        """
        # Get recent news for symbol
        # Analyze headline + snippet
        # Store sentiment scores
        pass
```

### 4. API Endpoints

```python
# apps/backend/src/social_sentiment/api.py
from ninja import Router

router = Router()

@router.get("/sentiment/{symbol}")
def get_sentiment(request, symbol: str, source: str = None):
    """Get current sentiment for symbol"""
    pass

@router.get("/sentiment/{symbol}/history")
def get_sentiment_history(request, symbol: str, days: int = 7):
    """Get sentiment history for symbol"""
    pass

@router.get("/sentiment/{symbol}/trend")
def get_sentiment_trend(request, symbol: str):
    """Get sentiment trend (up/down/neutral)"""
    pass

@router.get("/sentiment/top")
def get_top_mentions(request, limit: int = 10):
    """Get top mentioned symbols by sentiment"""
    pass

@router.get("/sentiment/spikes")
def get_sentiment_spikes(request, hours: int = 24):
    """Get symbols with unusual sentiment spikes"""
    pass

@router.post("/sentiment/alerts")
def create_sentiment_alert(request, symbol: str, alert_type: str,
                          threshold: float):
    """Create alert for sentiment changes"""
    pass

@router.get("/social/mentions/{symbol}")
def get_social_mentions(request, symbol: str, source: str = None,
                       limit: int = 20):
    """Get recent social media mentions"""
    pass
```

### 5. Frontend Components

```typescript
// apps/frontend/src/components/sentiment/SentimentGauge.tsx
export function SentimentGauge({ symbol }: Props) {
  // Gauge showing sentiment (-1 to 1)
  // Color-coded (red for negative, green for positive)
  // Volume indicator
  // Source breakdown
}

// apps/frontend/src/components/sentiment/SentimentChart.tsx
export function SentimentChart({ symbol, days }: Props) {
  // Line chart of sentiment over time
  // Show Twitter, Reddit, News separately
  - Volume chart
  - Trend indicator
}

// apps/frontend/src/components/sentiment/SocialMentionsList.tsx
export function SocialMentionsList({ symbol }: Props) {
  // List recent mentions
  // Show source (Twitter/Reddit)
  // Show sentiment label
  // Link to original post
  // Filter by source and sentiment
}

// apps/frontend/src/components/sentiment/SentimentAlerts.tsx
export function SentimentAlerts() {
  // Create sentiment alerts
  // List active alerts
  // Show triggered alerts
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Sentiment analysis from text
- [ ] Twitter mention tracking (if API available)
- [ ] Reddit mention tracking (r/wallstreetbets, r/stocks)
- [ ] News sentiment scoring
- [ ] Aggregate sentiment scores
- [ ] Sentiment history and trends
- [ ] Top mentions by volume
- [ ] Sentiment spike detection
- [ ] Sentiment alerts
- [ ] API endpoints for all operations
- [ ] Frontend sentiment visualization
- [ ] Tests for sentiment service
- [ ] Background tasks for data collection

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/social_sentiment/models.py`
- `apps/backend/src/social_sentiment/services/sentiment_service.py`
- `apps/backend/src/social_sentiment/services/twitter_service.py`
- `apps/backend/src/social_sentiment/services/reddit_service.py`
- `apps/backend/src/social_sentiment/services/news_sentiment_service.py`
- `apps/backend/src/social_sentiment/api.py`
- `apps/backend/src/social_sentiment/tests/test_sentiment.py`
- `apps/frontend/src/components/sentiment/SentimentGauge.tsx`
- `apps/frontend/src/components/sentiment/SentimentChart.tsx`
- `apps/frontend/src/components/sentiment/SocialMentionsList.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- News API exists
- TextBlob or similar NLP library
- Twitter API access (optional, requires API key)
- Reddit API access (requires API key)

**Related Tasks:**
- None (standalone feature)

---

## 📊 SENTIMENT SCORING

### Score Range
- **-1.0 to -0.5:** Very Bearish
- **-0.5 to -0.1:** Bearish
- **-0.1 to 0.1:** Neutral
- **0.1 to 0.5:** Bullish
- **0.5 to 1.0:** Very Bullish

### Volume Indicators
- **Low:** <100 mentions/day
- **Medium:** 100-1000 mentions/day
- **High:** 1000-10000 mentions/day
- **Viral:** >10000 mentions/day

### Trends
- **Up:** Sentiment improving (>0.1 change)
- **Down:** Sentiment worsening (<-0.1 change)
- **Neutral:** Stable (-0.1 to 0.1 change)

---

## 📊 DELIVERABLES

1. **Models:** SentimentScore, SentimentSummary, SocialMention
2. **Service:** Sentiment analysis with NLP
3. **Data Collection:** Twitter, Reddit, News services
4. **API:** All sentiment endpoints
5. **Frontend:** Gauges, charts, mentions list
6. **Background Tasks:** Scheduled data collection
7. **Tests:** Unit tests for sentiment scoring
8. **Documentation:** API guide for data sources

---

## 💬 NOTES

**NLP Library Options:**
- **TextBlob:** Simple, easy to use (recommended)
- **VADER:** Social media sentiment specialized
- **NLTK:** More advanced, requires more setup
- **spaCy:** Advanced NLP, overkill for this

**API Limitations:**
- **Twitter API:** Rate limited, requires paid tier for full access
- **Reddit API:** Free but rate limited
- Consider using third-party APIs:
  - StockTwits (social sentiment for stocks)
  - Sentiment analysis APIs (RapidAPI)

**Implementation Phases:**
1. Phase 1: Basic sentiment analysis with TextBlob
2. Phase 2: Manual data entry for testing
3. Phase 3: Reddit integration (free API)
4. Phase 4: Twitter integration (if API key available)
5. Phase 5: Advanced NLP models

**Alternative Approach:**
- Use third-party sentiment APIs
- Example: Alpha Vantage, NewsAPI, StockTwits
- More expensive but less maintenance

**Libraries:**
- Backend: `textblob`, `tweepy` (Twitter), `praw` (Reddit)
- Frontend: Charts (recharts)

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Linus)
**User Value:** HIGH - retail traders want social sentiment

---

#️⃣ *C-037: Social Sentiment Analysis*
*Track Twitter and Reddit sentiment - know what the crowd thinks*
