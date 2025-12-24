from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    """
    Separate model instead of Choice field for flexibility.
    Allows adding permissions, descriptions, hierarchy later.
    """
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ['name']

    def __str__(self):
        return self.name
