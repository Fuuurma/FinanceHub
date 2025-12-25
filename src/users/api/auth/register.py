# users/api.py
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from typing import List

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from utils.helpers.error_handler.exceptions import PermissionDeniedException


logger = get_logger(__name__)

User = get_user_model()

router = Router(tags=["users"])
auth_controller = NinjaJWTDefaultController()


# Public: Registration
@router.post("/register", response=RegisterOut, url_name="user-register")
def register(request, payload: RegisterIn):
    """
    Register a new user
    - Creates user with 'Investor' role by default
    - Email and username must be unique
    """
    logger.info(
        "User registration attempt",
        extra={"username": payload.username, "email": payload.email},
    )
    user = UserService.create_user(payload.dict())
    logger.info("User registered successfully", extra={"user_id": str(user.id)})
    return RegisterOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )


# Protected: Current user profile
@router.get("/me", response=UserOut, auth=JWTAuth())
def get_me(request):
    """Get current authenticated user's profile"""
    user = request.auth  # JWTAuth sets request.auth to user
    return user


@router.patch("/me", response=UserOut, auth=JWTAuth())
def update_me(request, payload: UserUpdate):
    """Update current user's profile"""
    user = UserService.update_user(request.auth, payload.dict(exclude_unset=True))
    logger.info("User profile updated", extra={"user_id": str(user.id)})
    return user


@router.post("/me/change-password", auth=JWTAuth())
def change_password(request, payload: PasswordChange):
    """Change current user's password"""
    payload.validate()
    UserService.change_password(
        request.auth, payload.current_password, payload.new_password
    )
    logger.info(
        "Password changed successfully", extra={"user_id": str(request.auth.id)}
    )
    return {"message": "Password changed successfully"}


# Admin-only: List all users
@router.get("/", response=List[UserOut], auth=JWTAuth())
def list_users(request):
    """List all users (Admin only)"""
    if not request.auth.is_staff:
        raise PermissionDeniedException()

    qs = User.objects.select_related().prefetch_related("roles").all()
    return qs


# Admin-only: Retrieve, Update, Deactivate user
@router.get("/{user_id}", response=UserOut, auth=JWTAuth())
def get_user(request, user_id: str):
    """Retrieve user by ID (Admin only)"""
    if not request.auth.is_staff:
        raise PermissionDeniedException()

    user = get_object_or_404(User, id=user_id)
    return user


@router.patch("/{user_id}", response=UserOut, auth=JWTAuth())
def update_user(request, user_id: str, payload: UserUpdate):
    """Update user by ID (Admin only)"""
    if not request.auth.is_staff:
        raise PermissionDeniedException()

    user = get_object_or_404(User, id=user_id)
    updated_user = UserService.update_user(user, payload.dict(exclude_unset=True))
    logger.info(
        "Admin updated user",
        extra={"admin_id": str(request.auth.id), "target_user_id": user_id},
    )
    return updated_user


@router.delete("/{user_id}", auth=JWTAuth())
def delete_user(request, user_id: str):
    """Soft-delete or deactivate user (Admin only)"""
    if not request.auth.is_staff:
        raise PermissionDeniedException()

    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        raise PermissionDeniedException(message="Cannot delete superuser")

    user.is_active = False
    user.save()
    logger.warning(
        "User deactivated by admin",
        extra={"admin_id": str(request.auth.id), "target_user_id": user_id},
    )
    return {"message": "User deactivated successfully"}
