from ninja import NinjaAPI

from utils.helpers.error_handler.error_handler import GlobalErrorHandler


api = NinjaAPI(
    title="FinanceHub API",
    version="1.0.0",
    description="Professional investment portfolio management API",
    docs_url="/docs",
    urls_namespace="api-v1",
)

GlobalErrorHandler.register_handlers(api)


# add routers from different modules here

from users.api.base import router as users_router
from assets.api.asset import router as assets_router
from portfolios.api.portfolio import router as portfolios_router
from api.unified_market_data import router as unified_market_data_router
from api.indicators import router as indicators_router
from api.alerts import router as alerts_router
from api.monitoring import router as monitoring_router
from api.websocket_auth import router as websocket_auth_router
from api.fundamentals import router as fundamentals_router
from api.market_overview import router as market_overview_router
from api.news_sentiment import router as news_sentiment_router
from api.portfolio_analytics import router as portfolio_analytics_router
from api.realtimedata import router as realtimedata_router
from api.health import router as health_router
from api.watchlist import router as watchlist_router
from api.analytics import router as analytics_router
from api.optimization import router as optimization_router
from api.options_pricing import router as options_pricing_router
from api.advanced_portfolio_optimization import router as advanced_portfolio_opt_router
from api.advanced_risk_management import router as advanced_risk_management_router
from api.fixed_income_analytics import router as fixed_income_analytics_router
from api.ai_advisor import router as ai_advisor_router
from api.ai_enhanced import router as ai_enhanced_router
from ai_advisor.api.templates import router as ai_templates_router
from ai_advisor.api.reports import router as ai_reports_router
from api.quantitative_models import router as quantitative_models_router
from trading.api.trading import router as trading_router
from charts.api.charts import router as charts_router
from api.currency import router as currency_router


# Register API exception handlers
from core.exceptions import APIException, ErrorResponse


@api.exception_handler(APIException)
def handle_api_exception(request, exc: APIException):
    """Handle APIException and return standardized error response."""
    return exc.to_response().model_dump()


api.add_router("/users", users_router)
api.add_router("/assets", assets_router)
api.add_router("/portfolios", portfolios_router)
api.add_router("/market", unified_market_data_router)
api.add_router("/indicators", indicators_router)
api.add_router("/alerts", alerts_router)
api.add_router("/monitoring", monitoring_router)
api.add_router("/watchlist", watchlist_router)
api.add_router("/auth", websocket_auth_router)
api.add_router("/fundamentals", fundamentals_router)
api.add_router("/overview", market_overview_router)
api.add_router("/news", news_sentiment_router)
api.add_router("/analytics", portfolio_analytics_router)
api.add_router("/realtime", realtimedata_router)
api.add_router("/health", health_router)
api.add_router("/analytics/v2", analytics_router)
api.add_router("/optimization", optimization_router)
api.add_router("/options", options_pricing_router)
api.add_router("/advanced-portfolio", advanced_portfolio_opt_router)
api.add_router("/advanced-risk", advanced_risk_management_router)
api.add_router("/fixed-income", fixed_income_analytics_router)
api.add_router("/ai", ai_advisor_router)
api.add_router("/ai/v2/enhanced", ai_enhanced_router)
api.add_router("/ai/v2/templates", ai_templates_router)
api.add_router("/ai/v2/reports", ai_reports_router)
api.add_router("/quantitative", quantitative_models_router)
api.add_router("/trading", trading_router)
api.add_router("/charts", charts_router)
api.add_router("/currency", currency_router)
