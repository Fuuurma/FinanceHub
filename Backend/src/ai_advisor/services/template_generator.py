"""
AI Template Generator Service
Generates AI templates using LLM with cache + live data fallback.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

from ai_advisor.models import AITemplate, AITemplateLog, TEMPLATE_TYPES
from utils.services.llm_advisor.ai_advisor import get_ai_advisor
from utils.services.cache_manager import get_cache_manager
from utils.services.data_orchestrator import get_data_orchestrator

logger = logging.getLogger(__name__)

# Cache TTLs in seconds
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_EXTRA_LONG = 21600  # 6 hours

# Tier access configuration
TEMPLATE_ACCESS_TIERS = {
    "market_summary": {
        "free": True,
        "premium": True,
        "ttl_free": 3600,
        "ttl_premium": 21600,
    },
    "asset_analysis": {
        "free": True,
        "premium": True,
        "ttl_free": 1800,
        "ttl_premium": 43200,
    },
    "sector_report": {"free": False, "premium": True, "ttl_premium": 86400},
    "risk_commentary": {
        "free": True,
        "premium": True,
        "ttl_free": 21600,
        "ttl_premium": 43200,
    },
    "sentiment_summary": {
        "free": True,
        "premium": True,
        "ttl_free": 7200,
        "ttl_premium": 21600,
    },
    "volatility_outlook": {"free": False, "premium": True, "ttl_premium": 43200},
    "options_strategy": {"free": False, "premium": True, "ttl_premium": 21600},
    "bond_market": {"free": False, "premium": True, "ttl_premium": 86400},
    "crypto_market": {
        "free": True,
        "premium": True,
        "ttl_free": 3600,
        "ttl_premium": 10800,
    },
    "earnings_preview": {"free": False, "premium": True, "ttl_premium": 43200},
    "macro_outlook": {"free": False, "premium": True, "ttl_premium": 86400},
}


class AITemplateGenerator:
    """
    Service for generating AI templates with caching and live data fallback.

    Features:
    - Cache-first data fetching
    - Fallback to live APIs on cache miss
    - LLM-powered content generation
    - Token usage tracking
    - Automatic refresh scheduling
    """

    def __init__(self):
        self.llm = get_ai_advisor()
        self.cache = get_cache_manager()
        self.orchestrator = get_data_orchestrator()
        self.refresh_intervals = {
            "market_summary": 6,  # Every 6 hours
            "asset_analysis": 12,  # Twice daily
            "sector_report": 24,  # Daily
            "risk_commentary": 12,  # Twice daily
            "sentiment_summary": 12,  # Twice daily
            "volatility_outlook": 12,  # Twice daily
            "options_strategy": 6,  # Every 6 hours
            "bond_market": 24,  # Daily
            "crypto_market": 6,  # Every 6 hours
            "earnings_preview": 12,  # Before earnings
            "macro_outlook": 24,  # Daily
        }

    async def generate_market_summary(self, force: bool = False) -> AITemplate:
        """Generate market summary template."""
        return await self._generate_template(
            template_type="market_summary",
            symbol="SPY",
            data_fetcher=self._fetch_market_summary_data,
            force=force,
        )

    async def generate_asset_analysis(
        self, symbol: str, force: bool = False
    ) -> AITemplate:
        """Generate asset analysis template for a specific symbol."""
        return await self._generate_template(
            template_type="asset_analysis",
            symbol=symbol.upper(),
            data_fetcher=lambda: self._fetch_asset_data(symbol),
            force=force,
        )

    async def generate_sector_report(
        self, sector: str, force: bool = False
    ) -> AITemplate:
        """Generate sector report template."""
        return await self._generate_template(
            template_type="sector_report",
            sector=sector,
            data_fetcher=lambda: self._fetch_sector_data(sector),
            force=force,
        )

    async def generate_risk_commentary(self, force: bool = False) -> AITemplate:
        """Generate risk commentary template."""
        return await self._generate_template(
            template_type="risk_commentary",
            symbol="SPY",
            data_fetcher=self._fetch_risk_data,
            force=force,
        )

    async def generate_sentiment_summary(self, force: bool = False) -> AITemplate:
        """Generate sentiment summary template."""
        return await self._generate_template(
            template_type="sentiment_summary",
            symbol="SPY",
            data_fetcher=self._fetch_sentiment_data,
            force=force,
        )

    async def generate_volatility_outlook(
        self, symbol: str = "SPY", force: bool = False
    ) -> AITemplate:
        """Generate volatility outlook template."""
        return await self._generate_template(
            template_type="volatility_outlook",
            symbol=symbol.upper(),
            data_fetcher=lambda: self._fetch_volatility_data(symbol),
            force=force,
        )

    async def generate_crypto_market(self, force: bool = False) -> AITemplate:
        """Generate crypto market analysis template."""
        return await self._generate_template(
            template_type="crypto_market",
            symbol="BTC",
            data_fetcher=self._fetch_crypto_data,
            force=force,
        )

    async def generate_bond_market(self, force: bool = False) -> AITemplate:
        """Generate bond market analysis template."""
        return await self._generate_template(
            template_type="bond_market",
            symbol="AGG",
            data_fetcher=self._fetch_bond_data,
            force=force,
        )

    async def _generate_template(
        self,
        template_type: str,
        data_fetcher,
        symbol: Optional[str] = None,
        sector: Optional[str] = None,
        asset_class: Optional[str] = None,
        force: bool = False,
    ) -> AITemplate:
        """Internal template generation with caching and logging."""

        # Check if template exists and is not stale
        if not force:
            existing = AITemplate.objects.filter(
                template_type=template_type,
                symbol=symbol,
                sector=sector,
                is_active=True,
            ).first()

            if existing and not existing.is_stale:
                return existing

        start_time = timezone.now()
        success = False
        error_message = None
        model_used = "glm-4.7"
        tokens_used = 0
        compute_time_ms = 0

        try:
            # Fetch data (cache-first, live fallback)
            data = await data_fetcher()

            # Build prompt based on template type
            prompt = self._build_prompt(template_type, data)

            # Generate content
            llm_result = await self.llm._call_llm(
                [
                    {
                        "role": "system",
                        "content": self._get_system_prompt(template_type),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )

            # Extract LLM metrics
            model_used = llm_result.model_used
            tokens_used = llm_result.tokens_used
            compute_time_ms = llm_result.compute_time_ms

            # Parse response
            content = llm_result.text
            title = self._extract_title(content, template_type, symbol or sector)
            summary = self._extract_summary(content)

            # Calculate next refresh
            interval_hours = self.refresh_intervals.get(template_type, 12)
            next_refresh = start_time + timedelta(hours=interval_hours)

            # Create or update template
            template, created = AITemplate.objects.update_or_create(
                template_type=template_type,
                symbol=symbol,
                sector=sector,
                asset_class=asset_class,
                defaults={
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "metadata": {
                        "data_sources": data.get("sources", []),
                        "model": model_used,
                        "tier": "premium"
                        if not TEMPLATE_ACCESS_TIERS.get(template_type, {}).get(
                            "free", True
                        )
                        else "free",
                    },
                    "version": 1,
                    "last_generated_at": start_time,
                    "next_refresh_at": next_refresh,
                    "is_active": True,
                    "generation_error": None,
                },
            )

            if not created:
                template.version += 1
                template.save()

            success = True

            # Log generation
            self._log_generation(
                template=template,
                template_type=template_type,
                symbol=symbol,
                success=True,
                model_used=model_used,
                tokens_used=tokens_used,
                compute_time_ms=compute_time_ms,
                input_data=data,
            )

            logger.info(f"Generated {template_type} template for {symbol or sector}")
            return template

        except Exception as e:
            error_message = str(e)
            success = False
            logger.error(f"Failed to generate {template_type} template: {e}")

            # Create or update template with error
            template, _ = AITemplate.objects.get_or_create(
                template_type=template_type,
                symbol=symbol,
                sector=sector,
                defaults={
                    "title": f"Error: {template_type.replace('_', ' ').title()}",
                    "content": f"Failed to generate: {error_message}",
                    "summary": "Generation failed",
                    "metadata": {},
                    "last_generated_at": start_time,
                    "next_refresh_at": start_time + timedelta(hours=1),
                    "is_active": False,
                    "generation_error": error_message,
                },
            )

            # Log failure
            self._log_generation(
                template=template,
                template_type=template_type,
                symbol=symbol,
                success=False,
                model_used=model_used,
                tokens_used=tokens_used,
                compute_time_ms=compute_time_ms,
                error_message=error_message,
            )

            raise

    async def _fetch_market_summary_data(self) -> Dict[str, Any]:
        """Fetch market summary data - cache first, live fallback."""
        data = {"sources": []}

        # Try cache first
        cached_indices = self.cache.get("market:indices")
        if cached_indices:
            data["indices"] = cached_indices
            data["sources"].append("cache")
        else:
            # Fetch live
            try:
                indices_data = await self.orchestrator.get_market_overview()
                data["indices"] = indices_data
                data["sources"].append("live")
                self.cache.set("market:indices", indices_data, ttl=CACHE_TTL_MEDIUM)
            except Exception as e:
                logger.warning(f"Failed to fetch indices: {e}")
                data["indices"] = {"SPY": {"price": 0, "change": 0}}

        # Get sentiment
        cached_sentiment = self.cache.get("market:sentiment")
        if cached_sentiment:
            data["sentiment"] = cached_sentiment
        else:
            try:
                sentiment = await self.orchestrator.get_sentiment_summary()
                data["sentiment"] = sentiment
                self.cache.set("market:sentiment", sentiment, ttl=CACHE_TTL_LONG)
            except Exception as e:
                logger.warning(f"Failed to fetch sentiment: {e}")

        return data

    async def _fetch_asset_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch asset-specific data."""
        data = {"symbol": symbol, "sources": []}

        # Try cache first
        cache_key = f"asset:{symbol}:analysis"
        cached = self.cache.get(cache_key)
        if cached:
            data.update(cached)
            data["sources"].append("cache")
            return data

        # Fetch live data
        try:
            overview = await self.orchestrator.get_asset_overview(symbol)
            fundamentals = await self.orchestrator.get_fundamentals(symbol)
            technical = await self.orchestrator.get_technical_indicators(symbol)
            sentiment = await self.orchestrator.get_sentiment(symbol)

            data.update(
                {
                    "overview": overview,
                    "fundamentals": fundamentals,
                    "technical": technical,
                    "sentiment": sentiment,
                }
            )
            data["sources"].append("live")

            # Cache result
            self.cache.set(cache_key, data, ttl=CACHE_TTL_MEDIUM)

        except Exception as e:
            logger.warning(f"Failed to fetch asset data for {symbol}: {e}")
            data["error"] = str(e)

        return data

    async def _fetch_sector_data(self, sector: str) -> Dict[str, Any]:
        """Fetch sector data."""
        data = {"sector": sector, "sources": []}

        cache_key = f"sector:{sector}:report"
        cached = self.cache.get(cache_key)
        if cached:
            data.update(cached)
            data["sources"].append("cache")
            return data

        try:
            sector_data = await self.orchestrator.get_sector_performance(sector)
            data["performance"] = sector_data
            data["sources"].append("live")
            self.cache.set(cache_key, data, ttl=CACHE_TTL_LONG)
        except Exception as e:
            logger.warning(f"Failed to fetch sector data for {sector}: {e}")

        return data

    async def _fetch_risk_data(self) -> Dict[str, Any]:
        """Fetch risk market data."""
        data = {"sources": []}

        cached = self.cache.get("market:risk")
        if cached:
            data.update(cached)
            data["sources"].append("cache")
        else:
            try:
                risk_metrics = await self.orchestrator.get_risk_metrics()
                data["risk"] = risk_metrics
                data["sources"].append("live")
                self.cache.set("market:risk", data, ttl=CACHE_TTL_MEDIUM)
            except Exception as e:
                logger.warning(f"Failed to fetch risk data: {e}")

        return data

    async def _fetch_sentiment_data(self) -> Dict[str, Any]:
        """Fetch market sentiment data."""
        data = {"sources": []}

        cached = self.cache.get("market:sentiment")
        if cached:
            data.update(cached)
            data["sources"].append("cache")
        else:
            try:
                sentiment = await self.orchestrator.get_sentiment_summary()
                data.update(sentiment)
                data["sources"].append("live")
                self.cache.set("market:sentiment", data, ttl=CACHE_TTL_MEDIUM)
            except Exception as e:
                logger.warning(f"Failed to fetch sentiment: {e}")

        return data

    async def _fetch_volatility_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch volatility data."""
        data = {"symbol": symbol, "sources": []}

        cache_key = f"asset:{symbol}:volatility"
        cached = self.cache.get(cache_key)
        if cached:
            data.update(cached)
            data["sources"].append("cache")
        else:
            try:
                vol_data = await self.orchestrator.get_volatility(symbol)
                data["volatility"] = vol_data
                data["sources"].append("live")
                self.cache.set(cache_key, data, ttl=CACHE_TTL_SHORT)
            except Exception as e:
                logger.warning(f"Failed to fetch volatility for {symbol}: {e}")

        return data

    async def _fetch_crypto_data(self) -> Dict[str, Any]:
        """Fetch crypto market data."""
        data = {"sources": []}

        cached = self.cache.get("crypto:market")
        if cached:
            data.update(cached)
            data["sources"].append("cache")
        else:
            try:
                crypto_data = await self.orchestrator.get_crypto_overview()
                data.update(crypto_data)
                data["sources"].append("live")
                self.cache.set("crypto:market", data, ttl=CACHE_TTL_SHORT)
            except Exception as e:
                logger.warning(f"Failed to fetch crypto data: {e}")

        return data

    async def _fetch_bond_data(self) -> Dict[str, Any]:
        """Fetch bond market data."""
        data = {"sources": []}

        cached = self.cache.get("fixed_income:market")
        if cached:
            data.update(cached)
            data["sources"].append("cache")
        else:
            try:
                bond_data = await self.orchestrator.get_bond_market_overview()
                data.update(bond_data)
                data["sources"].append("live")
                self.cache.set("fixed_income:market", data, ttl=CACHE_TTL_LONG)
            except Exception as e:
                logger.warning(f"Failed to fetch bond data: {e}")

        return data

    def _build_prompt(self, template_type: str, data: Dict[str, Any]) -> str:
        """Build LLM prompt based on template type and data."""
        base_prompts = {
            "market_summary": f"""
Generate a comprehensive market summary based on the following data:

Indices: {data.get("indices", {})}
Sentiment: {data.get("sentiment", {})}

Provide:
1. Market overview with key index movements
2. Sector performance highlights
3. Risk assessment
4. Outlook for next 24-48 hours

Keep it concise but informative. Use markdown formatting.
            """,
            "asset_analysis": f"""
Analyze {data.get("symbol", "this asset")} based on:

Overview: {data.get("overview", {})}
Fundamentals: {data.get("fundamentals", {})}
Technical: {data.get("technical", {})}
Sentiment: {data.get("sentiment", {})}

Provide:
1. Investment thesis (bull case & bear case)
2. Key metrics summary
3. Technical outlook
4. Risk factors
5. Recommendation (BUY/HOLD/SELL with confidence)

Use markdown formatting. Be objective and data-driven.
            """,
            "sector_report": f"""
Generate a sector report for {data.get("sector", "this sector")}:

Performance: {data.get("performance", {})}

Include:
1. Sector performance summary
2. Top performers and laggards
3. Key drivers
4. Outlook
5. Investment implications

Use markdown formatting.
            """,
            "crypto_market": f"""
Generate a crypto market analysis:

{data.get("data", {})}

Include:
1. Market overview (BTC, ETH, alts)
2. DeFi and NFT activity
3. Regulatory news
4. Technical outlook
5. Investment themes

Be concise and focus on actionable insights.
            """,
        }

        return base_prompts.get(template_type, f"Generate analysis for: {data}")

    def _get_system_prompt(self, template_type: str) -> str:
        """Get system prompt for template generation."""
        system_prompts = {
            "market_summary": """You are a senior market strategist. Provide clear, actionable market insights.""",
            "asset_analysis": """You are a fundamental analyst. Provide objective investment analysis based on data.""",
            "sector_report": """You are a sector analyst. Provide comprehensive sector analysis.""",
            "risk_commentary": """You are a risk manager. Assess market risks clearly.""",
            "sentiment_summary": """You are a market sentiment analyst. Interpret sentiment data objectively.""",
            "volatility_outlook": """You are a derivatives analyst. Analyze volatility patterns.""",
            "crypto_market": """You are a crypto market expert. Provide insights on digital assets.""",
            "bond_market": """You are a fixed income analyst. Analyze bond markets.""",
        }
        return system_prompts.get(template_type, "You are a financial analyst.")

    def _extract_title(self, content: str, template_type: str, scope: str) -> str:
        """Extract title from generated content."""
        lines = content.strip().split("\n")
        for line in lines[:5]:
            line = line.strip()
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return f"{template_type.replace('_', ' ').title()}: {scope}"

    def _extract_summary(self, content: str) -> str:
        """Extract summary from generated content (first ~200 chars)."""
        # Remove markdown headers
        text = "\n".join(
            line for line in content.split("\n") if not line.strip().startswith("#")
        )
        # Get first paragraph
        paragraphs = text.split("\n\n")
        for p in paragraphs:
            if p.strip():
                return p.strip()[:200]
        return content[:200]

    def _log_generation(
        self,
        template: AITemplate,
        template_type: str,
        symbol: Optional[str],
        success: bool,
        model_used: str,
        tokens_used: int,
        compute_time_ms: int,
        input_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
    ):
        """Log template generation event."""
        AITemplateLog.objects.create(
            template=template,
            template_type=template_type,
            symbol=symbol,
            success=success,
            error_message=error_message,
            model_used=model_used,
            input_tokens=tokens_used // 2,
            output_tokens=tokens_used // 2,
            total_tokens=tokens_used,
            compute_time_ms=compute_time_ms,
            input_data=input_data or {},
        )


def get_template_generator() -> AITemplateGenerator:
    """Get template generator instance."""
    return AITemplateGenerator()
