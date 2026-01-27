from django.db import models
from users.models import User
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Portfolio(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    A user's collection of holdings. Can be real or simulated (paper trading).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    is_paper_trading = models.BooleanField(
        default=False, help_text="Simulated portfolio"
    )
    base_currency = models.CharField(max_length=3, default="USD")

    class Meta:
        unique_together = ("user", "name")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def current_value(self):
        """Calculate current total value (cached or computed via service later)"""
        # We'll implement this properly in a service with caching
        from .holdings import Holding

        return sum(
            holding.current_value for holding in self.holdings.filter(is_deleted=False)
        )
