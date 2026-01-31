from django.core.management.base import BaseCommand
from users.models.token_blacklist import BlacklistedToken


class Command(BaseCommand):
    help = "Clean up expired blacklisted tokens from the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        """Execute the cleanup command."""
        dry_run = options.get("dry_run", False)

        if dry_run:
            # Count expired tokens without deleting
            from django.utils import timezone

            count = BlacklistedToken.objects.filter(
                expires_at__lte=timezone.now()
            ).count()
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} expired blacklisted tokens"
                )
            )
        else:
            # Actually delete expired tokens
            deleted_count = BlacklistedToken.cleanup_expired()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} expired blacklisted tokens"
                )
            )
