from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from users.models.role import Role
from users.models.user_manager import UserManager





class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as unique identifier.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("Email Address"), unique=True)
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    
    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    date_joined = models.DateTimeField(_("Date Joined"), default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship to Role (many-to-many for future multi-role support)
    roles = models.ManyToManyField(Role, verbose_name=_("Roles"), blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Optional but good for createsuperuser

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def has_role(self, role_name: str) -> bool:
        return self.roles.filter(name__iexact=role_name).exists()


