from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("investments", "0050_dashboard_layout"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardwidget",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, auto_now_add=True
            ),
        ),
        migrations.AddField(
            model_name="dashboardwidget",
            name="updated_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, auto_now=True
            ),
        ),
        migrations.AddField(
            model_name="dashboardwidget",
            name="deleted_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
