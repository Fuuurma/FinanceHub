from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.user import User

class UserProfile(models.Model):
    """
    One-to-one extension for non-auth related user data.
    Keeps User model clean and focused on authentication.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    currency_preference = models.CharField(max_length=3, default='USD')  # e.g., USD, EUR
    timezone = models.CharField(max_length=50, default='UTC')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"