from decimal import Decimal
from django.db import models

from fundamentals.base import (
    PeriodFundamental,
    MarketCapMixin,
    RatioMixin,
    GrowthMixin,
    ProfitabilityMixin,
    FinancialHealthMixin,
)


class EquityValuation(PeriodFundamental, MarketCapMixin, RatioMixin):
    """
    Equity valuation metrics and ratios.
    Includes P/E, P/B, P/S, EV/EBITDA, dividend yields, and market caps.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_equity_valuation"
        verbose_name = "Equity Valuation"
        verbose_name_plural = "Equity Valuations"

    beta = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Stock beta relative to market",
    )

    beta_5y = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="5-year beta",
    )

    wacc = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Weighted Average Cost of Capital as decimal",
    )

    cost_of_equity = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Cost of equity as decimal",
    )

    price_to_fcf = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price to Free Cash Flow ratio",
    )

    ev_to_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Enterprise Value to Revenue ratio",
    )

    market_cap_to_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Market Cap to Revenue ratio (Price/Sales)",
    )

    price_to_nav = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price to Net Asset Value ratio",
    )

    price_to_earnings_growth = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price/Earnings to Growth ratio (PEG)",
    )

    ev_to_gbv = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Enterprise Value to Gross Book Value",
    )

    book_value_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Book value per share in USD",
    )

    earnings_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Earnings per share (EPS) in USD",
    )

    sales_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Sales per share in USD",
    )

    free_cash_flow_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Free cash flow per share in USD",
    )

    revenue_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Revenue per share in USD",
    )

    dividend_per_share = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Annual dividend per share in USD",
    )

    tangibles_book_value_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Tangible book value per share in USD",
    )
