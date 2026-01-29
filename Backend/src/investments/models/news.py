"""
News Article Model
Stores news articles with sentiment analysis from various providers
"""

from django.db import models
from django.core.validators import URLValidator
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class NewsArticle(UUIDModel, TimestampedModel):
    """News article with sentiment analysis"""

    class Sentiment(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEGATIVE = "negative", "Negative"
        NEUTRAL = "neutral", "Neutral"

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=1000)
    source = models.CharField(max_length=100, db_index=True)
    author = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(db_index=True)

    # Sentiment analysis
    sentiment = models.CharField(
        max_length=20,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL,
        db_index=True,
    )
    sentiment_score = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="-1.0 to 1.0, negative is bearish, positive is bullish",
    )

    # Related assets
    related_symbols = models.JSONField(
        default=list,
        blank=True,
        help_text="List of ticker symbols mentioned in the article",
    )

    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="News category (e.g., 'technology', 'finance')",
    )

    # Images
    image_url = models.URLField(max_length=1000, blank=True)
    thumbnail_url = models.URLField(max_length=1000, blank=True)

    class Meta:
        db_table = "news_articles"
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["source"]),
            models.Index(fields=["sentiment"]),
            models.Index(fields=["category"]),
            models.Index(fields=["published_at", "source"]),
        ]

    def __str__(self):
        return f"{self.source}: {self.title[:50]}"
