from decimal import Decimal
from django.db import models

from fundamentals.base import FundamentalData


class CommodityMetrics(FundamentalData):
    """
    Commodity metrics including supply, demand, and production data.
    Sources: USGS, World Gold Council, EIA, LME.
    """

    class Meta(FundamentalData.Meta):
        db_table = "fundamentals_commodity_metrics"
        verbose_name = "Commodity Metrics"
        verbose_name_plural = "Commodity Metrics"

    commodity_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Commodity type (e.g., Gold, Oil, Wheat)",
    )

    spot_price = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        db_index=True,
        help_text="Current spot price in USD",
    )

    spot_price_change_24h = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="24-hour price change as decimal",
    )

    spot_price_change_30d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="30-day price change as decimal",
    )

    spot_price_change_ytd = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-to-date price change as decimal",
    )

    global_reserves = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Global reserves in ounces/tonnes/units",
    )

    global_reserves_change_1y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Annual change in reserves as decimal",
    )

    annual_production = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual production in ounces/tonnes",
    )

    annual_production_value = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual production value in USD",
    )

    annual_demand = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual demand in ounces/tonnes",
    )

    annual_demand_value = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual demand value in USD",
    )

    supply_demand_balance = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual supply/demand balance (surplus/deficit)",
    )

    inventory_levels = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Global inventory levels",
    )

    inventory_change_30d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="30-day inventory change as decimal",
    )

    backwardation_contango = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Contango/backwardation ratio (front/next month)",
    )

    basis_spread = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Basis spread between spot and futures",
    )

    cost_of_production = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Average cost of production in USD per unit",
    )

    all_in_sustaining_cost = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="AISC in USD per ounce (for metals)",
    )

    top_producers = models.JSONField(
        default=list,
        blank=True,
        help_text="List of top producing countries with volumes",
    )

    major_supply_sources = models.JSONField(
        default=list,
        blank=True,
        help_text="Major supply sources and percentages",
    )

    demand_breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text="Breakdown of demand by sector (jewelry, industrial, etc.)",
    )

    central_bank_holdings = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Central bank holdings in ounces",
    )

    central_bank_holdings_change = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Central bank net purchases in last year (ounces)",
    )

    jewelry_demand = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual jewelry demand in ounces",
    )

    industrial_demand = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual industrial demand in ounces",
    )

    investment_demand = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual investment demand in ounces",
    )

    open_interest = models.DecimalField(
        max_digits=30,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Futures open interest",
    )

    trading_volume_24h = models.DecimalField(
        max_digits=30,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="24-hour trading volume",
    )

    implied_volatility = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Implied volatility from options",
    )

    gold_silver_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Gold/Silver ratio (for precious metals)",
    )

    gold_platinum_spread = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Gold/Platinum spread in USD",
    )
