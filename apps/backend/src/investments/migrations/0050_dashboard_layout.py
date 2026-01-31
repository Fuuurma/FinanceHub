from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_account_type_alter_user_status"),
        ("investments", "0019_alter_currency_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardLayout",
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
                ("name", models.CharField(default="Default", max_length=100)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dashboard_layouts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "name")},
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DashboardWidget",
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
                ("widget_id", models.CharField(max_length=100)),
                (
                    "widget_type",
                    models.CharField(
                        choices=[
                            ("chart", "Chart"),
                            ("watchlist", "Watchlist"),
                            ("portfolio", "Portfolio"),
                            ("news", "News"),
                            ("screener", "Screener"),
                            ("metrics", "Metrics"),
                            ("positions", "Positions"),
                            ("performance", "Performance"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                            ("full", "Full"),
                        ],
                        default="medium",
                        max_length=10,
                    ),
                ),
                ("position_x", models.IntegerField(default=0)),
                ("position_y", models.IntegerField(default=0)),
                ("config", models.JSONField(blank=True, default=dict)),
                ("visible", models.BooleanField(default=True)),
                ("order", models.IntegerField(default=0)),
                (
                    "layout",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="widgets",
                        to="investments.dashboardlayout",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
    ]
