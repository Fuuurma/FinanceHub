from django.db import models
from django.core.validators import MinValueValidator

from assets.models.asset import Asset


class StockAsset(Asset):
    """Equity-specific fundamentals.

    Note: Most stock-specific fields (industry, sector, isin, cusip, pe_ratio, dividend_yield, eps, revenue_ttm)
    are now defined in the parent Asset model to support multiple asset types.
    This class is kept for future stock-specific extensions.
    """

    # todo: balance sheet, cash flow, dividends specific fields

    class Meta:
        db_table = "assets_stocks"
