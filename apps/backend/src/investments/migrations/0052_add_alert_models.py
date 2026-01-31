from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portfolios", "0002_portfolioperformance"),
        ("assets", "0013_country_deleted_at_country_deleted_by_and_more"),
        ("investments", "0051_add_base_fields_to_dashboardwidget"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertTrigger",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("triggered_at", models.DateTimeField(auto_now_add=True)),
                ("trigger_value", models.DecimalField(decimal_places=4, max_digits=20)),
                (
                    "asset_price",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=20, null=True
                    ),
                ),
                ("asset_name", models.CharField(blank=True, max_length=200)),
                ("email_sent", models.BooleanField(default=False)),
                ("email_sent_at", models.DateTimeField(blank=True, null=True)),
                ("email_error", models.TextField(blank=True)),
                ("push_sent", models.BooleanField(default=False)),
                ("push_sent_at", models.DateTimeField(blank=True, null=True)),
                ("push_error", models.TextField(blank=True)),
                ("sms_sent", models.BooleanField(default=False)),
                ("sms_sent_at", models.DateTimeField(blank=True, null=True)),
                ("sms_error", models.TextField(blank=True)),
                ("in_app_sent", models.BooleanField(default=False)),
                ("in_app_sent_at", models.DateTimeField(blank=True, null=True)),
                ("viewed", models.BooleanField(default=False)),
                ("viewed_at", models.DateTimeField(blank=True, null=True)),
                ("dismissed", models.BooleanField(default=False)),
                ("dismissed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "alert",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="triggers",
                        to="investments.alert",
                    ),
                ),
            ],
            options={
                "ordering": ["-triggered_at"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("notification_type", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("priority", models.CharField(default="normal", max_length=20)),
                ("read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("action_url", models.CharField(blank=True, max_length=500)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "related_asset",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="assets.asset",
                    ),
                ),
                (
                    "related_alert_trigger",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="investments.alerttrigger",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "channel",
                    models.CharField(
                        choices=[
                            ("email", "Email"),
                            ("push", "Push Notification"),
                            ("sms", "SMS"),
                            ("in_app", "In-App"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "alert_type",
                    models.CharField(
                        choices=[
                            ("price_above", "Price Above"),
                            ("price_below", "Price Below"),
                            ("percent_change", "Percent Change"),
                            ("volume_above", "Volume Above"),
                            ("news_mention", "News Mention"),
                            ("portfolio_change", "Portfolio Value Change"),
                            ("volatility", "Volatility Alert"),
                            ("rsi", "RSI Level"),
                            ("earning_above", "Earnings Above Estimate"),
                            ("earning_below", "Earnings Below Estimate"),
                            ("dividend", "Dividend Announced"),
                            ("custom", "Custom Condition"),
                        ],
                        max_length=30,
                    ),
                ),
                ("enabled", models.BooleanField(default=True)),
                ("quiet_hours_enabled", models.BooleanField(default=False)),
                ("quiet_hours_start", models.TimeField(blank=True, null=True)),
                ("quiet_hours_end", models.TimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_preferences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "channel", "alert_type")},
            },
        ),
        migrations.CreateModel(
            name="ScreenerPreset",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("filters", models.JSONField(default=dict)),
                ("is_public", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="screener_presets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("user", "name")},
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["user", "read", "created_at"],
                name="investments_notif_user_re_9d9c89_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["notification_type", "created_at"],
                name="investments_notif_notific_651f92_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="alerttrigger",
            index=models.Index(
                fields=["alert", "triggered_at"],
                name="investments_alert_alert_id_85d097_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="alerttrigger",
            index=models.Index(
                fields=["viewed", "dismissed"],
                name="investments_alert_viewed__7f9aa3_idx",
            ),
        ),
    ]
