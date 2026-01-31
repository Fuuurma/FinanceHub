from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SavedSearch(models.Model):
    user_id = models.IntegerField()

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    search_query = models.CharField(max_length=200, blank=True, default="")
    filters = models.JSONField(default=dict)
    sort_by = models.CharField(max_length=50, default="market_cap")
    sort_order = models.CharField(max_length=10, default="desc")

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    use_count = models.IntegerField(default=0)

    class Meta:
        db_table = "investments_saved_search"
        ordering = ["-is_default", "-use_count", "-last_used_at"]
        indexes = [
            models.Index(fields=["user_id", "-use_count"]),
            models.Index(fields=["user_id", "-last_used_at"]),
        ]


class SearchHistory(models.Model):
    user_id = models.IntegerField()

    query = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, null=True, blank=True)

    results_count = models.IntegerField()
    clicked_asset_id = models.IntegerField(null=True, blank=True)

    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "investments_search_history"
        ordering = ["-searched_at"]
        indexes = [
            models.Index(fields=["user_id", "-searched_at"]),
            models.Index(fields=["user_id", "query"]),
        ]


class ScreenTemplate(models.Model):
    CATEGORY_CHOICES = [
        ("value", "Value Investing"),
        ("growth", "Growth Investing"),
        ("dividend", "Dividend Stocks"),
        ("momentum", "Momentum Trading"),
        ("quality", "Quality Companies"),
        ("small_cap", "Small Cap Opportunities"),
        ("etf", "ETF Screener"),
        ("crypto", "Crypto Screener"),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()

    filters = models.JSONField(default=dict)

    default_sort_by = models.CharField(max_length=50)
    default_sort_order = models.CharField(max_length=10)

    is_featured = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_screen_template"
        ordering = ["-is_featured", "-use_count", "name"]


class AssetComparison(models.Model):
    user_id = models.IntegerField()

    name = models.CharField(max_length=200)
    assets = models.JSONField(default=list)

    metrics = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_asset_comparison"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user_id", "-updated_at"]),
        ]


class SearchSuggestionLog(models.Model):
    query = models.CharField(max_length=200)
    suggestion = models.CharField(max_length=200)
    asset_id = models.IntegerField()
    clicked = models.BooleanField(default=True)
    position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "investments_search_suggestion_log"
        indexes = [
            models.Index(fields=["query", "-created_at"]),
        ]


class ScreenerPreset(models.Model):
    user_id = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    preset_type = models.CharField(max_length=50, default="custom")
    category = models.CharField(max_length=50, blank=True, default="")

    criteria = models.JSONField(default=dict)
    sort_by = models.CharField(max_length=50, default="market_cap")
    sort_order = models.CharField(max_length=10, default="desc")

    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_screener_preset"
        ordering = ["-is_default", "-use_count", "-created_at"]
        indexes = [
            models.Index(fields=["user_id", "-created_at"]),
            models.Index(fields=["preset_type", "category"]),
        ]
