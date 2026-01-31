from django.db import models
from portfolios.models.portfolio import Portfolio
from assets.models.asset import Asset
from decimal import Decimal


class PortfolioSectorAllocation(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="sector_allocations"
    )
    sector = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["portfolio", "sector"]
        ordering = ["-percentage"]
        indexes = [
            models.Index(fields=["portfolio", "sector"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - {self.sector}: {self.percentage}%"


class PortfolioGeographicAllocation(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="geographic_allocations"
    )
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, default="")
    country_code = models.CharField(max_length=3, blank=True, default="")
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["portfolio", "country"]
        ordering = ["-percentage"]
        indexes = [
            models.Index(fields=["portfolio", "country"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - {self.country}: {self.percentage}%"


class PortfolioAssetClassAllocation(models.Model):
    ASSET_CLASS_CHOICES = [
        ("stock", "Stock"),
        ("bond", "Bond"),
        ("crypto", "Crypto"),
        ("cash", "Cash"),
        ("commodity", "Commodity"),
        ("etf", "ETF"),
        ("real_estate", "Real Estate"),
        ("other", "Other"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="asset_class_allocations"
    )
    asset_class = models.CharField(max_length=50, choices=ASSET_CLASS_CHOICES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["portfolio", "asset_class"]
        ordering = ["asset_class"]
        indexes = [
            models.Index(fields=["portfolio", "asset_class"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset_class}: {self.percentage}%"


class PortfolioConcentrationRisk(models.Model):
    CONCENTRATION_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("VERY_HIGH", "Very High"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="concentration_risks"
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="concentration_records"
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    concentration_score = models.DecimalField(max_digits=5, decimal_places=2)
    concentration_level = models.CharField(
        max_length=20, choices=CONCENTRATION_LEVEL_CHOICES
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-percentage"]
        indexes = [
            models.Index(fields=["portfolio", "asset"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.symbol}: {self.percentage}% ({self.concentration_level})"


class PortfolioBeta(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="beta_records"
    )
    benchmark = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Benchmark asset (e.g., SPY)",
    )
    beta = models.DecimalField(max_digits=10, decimal_places=4)
    correlation = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    r_squared = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    calculated_at = models.DateTimeField(auto_now=True)
    calculation_period_days = models.IntegerField(default=252)

    class Meta:
        ordering = ["-calculated_at"]
        indexes = [
            models.Index(fields=["portfolio", "benchmark"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - Beta: {self.beta} vs {self.benchmark.symbol}"


class PerformanceAttribution(models.Model):
    ATTRIBUTION_TYPE_CHOICES = [
        ("SECURITY", "By Security"),
        ("SECTOR", "By Sector"),
        ("FACTOR", "By Factor"),
        ("ASSET_CLASS", "By Asset Class"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="performance_attributions"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    attribution_type = models.CharField(max_length=20, choices=ATTRIBUTION_TYPE_CHOICES)
    category = models.CharField(
        max_length=100, help_text="Security, sector, or factor name"
    )
    category_return = models.DecimalField(max_digits=10, decimal_places=4)
    benchmark_return = models.DecimalField(max_digits=10, decimal_places=4)
    allocation_effect = models.DecimalField(max_digits=10, decimal_places=4)
    selection_effect = models.DecimalField(max_digits=10, decimal_places=4)
    interaction_effect = models.DecimalField(max_digits=10, decimal_places=4)
    total_attribution = models.DecimalField(max_digits=10, decimal_places=4)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end", "-calculated_at"]
        indexes = [
            models.Index(fields=["portfolio", "period_start", "period_end"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - {self.period_start} to {self.period_end}: {self.attribution_type}"


class PortfolioRiskMetrics(models.Model):
    RISK_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("VERY_HIGH", "Very High"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="risk_metrics"
    )
    calculated_at = models.DateTimeField(auto_now=True)
    calculation_period_days = models.IntegerField(default=252)

    volatility_30d = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    volatility_90d = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    volatility_1y = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    sharpe_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    sortino_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    max_drawdown = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    var_95 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Value at Risk 95%",
    )
    var_99 = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Value at Risk 99%",
    )
    risk_score = models.IntegerField(null=True, blank=True)
    risk_level = models.CharField(
        max_length=20, choices=RISK_LEVEL_CHOICES, null=True, blank=True
    )

    class Meta:
        ordering = ["-calculated_at"]
        indexes = [
            models.Index(fields=["portfolio", "calculated_at"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} - Risk: {self.risk_level or 'N/A'}"
