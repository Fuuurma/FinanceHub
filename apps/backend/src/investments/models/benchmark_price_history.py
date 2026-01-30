from django.db import models

from investments.models.benchmark import Benchmark
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class BenchmarkPriceHistory(UUIDModel, TimestampedModel):
    benchmark = models.ForeignKey(
        Benchmark, on_delete=models.CASCADE, related_name="prices"
    )
    date = models.DateField()
    close = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ("benchmark", "date")
