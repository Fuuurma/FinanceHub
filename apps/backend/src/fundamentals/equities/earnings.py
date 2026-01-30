from decimal import Decimal
from django.db import models

from fundamentals.base import PeriodFundamental


class EarningsReport(PeriodFundamental):
    """
    Quarterly and annual earnings reports.
    Tracks EPS, revenue, and earnings surprises.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_earnings_report"
        verbose_name = "Earnings Report"
        verbose_name_plural = "Earnings Reports"

    eps_actual = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Actual EPS for the period",
    )

    eps_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Estimated EPS (consensus)",
    )

    eps_difference = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="EPS difference (actual - estimate)",
    )

    eps_surprise_pct = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="EPS surprise percentage",
    )

    revenue_actual = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual revenue in USD",
    )

    revenue_estimate = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated revenue (consensus) in USD",
    )

    revenue_difference = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Revenue difference (actual - estimate) in USD",
    )

    revenue_surprise_pct = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Revenue surprise percentage",
    )

    net_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income in USD",
    )

    net_income_yoy_change = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year net income change",
    )

    gross_profit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross profit in USD",
    )

    operating_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Operating income in USD",
    )

    ebitda = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="EBITDA in USD",
    )

    eps_growth_qoq = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Quarter-over-quarter EPS growth",
    )

    eps_growth_yoy = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year EPS growth",
    )

    revenue_growth_qoq = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Quarter-over-quarter revenue growth",
    )

    revenue_growth_yoy = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year revenue growth",
    )

    number_of_estimates = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of analyst estimates used",
    )

    high_eps_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Highest EPS estimate",
    )

    low_eps_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Lowest EPS estimate",
    )

    standard_deviation_eps = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Standard deviation of EPS estimates",
    )

    announcement_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time of earnings announcement",
    )

    is_premarket = models.BooleanField(
        default=False,
        help_text="Whether earnings were announced pre-market",
    )

    is_after_hours = models.BooleanField(
        default=False,
        help_text="Whether earnings were announced after hours",
    )

    next_earnings_date = models.DateField(
        null=True,
        blank=True,
        help_text="Next estimated earnings date",
    )

    fiscal_guidance = models.TextField(
        null=True,
        blank=True,
        help_text="Company's fiscal guidance text",
    )

    eps_guidance_low = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Low end of EPS guidance range",
    )

    eps_guidance_high = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="High end of EPS guidance range",
    )

    revenue_guidance_low = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Low end of revenue guidance in USD",
    )

    revenue_guidance_high = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="High end of revenue guidance in USD",
    )

    quarter_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Fiscal quarter number (1-4)",
    )

    is_leap_year = models.BooleanField(
        default=False,
        help_text="Whether this is a leap year quarter",
    )

    trading_paused = models.BooleanField(
        default=False,
        help_text="Whether trading was paused during announcement",
    )
