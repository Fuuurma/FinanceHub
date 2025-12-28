from datetime import timedelta
from django.db import models
from assets.models.asset import Asset
from investments.models.data_provider import DataProvider
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from decimal import Decimal


class AssetMetricsHistory(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField(db_index=True)
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    fdv = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    circulating_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    total_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    max_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)

    price = models.DecimalField(max_digits=30, decimal_places=10, null=True, blank=True)
    volume = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    price_change_1d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_1d = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_1d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_1d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    price_change_7d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_7d = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_7d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_7d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    price_change_30d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_30d = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_30d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_30d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    price_change_90d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_90d = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_90d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_90d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    price_change_180d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_180d = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_180d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_180d_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    price_change_1y = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    volume_change_1y = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    price_change_1y_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    volume_change_1y_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    ath_price_7d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    ath_price_date_7d = models.DateField(null=True)
    atl_price_7d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    atl_price_date_7d = models.DateField(null=True)

    ath_price_30d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    ath_price_date_30d = models.DateField(null=True)
    atl_price_30d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    atl_price_date_30d = models.DateField(null=True)

    ath_price_90d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    ath_price_date_90d = models.DateField(null=True)
    atl_price_90d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    atl_price_date_90d = models.DateField(null=True)

    ath_price_180d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    ath_price_date_180d = models.DateField(null=True)
    atl_price_180d = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    atl_price_date_180d = models.DateField(null=True)

    ath_price_1y = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    ath_price_date_1y = models.DateField(null=True)
    atl_price_1y = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    atl_price_date_1y = models.DateField(null=True)

    source = models.ForeignKey(
        DataProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="metric_history",
    )

    class Meta:
        unique_together = (
            "asset",
            "date",
            "source",
        )  # Multiple per day if different sources
        indexes = [models.Index(fields=["asset", "-date", "source"])]

    def __str__(self):
        return f"{self.asset.ticker} Metrics - {self.date}"

    def calculate_pct_changes(self, interval: str):
        """
        Auto-calculate % changes for the given interval if empty.
        Fetches previous data based on interval and computes.
        """
        intervals_days = {
            "1h": 1 / 24,  # Approximate
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "180d": 180,
            "1y": 365,
        }
        days = intervals_days.get(interval, 1)
        previous_date = self.date - timedelta(days=days)
        previous = AssetMetricsHistory.objects.filter(
            asset=self.asset, date=previous_date, source=self.source
        ).first()

        if previous:
            # Price
            price_field = f"price_change_{interval}"
            price_pct_field = f"price_change_{interval}_pct"
            setattr(self, price_field, self.price - previous.price)
            setattr(
                self,
                price_pct_field,
                (
                    ((self.price - previous.price) / previous.price * 100)
                    if previous.price
                    else Decimal("0")
                ),
            )

            # Volume
            volume_field = f"volume_change_{interval}"
            volume_pct_field = f"volume_change_{interval}_pct"
            setattr(self, volume_field, self.volume - previous.volume)
            setattr(
                self,
                volume_pct_field,
                (
                    ((self.volume - previous.volume) / previous.volume * 100)
                    if previous.volume
                    else Decimal("0")
                ),
            )

        self.save()

    def update_ath_atl(self, interval: str):
        """
        Update ATH/ATL for price and volume based on interval.
        Fetches historical data for the period and computes.
        """
        intervals_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "180d": 180,
            "1y": 365,
        }
        days = intervals_days.get(interval, 365)
        start_date = self.date - timedelta(days=days)
        historics = AssetMetricsHistory.objects.filter(
            asset=self.asset,
            date__gte=start_date,
            date__lte=self.date,
            source=self.source,
        ).order_by("date")

        if historics.exists():
            prices = list(historics.values_list("price", flat=True))
            volumes = list(historics.values_list("volume", flat=True))
            dates = list(historics.values_list("date", flat=True))

            # Price ATH/ATL
            ath_price = max(prices)
            ath_index = prices.index(ath_price)
            setattr(self, f"ath_price_{interval}", ath_price)
            setattr(self, f"ath_price_date_{interval}", dates[ath_index])

            atl_price = min(prices)
            atl_index = prices.index(atl_price)
            setattr(self, f"atl_price_{interval}", atl_price)
            setattr(self, f"atl_price_date_{interval}", dates[atl_index])

            # Volume ATH/ATL
            ath_volume = max(volumes)
            ath_v_index = volumes.index(ath_volume)
            setattr(self, f"ath_volume_{interval}", ath_volume)
            setattr(self, f"ath_volume_date_{interval}", dates[ath_v_index])

            # This fields does not exist.
            atl_volume = min(volumes)
            atl_v_index = volumes.index(atl_volume)
            setattr(self, f"atl_volume_{interval}", atl_volume)
            setattr(self, f"atl_volume_date_{interval}", dates[atl_v_index])

        self.save()
