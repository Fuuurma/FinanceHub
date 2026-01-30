from decimal import Decimal
from django.db import models

from fundamentals.base import FundamentalData


class BondMetrics(FundamentalData):
    """
    Bond metrics including treasury yields, corporate bonds, and credit ratings.
    Data primarily from FRED (Federal Reserve).
    """

    class Meta(FundamentalData.Meta):
        db_table = "fundamentals_bond_metrics"
        verbose_name = "Bond Metrics"
        verbose_name_plural = "Bond Metrics"

    bond_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Bond type (Treasury, Corporate, Municipal, etc.)",
    )

    yield_to_maturity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        db_index=True,
        help_text="Yield to maturity as decimal",
    )

    yield_to_maturity_change_1d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="1-day YTM change in basis points",
    )

    yield_to_maturity_change_30d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="30-day YTM change in basis points",
    )

    yield_to_maturity_change_ytd = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-to-date YTM change in basis points",
    )

    current_yield = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Current yield as decimal",
    )

    clean_price = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Clean price as percentage of par",
    )

    dirty_price = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Dirty price (including accrued interest)",
    )

    accrued_interest = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Accrued interest in percentage",
    )

    duration = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Macaulay duration in years",
    )

    modified_duration = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Modified duration",
    )

    convexity = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Convexity measure",
    )

    dv01 = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Dollar value of 01 (price change per bp move)",
    )

    maturity_years = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Years to maturity",
    )

    maturity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of maturity",
    )

    coupon_rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Annual coupon rate as decimal",
    )

    coupon_frequency = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Coupon frequency (annual, semi-annual, quarterly, monthly)",
    )

    next_coupon_date = models.DateField(
        null=True,
        blank=True,
        help_text="Next coupon payment date",
    )

    face_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Face/par value in USD",
    )

    issue_size = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total issue size in USD",
    )

    outstanding_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Outstanding amount in USD",
    )

    credit_rating = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Credit rating (AAA, AA+, AA, A+, A, BBB+, etc.)",
    )

    credit_rating_agency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Rating agency (S&P, Moody's, Fitch)",
    )

    credit_rating_outlook = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Rating outlook (Positive, Negative, Stable)",
    )

    credit_spread = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Credit spread over risk-free rate in basis points",
    )

    z_spread = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Z-spread in basis points",
    )

    OAS = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Option-adjusted spread in basis points",
    )

    recovery_rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Expected recovery rate in case of default",
    )

    default_probability = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Implied default probability",
    )

    isin = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        help_text="International Securities Identification Number",
    )

    cusip = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        help_text="Committee on Uniform Securities Identification Procedures number",
    )

    ticker = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Bond ticker symbol",
    )

    issuer_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Name of the bond issuer",
    )

    sector_fk = models.ForeignKey(
        "assets.Sector",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bond_metrics",
        help_text="Issuer sector (foreign key)",
    )
    sector = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="[DEPRECATED] Use sector_fk instead. Issuer sector (Technology, Financial, Government, etc.)",
    )

    country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Issuer country",
    )

    currency = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Bond currency (USD, EUR, GBP, etc.)",
    )

    putable = models.BooleanField(
        default=False,
        help_text="Whether bond is putable",
    )

    callable = models.BooleanField(
        default=False,
        help_text="Whether bond is callable",
    )

    convertible = models.BooleanField(
        default=False,
        help_text="Whether bond is convertible to equity",
    )

    first_call_date = models.DateField(
        null=True,
        blank=True,
        help_text="First call date if callable",
    )

    call_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Call price as percentage of par",
    )

    put_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Put price as percentage of par",
    )

    sinkable = models.BooleanField(
        default=False,
        help_text="Whether bond has sinking fund provision",
    )

    settlement_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Settlement period in business days",
    )

    day_count_convention = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Day count convention (30/360, Actual/Actual, etc.)",
    )

    trading_volume = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Daily trading volume in USD",
    )

    bid_price = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Bid price",
    )

    ask_price = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Ask price",
    )

    bid_ask_spread = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Bid-ask spread in basis points",
    )

    last_trade_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last trade",
    )

    trade_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of trades on last trade date",
    )
