"""
Options Models for Polygon.io Integration
Stores options contracts, chains, and Greeks data
"""

from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator

from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class OptionContract(UUIDModel, TimestampedModel):
    """Options contract with Greeks and pricing data from Polygon.io"""

    class OptionType(models.TextChoices):
        CALL = "C", "Call"
        PUT = "P", "Put"

    class ExerciseStyle(models.TextChoices):
        AMERICAN = "american", "American"
        EUROPEAN = "european", "European"
        BERMUDA = "bermuda", "Bermuda"

    class SettlementType(models.TextChoices):
        CASH = "cash", "Cash"
        PHYSICAL = "physical", "Physical"

    underlying_asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="option_contracts",
        db_index=True,
        help_text="Underlying asset for this option",
    )

    option_symbol = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Full option symbol (e.g., O:AAPL230120C00150000)",
    )

    ticker = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Option ticker without O: prefix",
    )

    underlying_symbol = models.CharField(
        max_length=10,
        db_index=True,
        help_text="Underlying stock symbol (e.g., AAPL)",
    )

    expiry_date = models.DateField(
        db_index=True,
        help_text="Option expiration date",
    )

    option_type = models.CharField(
        max_length=1,
        choices=OptionType.choices,
        db_index=True,
        help_text="C for Call, P for Put",
    )

    strike_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Strike price in USD",
    )

    contract_size = models.IntegerField(
        default=100,
        validators=[MinValue(1)],
        help_text="Number of shares per contract (usually 100)",
    )

    exercise_style = models.CharField(
        max_length=20,
        choices=ExerciseStyle.choices,
        default=ExerciseStyle.AMERICAN,
        help_text="Exercise style (American, European, Bermuda)",
    )

    settlement_type = models.CharField(
        max_length=20,
        choices=SettlementType.choices,
        default=SettlementType.PHYSICAL,
        help_text="Settlement type",
    )

    is_standard = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this is a standard contract (non-leveraged, non-mini)",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this contract is currently tradeable",
    )

    last_trade_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last trade timestamp",
    )

    last_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Last traded price",
    )

    bid = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Current bid price",
    )

    bid_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Bid size (number of contracts)",
    )

    ask = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Current ask price",
    )

    ask_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Ask size (number of contracts)",
    )

    bid_ask_spread = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Bid-ask spread",
    )

    volume = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Trading volume (number of contracts)",
    )

    open_interest = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Open interest (number of open contracts)",
    )

    open_interest_change = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Change in open interest from previous day",
    )

    implied_volatility = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MaxValueValidator(Decimal("5.0"))],
        help_text="Implied volatility as decimal (e.g., 0.25 for 25%)",
    )

    delta = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValue(Decimal("-1.0")), MaxValue(Decimal("1.0"))],
        help_text="Delta - price change per $1 move in underlying",
    )

    gamma = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValue(Decimal("0"))],
        help_text="Gamma - delta change per $1 move in underlying",
    )

    theta = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Theta - time decay per day in dollars",
    )

    vega = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Vega - price change per 1% change in IV",
    )

    rho = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValue(Decimal("-1.0")), MaxValue(Decimal("1.0"))],
        help_text="Rho - sensitivity to interest rates",
    )

    intrinsic_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Intrinsic value (in-the-money amount)",
    )

    extrinsic_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Extrinsic value (time value)",
    )

    theoretical_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Theoretical/model value",
    )

    break_even = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Break-even price at expiration",
    )

    days_to_expiration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Days until expiration",
    )

    time_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Time value as percentage",
    )

    put_call_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Put/Call volume ratio for this expiration",
    )

    vwap = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Volume-weighted average price",
    )

    premium = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total premium (price * contract_size * 100)",
    )

    change = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price change from previous close",
    )

    change_percent = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price change percentage",
    )

    high = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="High price of the day",
    )

    low = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Low price of the day",
    )

    open = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Opening price",
    )

    close = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Closing price",
    )

    settlement_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Settlement price (end of day)",
    )

    previous_close = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Previous day's closing price",
    )

    tick_size = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal("0.01"),
        help_text="Minimum price increment",
    )

    exchange = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Primary exchange where option trades",
    )

    primary_exchange = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Primary exchange code",
    )

    market_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Market status (open, closed, pre-market, after-hours)",
    )

    fetched_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time data was fetched from Polygon.io",
    )

    class Meta:
        db_table = "option_contracts"
        verbose_name = "Option Contract"
        verbose_name_plural = "Option Contracts"
        ordering = ["-volume", "-open_interest"]
        indexes = [
            models.Index(fields=["underlying_symbol", "expiry_date"]),
            models.Index(fields=["underlying_symbol", "option_type", "strike_price"]),
            models.Index(fields=["underlying_symbol", "expiry_date", "option_type"]),
            models.Index(fields=["implied_volatility"]),
            models.Index(fields=["delta"]),
            models.Index(fields=["theta"]),
            models.Index(fields=["volume"]),
            models.Index(fields=["open_interest"]),
            models.Index(fields=["is_active", "is_standard"]),
        ]

    def __str__(self):
        option_type_str = "Call" if self.option_type == "C" else "Put"
        return f"{self.underlying_symbol} {self.expiry_date} {option_type_str} ${self.strike_price}"

    @property
    def is_call(self) -> bool:
        return self.option_type == "C"

    @property
    def is_put(self) -> bool:
        return self.option_type == "P"

    @property
    def is_in_the_money(self) -> bool:
        if not self.underlying_asset.last_price:
            return None
        if self.is_call:
            return self.underlying_asset.last_price > self.strike_price
        return self.underlying_asset.last_price < self.strike_price

    @property
    def is_out_of_the_money(self) -> bool:
        itm = self.is_in_the_money
        return itm is not None and not itm

    @property
    def is_at_the_money(self) -> bool:
        if not self.underlying_asset.last_price:
            return False
        return abs(self.underlying_asset.last_price - self.strike_price) < Decimal(
            "1.00"
        )


class OptionsContractSnapshot(UUIDModel, TimestampedModel):
    """Daily snapshot of options contract pricing and Greeks"""

    contract = models.ForeignKey(
        OptionContract,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )

    trade_date = models.DateField(
        db_index=True,
        help_text="Date of the snapshot",
    )

    open = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Opening price",
    )

    high = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="High price of the day",
    )

    low = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Low price of the day",
    )

    close = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Closing price",
    )

    volume = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Trading volume",
    )

    open_interest = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Open interest at end of day",
    )

    implied_volatility = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Implied volatility",
    )

    delta = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    gamma = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )

    theta = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    vega = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    rho = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "options_contract_snapshots"
        verbose_name = "Options Contract Snapshot"
        verbose_name_plural = "Options Contract Snapshots"
        ordering = ["-trade_date"]
        indexes = [
            models.Index(fields=["contract", "trade_date"]),
            models.Index(fields=["trade_date", "implied_volatility"]),
        ]

    def __str__(self):
        return f"{self.contract.option_symbol} - {self.trade_date}"


class OptionsGreeksHistory(UUIDModel):
    """Historical Greeks data for options contracts"""

    contract = models.ForeignKey(
        OptionContract,
        on_delete=models.CASCADE,
        related_name="greeks_history",
    )

    timestamp = models.DateTimeField(
        db_index=True,
        help_text="Timestamp of the Greeks calculation",
    )

    delta = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    gamma = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )

    theta = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    vega = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    rho = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    implied_volatility = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    theoretical_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    underlying_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Underlying asset price at time of calculation",
    )

    risk_free_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Risk-free rate used in calculation",
    )

    days_to_expiration = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    time_to_expiration = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Time to expiration in years",
    )

    class Meta:
        db_table = "options_greeks_history"
        verbose_name = "Options Greeks History"
        verbose_name_plural = "Options Greeks History"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["contract", "timestamp"]),
            models.Index(fields=["timestamp", "delta"]),
        ]

    def __str__(self):
        return f"{self.contract.option_symbol} - {self.timestamp}"
