# C-013: AI-Powered News Summarization & Sentiment

**Priority:** P2 - MEDIUM  
**Assigned to:** Backend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** None  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement AI-powered news summarization and sentiment analysis for financial news.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 6.1 - News Feed):**

- AI-powered news summarization
- Sentiment analysis
- News filtering by asset/portfolio
- Breaking news alerts
- News impact score on assets
- Historical news lookup

---

## ✅ CURRENT STATE

**What exists:**
- NewsAPIScraper for fetching news
- Basic NewsArticle model

**What's missing:**
- AI summarization
- Sentiment scoring
- News impact calculation
- Asset-news correlation

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Enhance NewsArticle Model** (2-3 hours)

**Update `apps/backend/src/investments/models/news.py`:**

```python
from django.db import models

class NewsArticle(models.Model):
    # ... existing fields ...
    
    # New fields
    summary = models.TextField(blank=True, null=True)
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    sentiment_label = models.CharField(max_length=20, blank=True)  # POSITIVE, NEGATIVE, NEUTRAL
    impact_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    mentioned_assets = models.ManyToManyField('Asset', related_name='news_mentions')
    summary_generated_at = models.DateTimeField(null=True, blank=True)
```

---

### **Phase 2: AI Service Integration** (6-8 hours)

**Create `apps/backend/src/investments/services/ai_news_service.py`:**

```python
import openai
from typing import List, Dict
from decouple import config
from investments.models import NewsArticle, Asset

class AINewsService:
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=config('OPENAI_API_KEY'))
    
    async def summarize_article(self, article: NewsArticle) -> str:
        """
        Generate AI summary of news article
        """
        prompt = f"""
        Summarize this financial news article in 2-3 sentences:
        
        Title: {article.title}
        Content: {article.content}
        
        Focus on key information that affects investors.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    async def analyze_sentiment(self, article: NewsArticle) -> Dict:
        """
        Analyze sentiment of news article
        Returns: {score, label, key_points}
        """
        prompt = f"""
        Analyze the sentiment of this financial news article:
        
        Title: {article.title}
        Content: {article.content}
        
        Return JSON:
        {{
            "score": <float from -1.0 (very negative) to 1.0 (very positive)>,
            "label": <"POSITIVE", "NEGATIVE", or "NEUTRAL">,
            "key_points": [<list of 3-5 key points>]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def extract_asset_mentions(self, article: NewsArticle) -> List[str]:
        """
        Extract asset symbols mentioned in article
        Returns: List of asset symbols
        """
        prompt = f"""
        Extract all stock/crypto symbols mentioned in this article:
        
        Title: {article.title}
        Content: {article.content}
        
        Return JSON: {{"symbols": ["AAPL", "TSLA", "BTC"]}}
        Only include symbols that are clearly ticker symbols or cryptocurrencies.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        data = json.loads(response.choices[0].message.content)
        return data.get('symbols', [])
    
    async def calculate_impact_score(self, article: NewsArticle, sentiment: Dict) -> float:
        """
        Calculate news impact score on assets
        Returns: Impact score (0-100)
        """
        # Base score from sentiment magnitude
        sentiment_magnitude = abs(sentiment['score'])
        
        # Boost for breaking news
        if article.is_breaking:
            sentiment_magnitude *= 1.5
        
        # Boost for high-credibility sources
        source_boost = {
            'Bloomberg': 1.3,
            'Reuters': 1.2,
            'WSJ': 1.2,
            'CNBC': 1.1
        }
        boost = source_boost.get(article.source, 1.0)
        
        # Calculate final impact score
        impact = min(100, sentiment_magnitude * boost * 50)
        
        return round(impact, 2)
    
    async def process_article(self, article_id: int) -> NewsArticle:
        """
        Full processing pipeline: summarize, sentiment, extract assets, calculate impact
        """
        article = NewsArticle.objects.get(id=article_id)
        
        # Generate summary
        summary = await self.summarize_article(article)
        article.summary = summary
        
        # Analyze sentiment
        sentiment = await self.analyze_sentiment(article)
        article.sentiment_score = sentiment['score']
        article.sentiment_label = sentiment['label']
        
        # Extract asset mentions
        symbols = await self.extract_asset_mentions(article)
        assets = Asset.objects.filter(symbol__in=symbols)
        article.mentioned_assets.set(assets)
        
        # Calculate impact
        impact = await self.calculate_impact_score(article, sentiment)
        article.impact_score = impact
        
        article.summary_generated_at = timezone.now()
        article.save()
        
        return article
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/ai_news.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.services.ai_news_service import AINewsService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def generate_article_summary(request, article_id):
    """
    POST /api/news/{id}/summarize/
    Generate AI summary for article
    """
    service = AINewsService()
    article = await service.process_article(article_id)
    return Response({
        'summary': article.summary,
        'sentiment': article.sentiment_label,
        'sentiment_score': article.sentiment_score,
        'impact_score': article.impact_score
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_for_asset(request, asset_symbol):
    """
    GET /api/assets/{symbol}/news/
    Get news for specific asset with AI analysis
    """
    articles = NewsArticle.objects.filter(
        mentioned_assets__symbol=asset_symbol,
        summary__isnull=False
    ).order_by('-published_date')[:20]
    
    data = [{
        'title': a.title,
        'summary': a.summary,
        'sentiment': a.sentiment_label,
        'sentiment_score': a.sentiment_score,
        'impact_score': a.impact_score,
        'published_date': a.published_date
    } for a in articles]
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_news_sentiment(request, portfolio_id):
    """
    GET /api/portfolios/{id}/news-sentiment/
    Get news sentiment for portfolio holdings
    """
    # Get assets in portfolio
    assets = PortfolioPosition.objects.filter(
        portfolio_id=portfolio_id
    ).values_list('asset_id', flat=True)
    
    # Get recent news for these assets
    articles = NewsArticle.objects.filter(
        mentioned_assets__in=assets,
        summary__isnull=False
    ).distinct().order_by('-published_date')[:50]
    
    # Aggregate sentiment
    total_sentiment = sum(a.sentiment_score or 0 for a in articles)
    avg_sentiment = total_sentiment / len(articles) if articles else 0
    
    return Response({
        'article_count': len(articles),
        'average_sentiment': avg_sentiment,
        'sentiment_label': 'POSITIVE' if avg_sentiment > 0.1 else 'NEGATIVE' if avg_sentiment < -0.1 else 'NEUTRAL',
        'articles': [{
            'title': a.title,
            'summary': a.summary,
            'sentiment': a.sentiment_label,
            'impact_score': a.impact_score
        } for a in articles[:10]]
    })
```

---

### **Phase 4: Task Queue Integration** (2-3 hours)

**Create Dramatiq task for async processing:**

```python
import dramatiq
from investments.services.ai_news_service import AINewsService

@dramatiq.actor
def process_new_article(article_id: int):
    """
    Async task to process new article with AI
    """
    service = AINewsService()
    asyncio.run(service.process_article(article_id))
```

---

## 📋 DELIVERABLES

- [ ] Enhanced NewsArticle model
- [ ] AINewsService with 5 methods
- [ ] 3 API endpoints
- [ ] Async Dramatiq task
- [ ] Tests
- [ ] Documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] AI summaries generated in <5 seconds
- [ ] Sentiment score between -1.0 and 1.0
- [ ] Asset mentions extracted with >80% accuracy
- [ ] Impact score calculated (0-100)
- [ ] All tests passing

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/013-ai-news-summarization.md
