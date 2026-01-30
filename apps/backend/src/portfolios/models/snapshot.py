# investments/models/portfolio.py
from django.db import models
from portfolios.models.portfolio import Portfolio
from users.models import User

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class PortfolioSnapshot(UUIDModel, TimestampedModel):
    """
    Daily snapshot of portfolio value and performance.
    Great for historical charts and reporting.
    """

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="snapshots"
    )
    date = models.DateField(db_index=True)
    total_value = models.DecimalField(max_digits=20, decimal_places=2)
    cash_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    invested_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_return = models.DecimalField(
        max_digits=10, decimal_places=4, default=0
    )  # Percentage
    daily_return = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        unique_together = ("portfolio", "date")
        ordering = ["-date"]
        indexes = [models.Index(fields=["portfolio", "-date"])]

    def __str__(self):
        return f"{self.portfolio} - {self.date} - ${self.total_value}"
