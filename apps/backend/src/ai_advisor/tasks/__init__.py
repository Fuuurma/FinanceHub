"""
AI Advisor Tasks Package
Background tasks for template refresh and report generation.
"""

from ai_advisor.tasks.template_refresh import (
    refresh_stale_templates,
    generate_market_summary_task,
    generate_crypto_market_task,
    generate_asset_analysis_task,
    generate_sector_report_task,
    generate_risk_commentary_task,
    generate_sentiment_summary_task,
    generate_volatility_outlook_task,
    generate_bond_market_task,
    cleanup_old_template_logs,
)

from ai_advisor.tasks.user_reports import (
    generate_portfolio_report,
    generate_all_user_reports,
    generate_watchlist_report,
)

__all__ = [
    "refresh_stale_templates",
    "generate_market_summary_task",
    "generate_crypto_market_task",
    "generate_asset_analysis_task",
    "generate_sector_report_task",
    "generate_risk_commentary_task",
    "generate_sentiment_summary_task",
    "generate_volatility_outlook_task",
    "generate_bond_market_task",
    "cleanup_old_template_logs",
    "generate_portfolio_report",
    "generate_all_user_reports",
    "generate_watchlist_report",
]
