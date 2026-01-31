from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SentimentAnalysis",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
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
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "symbol",
                    models.CharField(db_index=True, max_length=20),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("twitter", "Twitter"),
                            ("reddit", "Reddit"),
                            ("news", "News"),
                            ("combined", "Combined"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "sentiment",
                    models.CharField(
                        choices=[
                            ("positive", "Positive"),
                            ("negative", "Negative"),
                            ("neutral", "Neutral"),
                            ("mixed", "Mixed"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "vader_score",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "vader_positive",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "vader_negative",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "vader_neutral",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "vader_compound",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "textblob_polarity",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "textblob_subjectivity",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "weighted_sentiment",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "confidence",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                ("posts_analyzed", models.IntegerField(default=0)),
                ("total_posts", models.IntegerField(default=0)),
                ("positive_posts", models.IntegerField(default=0)),
                ("negative_posts", models.IntegerField(default=0)),
                ("neutral_posts", models.IntegerField(default=0)),
                ("mentions", models.JSONField(default=list)),
                ("hashtags", models.JSONField(default=list)),
                ("source_count", models.JSONField(default=dict)),
                (
                    "analysis_period_start",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("analysis_period_end", models.DateTimeField(blank=True, null=True)),
                ("cached_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("cache_ttl_minutes", models.IntegerField(default=60)),
            ],
            options={
                "db_table": "sentiment_analyses",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SocialPost",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
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
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "post_id",
                    models.CharField(max_length=200, unique=True),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[("twitter", "Twitter"), ("reddit", "Reddit")],
                        max_length=20,
                    ),
                ),
                (
                    "symbol",
                    models.CharField(db_index=True, max_length=20),
                ),
                ("author", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("url", models.URLField(blank=True, max_length=500)),
                ("followers_count", models.IntegerField(default=0)),
                (
                    "engagement_score",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "sentiment",
                    models.CharField(
                        choices=[
                            ("positive", "Positive"),
                            ("negative", "Negative"),
                            ("neutral", "Neutral"),
                            ("mixed", "Mixed"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "vader_score",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "textblob_polarity",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                ("posted_at", models.DateTimeField(db_index=True)),
                ("fetched_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("mentions", models.JSONField(default=list)),
                ("hashtags", models.JSONField(default=list)),
                ("is_retweet", models.BooleanField(default=False)),
                ("is_reply", models.BooleanField(default=False)),
                ("reply_to_post_id", models.CharField(blank=True, max_length=200)),
                ("upvotes", models.IntegerField(default=0)),
                ("downvotes", models.IntegerField(default=0)),
                ("comments", models.IntegerField(default=0)),
                ("shares", models.IntegerField(default=0)),
            ],
            options={
                "db_table": "social_posts",
                "ordering": ["-posted_at"],
            },
        ),
        migrations.CreateModel(
            name="TickerMention",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
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
                ("ticker", models.CharField(db_index=True, max_length=10)),
                ("source", models.CharField(max_length=20)),
                ("mention_count", models.IntegerField(default=0)),
                ("unique_users", models.IntegerField(default=0)),
                ("total_engagement", models.BigIntegerField(default=0)),
                ("period_start", models.DateTimeField()),
                ("period_end", models.DateTimeField()),
                ("sentiment_distribution", models.JSONField(default=dict)),
                ("top_posts", models.JSONField(default=list)),
                (
                    "trending_score",
                    models.DecimalField(decimal_places=4, default=0, max_digits=10),
                ),
                ("is_trending", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "ticker_mentions",
            },
        ),
        migrations.CreateModel(
            name="SentimentAlert",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
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
                (
                    "alert_type",
                    models.CharField(
                        choices=[
                            ("sentiment_spike", "Sentiment Spike"),
                            ("sentiment_reversal", "Sentiment Reversal"),
                            ("extreme_sentiment", "Extreme Sentiment"),
                            ("trending_mention", "Trending Mention"),
                            ("volume_spike", "Volume Spike"),
                        ],
                        max_length=30,
                    ),
                ),
                ("symbol", models.CharField(max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("triggered", "Triggered"),
                            ("expired", "Expired"),
                            ("dismissed", "Dismissed"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                (
                    "threshold",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                (
                    "threshold_direction",
                    models.CharField(
                        choices=[("above", "Above"), ("below", "Below")],
                        max_length=10,
                    ),
                ),
                ("triggered_at", models.DateTimeField(blank=True, null=True)),
                (
                    "triggered_value",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=5, null=True
                    ),
                ),
                ("notification_sent", models.BooleanField(default=False)),
                ("notification_channels", models.JSONField(default=list)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "sentiment_alerts",
            },
        ),
        migrations.CreateModel(
            name="SentimentCache",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
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
                ("symbol", models.CharField(db_index=True, max_length=20)),
                ("source", models.CharField(max_length=20)),
                ("cached_sentiment", models.JSONField()),
                ("cached_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField()),
            ],
            options={
                "db_table": "sentiment_cache",
            },
        ),
        migrations.AddIndex(
            model_name="sentimentanalysis",
            index=models.Index(
                fields=["symbol", "source"], name="sentiment_a_symbol_8c9a8c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="sentimentanalysis",
            index=models.Index(
                fields=["symbol", "created_at"], name="sentiment_a_symbol_2b0f5c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="sentimentanalysis",
            index=models.Index(
                fields=["cached_at"], name="sentiment_a_cached__322a2f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="socialpost",
            index=models.Index(
                fields=["symbol", "posted_at"], name="social_post_symbol_8a8a8a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="socialpost",
            index=models.Index(
                fields=["source", "symbol"], name="social_post_source_9b9b9b_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="tickermention",
            constraint=models.UniqueConstraint(
                fields=["ticker", "source", "period_start"],
                name="unique_ticker_source_period",
            ),
        ),
        migrations.AddConstraint(
            model_name="sentimentcache",
            constraint=models.UniqueConstraint(
                fields=["symbol", "source"], name="unique_symbol_source"
            ),
        ),
    ]
