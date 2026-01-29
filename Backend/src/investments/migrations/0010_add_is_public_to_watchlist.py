# Generated migration to add is_public field before indexes are added

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("investments", "0009_dataprovider_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="watchlist",
            name="is_public",
            field=models.BooleanField(
                default=False, help_text="Make this watchlist visible to others"
            ),
        ),
    ]
