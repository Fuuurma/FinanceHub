"""
Sentiment Analysis Service
VADER + TextBlob based sentiment analysis
"""

import re
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logging.warning("VADER not installed. Install with: pip install vaderSentiment")

try:
    from textblob import TextBlob

    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not installed. Install with: pip install textblob")

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    sentiment: str
    vader_positive: Decimal
    vader_negative: Decimal
    vader_neutral: Decimal
    vader_compound: Decimal
    textblob_polarity: Decimal
    textblob_subjectivity: Decimal
    confidence: Decimal
    mentions: List[str]
    hashtags: List[str]


class TickerDetector:
    TICKER_PATTERN = re.compile(r"\$([A-Za-z]{1,5})\b")

    COMMON_STOCKS = {
        "AAPL",
        "MSFT",
        "GOOGL",
        "GOOG",
        "AMZN",
        "META",
        "NVDA",
        "TSLA",
        "BRK.B",
        "JPM",
        "V",
        "JNJ",
        "WMT",
        "PG",
        "MA",
        "UNH",
        "HD",
        "DIS",
        "BAC",
        "ADBE",
        "CRM",
        "NFLX",
        "PYPL",
        "INTC",
        "CSCO",
        "PFE",
        "T",
        "ABT",
        "ABBV",
        "NKE",
        "MRK",
        "PEP",
        "KO",
        "COST",
        "AVGO",
        "ACN",
        "MCD",
        "DHR",
        "TXN",
        "NEE",
        "MDT",
        "LLY",
        "AMD",
        "QCOM",
        "HON",
        "UPS",
        "BMY",
        "PM",
        "ORCL",
        "IBM",
    }

    CRYPTO = {
        "BTC",
        "ETH",
        "XRP",
        "ADA",
        "SOL",
        "DOGE",
        "DOT",
        "LTC",
        "LINK",
        "BCH",
        "XLM",
        "USDT",
        "USDC",
        "BNB",
        "MATIC",
        "AVAX",
    }

    @classmethod
    def extract_tickers(cls, text: str) -> List[str]:
        matches = cls.TICKER_PATTERN.findall(text)
        tickers = set()
        for match in matches:
            upper = match.upper()
            if upper in cls.COMMON_STOCKS or upper in cls.CRYPTO:
                tickers.add(upper)
        return list(tickers)

    @classmethod
    def is_crypto(cls, ticker: str) -> bool:
        return ticker.upper() in cls.CRYPTO


class SentimentAnalyzer:
    VADER_THRESHOLDS = {
        "positive": Decimal("0.05"),
        "negative": Decimal("-0.05"),
    }

    def __init__(self):
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
        else:
            self.vader_analyzer = None

        self._cache = {}
        self._cache_ttl = 300

    def analyze(self, text: str) -> SentimentResult:
        mentions = TickerDetector.extract_tickers(text)
        hashtags = self._extract_hashtags(text)
        clean_text = self._clean_text(text)

        vader_scores = self._analyze_vader(clean_text)
        textblob_scores = self._analyze_textblob(clean_text)

        sentiment = self._determine_sentiment(
            vader_scores["compound"], textblob_scores["polarity"]
        )

        confidence = self._calculate_confidence(vader_scores, textblob_scores)

        return SentimentResult(
            sentiment=sentiment,
            vader_positive=Decimal(str(vader_scores["pos"])),
            vader_negative=Decimal(str(vader_scores["neg"])),
            vader_neutral=Decimal(str(vader_scores["neu"])),
            vader_compound=Decimal(str(vader_scores["compound"])),
            textblob_polarity=Decimal(str(textblob_scores["polarity"])),
            textblob_subjectivity=Decimal(str(textblob_scores["subjectivity"])),
            confidence=confidence,
            mentions=mentions,
            hashtags=hashtags,
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(text) for text in texts]

    def _analyze_vader(self, text: str) -> Dict[str, float]:
        if not VADER_AVAILABLE or not self.vader_analyzer:
            return {"pos": 0.0, "neg": 0.0, "neu": 1.0, "compound": 0.0}

        scores = self.vader_analyzer.polarity_scores(text)
        return {
            "pos": scores["pos"],
            "neg": scores["neg"],
            "neu": scores["neu"],
            "compound": scores["compound"],
        }

    def _analyze_textblob(self, text: str) -> Dict[str, float]:
        if not TEXTBLOB_AVAILABLE:
            return {"polarity": 0.0, "subjectivity": 0.5}

        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
        }

    def _determine_sentiment(
        self, vader_compound: float, textblob_polarity: float
    ) -> str:
        avg_score = (Decimal(str(vader_compound)) + Decimal(str(textblob_polarity))) / 2

        if avg_score > self.VADER_THRESHOLDS["positive"]:
            return "positive"
        elif avg_score < self.VADER_THRESHOLDS["negative"]:
            return "negative"
        elif abs(avg_score) < Decimal("0.1"):
            return "neutral"
        else:
            return "mixed"

    def _calculate_confidence(self, vader: Dict, textblob: Dict) -> Decimal:
        vader_magnitude = abs(vader["compound"])
        textblob_magnitude = abs(textblob["polarity"])

        agreement = 1.0 - abs(vader["compound"] - textblob["polarity"]) / 2

        confidence = (vader_magnitude * 0.6 + textblob_magnitude * 0.4) * agreement
        confidence = min(Decimal("1.0"), max(Decimal("0.0"), Decimal(str(confidence))))

        return confidence

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"#(\w+)", r"\1", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return text.strip()

    def _extract_hashtags(self, text: str) -> List[str]:
        matches = re.findall(r"#(\w+)", text, re.IGNORECASE)
        return list(set([h.lower() for h in matches]))


class AggregatedSentiment:
    @staticmethod
    def aggregate(
        results: List[SentimentResult], weights: Optional[List[float]] = None
    ) -> Dict:
        if not results:
            return {
                "sentiment": "neutral",
                "vader_compound": Decimal("0"),
                "textblob_polarity": Decimal("0"),
                "confidence": Decimal("0"),
                "post_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        n = len(results)
        weights = weights or [1.0] * n

        vader_compound_sum = sum(
            float(r.vader_compound) * w for r, w in zip(results, weights)
        ) / sum(weights)

        textblob_polarity_sum = sum(
            float(r.textblob_polarity) * w for r, w in zip(results, weights)
        ) / sum(weights)

        confidence_sum = sum(
            float(r.confidence) * w for r, w in zip(results, weights)
        ) / sum(weights)

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
        for r in results:
            sentiment_counts[r.sentiment] += 1

        all_mentions = set()
        all_hashtags = set()
        for r in results:
            all_mentions.update(r.mentions)
            all_hashtags.update(r.hashtags)

        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)

        return {
            "sentiment": dominant_sentiment,
            "vader_compound": Decimal(str(vader_compound_sum)),
            "textblob_polarity": Decimal(str(textblob_polarity_sum)),
            "confidence": Decimal(str(confidence_sum)),
            "post_count": n,
            "positive_count": sentiment_counts["positive"],
            "negative_count": sentiment_counts["negative"],
            "neutral_count": sentiment_counts["neutral"],
            "mixed_count": sentiment_counts["mixed"],
            "top_mentions": list(all_mentions)[:10],
            "top_hashtags": list(all_hashtags)[:10],
        }

    @staticmethod
    def calculate_weight(post: Dict) -> float:
        weight = 1.0

        if post.get("followers_count", 0) > 10000:
            weight *= 1.5
        elif post.get("followers_count", 0) > 1000:
            weight *= 1.2

        engagement = post.get("engagement_score", 0)
        if engagement > 1000:
            weight *= 1.5
        elif engagement > 100:
            weight *= 1.2

        if post.get("is_retweet", False):
            weight *= 0.8

        return weight
