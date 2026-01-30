from ninja import Schema


class UserLoginSchema(Schema):
    """User login schema"""

    username: str
    password: str
