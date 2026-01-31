from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ValueAtRisk(models.Model):
    METHOD_CHOICES = [
        ("parametric", "Parametric (Variance-Covariance)"),
        ("historical", "Historical Simulation"),
        ("monte_carlo", "Monte Carlo Simulation"),
    ]

    CONFIDENCE_CHOICES = [
        (90, "90%"),
        (95, "95%"),
        (99, "99%"),
        (99.9, "99.9%"),
    ]

    portfolio_id = models.IntegerField()
    portfolio_name = models.CharField(max_length=200)
    user_id = models.IntegerField()

    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    confidence_level = models.IntegerField(choices=CONFIDENCE_CHOICES)
    time_horizon = models.IntegerField()

    var_amount = models.DecimalField(max_digits=20, decimal_places=2)
    var_percentage = models.DecimalField(max_digits=10, decimal_places=4)
    expected_shortfall = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    portfolio_value = models.DecimalField(max_digits=20, decimal_places=2)

    calculated_at = models.DateTimeField(auto_now_add=True)
    calculation_time_ms = models.IntegerField()

    class Meta:
        db_table = "investments_value_at_risk"
        indexes = [
            models.Index(fields=["portfolio_id", "-calculated_at"]),
            models.Index(fields=["method", "confidence_level"]),
            models.Index(fields=["user_id", "-calculated_at"]),
        ]
        ordering = ["-calculated_at"]


class StressTest(models.Model):
    SCENARIO_TYPE_CHOICES = [
        ("historical", "Historical Event"),
        ("custom", "Custom Scenario"),
        ("sensitivity", "Sensitivity Analysis"),
    ]

    portfolio_id = models.IntegerField()
    portfolio_name = models.CharField(max_length=200)
    user_id = models.IntegerField()

    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPE_CHOICES)
    scenario_name = models.CharField(max_length=100)
    scenario_description = models.TextField(blank=True, default="")

    historical_event = models.CharField(max_length=100, blank=True, default="")
    historical_date_start = models.DateField(null=True, blank=True)
    historical_date_end = models.DateField(null=True, blank=True)

    market_shock_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    sector_shocks = models.JSONField(default=dict)
    fx_shocks = models.JSONField(default=dict)

    portfolio_value_before = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_value_after = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_loss = models.DecimalField(max_digits=20, decimal_places=2)
    portfolio_loss_pct = models.DecimalField(max_digits=10, decimal_places=4)

    worst_performing_assets = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "investments_stress_test"
        ordering = ["-created_at"]


class RiskContribution(models.Model):
    portfolio_id = models.IntegerField()
    var_calculation_id = models.IntegerField()
    user_id = models.IntegerField()

    asset_id = models.IntegerField()
    asset_symbol = models.CharField(max_length=20)
    asset_name = models.CharField(max_length=200, blank=True, default="")

    position_value = models.DecimalField(max_digits=20, decimal_places=2)
    position_weight = models.DecimalField(max_digits=10, decimal_places=6)

    marginal_var = models.DecimalField(max_digits=20, decimal_places=2)
    component_var = models.DecimalField(max_digits=20, decimal_places=2)
    pct_contribution = models.DecimalField(max_digits=10, decimal_places=4)

    beta = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    volatility = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    correlation_to_portfolio = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )

    class Meta:
        db_table = "investments_risk_contribution"
        indexes = [
            models.Index(fields=["var_calculation_id", "-pct_contribution"]),
            models.Index(fields=["portfolio_id"]),
        ]


class RiskLimit(models.Model):
    LIMIT_TYPE_CHOICES = [
        ("var", "VaR Limit"),
        ("concentration", "Concentration Limit"),
        ("beta", "Beta Limit"),
        ("drawdown", "Max Drawdown Limit"),
    ]

    user_id = models.IntegerField()
    portfolio_id = models.IntegerField(null=True, blank=True)

    limit_type = models.CharField(max_length=20, choices=LIMIT_TYPE_CHOICES)
    limit_name = models.CharField(max_length=100)

    threshold_value = models.DecimalField(max_digits=20, decimal_places=2)
    threshold_percentage = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    alert_threshold_pct = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("80")
    )

    current_value = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    current_percentage = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    breached = models.BooleanField(default=False)
    last_alert_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_risk_limit"
        indexes = [
            models.Index(fields=["user_id", "limit_type", "breached"]),
            models.Index(fields=["portfolio_id"]),
        ]
