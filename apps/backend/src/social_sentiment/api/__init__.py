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


@router.get("/sentiment/{symbol}", response=AggregatedSentimentSchema)
def get_symbol_sentiment(
    request, symbol: str, source: Optional[str] = None, timeframe: Optional[str] = "24h"
):
    analyzer = SentimentAnalyzer()
    return analyzer.get_aggregated_sentiment(symbol, source, timeframe)


@router.get("/sentiment/{symbol}/posts", response=List[SocialPostSchema])
def get_symbol_posts(
    request, symbol: str, source: Optional[str] = None, limit: int = 50
):
    posts = SocialPost.objects.filter(symbols__icontains=symbol)
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
            "symbols": post.symbols_list,
            "followers_count": post.followers_count,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "engagement_score": post.engagement_score,
            "created_at": post.created_at,
        }
        if sentiment:
            post_data["sentiment_analysis"] = {
                "id": sentiment.id,
                "source": sentiment.source,
                "content_hash": sentiment.content_hash,
                "vader_compound": sentiment.vader_compound,
                "vader_positive": sentiment.vader_positive,
                "vader_negative": sentiment.vader_negative,
                "vader_neutral": sentiment.vader_neutral,
                "textblob_polarity": sentiment.textblob_polarity,
                "textblob_subjectivity": sentiment.textblob_subjectivity,
                "combined_score": sentiment.combined_score,
                "confidence": sentiment.confidence,
                "sentiment_label": sentiment.sentiment_label,
                "created_at": sentiment.created_at,
            }
        result.append(SocialPostSchema(**post_data))
    return result


@router.post("/sentiment/analyze", response=SentimentResponseSchema)
def analyze_sentiment(request, payload: SentimentRequestSchema):
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
    mentions = TickerMention.objects.all()
    if source:
        mentions = mentions.filter(source=source)

    mentions = mentions.order_by("-mention_count")[:limit]

    return [
        TickerTrendingSchema(
            symbol=m.symbol,
            mention_count=m.mention_count,
            sentiment_score=m.avg_sentiment,
            sentiment_change=m.sentiment_change,
            volume_spike=m.volume_spike,
        )
        for m in mentions
    ]


@router.get("/alerts", response=List[dict])
def get_sentiment_alerts(
    request, symbol: Optional[str] = None, active_only: bool = True
):
    alerts = SentimentAlert.objects.all()
    if symbol:
        alerts = alerts.filter(symbol=symbol.upper())
    if active_only:
        alerts = alerts.filter(is_active=True)

    return [
        {
            "id": alert.id,
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "threshold": alert.threshold,
            "direction": alert.direction,
            "is_active": alert.is_active,
            "is_triggered": alert.is_triggered,
            "last_triggered_at": alert.last_triggered_at,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]


@router.post("/alerts")
def create_sentiment_alert(
    request,
    symbol: str,
    alert_type: str,
    threshold: float,
    direction: str = "above",
):
    alert = SentimentAlert.objects.create(
        symbol=symbol.upper(),
        alert_type=alert_type,
        threshold=threshold,
        direction=direction,
    )
    return {"id": alert.id, "status": "created"}


@router.delete("/alerts/{alert_id}")
def delete_sentiment_alert(request, alert_id: int):
    SentimentAlert.objects.filter(id=alert_id).delete()
    return {"status": "deleted"}
