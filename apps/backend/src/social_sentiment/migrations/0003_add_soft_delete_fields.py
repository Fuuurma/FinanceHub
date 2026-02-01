from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social_sentiment", "0002_add_missing_fields"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialpost",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="+",
                to="users.user",
            ),
        ),
        migrations.AddField(
            model_name="sentimentanalysis",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="+",
                to="users.user",
            ),
        ),
    ]
