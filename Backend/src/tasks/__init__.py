"""
AI Tasks Package
Template generation and user report tasks.
"""

from tasks.ai_template_generation import (
    generate_all_templates,
    generate_market_summaries,
    generate_asset_analysis,
    generate_sector_reports,
    generate_risk_commentary,
    generate_sentiment_summaries,
    generate_volatility_outlook,
    generate_options_strategies,
    generate_bond_market_analysis,
    generate_crypto_market_analysis,
    cleanup_expired_templates,
    cleanup_old_logs,
)

from tasks.ai_user_reports import (
    generate_user_portfolio_reports,
    generate_single_portfolio_report,
    generate_user_holdings_analysis,
    regenerate_stale_reports,
    cleanup_expired_user_reports,
)

__all__ = [
    # Template generation
    "generate_all_templates",
    "generate_market_summaries",
    "generate_asset_analysis",
    "generate_sector_reports",
    "generate_risk_commentary",
    "generate_sentiment_summaries",
    "generate_volatility_outlook",
    "generate_options_strategies",
    "generate_bond_market_analysis",
    "generate_crypto_market_analysis",
    "cleanup_expired_templates",
    "cleanup_old_logs",
    # User reports
    "generate_user_portfolio_reports",
    "generate_single_portfolio_report",
    "generate_user_holdings_analysis",
    "regenerate_stale_reports",
    "cleanup_expired_user_reports",
]
