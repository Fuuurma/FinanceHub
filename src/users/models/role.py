from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.permision import Permission
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.soft_delete_model import SoftDeleteModel
class Role(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Role model for role-based access control"""
    
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique role code"
    )
    name = models.CharField(
        max_length=150,
        help_text="Human-readable role name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this role"
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True,
        help_text="Permissions granted to this role"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="Whether this is a system role (cannot be deleted)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is active"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Role hierarchy level (higher = more privileged)"
    )

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name

    def has_permission(self, permission_code: str) -> bool:
        """Check if role has a specific permission"""
        return self.permissions.filter(
            code=permission_code,
            is_active=True
        ).exists()
