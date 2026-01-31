from django.db import models
from django.utils import timezone
from datetime import timedelta


class BlacklistedToken(models.Model):
    """
    Store blacklisted JWT tokens to prevent replay attacks.

    When a refresh token is used, it's added to this blacklist
    to prevent it from being reused.
    """

    token = models.CharField(max_length=500, unique=True, db_index=True)
    user_id = models.CharField(max_length=36, db_index=True)  # UUID
    blacklisted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["blacklisted_at"]),
        ]
        verbose_name = "Blacklisted Token"
        verbose_name_plural = "Blacklisted Tokens"

    @classmethod
    def blacklist_token(cls, token: str, user_id: str, expires_in: int = 86400):
        """
        Blacklist a token until its expiration.

        Args:
            token: The JWT token string to blacklist
            user_id: The UUID of the user
            expires_in: Seconds until token expires (default: 24 hours)
        """
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        cls.objects.get_or_create(
            token=token, defaults={"user_id": user_id, "expires_at": expires_at}
        )

    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: The JWT token string to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        return cls.objects.filter(token=token, expires_at__gt=timezone.now()).exists()

    @classmethod
    def cleanup_expired(cls):
        """
        Remove expired blacklisted tokens.

        Returns:
            Number of tokens deleted
        """
        count, _ = cls.objects.filter(expires_at__lte=timezone.now()).delete()
        return count

    def __str__(self):
        return f"BlacklistedToken({self.user_id}, {self.blacklisted_at})"
