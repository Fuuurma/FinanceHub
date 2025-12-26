from users.models.user import User
from users.models.user_status import UserStatus
from users.models.account_type import AccountType
from users.models.role import Role
from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_type import AssetType

# 1. Create UserStatus
active_status, _ = UserStatus.objects.get_or_create(
    code="ACTIVE", defaults={"name": "Active", "description": "Active account"}
)
inactive_status, _ = UserStatus.objects.get_or_create(
    code="INACTIVE", defaults={"name": "Inactive", "description": "Inactive account"}
)

# 2. Create AccountType
free_type, _ = AccountType.objects.get_or_create(
    name="free", defaults={"description": "Free tier", "max_portfolios": 5}
)
premium_type, _ = AccountType.objects.get_or_create(
    name="premium", defaults={"description": "Premium tier", "max_portfolios": 50}
)

# 3. Create Roles
admin_role, _ = Role.objects.get_or_create(
    name="Admin", defaults={"description": "Full system access"}
)
investor_role, _ = Role.objects.get_or_create(
    name="Investor", defaults={"description": "Standard user"}
)

# 4. Create Superuser (you'll be prompted for password)
# This will use the defaults we just created
User.objects.create_superuser(
    username="admin",
    email="admin@financehub.com",
    password="supersecret123",  # Change this immediately after!
    first_name="Admin",
    last_name="User",
    status=active_status,
    account_type=premium_type,
)

# The superuser automatically gets is_staff=True, is_superuser=True
# Let's also assign the Admin role
superuser = User.objects.get(username="admin")
superuser.roles.add(admin_role)

print("Superuser created: username=admin, email=admin@financehub.com")

# 5. Create a regular test user
test_user = User.objects.create_user(
    username="tester",
    email="tester@example.com",
    password="testpass123",
    first_name="Test",
    last_name="User",
    status=active_status,
    account_type=free_type,
)
test_user.roles.add(investor_role)
print("Test user created: username=tester")

# 6. Create some dummy Asset Classes & Types
equity_class, _ = AssetClass.objects.get_or_create(name="Equity")
crypto_class, _ = AssetClass.objects.get_or_create(name="Cryptocurrency")

stock_type, _ = AssetType.objects.get_or_create(name="Stock", asset_class=equity_class)
crypto_type, _ = AssetType.objects.get_or_create(
    name="Cryptocurrency", asset_class=crypto_class
)

# 7. Create dummy Assets
Asset.objects.get_or_create(
    ticker="AAPL",
    defaults={"name": "Apple Inc.", "asset_type": stock_type, "currency": "USD"},
)
Asset.objects.get_or_create(
    ticker="GOOGL",
    defaults={"name": "Alphabet Inc.", "asset_type": stock_type, "currency": "USD"},
)
Asset.objects.get_or_create(
    ticker="BTC-USD",
    defaults={"name": "Bitcoin", "asset_type": crypto_type, "currency": "USD"},
)

print("Dummy assets created: AAPL, GOOGL, BTC-USD")
