from decimal import Decimal
from django.db import models

from fundamentals.base import FundamentalData


class CryptoProtocolMetrics(FundamentalData):
    """
    DeFi protocol metrics including TVL, revenue, and DeFi-specific data.
    Data primarily from DeFi Llama API.
    """

    class Meta(FundamentalData.Meta):
        db_table = "fundamentals_crypto_protocol"
        verbose_name = "Crypto Protocol Metrics"
        verbose_name_plural = "Crypto Protocol Metrics"

    tvl = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        help_text="Total Value Locked in USD",
    )

    tvl_change_24h = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="TVL change in last 24 hours as decimal",
    )

    tvl_change_7d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="TVL change in last 7 days as decimal",
    )

    tvl_change_30d = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="TVL change in last 30 days as decimal",
    )

    tvl_change_1y = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="TVL change in last year as decimal",
    )

    protocol_revenue_24h = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Protocol revenue in last 24 hours in USD",
    )

    protocol_revenue_7d = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Protocol revenue in last 7 days in USD",
    )

    protocol_revenue_30d = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Protocol revenue in last 30 days in USD",
    )

    total_revenue_all_time = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="All-time protocol revenue in USD",
    )

    fee_per_transaction = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Average fee per transaction in USD",
    )

    dex_volume_24h = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="DEX trading volume in last 24 hours in USD",
    )

    dex_volume_7d = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="DEX trading volume in last 7 days in USD",
    )

    dex_trades_24h = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Number of DEX trades in last 24 hours",
    )

    lending_borrowed_24h = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount borrowed in last 24 hours in USD",
    )

    lending_deposits_24h = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount deposited in last 24 hours in USD",
    )

    lending_borrowed_total = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total borrowed amount in USD",
    )

    lending_deposits_total = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total deposited amount in USD",
    )

    lending_supply_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Average supply APR for lenders",
    )

    lending_borrow_apr = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Average borrow APR for borrowers",
    )

    stablecoin_tvl = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="TVL in stablecoins in USD",
    )

    eth_tvl = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="TVL in ETH",
    )

    btc_tvl = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="TVL in BTC",
    )

    chain = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Blockchain name (e.g., Ethereum, Solana)",
    )

    category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Protocol category (e.g., DEX, Lending, Yield)",
    )

    number_of_pools = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of liquidity pools",
    )

    number_of_markets = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of lending markets",
    )

    governance_token_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Governance token price in USD",
    )

    governance_token_market_cap = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Governance token market cap in USD",
    )

    fully_diluted_valuation = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fully diluted valuation in USD",
    )

    tvl_to_fdv_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="TVL to FDV ratio",
    )


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

    slashing_enabled = models.BooleanField(
        default=False,
        help_text="Whether slashing is enabled",
    )

    slashing_penalty = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Slashing penalty as decimal",
    )

    token_inflation_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Token inflation rate as decimal",
    )

    token_deflation_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Token deflation rate (burn) as decimal",
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

    burned_value_usd = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Value of burned tokens in USD",
    )

    treasury_balance = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Treasury balance in USD",
    )

    treasury_tokens = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Treasury balance in native tokens",
    )

    team_allocation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Team allocation as percentage",
    )

    investor_allocation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Investor allocation as percentage",
    )

    public_sale_allocation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Public sale allocation as percentage",
    )

    ecosystem_allocation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ecosystem/community allocation as percentage",
    )

    vesting_active = models.BooleanField(
        default=False,
        help_text="Whether vesting is active",
    )

    vesting_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Vesting end date",
    )

    emission_rate_per_year = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Token emission rate per year",
    )

    hash_rate = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Network hash rate (for PoW chains)",
    )

    difficulty = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Network difficulty (for PoW chains)",
    )

    block_time_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average block time in seconds",
    )

    blocks_last_24h = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of blocks produced in last 24 hours",
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

    network_value = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Network value (market cap) in USD",
    )

    nvt_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="NVT ratio (Network Value / Transaction Volume)",
    )

    mvrv_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MVRV ratio (Market Value / Realized Value)",
    )
