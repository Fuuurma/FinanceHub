from ninja import Schema


class TokenSchema(Schema):
    """Token response schema"""

    access: str
    refresh: str


class TokenRefreshSchema(Schema):
    """Token refresh request"""

    refresh: str
