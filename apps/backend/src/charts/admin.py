from django.contrib import admin
from .models.chart_drawing import (
    ChartDrawing,
    TechnicalIndicatorValue,
    ChartDrawingManager,
)


@admin.register(ChartDrawing)
class ChartDrawingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "asset",
        "drawing_type",
        "timeframe",
        "visible",
        "created_at",
    ]
    list_filter = ["drawing_type", "timeframe", "visible"]
    search_fields = ["user__email", "asset__symbol"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TechnicalIndicatorValue)
class TechnicalIndicatorValueAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "asset",
        "indicator_type",
        "timeframe",
        "timestamp",
        "value",
        "signal",
        "strength",
    ]
    list_filter = ["indicator_type", "timeframe", "signal", "strength"]
    search_fields = ["asset__symbol"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ChartDrawingManager)
class ChartDrawingManagerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "name",
        "is_default",
        "chart_type",
        "default_timeframe",
        "created_at",
    ]
    list_filter = ["is_default", "chart_type", "default_timeframe"]
    search_fields = ["user__email", "name"]
    readonly_fields = ["created_at", "updated_at"]
