from django.db import models

from investments.models.currency import Currency
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Dividend(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.CASCADE, related_name="dividends"
    )
    ex_date = models.DateField()
    pay_date = models.DateField()
    amount_per_share = models.DecimalField(max_digits=15, decimal_places=6)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    declared_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-ex_date"]

    def __str__(self):
        return f"{self.asset.ticker} Dividend ${self.amount_per_share} ({self.ex_date})"
