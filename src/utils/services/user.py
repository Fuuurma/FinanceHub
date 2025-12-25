# users/services.py
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from users.models.role import Role
from users.models.user import User
from utils.helpers.error_handler.exceptions import ValidationException


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(data: dict) -> User:
        password = data.pop("password")
        user = User.objects.create_user(password=password, **data)
        # Optionally assign default role
        try:
            investor_role = Role.objects.get(name="Investor")
            user.roles.add(investor_role)
        except Role.DoesNotExist:
            pass
        return user

    @staticmethod
    def update_user(user: User, data: dict) -> User:
        for attr, value in data.items():
            if value is not None:
                setattr(user, attr, value)
        user.save()
        return user

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str):
        if not user.check_password(current_password):
            raise ValidationException(
                message="Current password is incorrect", code="invalid_current_password"
            )
        user.set_password(new_password)
        user.save()
        # Keep user logged in after password change
        update_session_auth_hash(None, user)  # Not needed in JWT, but safe
