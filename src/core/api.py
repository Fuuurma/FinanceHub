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
