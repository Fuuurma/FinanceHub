from users.models.account_type import AccountType
from users.models.role import Role
from users.models.user_status import UserStatus
from utils.constants.default import (
    DEFAULT_ACCOUNT_TYPE_NAME,
    DEFAULT_ADMIN_ROLE_NAME,
    DEFAULT_USER_STATUS_NAME,
)


def get_default_user_status():
    try:
        return UserStatus.objects.get_or_create(name=DEFAULT_USER_STATUS_NAME)[0].id
    except Exception:
        return None


def get_default_account_type():
    try:
        return AccountType.objects.get_or_create(name=DEFAULT_ACCOUNT_TYPE_NAME)[0].id
    except Exception:
        return None


def get_default_admin_role():
    try:
        return Role.objects.get_or_create(name=DEFAULT_ADMIN_ROLE_NAME)[0].id
    except Exception:
        return None
