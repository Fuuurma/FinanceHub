from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class FundamentalData(UUIDModel, TimestampedModel):
    """
    Abstract base model for all fundamental data.
    All fundamental data models inherit from this.
    """

    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        help_text="The asset this fundamental data belongs to",
    )

    report_date = models.DateField(
        db_index=True,
        help_text="The date of the report or data point",
    )

    source = models.ForeignKey(
        "investments.DataProvider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_set",
        help_text="The data provider source",
    )

    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("1.00"))],
        help_text="Confidence score for the data (0.01-1.00)",
    )

    is_estimated = models.BooleanField(
        default=False,
        help_text="Whether this data point is estimated (not actual)",
    )

    data_quality_flags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of quality flags (e.g., ['adjusted', 'preliminary'])",
    )

    class Meta:
        abstract = True
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["asset", "-report_date"]),
            models.Index(fields=["report_date"]),
        ]


class PeriodFundamental(FundamentalData):
    """
    Abstract base for fundamental data with fiscal period information.
    Used for quarterly and annual data like earnings and financial statements.
    """

    class PeriodType(models.TextChoices):
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"
        TTM = "ttm", "Trailing 12 Months"
        MRQ = "mrq", "Most Recent Quarter"

    period_type = models.CharField(
        max_length=10,
        choices=PeriodType.choices,
        default=PeriodType.QUARTERLY,
        help_text="Type of fiscal period",
    )

    fiscal_year = models.IntegerField(
        db_index=True,
        help_text="Fiscal year of the report",
    )

    fiscal_period = models.IntegerField(
        null=True,
        blank=True,
        help_text="Fiscal quarter (1-4) or null for annual",
    )

    period_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date of the fiscal period",
    )

    is_restated = models.BooleanField(
        default=False,
        help_text="Whether this data has been restated from original filing",
    )

    original_report_date = models.DateField(
        null=True,
        blank=True,
        help_text="Original report date before restatement",
    )

    class Meta(FundamentalData.Meta):
        abstract = True
        unique_together = ["asset", "period_type", "fiscal_year", "fiscal_period"]
        indexes = [
            models.Index(fields=["asset", "period_type", "-fiscal_year", "fiscal_period"]),
        ]


class MarketCapMixin(models.Model):
    """
    Mixin for market capitalization related fields.
    """

    market_cap = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Market capitalization in USD",
    )

    enterprise_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enterprise value in USD",
    )

    class Meta:
        abstract = True


class RatioMixin(models.Model):
    """
    Mixin for common valuation ratio fields.
    """

    pe_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price to Earnings ratio",
    )

    pe_forward = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Forward P/E ratio",
    )

    pb_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price to Book ratio",
    )

    ps_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price to Sales ratio",
    )

    ev_ebitda = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Enterprise Value to EBITDA ratio",
    )

    ev_sales = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Enterprise Value to Sales ratio",
    )

    peg_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="PEG ratio (P/E to Growth)",
    )

    dividend_yield = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Dividend yield as decimal (e.g., 0.025 for 2.5%)",
    )

    payout_ratio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("100.00"))],
        help_text="Dividend payout ratio as percentage",
    )

    class Meta:
        abstract = True


class GrowthMixin(models.Model):
    """
    Mixin for growth rate fields.
    """

    revenue_growth_yoy = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year revenue growth as decimal",
    )

    earnings_growth_yoy = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year earnings growth as decimal",
    )

    revenue_growth_3y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="3-year annual revenue growth rate as decimal",
    )

    earnings_growth_3y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="3-year annual earnings growth rate as decimal",
    )

    revenue_growth_5y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="5-year annual revenue growth rate as decimal",
    )

    eps_growth_5y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="5-year annual EPS growth rate as decimal",
    )

    class Meta:
        abstract = True


class ProfitabilityMixin(models.Model):
    """
    Mixin for profitability margin fields.
    """

    gross_margin = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("100.00"))],
        help_text="Gross profit margin as percentage",
    )

    operating_margin = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("100.00"))],
        help_text="Operating margin as percentage",
    )

    net_margin = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("100.00"))],
        help_text="Net profit margin as percentage",
    )

    roe = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Return on Equity as decimal",
    )

    roa = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Return on Assets as decimal",
    )

    roic = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Return on Invested Capital as decimal",
    )

    ebitda_margin = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("100.00"))],
        help_text="EBITDA margin as percentage",
    )

    class Meta:
        abstract = True


class FinancialHealthMixin(models.Model):
    """
    Mixin for financial health and leverage fields.
    """

    debt_to_equity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Debt to Equity ratio",
    )

    debt_to_assets = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Debt to Assets ratio",
    )

    current_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Current ratio (current assets / current liabilities)",
    )

    quick_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Quick ratio (acid test)",
    )

    cash_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Cash ratio",
    )

    interest_coverage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Interest coverage ratio (EBIT / Interest Expense)",
    )

    equity_multiplier = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Equity multiplier (Assets / Equity)",
    )

    class Meta:
        abstract = True
