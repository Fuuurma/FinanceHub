from decimal import Decimal
from django.db import models

from fundamentals.base import FundamentalData


class StakingData(FundamentalData):
    """
    Staking and token economics data.
    Tracks staking ratios, APR, and supply metrics.
    """

    class Meta(FundamentalData.Meta):
        db_table = "fundamentals_crypto_staking"
        verbose_name = "Staking Data"
        verbose_name_plural = "Staking Data"

    staking_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Staking APR as decimal",
    )

    delegation_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Delegation APR as decimal",
    )

    inflation_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Inflation APR as decimal",
    )

    reward_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Total reward APR as decimal",
    )

    total_staked = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        help_text="Total amount staked in native tokens",
    )

    total_staked_usd = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total amount staked in USD",
    )

    staking_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Staking ratio (staked / circulating supply)",
    )

    active_validators = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of active validators",
    )

    total_validators = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total number of validators",
    )

    minimum_stake = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Minimum stake amount in native tokens",
    )

    unbonding_period_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Unbonding period in days",
    )


class CryptoSupplyMetrics(FundamentalData):
    """
    Token supply and distribution metrics.
    Tracks circulating supply, max supply, and distribution.
    """

    class Meta(FundamentalData.Meta):
        db_table = "fundamentals_crypto_supply"
        verbose_name = "Crypto Supply Metrics"
        verbose_name_plural = "Crypto Supply Metrics"

    max_supply = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        help_text="Maximum token supply",
    )

    total_supply = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total token supply",
    )

    circulating_supply = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        help_text="Circulating token supply",
    )

    circulating_supply_pct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Circulating supply as percentage of max supply",
    )

    tokens_burned = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total tokens burned",
    )

    tokens_burned_24h = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tokens burned in last 24 hours",
    )

    treasury_balance = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Treasury balance in USD",
    )

    inflation_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Token inflation rate as decimal",
    )

    block_time_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average block time in seconds",
    )

    transactions_last_24h = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Number of transactions in last 24 hours",
    )

    active_addresses_24h = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Number of active addresses in last 24 hours",
    )
