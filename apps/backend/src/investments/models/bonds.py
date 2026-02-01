from django.db import models
from django.contrib.auth import get_user_model
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel

User = get_user_model()


class Bond(UUIDModel, TimestampedModel):
    """
    Bond model for tracking bond information and yields.

    Attributes:
        symbol: Bond ticker symbol (e.g., "US10Y" for 10-year Treasury)
        bond_type: Type of bond (treasury, corporate, municipal, agency)
        face_value: Par value (usually $1000)
        coupon_rate: Annual coupon rate as decimal (0.05 = 5%)
        current_price: Current market price
        maturity_date: Date when bond matures
        call_date: Date when bond can be called (optional)
        call_price: Price at which bond can be called (optional)
        frequency: Number of coupon payments per year (1, 2, or 4)
        rating: Credit rating (AAA, AA, A, BBB, etc.)
        issuer: Bond issuer name
        description: Additional description
        is_active: Whether bond is actively tracked
    """

    BOND_TYPE_CHOICES = [
        ("treasury", "Treasury Bond"),
        ("corporate", "Corporate Bond"),
        ("municipal", "Municipal Bond"),
        ("agency", "Agency Bond"),
        ("treasury_note", "Treasury Note"),
        ("treasury_bill", "Treasury Bill"),
        ("commercial_paper", "Commercial Paper"),
        ("cd", "Certificate of Deposit"),
        ("mbs", "Mortgage-Backed Security"),
        ("other", "Other"),
    ]

    FREQUENCY_CHOICES = [
        (1, "Annual"),
        (2, "Semi-Annual"),
        (4, "Quarterly"),
        (12, "Monthly"),
    ]

    RATING_CHOICES = [
        ("AAA", "AAA"),
        ("AA+", "AA+"),
        ("AA", "AA"),
        ("AA-", "AA-"),
        ("A+", "A+"),
        ("A", "A"),
        ("A-", "A-"),
        ("BBB+", "BBB+"),
        ("BBB", "BBB"),
        ("BBB-", "BBB-"),
        ("BB+", "BB+"),
        ("BB", "BB"),
        ("BB-", "BB-"),
        ("B+", "B+"),
        ("B", "B"),
        ("B-", "B-"),
        ("CCC+", "CCC+"),
        ("CCC", "CCC"),
        ("CCC-", "CCC-"),
        ("CC", "CC"),
        ("C", "C"),
        ("D", "D"),
        ("NR", "Not Rated"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bonds", null=True, blank=True
    )

    symbol = models.CharField(max_length=20, help_text="Bond ticker symbol")
    bond_type = models.CharField(max_length=20, choices=BOND_TYPE_CHOICES)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    coupon_rate = models.DecimalField(
        max_digits=6, decimal_places=4, help_text="Annual coupon rate as decimal"
    )
    current_price = models.DecimalField(max_digits=10, decimal_places=4)
    maturity_date = models.DateField()
    call_date = models.DateField(null=True, blank=True)
    call_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    frequency = models.IntegerField(
        choices=FREQUENCY_CHOICES, default=2, help_text="Coupons per year"
    )
    rating = models.CharField(max_length=5, choices=RATING_CHOICES, default="NR")
    issuer = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["bond_type"]),
            models.Index(fields=["maturity_date"]),
        ]

    def __str__(self):
        return f"{self.symbol} ({self.bond_type})"

    @property
    def annual_coupon(self):
        """Calculate annual coupon payment."""
        return self.face_value * self.coupon_rate

    @property
    def coupon_payment(self):
        """Calculate coupon payment per period."""
        return self.annual_coupon / self.frequency

    @property
    def years_to_maturity(self):
        """Calculate years to maturity from today."""
        from datetime import date

        delta = self.maturity_date - date.today()
        return max(delta.days / 365.0, 0)

    def to_dict(self):
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "bond_type": self.bond_type,
            "face_value": str(self.face_value),
            "coupon_rate": str(self.coupon_rate),
            "current_price": str(self.current_price),
            "maturity_date": str(self.maturity_date),
            "years_to_maturity": self.years_to_maturity,
            "rating": self.rating,
        }


class BondCalculation(UUIDModel, TimestampedModel):
    """
    Record of bond yield calculations for tracking and comparison.

    Attributes:
        bond: Reference to the bond
        calculation_type: Type of calculation performed
        yield_value: Calculated yield value
        input_parameters: JSON storing input parameters
        error_message: Error message if calculation failed
    """

    CALCULATION_TYPE_CHOICES = [
        ("current_yield", "Current Yield"),
        ("ytm", "Yield to Maturity"),
        ("ytc", "Yield to Call"),
        ("zero_coupon_yield", "Zero-Coupon Yield"),
        ("treasury_yield", "Treasury Bill Yield"),
        ("bond_price", "Bond Price"),
        (" Macaulay Duration", "Macaulay Duration"),
        ("Modified Duration", "Modified Duration"),
        ("convexity", "Convexity"),
    ]

    bond = models.ForeignKey(
        Bond, on_delete=models.CASCADE, related_name="calculations"
    )
    calculation_type = models.CharField(max_length=25, choices=CALCULATION_TYPE_CHOICES)
    yield_value = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    price_value = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    input_parameters = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["bond", "calculation_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.bond.symbol} - {self.calculation_type}: {self.yield_value}"

    def to_dict(self):
        return {
            "id": str(self.id),
            "bond_symbol": self.bond.symbol,
            "calculation_type": self.calculation_type,
            "yield_value": str(self.yield_value) if self.yield_value else None,
            "price_value": str(self.price_value) if self.price_value else None,
            "input_parameters": self.input_parameters,
            "calculated_at": self.created_at.isoformat(),
        }


class BondPortfolio(models.Model):
    """
    Portfolio of bonds for tracking total holdings.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bond_portfolios"
    )
    name = models.CharField(max_length=255)
    bonds = models.ManyToManyField(Bond, related_name="portfolios")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        """Calculate total market value of all bonds in portfolio."""
        from decimal import Decimal

        total = Decimal("0")
        for bond in self.bonds.all():
            total += bond.current_price * (bond.face_value / 1000)
        return total

    @property
    def average_yield(self):
        """Calculate weighted average yield."""
        from decimal import Decimal

        total_weighted_yield = Decimal("0")
        total_value = self.total_value
        if total_value == 0:
            return Decimal("0")
        for bond in self.bonds.all():
            weight = (bond.current_price * (bond.face_value / 1000)) / total_value
            total_weighted_yield += weight * Decimal("0.05")  # Simplified
        return total_weighted_yield
