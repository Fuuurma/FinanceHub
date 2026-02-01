"""
Social Sentiment Analysis Models
VADER + TextBlob sentiment analysis with Twitter/Reddit integration
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.soft_delete_model import SoftDeleteModel

User = get_user_model()


class SentimentAnalysis(UUIDModel, TimestampedModel, SoftDeleteModel):
    SENTIMENT_CHOICES = [
        ("positive", "Positive"),
        ("negative", "Negative"),
        ("neutral", "Neutral"),
        ("mixed", "Mixed"),
    ]

    SOURCE_CHOICES = [
        ("twitter", "Twitter"),
        ("reddit", "Reddit"),
        ("news", "News"),
        ("combined", "Combined"),
    ]

    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sentiment_analyses",
    )
    symbol = models.CharField(max_length=20, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)

    vader_score = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    vader_positive = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    vader_negative = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    vader_neutral = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    vader_compound = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    textblob_polarity = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    textblob_subjectivity = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    weighted_sentiment = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    confidence = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    posts_analyzed = models.IntegerField(default=0)
    total_posts = models.IntegerField(default=0)
    positive_posts = models.IntegerField(default=0)
    negative_posts = models.IntegerField(default=0)
    neutral_posts = models.IntegerField(default=0)

    mentions = models.JSONField(default=list)
    hashtags = models.JSONField(default=list)

    source_count = models.JSONField(default=dict)

    analysis_period_start = models.DateTimeField(null=True, blank=True)
    analysis_period_end = models.DateTimeField(null=True, blank=True)

    cached_at = models.DateTimeField(default=timezone.now)
    cache_ttl_minutes = models.IntegerField(default=60)

    class Meta:
        db_table = "sentiment_analyses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["symbol", "source"]),
            models.Index(fields=["symbol", "created_at"]),
            models.Index(fields=["cached_at"]),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.sentiment} ({self.vader_compound})"


class SocialPost(UUIDModel, TimestampedModel, SoftDeleteModel):
    SOURCE_CHOICES = [
        ("twitter", "Twitter"),
        ("reddit", "Reddit"),
    ]

    post_id = models.CharField(max_length=200, unique=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    symbol = models.CharField(max_length=20, db_index=True)

    author = models.CharField(max_length=200)
    content = models.TextField()
    url = models.URLField(max_length=500, blank=True)

    followers_count = models.IntegerField(default=0)
    engagement_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    sentiment = models.CharField(
        max_length=20, choices=SentimentAnalysis.SENTIMENT_CHOICES, null=True
    )
    vader_score = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    textblob_polarity = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    posted_at = models.DateTimeField(db_index=True)
    fetched_at = models.DateTimeField(default=timezone.now)

    mentions = models.JSONField(default=list)
    hashtags = models.JSONField(default=list)

    is_retweet = models.BooleanField(default=False)
    is_reply = models.BooleanField(default=False)
    reply_to_post_id = models.CharField(max_length=200, blank=True)

    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    class Meta:
        db_table = "social_posts"
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["symbol", "posted_at"]),
            models.Index(fields=["source", "symbol"]),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.post_id[:20]}"


class TickerMention(UUIDModel, TimestampedModel):
    ticker = models.CharField(max_length=10, db_index=True)
    source = models.CharField(max_length=20)
    mention_count = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    total_engagement = models.BigIntegerField(default=0)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    avg_sentiment = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    sentiment_change = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    sentiment_distribution = models.JSONField(default=dict)
    top_posts = models.JSONField(default=list)

    trending_score = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    is_trending = models.BooleanField(default=False)

    class Meta:
        db_table = "ticker_mentions"
        unique_together = [["ticker", "source", "period_start"]]

    def __str__(self):
        return f"{self.ticker} - {self.mention_count} mentions"


class SentimentAlert(UUIDModel, TimestampedModel):
    ALERT_TYPE_CHOICES = [
        ("sentiment_spike", "Sentiment Spike"),
        ("sentiment_reversal", "Sentiment Reversal"),
        ("extreme_sentiment", "Extreme Sentiment"),
        ("trending_mention", "Trending Mention"),
        ("volume_spike", "Volume Spike"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("triggered", "Triggered"),
        ("expired", "Expired"),
        ("dismissed", "Dismissed"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sentiment_alerts"
    )

    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    symbol = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    threshold = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    threshold_direction = models.CharField(
        max_length=10, choices=[("above", "Above"), ("below", "Below")]
    )

    triggered_at = models.DateTimeField(null=True, blank=True)
    triggered_value = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    notification_sent = models.BooleanField(default=False)
    notification_channels = models.JSONField(default=list)

    expires_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_triggered(self) -> bool:
        return self.status == "triggered"

    @property
    def last_triggered_at(self):
        return self.triggered_at

    class Meta:
        db_table = "sentiment_alerts"

    def __str__(self):
        return f"{self.alert_type} - {self.symbol}"


class SentimentCache(UUIDModel, TimestampedModel):
    symbol = models.CharField(max_length=20, db_index=True)
    source = models.CharField(max_length=20)
    cached_sentiment = models.JSONField()
    cached_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "sentiment_cache"
        unique_together = [["symbol", "source"]]

    def __str__(self):
        return f"{self.symbol} - {self.source}"
