"""
AI News Service
Provides AI-powered summarization, sentiment analysis, and asset extraction for news articles.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors"""

    pass


class AINewsService:
    """
    Service for AI-powered news analysis including:
    - Summarization
    - Sentiment analysis
    - Asset extraction
    - Impact scoring
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
                logger.info("AI News Service initialized with OpenAI client")
            except ImportError:
                logger.warning(
                    "OpenAI client not available. AI features will be mocked."
                )
                self.client = None
        else:
            logger.warning("No OpenAI API key configured. AI features will be mocked.")

    async def summarize_article(
        self, title: str, content: str, max_tokens: int = 150
    ) -> str:
        """
        Generate AI summary of a news article.

        Args:
            title: Article title
            content: Article content
            max_tokens: Maximum tokens for summary

        Returns:
            AI-generated summary (2-3 sentences)
        """
        if not self.client:
            return self._mock_summarize(title, content)

        prompt = f"""
        Summarize this financial news article in exactly 2-3 sentences.
        Focus on key information that affects investors.

        Title: {title}
        Content: {content[:3000]}

        Summary:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to summarize article: {e}")
            return self._mock_summarize(title, content)

    async def analyze_sentiment(self, title: str, content: str) -> Dict:
        """
        Analyze sentiment of a news article.

        Returns:
            {
                'score': float (-1.0 to 1.0),
                'label': str (POSITIVE/NEGATIVE/NEUTRAL),
                'key_points': List[str]
            }
        """
        if not self.client:
            return self._mock_sentiment(title, content)

        prompt = f"""
        Analyze the sentiment of this financial news article.
        Consider how this news might affect stock prices or market sentiment.

        Title: {title}
        Content: {content[:2000]}

        Return a JSON object with:
        - score: float from -1.0 (very negative/bearish) to 1.0 (very positive/bullish)
        - label: "POSITIVE", "NEGATIVE", or "NEUTRAL"
        - key_points: list of 3-5 key takeaways for investors
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "score": float(result.get("score", 0)),
                "label": result.get("label", "NEUTRAL"),
                "key_points": result.get("key_points", []),
            }
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return self._mock_sentiment(title, content)

    async def extract_asset_mentions(self, title: str, content: str) -> List[str]:
        """
        Extract stock/crypto symbols mentioned in article.

        Returns:
            List of asset symbols (e.g., ['AAPL', 'BTC', 'TSLA'])
        """
        if not self.client:
            return self._mock_extract_assets(title, content)

        prompt = f"""
        Extract all stock ticker symbols and cryptocurrency symbols mentioned in this article.
        Only include symbols that are clearly mentioned as ticker symbols (e.g., AAPL, TSLA, BTC, ETH).

        Title: {title}
        Content: {content[:2000]}

        Return a JSON object with:
        - symbols: list of symbols found
        - mentioned_count: how many times each symbol is mentioned
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("symbols", [])
        except Exception as e:
            logger.error(f"Failed to extract asset mentions: {e}")
            return self._mock_extract_assets(title, content)

    async def calculate_impact_score(
        self,
        title: str,
        content: str,
        sentiment_score: float,
        asset_mentions: List[str],
    ) -> float:
        """
        Calculate news impact score (0-100).

        Factors:
        - Sentiment strength
        - Number of assets mentioned
        - Keywords indicating market-moving news
        """
        if not self.client:
            return self._mock_impact_score(
                title, content, sentiment_score, asset_mentions
            )

        prompt = f"""
        Calculate an impact score (0-100) for this financial news article.
        Consider:
        - How market-moving is this news?
        - Does it affect multiple assets or the broader market?
        - Is it unexpected or anticipated?

        Title: {title}
        Content: {content[:1500]}
        Sentiment Score: {sentiment_score} (-1 to 1)
        Assets Mentioned: {", ".join(asset_mentions) if asset_mentions else "None"}

        Return JSON: {{"impact_score": <number 0-100>}}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            result = json.loads(response.choices[0].message.content)
            return min(100, max(0, float(result.get("impact_score", 50))))
        except Exception as e:
            logger.error(f"Failed to calculate impact score: {e}")
            return self._mock_impact_score(
                title, content, sentiment_score, asset_mentions
            )

    async def analyze_article_full(
        self, title: str, content: str, source: str = "unknown"
    ) -> Dict:
        """
        Complete analysis of a news article.

        Returns:
            {
                'summary': str,
                'sentiment': {'score': float, 'label': str, 'key_points': []},
                'asset_mentions': List[str],
                'impact_score': float
            }
        """
        logger.info(f"Analyzing article from {source}: {title[:50]}...")

        summary = await self.summarize_article(title, content)
        sentiment = await self.analyze_sentiment(title, content)
        asset_mentions = await self.extract_asset_mentions(title, content)
        impact_score = await self.calculate_impact_score(
            title, content, sentiment["score"], asset_mentions
        )

        return {
            "summary": summary,
            "sentiment": sentiment,
            "asset_mentions": asset_mentions,
            "impact_score": impact_score,
            "analyzed_at": timezone.now().isoformat(),
        }

    def _mock_summarize(self, title: str, content: str) -> str:
        """Mock summarization when AI is unavailable"""
        return f"News regarding {title[:30]}... Article discusses key developments that may impact market sentiment."

    def _mock_sentiment(self, title: str, content: str) -> Dict:
        """Mock sentiment when AI is unavailable"""
        content_lower = content.lower() if content else ""
        title_lower = title.lower() if title else ""

        keywords_positive = [
            "surge",
            "soar",
            "jump",
            "gain",
            "growth",
            "profit",
            "beat",
            "record",
        ]
        keywords_negative = [
            "fall",
            "drop",
            "plunge",
            "loss",
            "decline",
            "miss",
            "warning",
            "cut",
        ]

        score = 0
        for kw in keywords_positive:
            if kw in content_lower or kw in title_lower:
                score += 0.2
        for kw in keywords_negative:
            if kw in content_lower or kw in title_lower:
                score -= 0.2

        score = max(-1.0, min(1.0, score))

        if score > 0.2:
            label = "POSITIVE"
        elif score < -0.2:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        return {
            "score": round(score, 4),
            "label": label,
            "key_points": ["Key developments discussed in article"],
        }

    def _mock_extract_assets(self, title: str, content: str) -> List[str]:
        """Mock asset extraction when AI is unavailable"""
        import re

        patterns = [
            r"\b[A-Z]{1,5}\b",  # Potential stock symbols
        ]
        matches = set()
        text = f"{title} {content[:2000]}"
        for pattern in patterns:
            found = re.findall(pattern, text)
            for match in found:
                if len(match) >= 2 and match not in [
                    "THE",
                    "AND",
                    "FOR",
                    "THIS",
                    "THAT",
                    "WITH",
                    "FROM",
                    "HAVE",
                    "NOT",
                    "BUT",
                    "WILL",
                    "ARE",
                    "WAS",
                    "HAS",
                    "HAD",
                    "CAN",
                    "ALL",
                    "ONE",
                    "NEW",
                    "YEAR",
                    "AFTER",
                    "MORE",
                    "THAN",
                    "OVER",
                    "INTO",
                    "THEN",
                    "ONLY",
                    "ALSO",
                    "BACK",
                    "LIKE",
                    "EVEN",
                    "MOST",
                    "JUST",
                    "BEEN",
                    "NOW",
                    "SEE",
                    "WAY",
                    "WHO",
                    "GET",
                    "HOW",
                    "OUR",
                    "OUT",
                    "UP",
                    "US",
                    "IF",
                    "IS",
                    "IT",
                    "ON",
                    "BY",
                    "BE",
                    "AS",
                    "AT",
                    "SO",
                    "OR",
                    "AN",
                ]:
                    matches.add(match)
        return list(matches)[:10]

    def _mock_impact_score(
        self,
        title: str,
        content: str,
        sentiment_score: float,
        asset_mentions: List[str],
    ) -> float:
        """Mock impact score when AI is unavailable"""
        base_score = 50

        impact_keywords = {
            "earnings": 10,
            "quarterly": 8,
            "revenue": 7,
            "profit": 8,
            "acquisition": 12,
            "merger": 12,
            "lawsuit": 10,
            "investigation": 10,
            "ceo": 5,
            "founder": 5,
            "resign": 8,
            "fired": 8,
            "ipo": 15,
            "上市": 15,
            "offer": 5,
            "breaking": 15,
            "exclusive": 12,
            "report": 3,
            "fed": 10,
            "rate": 8,
            "inflation": 8,
            "recession": 10,
        }

        text = f"{title} {content[:1000]}".lower()
        for keyword, impact in impact_keywords.items():
            if keyword in text:
                base_score += impact

        sentiment_impact = abs(sentiment_score) * 15
        base_score += sentiment_impact

        asset_bonus = min(len(asset_mentions) * 2, 10)
        base_score += asset_bonus

        return min(100, max(0, round(base_score, 1)))


class NewsAggregatorService:
    """
    Service for aggregating and processing news from multiple sources.
    """

    def __init__(self):
        self.ai_service = AINewsService()

    async def process_article(
        self,
        title: str,
        content: str,
        url: str,
        source: str,
        published_at: datetime,
        description: Optional[str] = None,
        author: Optional[str] = None,
        image_url: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict:
        """
        Process a news article through AI analysis.

        Returns analyzed article data ready for database storage.
        """
        analysis = await self.ai_service.analyze_article_full(
            title=title, content=content or description or "", source=source
        )

        sentiment_label = analysis["sentiment"]["label"]
        sentiment_score = Decimal(str(analysis["sentiment"]["score"]))

        return {
            "title": title,
            "description": description,
            "url": url,
            "source": source,
            "author": author,
            "published_at": published_at,
            "image_url": image_url,
            "category": category,
            "sentiment": sentiment_label.lower(),
            "sentiment_score": sentiment_score,
            "related_symbols": analysis["asset_mentions"],
            "summary": analysis["summary"],
            "impact_score": Decimal(str(analysis["impact_score"])),
            "summary_generated_at": timezone.now(),
        }

    async def batch_process(self, articles: List[Dict]) -> List[Dict]:
        """
        Process multiple articles in batch.
        """
        results = []
        for article in articles:
            try:
                processed = await self.process_article(**article)
                results.append(processed)
            except Exception as e:
                logger.error(f"Failed to process article: {e}")
                results.append(
                    {"title": article.get("title", "Unknown"), "error": str(e)}
                )
        return results
