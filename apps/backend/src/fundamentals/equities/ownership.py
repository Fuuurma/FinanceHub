from decimal import Decimal
from django.db import models

from fundamentals.base import PeriodFundamental


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
