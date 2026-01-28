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

api.add_router("/users", users_router)
api.add_router("/assets", assets_router)
api.add_router("/portfolios", portfolios_router)
api.add_router("/market", unified_market_data_router)
api.add_router("/indicators", indicators_router)
api.add_router("/alerts", alerts_router)
api.add_router("/monitoring", monitoring_router)
api.add_router("/auth", websocket_auth_router)
api.add_router("/fundamentals", fundamentals_router)
api.add_router("/overview", market_overview_router)
api.add_router("/news", news_sentiment_router)
api.add_router("/analytics", portfolio_analytics_router)
api.add_router("/realtime", realtimedata_router)
api.add_router("/health", health_router)
