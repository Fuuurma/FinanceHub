from django.db import models

from investments.models.currency import Currency
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class ExchangeRate(UUIDModel, TimestampedModel):
    base_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="rates_as_base"
    )
    quote_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="rates_as_quote"
    )
    rate = models.DecimalField(max_digits=20, decimal_places=10)
    date = models.DateField(db_index=True)

    class Meta:
        unique_together = ("base_currency", "quote_currency", "date")
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return (
            f"{self.base_currency}/{self.quote_currency} @ {self.rate} on {self.date}"
        )
