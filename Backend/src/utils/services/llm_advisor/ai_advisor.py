"""
AI Advisor Service
Multi-provider LLM integration for financial advice and explanations.
Routes through local smart proxy server.
"""
import json
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

LLM_PROXY_URL = "http://localhost:8888/v4/chat/completions"
LLM_API_KEY = "dummy"

AI_FEATURE_CODE = "ai_advisor"
AI_USAGE_CACHE_KEY = "ai_usage:{user_id}:{date}"
MAX_DAILY_REQUESTS_FREE = 5
MAX_DAILY_REQUESTS_PAID = 100


@dataclass
class AIResponse:
    """AI response container."""
    text: str
    model_used: str
    tokens_used: int
    compute_time_ms: float
    cached: bool = False


@dataclass
class UsageStats:
    """AI usage statistics."""
    requests_today: int
    tokens_used_today: int
    last_request_at: Optional[datetime]
    remaining_today: int


class AIAdvisorService:
    """
    AI Advisor service with multi-provider LLM support.
    
    Uses local proxy to route to GLM (Zhipu AI) or MiniMax models.
    Supports feature gating based on subscription tier.
    """

    def __init__(self):
        self.proxy_url = LLM_PROXY_URL
        self.api_key = LLM_API_KEY
        self.default_model = "glm-4.7"
        self.coding_model = "minimax-m2.1"
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def check_feature_access(self, user) -> Dict[str, Any]:
        """
        Check if user has access to AI features.
        
        Args:
            user: Django user instance
            
        Returns:
            Dict with access status and limits
        """
        from users.models import AccountType

        is_active = user.is_subscription_active
        has_trial = user.is_trial_active
        
        account_type = user.account_type
        features = account_type.features or {}
        ai_enabled = features.get(AI_FEATURE_CODE, False)
        
        if isinstance(ai_enabled, str):
            ai_enabled = ai_enabled.lower() in ("true", "1", "yes")

        return {
            "has_access": is_active or has_trial or ai_enabled,
            "is_paid": is_active or ai_enabled,
            "is_trial": has_trial and not is_active,
            "max_requests": MAX_DAILY_REQUESTS_PAID if (is_active or ai_enabled) else MAX_DAILY_REQUESTS_FREE,
            "account_type": account_type.name,
            "feature_flag": ai_enabled
        }

    def get_usage_stats(self, user_id: str, date: str = None) -> UsageStats:
        """
        Get user's AI usage stats for today.
        
        Args:
            user_id: User UUID
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            UsageStats with request counts
        """
        from django.core.cache import cache
        from django.utils import timezone

        if date is None:
            date = timezone.now().strftime("%Y-%m-%d")

        cache_key = AI_USAGE_CACHE_KEY.format(user_id=str(user_id), date=date)
        cached = cache.get(cache_key, {"requests": 0, "tokens": 0, "last_request": None})

        return UsageStats(
            requests_today=cached["requests"],
            tokens_used_today=cached["tokens"],
            last_request_at=cached["last_request"],
            remaining_today=self.check_feature_access(
                type('User', (), {'account_type': type('AT', (), {'features': {AI_FEATURE_CODE: True}})(), 
                                 'is_subscription_active': True, 'is_trial_active': False})()
            )["max_requests"] - cached["requests"]
        )

    def record_usage(self, user_id: str, tokens: int) -> None:
        """
        Record AI usage for rate limiting.
        
        Args:
            user_id: User UUID
            tokens: Tokens used in request
        """
        from django.core.cache import cache
        from django.utils import timezone

        date = timezone.now().strftime("%Y-%m-%d")
        cache_key = AI_USAGE_CACHE_KEY.format(user_id=str(user_id), date=date)

        current = cache.get(cache_key, {"requests": 0, "tokens": 0, "last_request": None})
        current["requests"] = current["requests"] + 1
        current["tokens"] = current["tokens"] + tokens
        current["last_request"] = datetime.now()

        cache.set(cache_key, current, 86400)

    def _call_llm(self, messages: List[Dict[str, str]], model: str = None, 
                  max_tokens: int = 1000, temperature: float = 0.7) -> AIResponse:
        """
        Call LLM through local proxy.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to glm-4.7)
            max_tokens: Max response tokens
            temperature: Response creativity (0-1)
            
        Returns:
            AIResponse with generated text
        """
        start_time = time.perf_counter()
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = self._session.post(
                self.proxy_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            usage = data.get("usage", {})
            tokens = usage.get("total_tokens", len(content.split()) * 1.3)

            compute_time = (time.perf_counter() - start_time) * 1000

            return AIResponse(
                text=content,
                model_used=model,
                tokens_used=int(tokens),
                compute_time_ms=compute_time,
                cached=False
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM proxy error: {e}")
            raise AIAdvisorError(f"AI service unavailable: {str(e)}")

    def explain_options_strategy(
        self,
        strategy_type: str,
        underlying: str,
        strike: float,
        expiry: str,
        premium: float,
        direction: str = "long",
        user_context: str = ""
    ) -> AIResponse:
        """
        Generate plain-language explanation of an options strategy.
        
        Args:
            strategy_type: Strategy type (call, put, straddle, spread, etc.)
            underlying: Underlying asset symbol
            strike: Strike price
            expiry: Expiration date
            premium: Option premium
            direction: 'long' or 'short'
            user_context: Additional user context
            
        Returns:
            AIResponse with strategy explanation
        """
        system_prompt = """You are a financial advisor specializing in options. 
Explain options strategies in simple, clear language. Include:
1. What the strategy does in plain terms
2. Risk/reward profile
3. When to use it
4. Key risks to understand
Keep explanations concise but thorough. Use analogies when helpful."""

        user_prompt = f"""Explain this options strategy:

- Strategy: {strategy_type}
- Underlying: {underlying}
- Strike: ${strike}
- Expiration: {expiry}
- Premium: ${premium}
- Direction: {direction}
{f'- Additional context: {user_context}' if user_context else ''}

Explain in simple terms: What does this strategy do? What's the risk/reward? When would I use it?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self._call_llm(messages, max_tokens=800)

    def generate_forecast_narrative(
        self,
        symbol: str,
        current_price: float,
        forecast_data: Dict[str, Any],
        model_type: str,
        confidence_level: float,
        user_question: str = ""
    ) -> AIResponse:
        """
        Generate natural language forecast explanation.
        
        Args:
            symbol: Asset symbol
            current_price: Current price
            forecast_data: Forecast results from ARIMA/GARCH
            model_type: 'ARIMA' or 'GARCH'
            confidence_level: Confidence level (0-1)
            user_question: Specific question from user
            
        Returns:
            AIResponse with narrative explanation
        """
        system_prompt = """You are a financial analyst explaining forecasts. 
Make complex data understandable. Include:
1. What the forecast shows (in plain English)
2. Confidence level interpretation
3. Key drivers/trends
4. Important caveats
Be honest about uncertainty."""

        if model_type.upper() == "ARIMA":
            forecast_text = f"""ARIMA Forecast Analysis for {symbol}:

Current Price: ${current_price:.2f}

Forecast Points:
{chr(10).join([f'  - {k}: {v}' for k, v in forecast_data.get('forecast', {}).items()])}

Model Order (p,d,q): {forecast_data.get('order', 'N/A')}
AIC: {forecast_data.get('aic', 'N/A'):.2f}"""

        else:
            forecast_text = f"""GARCH Volatility Forecast for {symbol}:

Current Price: ${current_price:.2f}

Volatility Analysis:
- Current (Annualized): {forecast_data.get('current_volatility', 0)*100:.1f}%
- Forecast (Annualized): {forecast_data.get('forecast_volatility', 0)*100:.1f}%
- Model Parameters: omega={forecast_data.get('omega', 0):.6f}, alpha={forecast_data.get('alpha', 0):.4f}, beta={forecast_data.get('beta', 0):.4f}"""

        user_prompt = f"""{forecast_text}

Confidence Level: {confidence_level*100:.0f}%
{f'User Question: {user_question}' if user_question else ''}

Explain what this means in simple terms. What does the forecast suggest? What should I know about the uncertainty?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self._call_llm(messages, max_tokens=800)

    def suggest_options_strategy(
        self,
        market_outlook: str,
        risk_tolerance: str,
        underlying: str,
        current_price: float,
        time_horizon: str,
        preferred_direction: str = "both"
    ) -> AIResponse:
        """
        Suggest appropriate options strategies based on outlook.
        
        Args:
            market_outlook: Bullish, bearish, or neutral
            risk_tolerance: Low, medium, or high
            underlying: Asset symbol
            current_price: Current price
            time_horizon: Days/weeks/months
            preferred_direction: long, short, or both
            
        Returns:
            AIResponse with strategy suggestions
        """
        system_prompt = """You are an options strategist. Based on market outlook 
and risk tolerance, suggest appropriate option strategies. For each suggestion:
1. Strategy name
2. Why it fits the outlook
3. Risk/reward summary
4. Key considerations

Be practical and risk-aware. Suggest 2-3 strategies max."""

        user_prompt = f"""Suggest options strategies with details:

Market Outlook: {market_outlook}
Risk Tolerance: {risk_tolerance}
Underlying: {underlying}
Current Price: ${current_price:.2f}
Time Horizon: {time_horizon}
Preferred Direction: {preferred_direction}

For each strategy, include: strike range, expected premium, max risk, and potential return."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self._call_llm(messages, max_tokens=1000)

    def explain_risk_metric(
        self,
        metric_name: str,
        value: float,
        context: Dict[str, Any] = None,
        asset_type: str = "portfolio"
    ) -> AIResponse:
        """
        Explain risk metrics in plain language.
        
        Args:
            metric_name: VaR, CVaR, Beta, Sharpe, etc.
            value: Metric value
            context: Additional context (confidence level, etc.)
            asset_type: Portfolio, position, etc.
            
        Returns:
            AIResponse with explanation
        """
        system_prompt = """You are a risk analyst explaining metrics to retail investors.
Use simple analogies. Be accurate but accessible. Explain what the number means practically."""

        context_str = ""
        if context:
            context_parts = [f"{k}: {v}" for k, v in context.items()]
            context_str = f"\nAdditional context: {', '.join(context_parts)}"

        user_prompt = f"""Explain this risk metric:

Metric: {metric_name}
Value: {value}
Asset Type: {asset_type}{context_str}

What does this mean in simple terms? How should I interpret this number? What action (if any) should I take?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self._call_llm(messages, max_tokens=600)


class AIAdvisorError(Exception):
    """Custom exception for AI advisor errors."""
    pass


def get_ai_advisor() -> AIAdvisorService:
    """Get singleton AI advisor instance."""
    return AIAdvisorService()
