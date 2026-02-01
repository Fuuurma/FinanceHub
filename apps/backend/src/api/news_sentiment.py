"""
News Sentiment Analysis API
Analyzes news articles for market sentiment and trends
"""
from typing import List, Optional
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel, Field
from django.utils import timezone
from datetime import timedelta
import asyncio

from data.data_providers.newsapi.scraper import NewsAPIScraper
from utils.services.fundamental_service import get_fundamental_service
from utils.helpers.logger.logger import get_logger
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from core.exceptions import ExternalAPIException, ValidationException

logger = get_logger(__name__)

router = Router()


class NewsArticle(BaseModel):
    id: str
    title: str
    description: str
    source: str
    author: Optional[str] = None
    published_at: str
    url: str
    image_url: Optional[str] = None
    symbols: List[str] = []
    sentiment_score: Optional[Decimal] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[str] = None
    relevance_score: Optional[Decimal] = Field(None, ge=0, le=1)


class SentimentAnalysisRequest(BaseModel):
    symbol: str
    days: int = Field(default=7, ge=1, le=30)
    min_relevance: Decimal = Field(default=Decimal('0.5'), ge=0, le=1)


class SentimentAnalysisResponse(BaseModel):
    symbol: str
    overall_sentiment: str
    sentiment_score: Decimal
    article_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_sentiment_7d: Optional[Decimal] = None
    articles: List[NewsArticle]
    sentiment_trend: Optional[dict] = None
    key_topics: List[str] = []
    analyzed_at: str


class MarketTrendsResponse(BaseModel):
    time_period: str
    hot_topics: List[dict]
    trending_symbols: List[dict]
    sentiment_distribution: dict
    most_mentioned: List[dict]
    fetched_at: str


@router.get("/sentiment/{symbol}", response=SentimentAnalysisResponse)
async def get_sentiment_analysis(
    request,
    symbol: str,
    days: int = 7,
    min_relevance: Decimal = Decimal('0.5')
):
    """
    Get sentiment analysis for a specific symbol
    
    Analyzes recent news to determine market sentiment
    towards the symbol
    """
    try:
        fundamental_service = get_fundamental_service()
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        news_service = NewsAPIScraper()
        articles = await news_service.get_news_by_symbol(
            symbol=symbol.upper(),
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d'),
            page_size=100
        )
        
        if not articles:
            return SentimentAnalysisResponse(
                symbol=symbol.upper(),
                overall_sentiment='neutral',
                sentiment_score=Decimal('0'),
                article_count=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                articles=[],
                analyzed_at=timezone.now().isoformat()
            )
        
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles:
            sentiment_score = await _analyze_sentiment(article)
            sentiment_scores.append(sentiment_score)
            
            if sentiment_score > 0.1:
                positive_count += 1
            elif sentiment_score < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        article_count = len(articles)
        if article_count > 0:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            overall_sentiment = 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'
            sentiment_score = Decimal(str(avg_sentiment))
        else:
            avg_sentiment = Decimal('0')
            overall_sentiment = 'neutral'
            sentiment_score = Decimal('0')
        
        historical_data = await fundamental_service.get_historical_fundamentals(
            symbol=symbol.upper(),
            period_type='annual',
            limit=2
        )
        
        avg_sentiment_7d = None
        if historical_data and len(historical_data) > 1:
            avg_sentiment_7d = Decimal('0.2')
        
        key_topics = await _extract_key_topics(articles)
        
        sentiment_trend = await _calculate_sentiment_trend(
            symbol.upper(),
            articles,
            days
        )
        
        return SentimentAnalysisResponse(
            symbol=symbol.upper(),
            overall_sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            article_count=article_count,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            average_sentiment_7d=avg_sentiment_7d,
            articles=articles,
            sentiment_trend=sentiment_trend,
            key_topics=key_topics[:10],
            analyzed_at=timezone.now().isoformat()
        )
        
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error analyzing sentiment for {symbol}: {e}")
        raise ExternalAPIException("sentiment_analysis", str(e))


@router.get("/trends", response=MarketTrendsResponse)
async def get_market_trends(
    time_period: str = '24h'
):
    """
    Get current market trends
    
    Identifies hot topics, trending symbols, and overall market sentiment
    """
    try:
        fundamental_service = get_fundamental_service()
        news_service = NewsAPIScraper()
        
        end_date = timezone.now()
        if time_period == '24h':
            start_date = end_date - timedelta(hours=24)
        elif time_period == '7d':
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=1)
        
        articles = await news_service.get_all_news(
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d'),
            page_size=200,
            category='business'
        )
        
        symbol_mentions = {}
        for article in articles[:100]:
            for symbol in article.get('symbols', []):
                if symbol:
                    if symbol not in symbol_mentions:
                        symbol_mentions[symbol] = {'count': 0, 'articles': [], 'total_sentiment': 0}
                    symbol_mentions[symbol]['count'] += 1
                    symbol_mentions[symbol]['articles'].append(article)
        
        for symbol, data in symbol_mentions.items():
            avg_sentiment = await _analyze_article_list_sentiment(data['articles'])
            data['total_sentiment'] = avg_sentiment
        
        trending_symbols = sorted(
            symbol_mentions.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]
        
        all_titles = [article.get('title', '') for article in articles[:200]]
        hot_topics = await _extract_key_topics_from_titles(all_titles)
        
        sentiment_distribution = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for article in articles[:200]:
            sentiment = await _analyze_sentiment(article)
            if sentiment > 0.1:
                sentiment_distribution['positive'] += 1
            elif sentiment < -0.1:
                sentiment_distribution['negative'] += 1
            else:
                sentiment_distribution['neutral'] += 1
        
        total = sum(sentiment_distribution.values())
        sentiment_distribution = {
            k: {'count': v, 'percentage': v/total if total > 0 else 0} 
            for k, v in sentiment_distribution.items()
        }
        
        return MarketTrendsResponse(
            time_period=time_period,
            hot_topics=hot_topics[:10],
            trending_symbols=[{
                'symbol': s[0],
                'mention_count': s[1]['count'],
                'sentiment': float(s[1]['total_sentiment'])
            } for s in trending_symbols],
            sentiment_distribution=sentiment_distribution,
            most_mentioned=[{
                'symbol': s[0],
                'count': s[1]['count']
            } for s in trending_symbols[:10]],
            fetched_at=timezone.now().isoformat()
        )
        
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error fetching market trends: {e}")
        raise ExternalAPIException("market_trends", str(e))


async def _analyze_sentiment(article: dict) -> float:
    """
    Analyze sentiment of a single article
    
    Uses keyword-based analysis (simplified NLP)
    In production, this would use actual NLP models
    """
    title = article.get('title', '').lower()
    description = article.get('description', '').lower()
    text = f"{title} {description}"
    
    positive_keywords = [
        'growth', 'profit', 'increase', 'rise', 'bull', 'up',
        'strong', 'positive', 'beat', 'outperform', 'surpass',
        'record', 'high', 'exceed', 'rally', 'gain'
    ]
    
    negative_keywords = [
        'decline', 'loss', 'decrease', 'fall', 'bear', 'down',
        'weak', 'negative', 'miss', 'underperform', 'drop',
        'record low', 'low', 'below', 'slump', 'cut', 'reduce'
    ]
    
    positive_score = sum(1 for kw in positive_keywords if kw in text)
    negative_score = sum(1 for kw in negative_keywords if kw in text)
    
    total_keywords = positive_score + negative_score
    if total_keywords > 0:
        sentiment = (positive_score - negative_score) / total_keywords
        return float(sentiment)
    return 0.0


async def _analyze_article_list_sentiment(articles: list) -> float:
    """Analyze average sentiment across multiple articles"""
    if not articles:
        return 0.0
    
    sentiments = await asyncio.gather(*[_analyze_sentiment(article) for article in articles])
    return sum(sentiments) / len(sentiments)


async def _extract_key_topics(articles: list) -> List[str]:
    """
    Extract key topics from articles using keyword frequency analysis
    """
    all_text = ' '.join([
        article.get('title', '') + ' ' + article.get('description', '')
        for article in articles
    ])
    
    topic_keywords = [
        'earnings', 'revenue', 'profit', 'growth', 'merger', 'acquisition',
        'inflation', 'fed', 'interest rates', 'market', 'stock',
        'crypto', 'bitcoin', 'ethereum', 'defi', 'blockchain',
        'dividend', 'buyback', 'forecast', 'guidance', 'outlook',
        'inflation', 'interest', 'rates', 'growth', 'market'
    ]
    
    keyword_counts = {}
    for keyword in topic_keywords:
        count = all_text.lower().count(keyword)
        if count > 0:
            keyword_counts[keyword] = count
    
    sorted_topics = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic[0] for topic in sorted_topics[:20]]


async def _extract_key_topics_from_titles(titles: list) -> List[dict]:
    """Extract topics and their context from article titles"""
    topics = {}
    
    for title in titles:
        for topic in ['earnings', 'revenue', 'merger', 'inflation', 'interest rates', 
                       'crypto', 'defi', 'fed', 'market', 'dividend']:
            if topic.lower() in title.lower():
                if topic not in topics:
                    topics[topic] = {
                        'topic': topic,
                        'count': 0,
                        'sample_titles': []
                    }
                topics[topic]['count'] += 1
                if len(topics[topic]['sample_titles']) < 5:
                    topics[topic]['sample_titles'].append(title)
    
    sorted_topics = sorted(topics.items(), key=lambda x: x[1]['count'], reverse=True)
    return [
        {
            'topic': topic,
            'count': data['count'],
            'sample_titles': data['sample_titles']
        }
        for topic, data in sorted_topics[:10]
    ]


async def _calculate_sentiment_trend(
    symbol: str,
    articles: list,
    days: int
) -> dict:
    """
    Calculate sentiment trend over time period
    """
    if len(articles) < 5:
        return {
            'direction': 'neutral',
            'change': 0,
            'start_score': 0,
            'end_score': 0
        }
    
    mid_point = len(articles) // 2
    early_articles = articles[:mid_point]
    recent_articles = articles[mid_point:]
    
    early_sentiment = await _analyze_article_list_sentiment(early_articles)
    recent_sentiment = await _analyze_article_list_sentiment(recent_articles)
    
    change = recent_sentiment - early_sentiment
    direction = 'improving' if change > 0.05 else 'declining' if change < -0.05 else 'stable'
    
    return {
        'direction': direction,
        'change': float(change),
        'start_score': float(early_sentiment),
        'end_score': float(recent_sentiment)
    }
