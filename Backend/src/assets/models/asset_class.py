from django.db import models
from django.core.validators import MinValueValidator


class AssetClass(models.Model):
    """
    High-level classification: Equity, Crypto, Fixed Income, Real Estate, etc.
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    risk_level = models.PositiveSmallIntegerField(
        help_text="1 (lowest) to 10 (highest)",
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Asset Class"
        verbose_name_plural = "Asset Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name
