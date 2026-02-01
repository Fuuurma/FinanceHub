from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from typing import List

from users.schemas.user import (
    PasswordChange,
    RegisterIn,
    RegisterOut,
    UserOut,
    UserUpdate,
)
from utils.helpers.error_handler.exceptions import (
    PermissionDeniedException,
    ValidationException,
)
from utils.helpers.logger.audit_logger import AuditLogger
from utils.helpers.logger.logger import get_logger
from utils.services.user import UserService


logger = get_logger(__name__)
audit_logger = AuditLogger()
User = get_user_model()

router = Router(tags=["users"])


# Public: Registration
@router.post(
    "/register",
    response=RegisterOut,
    summary="Register a new user",
    description="Creates a new user with strong password validation and assigns default 'Investor' role.",
)
def register(request, payload: RegisterIn):
    user = UserService.create_user(payload.model_dump())

    audit_logger.user_action(
        user_id=str(user.id),
        action="user_registered",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.META.get("REMOTE_ADDR"),
    )

    logger.info(
        "New user registered",
        extra={"user_id": str(user.id), "username": user.username},
    )

    return RegisterOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )


# Protected: Profile
@router.get("/me", response=UserOut, auth=JWTAuth(), summary="Get current user profile")
def get_me(request):
    return request.auth


@router.patch(
    "/me", response=UserOut, auth=JWTAuth(), summary="Update current user profile"
)
def update_me(request, payload: UserUpdate):
    user = UserService.update_user(request.auth, payload.dict(exclude_unset=True))
    logger.info("Profile updated", extra={"user_id": str(user.id)})
    return user


@router.post("/me/change-password", auth=JWTAuth(), summary="Change password")
def change_password(request, payload: PasswordChange):
    try:
        UserService.change_password(
            request.auth, payload.current_password, payload.new_password
        )
        audit_logger.user_action(
            user_id=str(request.auth.id),
            action="password_changed",
            resource_type="user",
            resource_id=str(request.auth.id),
        )
        return {"message": "Password changed successfully"}
    except ValidationException:
        raise ValidationException(
            message="Current password is incorrect", code="invalid_current_password"
        )


# Admin Only
def admin_required(user):
    if not user.is_staff:
        raise PermissionDeniedException()


@router.get(
    "/", response=List[UserOut], auth=JWTAuth(), summary="List all users (Admin only)"
)
def list_users(request):
    admin_required(request.auth)
    return User.objects.prefetch_related("roles").all()


@router.get("/{user_id}", response=UserOut, auth=JWTAuth())
def get_user(request, user_id: str):
    admin_required(request.auth)
    user = get_object_or_404(User, id=user_id)
    return user


@router.patch("/{user_id}", response=UserOut, auth=JWTAuth())
def update_user_admin(request, user_id: str, payload: UserUpdate):
    admin_required(request.auth)
    user = get_object_or_404(User, id=user_id)
    updated = UserService.update_user(user, payload.dict(exclude_unset=True))
    audit_logger.user_action(
        user_id=str(request.auth.id),
        action="admin_updated_user",
        resource_type="user",
        resource_id=user_id,
    )
    return updated


@router.post(
    "/{user_id}/deactivate", auth=JWTAuth(), summary="Deactivate user (Admin only)"
)
def deactivate_user(request, user_id: str):
    admin_required(request.auth)
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        raise PermissionDeniedException("Cannot deactivate superuser")
    user.is_active = False
    user.save()
    audit_logger.security_event(
        event_type="user_deactivated",
        severity="warning",
        description=f"User {user.username} deactivated by admin",
        user_id=user_id,
        ip_address=request.META.get("REMOTE_ADDR"),
    )
    return {"message": "User deactivated"}
