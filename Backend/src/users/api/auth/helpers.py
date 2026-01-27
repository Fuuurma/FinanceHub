# apps/core/security.py
from ninja.security import HttpBearer

# from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError


class AuthBearer(JWTAuth):
    """Standard JWT Bearer Auth"""

    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and user.is_active:
            return user
        return None


def RoleRequired(roles: list):
    """RBAC Helper for endpoints"""

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.auth.roles.filter(code__in=roles).exists():
                raise HttpError(403, "You do not have the required role.")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
