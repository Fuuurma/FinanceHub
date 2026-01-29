"""
DEX Trading Pair Model
Stores DEX trading pair data from decentralized exchanges (Uniswap, SushiSwap, etc.)
"""

from django.db import models
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class DEXTradingPair(UUIDModel, TimestampedModel):
    """DEX Trading Pair for decentralized exchange data"""

    base_asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="dex_base_pairs", db_index=True
    )
    quote_asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="dex_quote_pairs", db_index=True
    )

    dex_name = models.CharField(
        max_length=100,
        help_text="DEX name (e.g., Uniswap, SushiSwap, PancakeSwap)",
        db_index=True,
    )

    pool_address = models.CharField(
        max_length=255,
        help_text="Contract address of the liquidity pool",
    )

    reserve_base = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        null=True,
        blank=True,
        help_text="Base asset reserves in the pool",
    )
    reserve_quote = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        null=True,
        blank=True,
        help_text="Quote asset reserves in the pool",
    )

    price = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        null=True,
        blank=True,
        help_text="Current price (quote/base)",
    )

    volume_24h = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="24h trading volume",
    )

    volume_24h_base = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        null=True,
        blank=True,
        help_text="24h trading volume in base asset",
    )

    liquidity_usd = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total liquidity in USD",
    )

    fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.003,
        help_text="Trading fee percentage (e.g., 0.003 for 0.3%)",
    )

    token_0_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token 0 contract address",
    )
    token_1_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token 1 contract address",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this trading pair is currently active",
    )

    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time data was synced from the DEX",
    )

    class Meta:
        db_table = "dex_trading_pairs"
        verbose_name = "DEX Trading Pair"
        verbose_name_plural = "DEX Trading Pairs"
        indexes = [
            models.Index(fields=["dex_name"]),
            models.Index(fields=["base_asset", "quote_asset"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["liquidity_usd"]),
        ]
        unique_together = [["dex_name", "pool_address"]]

    def __str__(self):
        return f"{self.base_asset.ticker}/{self.quote_asset.ticker} on {self.dex_name}"
