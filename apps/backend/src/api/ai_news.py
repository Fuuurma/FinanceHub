"""
AI News API
Provides AI-powered news summarization, sentiment analysis, and asset extraction.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from ninja import Router, Schema
from pydantic import BaseModel, Field
from django.utils import timezone
from django.db.models import Q

from investments.models.news import NewsArticle
from investments.services.ai_news_service import AINewsService, NewsAggregatorService
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)
router = Router(tags=["AI News"])


class NewsArticleResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    source: str
    author: Optional[str] = None
    published_at: str
    sentiment: str
    sentiment_score: Optional[Decimal] = None
    summary: Optional[str] = None
    impact_score: Optional[Decimal] = None
    related_symbols: List[str] = []
    category: Optional[str] = None
    image_url: Optional[str] = None


class ArticleAnalysisRequest(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    description: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class ArticleAnalysisResponse(BaseModel):
    summary: str
    sentiment: dict
    asset_mentions: List[str]
    impact_score: float
    analyzed_at: str


class NewsFilterRequest(BaseModel):
    symbols: List[str] = []
    sentiment: Optional[str] = None
    min_impact_score: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    source: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)


class NewsImpactResponse(BaseModel):
    symbol: str
    articles_count: int
    avg_sentiment: float
    avg_impact_score: float
    positive_articles: int
    negative_articles: int
    neutral_articles: int
    top_articles: List[dict]
    analyzed_at: str


class BatchAnalysisResponse(BaseModel):
    processed: int
    successful: int
    failed: int
    results: List[dict]


@router.post("/analyze", response=ArticleAnalysisResponse)
async def analyze_article(request, article: ArticleAnalysisRequest):
    """
    Analyze a single news article using AI.

    Returns summary, sentiment, asset mentions, and impact score.
    """
    ai_service = AINewsService()

    analysis = await ai_service.analyze_article_full(
        title=article.title, content=article.content, source=article.source
    )

    return ArticleAnalysisResponse(
        summary=analysis["summary"],
        sentiment=analysis["sentiment"],
        asset_mentions=analysis["asset_mentions"],
        impact_score=analysis["impact_score"],
        analyzed_at=analysis["analyzed_at"],
    )


@router.get("/articles", response=List[NewsArticleResponse])
async def get_ai_analyzed_news(
    symbol: Optional[str] = None,
    sentiment: Optional[str] = None,
    min_impact_score: Optional[Decimal] = None,
    category: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """
    Get news articles that have been analyzed by AI.

    Returns articles with summaries, impact scores, and sentiment analysis.
    """
    queryset = NewsArticle.objects.filter(summary__isnull=False)

    if symbol:
        queryset = queryset.filter(related_symbols__icontains=symbol.upper())

    if sentiment:
        queryset = queryset.filter(sentiment=sentiment.lower())

    if min_impact_score is not None:
        queryset = queryset.filter(impact_score__gte=min_impact_score)

    if category:
        queryset = queryset.filter(category=category.lower())

    if source:
        queryset = queryset.filter(source=source)

    articles = queryset[offset : offset + limit]

    return [
        NewsArticleResponse(
            id=str(a.id),
            title=a.title,
            description=a.description,
            url=a.url,
            source=a.source,
            author=a.author,
            published_at=a.published_at.isoformat(),
            sentiment=a.sentiment,
            sentiment_score=a.sentiment_score,
            summary=a.summary,
            impact_score=a.impact_score,
            related_symbols=a.related_symbols or [],
            category=a.category,
            image_url=a.image_url,
        )
        for a in articles
    ]


@router.get("/impact/{symbol}", response=NewsImpactResponse)
async def get_news_impact_for_symbol(symbol: str, days: int = 7):
    """
    Get news impact analysis for a specific symbol.

    Aggregates sentiment and impact scores from recent news.
    """
    from django.utils import timezone
    from datetime import timedelta

    start_date = timezone.now() - timedelta(days=days)

    articles = NewsArticle.objects.filter(
        related_symbols__icontains=symbol.upper(), published_at__gte=start_date
    )

    article_list = list(articles)
    count = len(article_list)

    if count == 0:
        return NewsImpactResponse(
            symbol=symbol.upper(),
            articles_count=0,
            avg_sentiment=0,
            avg_impact_score=0,
            positive_articles=0,
            negative_articles=0,
            neutral_articles=0,
            top_articles=[],
            analyzed_at=timezone.now().isoformat(),
        )

    total_sentiment = sum(
        float(a.sentiment_score) if a.sentiment_score else 0 for a in article_list
    )
    total_impact = sum(
        float(a.impact_score) if a.impact_score else 0 for a in article_list
    )

    positive = sum(1 for a in article_list if a.sentiment == "positive")
    negative = sum(1 for a in article_list if a.sentiment == "negative")
    neutral = count - positive - negative

    sorted_articles = sorted(
        article_list, key=lambda a: float(a.impact_score or 0), reverse=True
    )[:5]

    return NewsImpactResponse(
        symbol=symbol.upper(),
        articles_count=count,
        avg_sentiment=round(total_sentiment / count, 4),
        avg_impact_score=round(total_impact / count, 2),
        positive_articles=positive,
        negative_articles=negative,
        neutral_articles=neutral,
        top_articles=[
            {
                "title": a.title,
                "sentiment": a.sentiment,
                "impact_score": float(a.impact_score or 0),
                "published_at": a.published_at.isoformat(),
            }
            for a in sorted_articles
        ],
        analyzed_at=timezone.now().isoformat(),
    )


@router.post("/batch-analyze", response=BatchAnalysisResponse)
async def batch_analyze_articles(articles: List[ArticleAnalysisRequest]):
    """
    Analyze multiple news articles in batch.

    Useful for processing newly fetched news.
    """
    aggregator = NewsAggregatorService()

    article_dicts = [
        {
            "title": a.title,
            "content": a.content,
            "url": a.url,
            "source": a.source,
            "published_at": a.published_at,
            "description": a.description,
            "author": a.author,
            "image_url": a.image_url,
            "category": a.category,
        }
        for a in articles
    ]

    results = await aggregator.batch_process(article_dicts)

    successful = sum(1 for r in results if "error" not in r)
    failed = len(results) - successful

    return BatchAnalysisResponse(
        processed=len(results), successful=successful, failed=failed, results=results
    )


@router.get("/trending")
async def get_trending_news(limit: int = 10):
    """
    Get trending news by impact score.

    Returns high-impact articles that may affect markets.
    """
    articles = NewsArticle.objects.filter(impact_score__isnull=False).order_by(
        "-impact_score"
    )[:limit]

    return {
        "articles": [
            {
                "id": str(a.id),
                "title": a.title,
                "source": a.source,
                "impact_score": float(a.impact_score),
                "sentiment": a.sentiment,
                "related_symbols": a.related_symbols or [],
                "published_at": a.published_at.isoformat(),
            }
            for a in articles
        ],
        "fetched_at": timezone.now().isoformat(),
    }


@router.get("/market-sentiment")
async def get_market_sentiment():
    """
    Get overall market sentiment from analyzed news.
    """
    from datetime import timedelta

    now = timezone.now()

    periods = [
        ("24h", now - timedelta(hours=24)),
        ("7d", now - timedelta(days=7)),
        ("30d", now - timedelta(days=30)),
    ]

    results = {}

    for period_name, start_date in periods:
        articles = NewsArticle.objects.filter(
            published_at__gte=start_date, summary__isnull=False
        )

        count = articles.count()
        if count == 0:
            results[period_name] = {
                "article_count": 0,
                "avg_sentiment": 0,
                "dominant_sentiment": "neutral",
                "top_symbols": [],
            }
            continue

        total_sentiment = sum(
            float(a.sentiment_score) if a.sentiment_score else 0 for a in articles
        )
        avg_sentiment = total_sentiment / count

        positive = articles.filter(sentiment="positive").count()
        negative = articles.filter(sentiment="negative").count()

        if positive > negative and positive > count * 0.4:
            dominant = "positive"
        elif negative > positive and negative > count * 0.4:
            dominant = "negative"
        else:
            dominant = "neutral"

        symbol_counts = {}
        for a in articles:
            symbols = a.related_symbols or []
            for s in symbols:
                symbol_counts[s] = symbol_counts.get(s, 0) + 1

        top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        results[period_name] = {
            "article_count": count,
            "avg_sentiment": round(avg_sentiment, 4),
            "dominant_sentiment": dominant,
            "top_symbols": [s[0] for s in top_symbols],
        }

    return {"periods": results, "fetched_at": now.isoformat()}
