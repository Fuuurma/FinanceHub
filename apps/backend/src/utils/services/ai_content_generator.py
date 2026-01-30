"""
AI Content Generator
Prompt templates and content generation for AI advisor.
"""
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    MARKET_SUMMARY = "market_summary"
    ASSET_ANALYSIS = "asset_analysis"
    SECTOR_REPORT = "sector_report"
    RISK_COMMENTARY = "risk_commentary"
    SENTIMENT_SUMMARY = "sentiment_summary"
    VOLATILITY_OUTLOOK = "volatility_outlook"
    OPTIONS_STRATEGY = "options_strategy"
    BOND_MARKET = "bond_market"
    CRYPTO_MARKET = "crypto_market"
    PORTFOLIO_REPORT = "portfolio_report"
    HOLDINGS_ANALYSIS = "holdings_analysis"
    PERFORMANCE_ATTRIBUTION = "performance_attribution"
    RISK_ASSESSMENT = "risk_assessment"
    REBALANCING_SUGGESTION = "rebalancing_suggestion"


@dataclass
class ContentContext:
    """Context data for content generation."""
    symbol: Optional[str] = None
    sector: Optional[str] = None
    asset_class: Optional[str] = None
    
    # Price data
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    
    # Fundamentals
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    
    # Technicals
    rsi: Optional[float] = None
    macd: Optional[str] = None
    ma50: Optional[float] = None
    ma200: Optional[float] = None
    
    # Volatility
    volatility_daily: Optional[float] = None
    volatility_annual: Optional[float] = None
    
    # Sentiment
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    news_count: int = 0
    
    # Options
    iv_rank: Optional[float] = None
    put_call_ratio: Optional[float] = None
    
    # Portfolio data
    portfolio_value: Optional[float] = None
    total_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    var_95: Optional[float] = None
    holdings: List[Dict] = field(default_factory=list)
    sector_allocation: Dict[str, float] = field(default_factory=dict)
    
    # Risk metrics
    beta: Optional[float] = None
    max_drawdown: Optional[float] = None
    correlation_sp500: Optional[float] = None
    
    # Metadata
    model_used: str = "glm-4.7"
    confidence_level: float = 0.95
    generated_at: datetime = field(default_factory=datetime.now)


class PromptTemplates:
    """Prompt templates for different content types."""
    
    MARKET_SUMMARY = """You are a senior market analyst. Provide a comprehensive market summary.

**Market Data:**
- Index: {symbol}
- Current Level: {current_price}
- Daily Change: {price_change_pct:+.2f}%
- 52-Week Range: {low_52w:.2f} - {high_52w:.2f}
- Daily Volatility: {volatility_daily:.2f}%

**Sentiment:**
- Sentiment Score: {sentiment_score:.2f} ({sentiment_label})
- News Articles: {news_count}

**Technical:**
- RSI(14): {rsi}
- Distance from 50-MA: {ma50_distance:.2f}%

Generate a concise market summary with:
1. Market Direction (2-3 sentences)
2. Key Drivers (2-3 bullet points)
3. Technical Outlook
4. Sentiment Assessment
5. Watch List Levels (support/resistance)

Keep it professional, around 500 words. Use clear sections."""

    ASSET_ANALYSIS = """You are a senior equity analyst. Generate a comprehensive analysis for {symbol}.

**Price Data:**
- Current Price: ${current_price:.2f}
- Daily Change: {price_change_pct:+.2f}%
- 52-Week Range: ${low_52w:.2f} - ${high_52w:.2f}

**Fundamentals:**
- P/E Ratio: {pe_ratio:.2f}
- Market Cap: ${market_cap:,.0f}
- Dividend Yield: {dividend_yield:.2f}%
- EPS: ${eps:.2f}

**Technical Indicators:**
- RSI(14): {rsi}
- MACD: {macd}
- 50-Day MA: ${ma50:.2f} ({ma50_pct:.1f}% from price)
- 200-Day MA: ${ma200:.2f} ({ma200_pct:.1f}% from price)

**Volatility & Sentiment:**
- Annualized Volatility: {volatility_annual:.1f}%
- IV Rank: {iv_rank:.1f}%
- Put/Call Ratio: {put_call_ratio:.2f}
- Sentiment: {sentiment_score:.2f} ({sentiment_label})

Generate a comprehensive analysis with:
1. Executive Summary (2-3 sentences)
2. Fundamental Analysis
3. Technical Outlook
4. Options Market Insights
5. Sentiment Analysis
6. Catalysts to Watch
7. Risk Factors

Around 800 words. Be specific with numbers and price targets if applicable."""

    SECTOR_REPORT = """You are a sector strategist. Generate a sector analysis for {sector}.

**Sector Performance:**
- Daily Change: {price_change_pct:+.2f}%
- Volatility: {volatility_annual:.1f}%
- Sentiment: {sentiment_score:.2f} ({sentiment_label})

**Top Performers:**
{top_performers}

**Underperformers:**
{underperformers}

**Allocation Insights:**
{sector_allocation}

Generate a sector report with:
1. Sector Overview
2. Performance Drivers
3. Leading/Lagging Names
4. Technical Outlook
5. Sector-Specific Risks
6. Investment Implications

Around 700 words."""

    RISK_COMMENTARY = """You are a risk management specialist. Generate risk commentary for the portfolio/market.

**Risk Metrics:**
- VaR (95%): ${var_95:,.2f}
- Beta: {beta:.2f}
- Max Drawdown: {max_drawdown:.2f}%
- Correlation to S&P 500: {correlation_sp500:.2f}
- Volatility: {volatility_annual:.1f}%

**Market Conditions:**
- VIX/Sentiment: {sentiment_label} ({sentiment_score:.2f})
- Recent Drawdown: {price_change_pct:+.2f}%

**Historical Context:**
{historical_context}

Generate risk commentary with:
1. Current Risk Assessment
2. Key Risk Factors
3. Tail Risk Analysis
4. Hedging Recommendations
5. Portfolio Implications

Around 600 words. Be specific about potential losses under different scenarios."""

    SENTIMENT_SUMMARY = """You are a market sentiment analyst. Summarize sentiment for {symbol_or_market}.

**Sentiment Metrics:**
- Overall Score: {sentiment_score:.2f} ({sentiment_label})
- News Volume: {news_count} articles
- Social Mentions: {social_mentions:,}

**Sentiment Breakdown:**
- Positive: {positive_pct:.1f}%
- Neutral: {neutral_pct:.1f}%
- Negative: {negative_pct:.1f}%

**Key Themes:**
{key_themes}

**Recent Headlines:**
{headlines}

Generate a sentiment summary with:
1. Sentiment Overview
2. Key Themes Driving Sentiment
3. Noteworthy Headlines
4. Sentiment Trend (improving/deteriorating)
5. Trading Implications

Around 400 words."""

    VOLATILITY_OUTLOOK = """You are a volatility analyst. Generate volatility outlook for {symbol}.

**Volatility Metrics:**
- Current Daily Vol: {volatility_daily:.2f}%
- Annualized Vol: {volatility_annual:.1f}%
- IV Rank: {iv_rank:.1f}%
- IV Percentile: {iv_percentile:.1f}%

**GARCH Analysis:**
- Short-term Forecast: {garch_forecast:.1f}%
- Long-term Equilibrium: {garch_long_run:.1f}%
- Model Parameters: ω={omega:.6f}, α={alpha:.4f}, β={beta:.4f}

**Historical Volatility:**
- 10-day HV: {hv_10:.1f}%
- 30-day HV: {hv_30:.1f}%
- 60-day HV: {hv_60:.1f}%

Generate volatility outlook with:
1. Current Volatility Assessment
2. Volatility Forecast
3. Implied vs Realized Analysis
4. Trading/ hedging Implications
5. Key Dates/Events to Watch

Around 500 words."""

    OPTIONS_STRATEGY = """You are an options strategist. Generate strategy recommendations for {symbol}.

**Underlying:**
- Price: ${current_price:.2f}
- IV Rank: {iv_rank:.1f}%
- Put/Call Ratio: {put_call_ratio:.2f}

**Market Outlook:**
- Direction: {outlook}
- Time Horizon: {time_horizon}
- Volatility Expectation: {vol_expectation}

**Technical:**
- RSI: {rsi}
- Support: ${support:.2f}
- Resistance: ${resistance:.2f}

Generate options strategy recommendations with:
1. Outlook Summary
2. Recommended Strategies (2-3 max)
   - Strategy Name
   - Why it fits
   - Strike/Expiry rationale
   - Risk/Reward profile
   - Max risk and potential return
3. Key Risks
4. Alternative Strategies

Around 700 words. Be specific with strike prices and premiums."""

    BOND_MARKET = """You are a fixed income analyst. Generate bond market analysis.

**Yield Curve:**
- 2Y: {yield_2y:.2f}%
- 10Y: {yield_10y:.2f}%
- 30Y: {yield_30y:.2f}%
- 2s10s Spread: {spread_2s10s:.2f}%

**Bond Metrics:**
- Duration: {duration:.2f}
- Convexity: {convexity:.2f}
- OAS: {oas:.2f}%

**Credit Spreads:**
- IG Spread: {ig_spread:.2f}%
- HY Spread: {hy_spread:.2f}%

Generate bond market analysis with:
1. Yield Curve Assessment
2. Duration/Interest Rate Risk
3. Credit Market Conditions
4. Relative Value Analysis
5. Sector Recommendations

Around 600 words."""

    PORTFOLIO_REPORT = """You are a senior portfolio analyst. Generate a comprehensive portfolio report.

**Portfolio Summary:**
- Total Value: ${portfolio_value:,.2f}
- Total Return: {total_return:+.2f}%
- Sharpe Ratio: {sharpe_ratio:.2f}
- Max Drawdown: {max_drawdown:.2f}%

**Risk Metrics:**
- VaR (95%): ${var_95:,.2f}
- Beta: {beta:.2f}
- Correlation to S&P 500: {correlation_sp500:.2f}

**Top Holdings:**
{holdings_table}

**Sector Allocation:**
{sector_allocation}

**Performance Attribution:**
{performance_attribution}

**Risk Factors:**
{risk_factors}

Generate a comprehensive portfolio report with:
1. Executive Summary
2. Performance Analysis
3. Risk Assessment
4. Sector Exposure Analysis
5. Top Opportunities
6. Risk Mitigation Suggestions
7. Recommended Actions

Around 1200 words. Be specific with numbers and actionable recommendations."""


class ContentGenerator:
    """Generate AI content using prompt templates."""
    
    def __init__(self):
        self.templates = PromptTemplates()
    
    def generate(self, content_type: ContentType, context: ContentContext) -> Dict[str, Any]:
        """Generate content for given type and context."""
        template = getattr(self.templates, content_type.value.upper(), None)
        
        if not template:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Prepare template variables
        variables = self._prepare_variables(context)
        
        # Format template
        prompt = template.format(**variables)
        
        # Return structured data for LLM call
        return {
            "prompt": prompt,
            "content_type": content_type.value,
            "variables": variables,
            "max_tokens": self._get_max_tokens(content_type),
            "temperature": self._get_temperature(content_type),
        }
    
    def _prepare_variables(self, context: ContentContext) -> Dict[str, Any]:
        """Prepare template variables from context."""
        vars_dict = {
            "symbol": context.symbol or "MARKET",
            "sector": context.sector or "General",
            "asset_class": context.asset_class or "mixed",
            
            # Price data
            "current_price": context.current_price or 0,
            "price_change_pct": context.price_change_pct or 0,
            "high_52w": context.high_52w or 0,
            "low_52w": context.low_52w or 0,
            
            # Fundamentals
            "pe_ratio": context.pe_ratio or "N/A",
            "market_cap": context.market_cap or 0,
            "dividend_yield": context.dividend_yield or 0,
            "eps": context.eps or "N/A",
            
            # Technicals
            "rsi": context.rsi or "N/A",
            "macd": context.macd or "N/A",
            "ma50": context.ma50 or 0,
            "ma50_pct": round((context.current_price - context.ma50) / context.ma50 * 100, 1) if context.ma50 and context.current_price else 0,
            "ma200": context.ma200 or 0,
            "ma200_pct": round((context.current_price - context.ma200) / context.ma200 * 100, 1) if context.ma200 and context.current_price else 0,
            "ma50_distance": round((context.current_price - context.ma50) / context.ma50 * 100, 1) if context.ma50 and context.current_price else 0,
            
            # Volatility
            "volatility_daily": context.volatility_daily or 0,
            "volatility_annual": context.volatility_annual or 0,
            
            # Sentiment
            "sentiment_score": context.sentiment_score or 0.5,
            "sentiment_label": context.sentiment_label or "Neutral",
            "news_count": context.news_count,
            
            # Options
            "iv_rank": context.iv_rank or "N/A",
            "put_call_ratio": context.put_call_ratio or "N/A",
            
            # Portfolio data
            "portfolio_value": context.portfolio_value or 0,
            "total_return": context.total_return or 0,
            "sharpe_ratio": context.sharpe_ratio or 0,
            "var_95": context.var_95 or 0,
            
            # Risk metrics
            "beta": context.beta or 1.0,
            "max_drawdown": context.max_drawdown or 0,
            "correlation_sp500": context.correlation_sp500 or 0,
            
            # Holdings (formatted table)
            "holdings_table": self._format_holdings(context.holdings),
            "sector_allocation": self._format_sector_allocation(context.sector_allocation),
            
            # Top performers
            "top_performers": self._format_performers(context.holdings, top=True),
            "underperformers": self._format_performers(context.holdings, top=False),
            
            # Placeholders for complex fields
            "historical_context": "Recent market volatility has been elevated. VIX trading at elevated levels.",
            "key_themes": "- AI/LLM adoption\n- Interest rate policy\n- Earnings season",
            "headlines": "- Company X reports strong Q4 earnings\n- Analyst upgrades to Buy",
            "social_mentions": 15000,
            "positive_pct": 45,
            "neutral_pct": 35,
            "negative_pct": 20,
            
            # Vol specifics
            "garch_forecast": context.volatility_annual * 1.1 if context.volatility_annual else 25,
            "garch_long_run": context.volatility_annual * 0.9 if context.volatility_annual else 22,
            "omega": 0.0001,
            "alpha": 0.05,
            "beta": 0.90,
            "iv_percentile": context.iv_rank or 50,
            "hv_10": context.volatility_annual * 0.8 if context.volatility_annual else 20,
            "hv_30": context.volatility_annual if context.volatility_annual else 22,
            "hv_60": context.volatility_annual * 0.9 if context.volatility_annual else 23,
            
            # Options strategy
            "outlook": "bullish",
            "time_horizon": "1-2 weeks",
            "vol_expectation": "stable",
            "support": context.current_price * 0.95 if context.current_price else 0,
            "resistance": context.current_price * 1.05 if context.current_price else 0,
            
            # Bond market
            "yield_2y": 4.5,
            "yield_10y": 4.25,
            "yield_30y": 4.5,
            "spread_2s10s": -25,
            "duration": 6.5,
            "convexity": 0.8,
            "oas": 1.2,
            "ig_spread": 1.0,
            "hy_spread": 3.5,
            
            # Portfolio
            "performance_attribution": "Tech +2.1%, Energy -0.5%, Financials +0.8%",
            "risk_factors": "Concentration in tech (45%), Interest rate sensitivity, Market beta 1.15",
            
            # Generated at
            "generated_at": context.generated_at.strftime("%B %d, %Y"),
        }
        
        return vars_dict
    
    def _format_holdings(self, holdings: List[Dict]) -> str:
        """Format holdings as table."""
        if not holdings:
            return "No holdings data available."
        
        lines = ["| Symbol | Weight | Return | Risk |", "|-------|--------|--------|------|"]
        for h in holdings[:10]:
            lines.append(f"| {h.get('symbol', '?')} | {h.get('weight', 0):.1f}% | {h.get('return', 0):+.2f}% | {h.get('risk', 'M')} |")
        
        return "\n".join(lines)
    
    def _format_sector_allocation(self, allocation: Dict[str, float]) -> str:
        """Format sector allocation."""
        if not allocation:
            return "No allocation data available."
        
        lines = []
        for sector, weight in sorted(allocation.items(), key=lambda x: -x[1]):
            lines.append(f"- {sector}: {weight:.1f}%")
        
        return "\n".join(lines)
    
    def _format_performers(self, holdings: List[Dict], top: bool = True) -> str:
        """Format top/bottom performers."""
        if not holdings:
            return "No data available."
        
        sorted_holdings = sorted(holdings, key=lambda x: x.get('return', 0), reverse=top)
        performers = sorted_holdings[:5]
        
        lines = []
        for h in performers:
            lines.append(f"- {h.get('symbol', '?')}: {h.get('return', 0):+.2f}%")
        
        return "\n".join(lines)
    
    def _get_max_tokens(self, content_type: ContentType) -> int:
        """Get max tokens for content type."""
        token_limits = {
            ContentType.MARKET_SUMMARY: 800,
            ContentType.ASSET_ANALYSIS: 1200,
            ContentType.SECTOR_REPORT: 1000,
            ContentType.RISK_COMMENTARY: 800,
            ContentType.SENTIMENT_SUMMARY: 600,
            ContentType.VOLATILITY_OUTLOOK: 700,
            ContentType.OPTIONS_STRATEGY: 1000,
            ContentType.BOND_MARKET: 800,
            ContentType.PORTFOLIO_REPORT: 2000,
            ContentType.HOLDINGS_ANALYSIS: 1500,
            ContentType.PERFORMANCE_ATTRIBUTION: 1200,
            ContentType.RISK_ASSESSMENT: 1000,
            ContentType.REBALANCING_SUGGESTION: 1200,
        }
        return token_limits.get(content_type, 1000)
    
    def _get_temperature(self, content_type: ContentType) -> float:
        """Get temperature for content type."""
        if content_type in [ContentType.MARKET_SUMMARY, ContentType.SENTIMENT_SUMMARY]:
            return 0.5  # More factual
        elif content_type in [ContentType.OPTIONS_STRATEGY, ContentType.REBALANCING_SUGGESTION]:
            return 0.6  # Analytical but creative
        else:
            return 0.7  # Standard


def get_content_generator() -> ContentGenerator:
    """Get content generator singleton."""
    return ContentGenerator()
