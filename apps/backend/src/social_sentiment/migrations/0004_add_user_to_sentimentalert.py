from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social_sentiment", "0003_add_soft_delete_fields"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sentimentalert",
            name="user",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name="sentiment_alerts",
                to="users.user",
            ),
        ),
    ]
