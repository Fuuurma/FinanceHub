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
        """Calculate current total value using cached prices (N+1 fix).

        Uses select_related to avoid N+1 queries when accessing asset.last_price.
        """
        from .holdings import Holding

        holdings = self.holdings.select_related('asset').filter(is_deleted=False)
        return sum(holding.current_value for holding in holdings)
