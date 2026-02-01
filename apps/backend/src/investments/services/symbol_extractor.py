"""
Symbol Extraction Service
Extracts stock/crypto symbols from news articles using NLP and pattern matching
"""

import re
import logging
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import Counter

logger = logging.getLogger(__name__)


class SymbolExtractor:
    """
    Extract stock/crypto ticker symbols from article text.

    Methods:
    - Pattern matching for common formats ($AAPL, AAPL, BTC)
    - NLP-based entity recognition
    - Database lookup for validation
    - Symbol disambiguation
    """

    # Common ticker patterns
    TICKER_PATTERNS = [
        r"\$([A-Z]{1,5})\b",  # $AAPL, $BTC
        r"\b([A-Z]{1,5})\b",  # AAPL (standalone)
        r"\b([A-Z]{2,5})(?:\.|\s|$)",  # AAPL. or AAPL at end
        r"([A-Z]{2,5})\s+(?:stock|shares|shares)",  # AAPL stock
        r"(?:ticker|symbol)\s*[:=]?\s*([A-Z]{1,5})",  # ticker: AAPL
    ]

    # Crypto-specific patterns
    CRYPTO_PATTERNS = [
        r"\b(BTC|ETH|XRP|SOL|ADA|DOGE|BNB|LTC|LINK|MATIC|AVAX|DOT|UNI)\b",
        r"\b(Bitcoin|Ethereum|XRP|Solana|Cardano|Dogecoin)\b",
        r"(?:BTC|ETH|XRP)\s*(?:USD|USDT|DAI)?",
    ]

    # Keywords that indicate stock-related content
    STOCK_KEYWORDS = {
        "stock",
        "shares",
        "equity",
        "market",
        "trading",
        "traded",
        "nasdaq",
        "nyse",
        "sec",
        "earnings",
        "revenue",
        "quarterly",
        "ceo",
        "cfo",
        "board",
        "shareholder",
        "dividend",
        "ipo",
    }

    # Keywords that indicate crypto-related content
    CRYPTO_KEYWORDS = {
        "crypto",
        "cryptocurrency",
        "bitcoin",
        "ethereum",
        "blockchain",
        "defi",
        "token",
        "mining",
        "wallet",
        "exchange",
        "binance",
        "coin",
        "altcoin",
        "halving",
        " DAO ",
    }

    def __init__(self, valid_symbols: Set[str] = None, valid_cryptos: Set[str] = None):
        """
        Initialize symbol extractor.

        Args:
            valid_symbols: Set of valid stock ticker symbols
            valid_cryptos: Set of valid crypto symbols
        """
        self.valid_symbols = valid_symbols or set()
        self.valid_cryptos = valid_cryptos or set()

        # Common false positives to filter
        self.EXCLUDE_WORDS = {
            "THE",
            "AND",
            "FOR",
            "NOT",
            "BUT",
            "ALL",
            "ANY",
            "ARE",
            "WAS",
            "WERE",
            "HAS",
            "HAVE",
            "HAD",
            "CAN",
            "WILL",
            "JUST",
            "FROM",
            "THIS",
            "THAT",
            "WITH",
            "THEY",
            "YOU",
            "YOUR",
            "MORE",
            "ALSO",
            "NEW",
            "NOW",
            "YEAR",
            "YEARS",
            "FIRST",
            "LAST",
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE",
            "SAID",
            "SAYS",
            "US",
            "UK",
            "EU",
            "CEO",
            "CFO",
            "COO",
            "CTO",
            "IPO",
            "ETF",
            "USD",
            "EUR",
            "GBP",
            "JPY",
            "CNY",
            "GDP",
            "CPI",
            "PPI",
            "FED",
            "ECB",
            "BOE",
            "BOJ",
            "IMF",
            "WTO",
            "OIL",
            "GAS",
        }

        # Precompile regex patterns
        self._ticker_regex = [re.compile(p) for p in self.TICKER_PATTERNS]
        self._crypto_regex = [re.compile(p) for p in self.CRYPTO_PATTERNS]

    def load_valid_symbols(self, symbols: Set[str]):
        """Load valid stock ticker symbols"""
        self.valid_symbols = set(s.upper() for s in symbols)
        logger.info(f"Loaded {len(self.valid_symbols)} valid stock symbols")

    def load_valid_cryptos(self, cryptos: Set[str]):
        """Load valid crypto symbols"""
        self.valid_cryptos = set(s.upper() for s in cryptos)
        logger.info(f"Loaded {len(self.valid_cryptos)} valid crypto symbols")

    def load_from_database(self) -> bool:
        """Load symbols from Asset database"""
        try:
            from assets.models.asset import Asset

            stocks = Asset.objects.filter(
                asset_type__name__in=["stock", "etf"]
            ).values_list("symbol", flat=True)

            cryptos = Asset.objects.filter(
                asset_type__name__in=["crypto", "token"]
            ).values_list("symbol", flat=True)

            self.load_valid_symbols(set(s.upper() for s in stocks if s))
            self.load_valid_cryptos(set(s.upper() for s in cryptos if s))

            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error loading symbols from database: {e}")
            return False

    def extract_from_title(self, title: str) -> List[str]:
        """Extract symbols from article title (highest priority)"""
        if not title:
            return []

        symbols = set()
        title_upper = title.upper()

        # Check $ pattern first (most reliable)
        dollar_matches = re.findall(r"\$([A-Z]{1,5})\b", title_upper)
        for match in dollar_matches:
            if self._is_valid_symbol(match):
                symbols.add(match)

        # Check standalone tickers
        for pattern in self._ticker_regex:
            for match in pattern.findall(title):
                if self._is_valid_symbol(match):
                    symbols.add(match)

        # Check crypto names
        crypto_matches = self._extract_crypto_names(title)
        for match in crypto_matches:
            if self._is_valid_crypto(match):
                symbols.add(match)

        return list(symbols)

    def extract_from_text(self, text: str, max_symbols: int = 10) -> List[str]:
        """Extract symbols from full text"""
        if not text:
            return []

        symbols = set()
        text_upper = text.upper()

        # Extract from title first
        title_match = text.split("\n")[0][:200]  # First line/paragraph
        symbols.update(self.extract_from_title(title_match))

        # Extract $ patterns
        dollar_matches = re.findall(r"\$([A-Z]{1,5})\b", text_upper)
        for match in dollar_matches:
            if self._is_valid_symbol(match):
                symbols.add(match)

        # Limit to avoid noise
        if len(symbols) > max_symbols:
            # Keep only valid symbols that appear most frequently
            symbol_counts = Counter()
            for pattern in self._ticker_regex:
                for match in pattern.findall(text_upper):
                    if self._is_valid_symbol(match):
                        symbol_counts[match] += 1

            # Get top valid symbols
            valid_counts = {
                s: c for s, c in symbol_counts.items() if self._is_valid_symbol(s)
            }
            symbols = set(list(valid_counts.keys())[:max_symbols])

        return list(symbols)

    def extract_crypto_symbols(self, text: str) -> List[str]:
        """Extract crypto symbols from text"""
        if not text:
            return []

        symbols = set()
        text_upper = text.upper()

        # Check $ patterns for cryptos
        dollar_matches = re.findall(r"\$([A-Z]{2,5})\b", text_upper)
        for match in dollar_matches:
            if self._is_valid_crypto(match):
                symbols.add(match)

        # Check crypto names
        crypto_names = self._extract_crypto_names(text)
        for name in crypto_names:
            if self._is_valid_crypto(name):
                symbols.add(name)

        return list(symbols)

    def _extract_crypto_names(self, text: str) -> List[str]:
        """Extract full crypto names from text"""
        if not text:
            return []

        names = []
        text_lower = text.lower()

        crypto_names = {
            "BITCOIN": "BTC",
            "ETHEREUM": "ETH",
            "RIPPLE": "XRP",
            "SOLANA": "SOL",
            "CARDANO": "ADA",
            "DOGECOIN": "DOGE",
            "BINANCE": "BNB",
            "LITECOIN": "LTC",
            "CHAINLINK": "LINK",
            "POLYGON": "MATIC",
            "AVALANCHE": "AVAX",
            "POLKADOT": "DOT",
            "UNICORN": "UNI",
            "SHIBA INU": "SHIB",
        }

        for name, symbol in crypto_names.items():
            if name in text_lower:
                names.append(symbol)

        return names

    def _is_valid_symbol(self, symbol: str) -> bool:
        """Check if symbol is valid (in database or common list)"""
        if not symbol:
            return False

        symbol = symbol.upper()

        # Exclude common words
        if symbol in self.EXCLUDE_WORDS:
            return False

        # Must be in valid symbols or common stocks
        if self.valid_symbols and symbol not in self.valid_symbols:
            # Check if it's a known stock symbol
            if symbol not in self._get_common_stocks():
                return False

        return True

    def _is_valid_crypto(self, symbol: str) -> bool:
        """Check if symbol is a valid crypto"""
        if not symbol:
            return False

        symbol = symbol.upper()

        # Check explicit crypto list
        if self.valid_cryptos and symbol not in self.valid_cryptos:
            return False

        # Known cryptos
        known_cryptos = {
            "BTC",
            "ETH",
            "XRP",
            "SOL",
            "ADA",
            "DOGE",
            "BNB",
            "LTC",
            "LINK",
            "MATIC",
            "AVAX",
            "DOT",
            "UNI",
            "SHIB",
            "PEPE",
            "LRC",
            "NEAR",
            "ATOM",
            "ARB",
            "OP",
            "FIL",
            "STX",
        }

        if symbol not in known_cryptos:
            return False

        return True

    def _get_common_stocks(self) -> Set[str]:
        """Get common stock symbols for validation"""
        return {
            "AAPL",
            "MSFT",
            "GOOGL",
            "GOOG",
            "AMZN",
            "META",
            "TSLA",
            "NVDA",
            "JPM",
            "JNJ",
            "V",
            "PG",
            "UNH",
            "HD",
            "MA",
            "DIS",
            "BAC",
            "ADBE",
            "CRM",
            "NFLX",
            "PYPL",
            "INTC",
            "CMCSA",
            "KO",
            "PEP",
            "TMO",
            "COST",
            "ABBV",
            "ACN",
            "MCD",
            "DHR",
            "TXN",
            "AVGO",
            "LIN",
            "LLY",
            "NKE",
            "WMT",
            "MRK",
            "ABT",
            "ORCL",
            "MS",
            "RTX",
            "IBM",
            "CAT",
            "BMY",
            "AMGN",
            "UNP",
            "LOW",
            "GS",
            "HON",
            "UPS",
            "AMD",
            "DE",
            "SPGI",
            "PLD",
            "SBUX",
            "INTU",
            "AMAT",
            "SYK",
            "ZTS",
            "MSCI",
            "ADI",
            "NOW",
            "SHW",
        }

    def extract_all(self, title: str, text: str = "") -> List[str]:
        """
        Extract all symbols from title and text.

        Args:
            title: Article title
            text: Article body text (optional)

        Returns:
            List of extracted symbols
        """
        symbols = set()

        # Extract from title (highest priority)
        symbols.update(self.extract_from_title(title))

        # If no symbols from title, try text
        if not symbols and text:
            symbols.update(self.extract_from_text(text))

        return list(symbols)

    def count_symbols(self, articles: List[Dict]) -> Dict[str, int]:
        """Count symbol occurrences across multiple articles"""
        symbol_counts = Counter()

        for article in articles:
            symbols = self.extract_all(
                article.get("title", ""),
                article.get("description", "") + " " + article.get("content", ""),
            )
            for symbol in symbols:
                symbol_counts[symbol] += 1

        return dict(symbol_counts.most_common(50))

    def tag_articles(self, articles: List[Dict]) -> List[Dict]:
        """Add symbol tags to articles"""
        tagged = []

        for article in articles:
            symbols = self.extract_all(
                article.get("title", ""),
                article.get("description", "") + " " + article.get("content", ""),
            )

            tagged.append(
                {**article, "extracted_symbols": symbols, "symbol_count": len(symbols)}
            )

        return tagged


def extract_symbols_from_text(text: str, valid_symbols: Set[str] = None) -> List[str]:
    """Quick function to extract symbols from text"""
    extractor = SymbolExtractor(valid_symbols)
    return extractor.extract_all("", text)


class SentimentAnalyzer:
    """
    Simple sentiment analyzer for news articles.
    Falls back to VADER or Finnhub sentiment if available.
    """

    # Simple keyword-based sentiment (fallback)
    POSITIVE_WORDS = {
        "surge",
        "jump",
        "rise",
        "gain",
        "rally",
        "soar",
        "boom",
        "growth",
        "profit",
        "beat",
        "exceed",
        "optimistic",
        "bullish",
        "innovation",
        "breakthrough",
        "success",
        "record",
        "high",
    }

    NEGATIVE_WORDS = {
        "plunge",
        "drop",
        "fall",
        "crash",
        "slump",
        "sink",
        "tumble",
        "loss",
        "decline",
        "miss",
        "warning",
        "pessimistic",
        "bearish",
        "recession",
        "crisis",
        "risk",
        "threat",
        "concern",
        "fallout",
    }

    def __init__(self):
        self._vader_available = None

    def analyze_text(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of text.

        Returns:
            Tuple of (sentiment: 'positive'|'negative'|'neutral', score: -1.0 to 1.0)
        """
        if not text:
            return "neutral", 0.0

        # Try VADER if available
        if self._vader_available is None:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

                self._vader = SentimentIntensityAnalyzer()
                self._vader_available = True
            except ImportError:
                self._vader_available = False

        if self._vader_available:
            try:
                scores = self._vader.polarity_scores(text)
                compound = scores["compound"]

                if compound >= 0.05:
                    return "positive", compound
                elif compound <= -0.05:
                    return "negative", compound
                else:
                    return "neutral", compound
            except Exception:
                pass

        # Fallback to keyword-based
        return self._keyword_sentiment(text)

    def _keyword_sentiment(self, text: str) -> Tuple[str, float]:
        """Simple keyword-based sentiment analysis"""
        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))

        positive = len(words.intersection(self.POSITIVE_WORDS))
        negative = len(words.intersection(self.NEGATIVE_WORDS))

        total = positive + negative
        if total == 0:
            return "neutral", 0.0

        score = (positive - negative) / total

        if score > 0.2:
            return "positive", min(score, 1.0)
        elif score < -0.2:
            return "negative", max(score, -1.0)
        else:
            return "neutral", 0.0

    def analyze_article(self, article: Dict) -> Tuple[str, float]:
        """Analyze sentiment of article"""
        text = f"{article.get('title', '')} {article.get('description', '')}"
        return self.analyze_text(text)

    def batch_analyze(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment for batch of articles"""
        results = []

        for article in articles:
            sentiment, score = self.analyze_article(article)
            results.append(
                {**article, "sentiment": sentiment, "sentiment_score": round(score, 4)}
            )

        return results


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Factory function for sentiment analyzer"""
    return SentimentAnalyzer()
