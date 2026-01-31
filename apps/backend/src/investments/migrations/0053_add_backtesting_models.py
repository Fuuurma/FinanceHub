# Generated manually for backtesting models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.helpers.uuid_model
import utils.helpers.timestamped_model
import utils.helpers.soft_delete_model


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("investments", "0052_add_alert_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="TradingStrategy",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "strategy_type",
                    models.CharField(
                        choices=[
                            ("sma_crossover", "SMA Crossover"),
                            ("rsi_mean_reversion", "RSI Mean Reversion"),
                            ("custom", "Custom Python"),
                        ],
                        max_length=50,
                    ),
                ),
                ("config", models.JSONField(default=dict)),
                ("description", models.TextField(blank=True, default="")),
                ("is_public", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trading_strategies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "db_table": "trading_strategy",
            },
            bases=(
                utils.helpers.soft_delete_model.SoftDeleteModel,
                utils.helpers.timestamped_model.TimestampedModel,
                utils.helpers.uuid_model.UUIDModel,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Backtest",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "initial_capital",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                (
                    "total_return",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "sharpe_ratio",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                (
                    "sortino_ratio",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                (
                    "max_drawdown",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                (
                    "win_rate",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                (
                    "profit_factor",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                ("total_trades", models.IntegerField(null=True)),
                ("winning_trades", models.IntegerField(null=True)),
                ("losing_trades", models.IntegerField(null=True)),
                ("equity_curve", models.JSONField(default=list)),
                ("drawdown_curve", models.JSONField(default=list)),
                ("trades_data", models.JSONField(default=list)),
                ("error_message", models.TextField(blank=True, default="")),
                (
                    "strategy",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backtests",
                        to="investments.tradingstrategy",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backtests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "db_table": "backtest",
            },
            bases=(
                utils.helpers.timestamped_model.TimestampedModel,
                utils.helpers.uuid_model.UUIDModel,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="BacktestTrade",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("asset_symbol", models.CharField(max_length=20)),
                (
                    "action",
                    models.CharField(
                        choices=[("BUY", "Buy"), ("SELL", "Sell")], max_length=10
                    ),
                ),
                ("quantity", models.DecimalField(decimal_places=6, max_digits=15)),
                ("price", models.DecimalField(decimal_places=4, max_digits=15)),
                ("value", models.DecimalField(decimal_places=2, max_digits=15)),
                (
                    "commission",
                    models.DecimalField(decimal_places=4, default=0, max_digits=15),
                ),
                (
                    "slippage",
                    models.DecimalField(decimal_places=4, default=0, max_digits=15),
                ),
                ("timestamp", models.DateTimeField()),
                (
                    "pnl",
                    models.DecimalField(decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "pnl_percent",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                (
                    "backtest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trades",
                        to="investments.backtest",
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
                "db_table": "backtest_trade",
            },
            bases=(
                utils.helpers.timestamped_model.TimestampedModel,
                utils.helpers.uuid_model.UUIDModel,
                models.Model,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="tradingstrategy",
            unique_together={("user", "name")},
        ),
    ]
