"""
AI Advisor Models
Pre-generated templates and user-specific AI reports.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


TEMPLATE_TYPES = [
    ("market_summary", "Market Summary"),
    ("asset_analysis", "Asset Analysis"),
    ("sector_report", "Sector Report"),
    ("risk_commentary", "Risk Commentary"),
    ("sentiment_summary", "Sentiment Summary"),
    ("volatility_outlook", "Volatility Outlook"),
    ("options_strategy", "Options Strategy"),
    ("bond_market", "Bond Market Analysis"),
    ("crypto_market", "Crypto Market Analysis"),
    ("earnings_preview", "Earnings Preview"),
    ("macro_outlook", "Macro Economic Outlook"),
]

REPORT_TYPES = [
    ("portfolio_report", "Portfolio Report"),
    ("holdings_analysis", "Holdings Analysis"),
    ("performance_attribution", "Performance Attribution"),
    ("risk_assessment", "Risk Assessment"),
    ("rebalancing_suggestion", "Rebalancing Suggestion"),
    ("tax_efficiency", "Tax Efficiency Analysis"),
]


class AITemplate(UUIDModel, TimestampedModel):
    """
    Pre-generated AI templates refreshed twice daily.
    Covers market summaries, asset analysis, sector reports, etc.
    """

    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_TYPES,
        db_index=True,
        help_text="Type of AI template",
    )
    symbol = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True,
        help_text="Asset symbol (null for general templates)",
    )
    sector_fk = models.ForeignKey(
        "assets.Sector",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_templates",
        help_text="Sector (foreign key)",
    )
    sector = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="[DEPRECATED] Use sector_fk instead. Sector name for sector-level templates",
    )
    asset_class = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        db_index=True,
        help_text="Asset class: equity, crypto, fixed_income, commodity",
    )

    # Content
    title = models.CharField(max_length=255, help_text="Template title for display")
    content = models.TextField(help_text="AI-generated content (Markdown supported)")
    summary = models.TextField(
        max_length=500, blank=True, help_text="Brief summary for quick preview"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data: prices, metrics, model info",
    )
    version = models.IntegerField(
        default=1, help_text="Version number for cache busting"
    )

    # Refresh timing
    last_generated_at = models.DateTimeField(
        help_text="When this template was last generated"
    )
    next_refresh_at = models.DateTimeField(
        db_index=True, help_text="When this template should be refreshed"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this template is currently active",
    )
    generation_error = models.TextField(
        blank=True, null=True, help_text="Error message if generation failed"
    )

    class Meta:
        db_table = "ai_templates"
        verbose_name = "AI Template"
        verbose_name_plural = "AI Templates"
        ordering = ["-last_generated_at"]
        indexes = [
            models.Index(fields=["template_type", "symbol"]),
            models.Index(fields=["template_type", "sector"]),
            models.Index(fields=["template_type", "asset_class"]),
            models.Index(fields=["next_refresh_at", "is_active"]),
            models.Index(fields=["is_active", "template_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["template_type", "symbol", "sector"],
                name="unique_template_scope",
            ),
        ]

    def __str__(self):
        scope = self.symbol or self.sector or self.asset_class or "general"
        return f"{self.get_template_type_display()}: {scope}"

    @property
    def is_stale(self) -> bool:
        """Check if template needs refresh."""
        return timezone.now() >= self.next_refresh_at

    @property
    def age_hours(self) -> float:
        """Get template age in hours."""
        delta = timezone.now() - self.last_generated_at
        return delta.total_seconds() / 3600

    def refresh_needed(self) -> bool:
        """Check if refresh is needed based on template type."""
        refresh_intervals = {
            "market_summary": 6,  # Every 6 hours (4x daily)
            "asset_analysis": 12,  # Twice daily
            "sector_report": 24,  # Daily
            "risk_commentary": 12,  # Twice daily
            "sentiment_summary": 12,  # Twice daily
            "volatility_outlook": 12,  # Twice daily
            "options_strategy": 6,  # Every 6 hours
            "bond_market": 24,  # Daily
            "crypto_market": 6,  # Every 6 hours (24/7 trading)
            "earnings_preview": 12,  # Before earnings season
            "macro_outlook": 24,  # Daily
        }
        interval = refresh_intervals.get(self.template_type, 12)
        return self.is_stale or self.age_hours >= interval


class UserAIReport(UUIDModel, TimestampedModel):
    """
    User-specific AI reports generated nightly for premium users.
    Cached for 24 hours.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="ai_reports",
        help_text="Report owner",
    )
    report_type = models.CharField(
        max_length=50, choices=REPORT_TYPES, db_index=True, help_text="Type of report"
    )
    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ai_reports",
        help_text="Associated portfolio (if applicable)",
    )
    watchlist = models.ForeignKey(
        "investments.Watchlist",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ai_reports",
        help_text="Associated watchlist (if applicable)",
    )

    # Content
    title = models.CharField(max_length=255, help_text="Report title")
    content = models.TextField(
        help_text="AI-generated report content (Markdown supported)"
    )
    summary = models.TextField(
        max_length=500, blank=True, help_text="Brief summary for notifications"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report metrics: returns, risk, allocations, etc.",
    )
    version = models.IntegerField(default=1, help_text="Version for cache busting")

    # Timing
    generated_at = models.DateTimeField(help_text="When this report was generated")
    expires_at = models.DateTimeField(
        db_index=True, help_text="When this report expires"
    )

    # Status
    is_stale = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Marked stale if underlying data changed significantly",
    )
    generation_error = models.TextField(
        blank=True, null=True, help_text="Error message if generation failed"
    )

    class Meta:
        db_table = "user_ai_reports"
        verbose_name = "User AI Report"
        verbose_name_plural = "User AI Reports"
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["user", "report_type"]),
            models.Index(fields=["user", "report_type", "portfolio"]),
            models.Index(fields=["expires_at", "is_stale"]),
            models.Index(fields=["user", "report_type", "expires_at"]),
        ]

    def __str__(self):
        scope = self.portfolio.symbol if self.portfolio else "general"
        return f"{self.user.email}: {self.get_report_type_display()} - {scope}"

    @property
    def is_expired(self) -> bool:
        """Check if report has expired."""
        return timezone.now() >= self.expires_at

    @property
    def age_hours(self) -> float:
        """Get report age in hours."""
        delta = timezone.now() - self.generated_at
        return delta.total_seconds() / 3600

    @classmethod
    def get_active_report(cls, user, report_type, portfolio=None):
        """Get the most recent non-expired report."""
        queryset = cls.objects.filter(
            user=user,
            report_type=report_type,
            expires_at__gt=timezone.now(),
            is_stale=False,
        )
        if portfolio:
            queryset = queryset.filter(portfolio=portfolio)
        return queryset.order_by("-generated_at").first()


class AITemplateLog(UUIDModel, TimestampedModel):
    """
    Audit log for template generation.
    Track costs, errors, and performance.
    """

    template = models.ForeignKey(
        AITemplate,
        on_delete=models.CASCADE,
        related_name="generation_logs",
        null=True,
        blank=True,
    )
    template_type = models.CharField(
        max_length=50, choices=TEMPLATE_TYPES, db_index=True
    )
    symbol = models.CharField(max_length=20, null=True, blank=True)

    # Generation metrics
    success = models.BooleanField(default=False, db_index=True)
    error_message = models.TextField(blank=True, null=True)

    # Cost tracking
    model_used = models.CharField(max_length=50, help_text="LLM model used")
    input_tokens = models.IntegerField(default=0, help_text="Tokens in prompt")
    output_tokens = models.IntegerField(default=0, help_text="Tokens in response")
    total_tokens = models.IntegerField(default=0, db_index=True)
    compute_time_ms = models.IntegerField(
        default=0, help_text="Generation time in milliseconds"
    )

    # Data snapshots
    input_data = models.JSONField(
        default=dict, blank=True, help_text="Snapshot of input data used"
    )

    class Meta:
        db_table = "ai_template_logs"
        verbose_name = "AI Template Log"
        verbose_name_plural = "AI Template Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["template_type", "success"]),
            models.Index(fields=["created_at", "success"]),
            models.Index(fields=["total_tokens"]),
        ]

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.template_type} ({self.symbol or 'general'}) - {status}"


class AIQueryLog(UUIDModel, TimestampedModel):
    """
    Log for on-demand AI queries.
    Track usage for rate limiting and cost allocation.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="ai_queries",
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    # Query details
    query_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Type of query: portfolio, market, strategy, etc.",
    )
    query_text = models.TextField(help_text="User query or prompt")

    # Response
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(blank=True, null=True)
    response_text = models.TextField(
        blank=True, null=True, help_text="AI response (truncated if too long)"
    )

    # Cost tracking
    model_used = models.CharField(max_length=50)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    compute_time_ms = models.IntegerField(default=0)

    class Meta:
        db_table = "ai_query_logs"
        verbose_name = "AI Query Log"
        verbose_name_plural = "AI Query Logs"
        ordering = ["-created_at"]

    def __str__(self):
        user_id = self.user.email if self.user else self.session_id
        return f"{user_id}: {self.query_type}"
