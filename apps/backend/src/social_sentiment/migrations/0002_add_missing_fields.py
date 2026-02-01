from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social_sentiment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tickermention",
            name="avg_sentiment",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=5, null=True
            ),
        ),
        migrations.AddField(
            model_name="tickermention",
            name="sentiment_change",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=5, null=True
            ),
        ),
        migrations.AddField(
            model_name="tickermention",
            name="volume_spike",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="tickermention",
            name="last_mentioned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
