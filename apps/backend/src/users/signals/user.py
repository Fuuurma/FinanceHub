from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models.user import User
from users.models.user_profile import UserProfile
from trading.services.paper_trading_service import PaperTradingService


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_paper_trading_account(sender, instance, created, **kwargs):
    if created:
        service = PaperTradingService()
        service.get_or_create_account(instance)
