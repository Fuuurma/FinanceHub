# Generated migration for BlacklistedToken model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_account_type_alter_user_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlacklistedToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token", models.CharField(db_index=True, max_length=500, unique=True)),
                ("user_id", models.CharField(db_index=True, max_length=36)),
                (
                    "blacklisted_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
            options={
                "verbose_name": "Blacklisted Token",
                "verbose_name_plural": "Blacklisted Tokens",
                "indexes": [
                    models.Index(fields=["token"], name="users_black_token_idx"),
                    models.Index(fields=["user_id"], name="users_black_user_idx"),
                    models.Index(fields=["expires_at"], name="users_black_expires_idx"),
                    models.Index(
                        fields=["blacklisted_at"], name="users_black_blacklisted_idx"
                    ),
                ],
            },
        ),
    ]
