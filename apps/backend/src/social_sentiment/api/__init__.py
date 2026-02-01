from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from django.db.models import Avg, Count

from social_sentiment.models import (
    SentimentAnalysis,
    SocialPost,
    TickerMention,
    SentimentAlert,
)
from social_sentiment.services.sentiment_analysis import SentimentAnalyzer


router = Router()


class SentimentAnalysisSchema(BaseModel):
    id: int
    source: str
    content_hash: str
    vader_compound: float
    vader_positive: float
    vader_negative: float
    vader_neutral: float
    textblob_polarity: float
    textblob_subjectivity: float
    combined_score: float
    confidence: float
    sentiment_label: str
    created_at: datetime

    class Config:
        from_attributes = True


class SocialPostSchema(BaseModel):
    id: int
    source: str
    post_id: str
    author: str
    content: str
    symbols: List[str]
    followers_count: int
    likes_count: int
    comments_count: int
    shares_count: int
    engagement_score: float
    sentiment_analysis: Optional[SentimentAnalysisSchema] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TickerMentionSchema(BaseModel):
    id: int
    symbol: str
    source: str
    mention_count: int
    avg_sentiment: float
    sentiment_change: float
    volume_spike: bool
    last_mentioned_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AggregatedSentimentSchema(BaseModel):
    symbol: str
    source: Optional[str] = None
    timeframe: Optional[str] = None
    total_mentions: int
    avg_vader_compound: float
    avg_textblob_polarity: float
    combined_score: float
    sentiment_distribution: dict
    top_influencers: List[dict]
    last_updated: datetime


class SentimentRequestSchema(BaseModel):
    content: str
    symbols: Optional[List[str]] = None


class SentimentResponseSchema(BaseModel):
    symbol: Optional[str] = None
    vader_compound: float
    vader_positive: float
    vader_negative: float
    vader_neutral: float
    textblob_polarity: float
    textblob_subjectivity: float
    combined_score: float
    confidence: float
    sentiment_label: str
    detected_symbols: List[str]


class TickerTrendingSchema(BaseModel):
    symbol: str
    mention_count: int
    sentiment_score: float
    sentiment_change: float
    volume_spike: bool


class SentimentAlertCreateSchema(BaseModel):
    symbol: str
    alert_type: str
    threshold: float
    direction: str = "above"


class SentimentAlertResponseSchema(BaseModel):
    id: int
    symbol: str
    alert_type: str
    threshold: Optional[float] = None
    direction: str
    is_active: bool
    is_triggered: bool
    last_triggered_at: Optional[datetime] = None
    created_at: datetime


@router.post("/analyze", response=SentimentResponseSchema)
def analyze_sentiment(request, payload: SentimentRequestSchema):
    """Analyze sentiment of given text content."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text(payload.content)

    detected_symbols = []
    if payload.symbols:
        detected_symbols = payload.symbols
    else:
        detected_symbols = analyzer.detect_tickers(payload.content)

    return SentimentResponseSchema(
        symbol=detected_symbols[0] if detected_symbols else None,
        vader_compound=result["vader"]["compound"],
        vader_positive=result["vader"]["positive"],
        vader_negative=result["vader"]["negative"],
        vader_neutral=result["vader"]["neutral"],
        textblob_polarity=result["textblob"]["polarity"],
        textblob_subjectivity=result["textblob"]["subjectivity"],
        combined_score=result["combined_score"],
        confidence=result["confidence"],
        sentiment_label=result["sentiment_label"],
        detected_symbols=detected_symbols,
    )


@router.get("/trending", response=List[TickerTrendingSchema])
def get_trending_tickers(request, source: Optional[str] = None, limit: int = 20):
    """Get trending tickers by mention volume."""
    mentions = TickerMention.objects.all()
    if source:
        mentions = mentions.filter(source=source)

    mentions = mentions.order_by("-mention_count")[:limit]

    return [
        TickerTrendingSchema(
            symbol=m.symbol,
            mention_count=m.mention_count,
            sentiment_score=m.avg_sentiment if m.avg_sentiment else 0.0,
            sentiment_change=m.sentiment_change if m.sentiment_change else 0.0,
            volume_spike=False,
        )
        for m in mentions
    ]


@router.get("/alerts", response=List[SentimentAlertResponseSchema])
def get_sentiment_alerts(
    request, symbol: Optional[str] = None, active_only: bool = True
):
    """Get sentiment alerts for user."""
    alerts = SentimentAlert.objects.all()
    if symbol:
        alerts = alerts.filter(symbol=symbol.upper())
    if active_only:
        alerts = alerts.filter(status="active")

    return [
        SentimentAlertResponseSchema(
            id=alert.id,
            symbol=alert.symbol,
            alert_type=alert.alert_type,
            threshold=alert.threshold,
            direction=alert.threshold_direction,
            is_active=alert.is_active,
            is_triggered=alert.is_triggered,
            last_triggered_at=alert.last_triggered_at,
            created_at=alert.created_at,
        )
        for alert in alerts
    ]


@router.post("/alerts", response=SentimentAlertResponseSchema)
def create_sentiment_alert(request, payload: SentimentAlertCreateSchema):
    """Create a new sentiment alert."""
    alert = SentimentAlert.objects.create(
        symbol=payload.symbol.upper(),
        alert_type=payload.alert_type,
        threshold=payload.threshold,
        threshold_direction=payload.direction,
    )
    return SentimentAlertResponseSchema(
        id=alert.id,
        symbol=alert.symbol,
        alert_type=alert.alert_type,
        threshold=alert.threshold,
        direction=alert.threshold_direction,
        is_active=alert.is_active,
        is_triggered=alert.is_triggered,
        last_triggered_at=alert.last_triggered_at,
        created_at=alert.created_at,
    )


@router.delete("/alerts/{alert_id}")
def delete_sentiment_alert(request, alert_id: int):
    """Delete a sentiment alert."""
    SentimentAlert.objects.filter(id=alert_id).delete()
    return {"status": "deleted"}


@router.get("/{symbol}", response=AggregatedSentimentSchema)
def get_symbol_sentiment(
    request, symbol: str, source: Optional[str] = None, timeframe: Optional[str] = "24h"
):
    """Get aggregated sentiment for a symbol."""
    analyzer = SentimentAnalyzer()
    return analyzer.get_aggregated_sentiment(symbol, source, timeframe)


@router.get("/{symbol}/posts", response=List[SocialPostSchema])
def get_symbol_posts(
    request, symbol: str, source: Optional[str] = None, limit: int = 50
):
    """Get social media posts for a symbol."""
    posts = SocialPost.objects.filter(symbol=symbol.upper())
    if source:
        posts = posts.filter(source=source)
    posts = posts.order_by("-created_at")[:limit]

    result = []
    for post in posts:
        sentiment = SentimentAnalysis.objects.filter(post=post).first()
        post_data = {
            "id": post.id,
            "source": post.source,
            "post_id": post.post_id,
            "author": post.author,
            "content": post.content,
            "symbols": [post.symbol],
            "followers_count": post.followers_count,
            "likes_count": 0,
            "comments_count": post.comments,
            "shares_count": post.shares,
            "engagement_score": post.engagement_score,
            "created_at": post.created_at,
        }
        if sentiment:
            post_data["sentiment_analysis"] = {
                "id": sentiment.id,
                "source": sentiment.source,
                "content_hash": "",
                "vader_compound": sentiment.vader_compound,
                "vader_positive": sentiment.vader_positive,
                "vader_negative": sentiment.vader_negative,
                "vader_neutral": sentiment.vader_neutral,
                "textblob_polarity": sentiment.textblob_polarity,
                "textblob_subjectivity": sentiment.textblob_subjectivity,
                "combined_score": sentiment.weighted_sentiment,
                "confidence": sentiment.confidence,
                "sentiment_label": sentiment.sentiment,
                "created_at": sentiment.created_at,
            }
        result.append(SocialPostSchema(**post_data))
    return result
