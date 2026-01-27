from django.contrib import admin

from investments.models.alert import Alert
from investments.models.benchmark import Benchmark
from investments.models.benchmark_price_history import BenchmarkPriceHistory
from investments.models.corporate_action import CorporateAction
from investments.models.currency import Currency
from investments.models.data_provider import DataProvider
from investments.models.dividend import Dividend
from investments.models.exchange_rate import ExchangeRate
from investments.models.transaction import Transaction
from investments.models.transaction_type import TransactionType
from investments.models.watchlist import Watchlist
from investments.models.api_key import APIKey, APIKeyStatus
from investments.models.api_call_log import APIKeyUsageLog

admin.site.register(TransactionType)
admin.site.register(Transaction)
admin.site.register(Currency)
admin.site.register(ExchangeRate)
admin.site.register(Dividend)
admin.site.register(CorporateAction)
admin.site.register(Benchmark)
admin.site.register(BenchmarkPriceHistory)
admin.site.register(Alert)
admin.site.register(Watchlist)
admin.site.register(DataProvider)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'status', 'priority', 'usage_today', 'usage_this_hour', 'last_used_at', 'consecutive_failures']
    list_filter = ['status', 'key_type', 'provider']
    search_fields = ['name', 'provider__name']
    readonly_fields = ['total_usage_lifetime', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Key Details', {
            'fields': ('provider', 'name', 'key_value', 'key_type', 'status')
        }),
        ('Rate Limits', {
            'fields': ('rate_limit_per_minute', 'rate_limit_daily', 'priority')
        }),
        ('Usage Tracking', {
            'fields': ('usage_today', 'usage_this_hour', 'total_usage_lifetime', 'last_used_at')
        }),
        ('Health', {
            'fields': ('last_success_at', 'last_failure_at', 'consecutive_failures', 'auto_recover_after_minutes', 'max_consecutive_failures')
        }),
        ('Metadata', {
            'fields': ('metadata', 'notes')
        }),
    )
    
    actions = ['mark_as_active', 'reset_usage_counters']
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} keys marked as active")
    mark_as_active.short_description = "Mark as active"
    
    def reset_usage_counters(self, request, queryset):
        from django.utils import timezone
        now = timezone.now()
        queryset.update(
            usage_today=0,
            usage_this_hour=0,
            usage_today_reset=now,
            usage_this_hour_reset=now
        )
        self.message_user(request, f"Reset usage counters for {queryset.count()} keys")
    reset_usage_counters.short_description = "Reset usage counters"


@admin.register(APIKeyUsageLog)
class APIKeyUsageLogAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'endpoint', 'method', 'status_code', 'success', 'response_time_ms', 'error_type', 'created_at']
    list_filter = ['success', 'status_code', 'error_type', 'api_key']
    search_fields = ['endpoint', 'api_key__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
