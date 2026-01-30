# Task C-037: Social Sentiment Analysis

**Priority:** P1 HIGH  
**Estimated Time:** 18-24 hours  
**Assigned To:** Backend Coder + Frontend Coder  
**Status:** PENDING

## Overview
Implement social sentiment analysis by aggregating and analyzing data from Twitter, Reddit, and other social platforms to provide trading insights based on public sentiment.

## User Story
As a trader, I want to see social sentiment indicators for assets so I can gauge market sentiment and make more informed trading decisions based on public opinion.

## Acceptance Criteria

### Backend (14-18 hours)
- [ ] **Social Sentiment Data Model**
  - SentimentScore model - Store sentiment metrics per asset per day
  - SentimentSource model - Track different social platforms
  - Mention model - Store individual mentions/posts
  - SentimentTrend model - Historical sentiment trends

- [ ] **Social Data Scrapers**
  - Twitter/X scraper (using Twitter API v2)
  - Reddit scraper (using Reddit API or PRAW)
  - StockTwits scraper
  - Generic social media aggregator
  - Rate limiting and API quota management

- [ ] **Sentiment Analysis Engine**
  - Natural Language Processing (NLP) for sentiment scoring
  - Use libraries: TextBlob, VADER, or transformers
  - Score range: -1 (bearish) to +1 (bullish)
  - Confidence score for each sentiment
  - Detect sarcasm (advanced)
  - Handle emojis (🚀 = bullish, 📉 = bearish)

- [ ] **Sentiment Aggregation**
  - Aggregate mentions by asset (ticker symbol detection)
  - Calculate daily sentiment score
  - Calculate sentiment trend (7-day, 30-day)
  - Calculate mention volume
  - Calculate sentiment velocity (rate of change)
  - Identify sentiment outliers (unusual spikes)

- [ ] **API Endpoints**
  - `GET /api/sentiment/{asset_id}` - Get current sentiment
  - `GET /api/sentiment/{asset_id}/history` - Historical sentiment
  - `GET /api/sentiment/trending` - Most mentioned assets
  - `GET /api/sentiment/hottest` - Highest bullish sentiment
  - `GET /api/sentiment/mentions/{asset_id}` - Recent mentions

- [ ] **Background Tasks**
  - Scheduled scraping (every hour for hot assets)
  - On-demand scraping for user-requested assets
  - Sentiment calculation and aggregation
  - Cache sentiment data (Redis)

### Frontend (4-6 hours)
- [ ] **Sentiment Display Components**
  - SentimentGauge - Visual gauge showing bullish/bearish
  - SentimentChart - Historical sentiment line chart
  - MentionVolumeChart - Bar chart of mention volume
  - TrendingAssetsList - Top mentioned assets
  - SocialMentionsFeed - Recent social posts

- [ ] **Asset Detail Page Integration**
  - Add sentiment section to asset detail page
  - Show current sentiment score with gauge
  - Show 7-day sentiment trend chart
  - Show recent social mentions (Reddit, Twitter)
  - Link to "View all mentions"

- [ ] **Sentiment Dashboard Page**
  - `/sentiment` route
  - Trending assets table
  - Hottest bullish assets
  - Most bearish assets
  - Unusual sentiment spikes
  - Filter by asset type, market cap

- [ ] **Sentiment Alerts**
  - Alert when sentiment spikes (> 2 std dev)
  - Alert when sentiment flips (bullish → bearish)
  - Alert on high mention volume
  - Integrate with existing alerts system

## Technical Requirements

### Backend
- **Files to Create:**
  - `apps/backend/src/sentiment/models/sentiment.py`
  - `apps/backend/src/sentiment/scrapers/twitter_scraper.py`
  - `apps/backend/src/sentiment/scrapers/reddit_scraper.py`
  - `apps/backend/src/sentiment/scrapers/stocktwits_scraper.py`
  - `apps/backend/src/sentiment/services/sentiment_analyzer.py`
  - `apps/backend/src/sentiment/api/sentiment.py`
  - `apps/backend/src/sentiment/tasks/sentiment_tasks.py`

- **Database Schema:**
  ```python
  class SentimentScore(UUIDModel, TimestampedModel):
      asset = ForeignKey(Asset, on_delete=CASCADE)
      date = DateField()
      sentiment_score = FloatField()  # -1 to +1
      mention_count = IntegerField()
      bullish_count = IntegerField()
      bearish_count = IntegerField()
      neutral_count = IntegerField()
      source = CharField(max_length=50)  # twitter, reddit, stocktwits, all
      
  class SocialMention(UUIDModel, TimestampedModel):
      asset = ForeignKey(Asset, on_delete=CASCADE)
      platform = CharField(max_length=50)
      username = CharField(max_length=255)
      content = TextField()
      sentiment_score = FloatField()
      posted_at = DateTimeField()
      url = URLField()
      likes_count = IntegerField(default=0)
      comments_count = IntegerField(default=0)
  ```

- **Libraries:**
  - `tweepy` - Twitter API
  - `praw` - Reddit API
  - `textblob` or `vaderSentiment` - Sentiment analysis
  - `transformers` (optional) - Advanced NLP

### Frontend
- **Files to Create:**
  - `apps/frontend/src/app/(dashboard)/sentiment/page.tsx`
  - `apps/frontend/src/components/sentiment/SentimentGauge.tsx`
  - `apps/frontend/src/components/sentiment/SentimentChart.tsx`
  - `apps/frontend/src/components/sentiment/MentionVolumeChart.tsx`
  - `apps/frontend/src/components/sentiment/SocialMentionsFeed.tsx`
  - `apps/frontend/src/lib/api/sentiment.ts`

- **Visualizations:**
  - Use Recharts or Chart.js for charts
  - Gauge component for sentiment score
  - Color coding: Green (bullish), Red (bearish), Gray (neutral)
  - Trend lines with confidence intervals

- **API Integration:**
  - Fetch sentiment data on asset detail page
  - Poll for real-time updates (every 5 minutes)
  - Cache sentiment data in React Query

## Dependencies
- **Prerequisites:** C-001 (User System), C-002 (Asset Management), C-005 (Portfolio Core)
- **Related Tasks:** C-013 (AI News Summarization), C-020 (Alerts System)
- **External APIs:** Twitter API v2, Reddit API, StockTwits API

## API Keys Required
- Twitter API Bearer Token (https://developer.twitter.com/)
- Reddit API Client ID & Secret (https://www.reddit.com/prefs/apps)
- StockTwits API Key (https://stocktwits.com/developers)

## Testing Requirements
- **Backend:**
  - Test sentiment scoring accuracy
  - Test API rate limiting
  - Test sentiment aggregation logic
  - Test mention volume spikes detection
  - Test historical sentiment queries

- **Frontend:**
  - Test sentiment gauge rendering
  - Test sentiment chart interactivity
  - Test real-time updates
  - Test social feed rendering
  - Test responsive design

## Performance Considerations
- Cache sentiment data (5-minute TTL)
- Use Redis for hot assets
- Batch API requests to minimize rate limit hits
- Implement exponential backoff for rate limits
- Archive mentions older than 30 days

## Success Metrics
- Sentiment scores update every hour
- API rate limits respected (no 429 errors)
- Sentiment predictions align with price movements (backtest)
- Users find sentiment insights valuable
- Increased engagement with assets showing high sentiment

## Notes
- Social sentiment is a CONTRARIAN indicator (extreme bullish = potential top)
- Combine sentiment with technical indicators for best results
- Sentiment works best for short-term swings, not long-term trends
- Consider adding "sentiment divergence" alerts (price up, sentiment down)
- Twitter API is expensive, consider free alternatives first
- Reddit API is generous but has rate limits
- StockTwits has a free tier for basic data
