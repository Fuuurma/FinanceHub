from django.db import models

from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class CorporateAction(UUIDModel, TimestampedModel):
    """
    Tracks events like Stock Splits, Dividends, and Mergers.
    Essential for adjusting historical price calculations.
    """

    class ActionType(models.TextChoices):
        SPLIT = "split", "Stock Split"
        DIVIDEND = "dividend", "Dividend"
        MERGER = "merger", "Merger"
        SPINOFF = "spinoff", "Spinoff"

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="corporate_actions"
    )
    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    execution_date = models.DateField(db_index=True)

    # Data points
    ratio = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="e.g. 4.0 for 4-for-1 split",
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Dividend amount per share",
    )

    description = models.TextField(blank=True)

    class Meta:
        db_table = "asset_corporate_actions"
        ordering = ["-execution_date"]
