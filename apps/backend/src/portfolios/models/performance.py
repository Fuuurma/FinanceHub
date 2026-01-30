from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class PortfolioPerformance(UUIDModel, TimestampedModel):
    portfolio = models.ForeignKey(
        "portfolios.Portfolio", on_delete=models.CASCADE, related_name="performance"
    )
    date = models.DateField()
    total_return_pct = models.DecimalField(
        max_digits=10, decimal_places=4
    )  # Since inception
    ytd_return_pct = models.DecimalField(max_digits=10, decimal_places=4)
    mtd_return_pct = models.DecimalField(max_digits=10, decimal_places=4)
    sharpe_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    max_drawdown_pct = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    volatility = models.DecimalField(max_digits=8, decimal_places=4, null=True)

    class Meta:
        unique_together = ("portfolio", "date")
