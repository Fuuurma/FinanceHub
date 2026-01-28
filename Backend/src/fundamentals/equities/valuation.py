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


class EquityOwnership(PeriodFundamental):
    """
    Institutional and insider ownership data.
    Tracks holdings, transactions, and share statistics.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_equity_ownership"
        verbose_name = "Equity Ownership"
        verbose_name_plural = "Equity Ownership"

    shares_outstanding = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        db_index=True,
        help_text="Total shares outstanding",
    )

    shares_float = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Public float (shares available for trading)",
    )

    shares_restricted = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Restricted shares",
    )

    shares_owned_by_insiders = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Shares owned by insiders",
    )

    shares_owned_by_institutions = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Shares owned by institutions",
    )

    insider_ownership_pct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Insider ownership percentage",
    )

    institutional_ownership_pct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Institutional ownership percentage",
    )

    short_interest = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Short interest (shares sold short)",
    )

    short_interest_pct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Short interest as percentage of float",
    )

    days_to_cover = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Days to cover (short interest / avg daily volume)",
    )

    institutional_transactions_qty = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Net institutional buying/selling quantity",
    )

    institutional_transactions_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net institutional transaction value in USD",
    )

    insider_transactions_qty = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Net insider buying/selling quantity",
    )

    insider_transactions_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net insider transaction value in USD",
    )

    number_of_institutional_holders = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of institutional holders",
    )

    number_of_insider_holders = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of insider holders",
    )

    avg_daily_volume_30d = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="30-day average daily volume",
    )

    stock_buyback_qty = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Shares repurchased in period",
    )

    stock_buyback_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Value of shares repurchased in USD",
    )
