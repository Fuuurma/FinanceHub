"""
Unit tests for Chart Drawing Tools API.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.test import AsyncRequestFactory
from api.charts import router


class TestChartDrawingModel:
    """Unit tests for ChartDrawingModel."""

    def test_drawing_model_creation(self):
        """Test creating a chart drawing model instance."""
        from investments.models.chart_drawing import ChartDrawingModel

        drawing = ChartDrawingModel(
            symbol="AAPL",
            timeframe="1d",
            drawing_type="trend_line",
            coordinates={"x1": 100, "y1": 200, "x2": 300, "y2": 400},
            color="#3b82f6",
        )

        assert drawing.symbol == "AAPL"
        assert drawing.timeframe == "1d"
        assert drawing.drawing_type == "trend_line"
        assert drawing.color == "#3b82f6"
        assert drawing.is_visible is True

    def test_drawing_type_choices(self):
        """Test that all drawing types are valid."""
        from investments.models.chart_drawing import ChartDrawingModel

        valid_types = [
            "horizontal_line",
            "vertical_line",
            "trend_line",
            "support",
            "resistance",
            "fibonacci",
            "rectangle",
            "text",
        ]

        for drawing_type in valid_types:
            drawing = ChartDrawingModel(
                symbol="AAPL",
                timeframe="1d",
                drawing_type=drawing_type,
                coordinates={},
            )
            assert drawing.drawing_type == drawing_type

    def test_chart_layout_model_creation(self):
        """Test creating a chart layout model instance."""
        from investments.models.chart_drawing import ChartLayoutModel

        layout = ChartLayoutModel(
            name="My Layout",
            description="A custom chart layout",
            is_default=False,
            layout_config={"indicators": ["SMA", "EMA"]},
        )

        assert layout.name == "My Layout"
        assert layout.is_default is False
        assert "indicators" in layout.layout_config

    def test_technical_indicator_model_creation(self):
        """Test creating a technical indicator model instance."""
        from investments.models.chart_drawing import TechnicalIndicator

        indicator = TechnicalIndicator(
            symbol="BTC",
            timeframe="1h",
            indicator_type="rsi",
            value=Decimal("65.5"),
            signal="neutral",
        )

        assert indicator.symbol == "BTC"
        assert indicator.indicator_type == "rsi"
        assert float(indicator.value) == 65.5

    def test_chart_screenshot_model_creation(self):
        """Test creating a chart screenshot model instance."""
        from investments.models.chart_drawing import ChartScreenshot

        screenshot = ChartScreenshot(
            symbol="TSLA",
            timeframe="4h",
            share_id="abc123xyz",
            drawings=[{"type": "trend_line", "points": [1, 2, 3, 4]}],
        )

        assert screenshot.symbol == "TSLA"
        assert screenshot.share_id == "abc123xyz"
        assert len(screenshot.drawings) == 1
        assert screenshot.view_count == 0


class TestChartsApiUnit:
    """Unit tests for Charts API endpoints."""

    def test_chart_data_point_schema(self):
        """Test ChartDataPoint response schema."""
        from api.charts import ChartDataPoint

        data_point = ChartDataPoint(
            timestamp="2026-01-30T12:00:00Z",
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=1000000,
        )

        assert data_point.timestamp == "2026-01-30T12:00:00Z"
        assert data_point.open == 150.0
        assert data_point.high == 155.0
        assert data_point.close == 153.0

    def test_chart_drawing_schema(self):
        """Test ChartDrawing response schema."""
        from api.charts import ChartDrawing

        drawing = ChartDrawing(
            id="test-id",
            user="testuser",
            symbol="AAPL",
            timeframe="1d",
            drawing_type="fibonacci",
            coordinates={"start": 100, "end": 200},
            color="#ff0000",
            is_visible=True,
            created_at="2026-01-30T12:00:00Z",
            updated_at="2026-01-30T12:00:00Z",
        )

        assert drawing.id == "test-id"
        assert drawing.drawing_type == "fibonacci"
        assert drawing.color == "#ff0000"

    def test_drawing_create_request_schema(self):
        """Test DrawingCreateRequest request schema."""
        from api.charts import DrawingCreateRequest

        request = DrawingCreateRequest(
            symbol="MSFT",
            timeframe="1h",
            drawing_type="horizontal_line",
            coordinates={"y": 250.0},
            color="#00ff00",
        )

        assert request.symbol == "MSFT"
        assert request.drawing_type == "horizontal_line"
        assert request.color == "#00ff00"

    def test_drawing_update_request_schema(self):
        """Test DrawingUpdateRequest request schema."""
        from api.charts import DrawingUpdateRequest

        request = DrawingUpdateRequest(
            coordinates={"x1": 100, "y1": 200, "x2": 300, "y2": 400},
            color="#0000ff",
            is_visible=False,
        )

        assert request.coordinates["x1"] == 100
        assert request.is_visible is False

    def test_chart_layout_schema(self):
        """Test ChartLayout response schema."""
        from api.charts import ChartLayout

        layout = ChartLayout(
            id="layout-id",
            user="testuser",
            name="My Custom Layout",
            description="A layout for day trading",
            is_default=True,
            layout_config={"theme": "dark"},
            created_at="2026-01-30T12:00:00Z",
            updated_at="2026-01-30T12:00:00Z",
        )

        assert layout.name == "My Custom Layout"
        assert layout.is_default is True
        assert layout.layout_config["theme"] == "dark"

    def test_technical_indicator_value_schema(self):
        """Test TechnicalIndicatorValue response schema."""
        from api.charts import TechnicalIndicatorValue

        indicator = TechnicalIndicatorValue(
            id="ind-123",
            symbol="ETH",
            timeframe="15m",
            indicator_type="macd",
            timestamp="2026-01-30T12:00:00Z",
            value=0.5,
            signal="bullish",
            additional_data={"histogram": 0.1},
        )

        assert indicator.symbol == "ETH"
        assert indicator.indicator_type == "macd"
        assert indicator.signal == "bullish"


class TestScreenshotAndShare:
    """Tests for screenshot and share functionality."""

    def test_screenshot_request_schema(self):
        """Test ScreenshotRequest schema."""
        from api.charts import ScreenshotRequest

        request = ScreenshotRequest(
            image_data="data:image/png;base64,abc123",
            symbol="NVDA",
            timeframe="1w",
            drawings=[{"type": "trend_line", "color": "#ff0000"}],
        )

        assert "base64" in request.image_data
        assert request.symbol == "NVDA"
        assert len(request.drawings) == 1

    def test_share_response_schema(self):
        """Test ShareResponse schema."""
        from api.charts import ShareResponse

        response = ShareResponse(
            share_id="xyz789abc",
            share_url="/shared/chart/xyz789abc",
            expires_at="2026-02-06T12:00:00Z",
        )

        assert len(response.share_id) == 12
        assert "/shared/chart/" in response.share_url
        assert "2026-02" in response.expires_at

    def test_share_id_generation(self):
        """Test that share IDs are unique and properly formatted."""
        import uuid

        share_id = uuid.uuid4().hex[:12]

        assert len(share_id) == 12
        assert share_id.isalnum()

    def test_base64_image_handling(self):
        """Test base64 image data handling."""
        import base64

        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        header, encoded = image_data.split(",", 1)
        assert header == "data:image/png;base64"

        decoded = base64.b64decode(encoded)
        assert len(decoded) > 0


class TestDrawingToolsConstants:
    """Tests for drawing tools constants."""

    def test_drawing_tools_defined(self):
        """Test that all drawing tools are defined."""
        from api.charts import DRAWING_TOOLS, FIBONACCI_LEVELS

        assert len(DRAWING_TOOLS) >= 6

        tool_types = [tool["type"] for tool in DRAWING_TOOLS]
        assert "horizontal_line" in tool_types
        assert "vertical_line" in tool_types
        assert "trend_line" in tool_types
        assert "fibonacci" in tool_types

    def test_fibonacci_levels_defined(self):
        """Test that Fibonacci levels are correctly defined."""
        from api.charts import FIBONACCI_LEVELS

        expected_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

        assert len(FIBONACCI_LEVELS) == len(expected_levels)
        for i, level in enumerate(FIBONACCI_LEVELS):
            assert abs(level - expected_levels[i]) < 0.001


class TestChartsStore:
    """Tests for the frontend charts store."""

    def test_store_initial_state(self):
        """Test charts store initial state."""
        from frontend.stores.chartsStore import useChartsStore

        store = useChartsStore.getState()

        assert store.drawings == {}
        assert store.indicatorValues == {}
        assert store.layouts == []
        assert store.activeLayout is None
        assert store.isLoading is False
        assert store.error is None

    def test_store_set_drawings(self):
        """Test setting drawings for a symbol."""
        from frontend.stores.chartsStore import useChartsStore

        test_drawings = [
            {
                "id": "1",
                "type": "trend_line",
                "symbol": "AAPL",
                "timeframe": "1d",
                "coordinates": {},
                "color": "#ff0000",
                "is_visible": True,
                "created_at": "2026-01-30T12:00:00Z",
                "updated_at": "2026-01-30T12:00:00Z",
            }
        ]

        useChartsStore.getState().setDrawings("AAPL", test_drawings)

        drawings = useChartsStore.getState().drawings
        assert "AAPL" in drawings
        assert len(drawings["AAPL"]) == 1

    def test_store_add_drawing(self):
        """Test adding a drawing to a symbol."""
        from frontend.stores.chartsStore import useChartsStore

        new_drawing = {
            "id": "2",
            "type": "fibonacci",
            "symbol": "AAPL",
            "timeframe": "1d",
            "coordinates": {},
            "color": "#00ff00",
            "is_visible": True,
            "created_at": "2026-01-30T12:00:00Z",
            "updated_at": "2026-01-30T12:00:00Z",
        }

        useChartsStore.getState().addDrawing("AAPL", new_drawing)

        drawings = useChartsStore.getState().drawings
        assert len(drawings["AAPL"]) == 2

    def test_store_remove_drawing(self):
        """Test removing a drawing from a symbol."""
        from frontend.stores.chartsStore import useChartsStore

        useChartsStore.getState().removeDrawing("AAPL", "1")

        drawings = useChartsStore.getState().drawings
        assert len(drawings["AAPL"]) == 1
        assert drawings["AAPL"][0]["id"] == "2"

    def test_store_clear_drawings(self):
        """Test clearing all drawings for a symbol."""
        from frontend.stores.chartsStore import useChartsStore

        useChartsStore.getState().clearDrawings("AAPL")

        drawings = useChartsStore.getState().drawings
        assert drawings["AAPL"] == []

    def test_store_error_handling(self):
        """Test store error handling."""
        from frontend.stores.chartsStore import useChartsStore

        useChartsStore.getState().setError("Test error")
        assert useChartsStore.getState().error == "Test error"

        useChartsStore.getState().clearError()
        assert useChartsStore.getState().error is None


class TestChartIntegrationPoints:
    """Integration point tests for chart drawing tools."""

    def test_api_client_charts_endpoints(self):
        """Test that charts API client has required methods."""
        from frontend.lib.api.charts import chartsApi

        assert hasattr(chartsApi, "getHistoricalData")
        assert hasattr(chartsApi, "listDrawings")
        assert hasattr(chartsApi, "getDrawing")
        assert hasattr(chartsApi, "createDrawing")
        assert hasattr(chartsApi, "updateDrawing")
        assert hasattr(chartsApi, "deleteDrawing")
        assert hasattr(chartsApi, "listLayouts")
        assert hasattr(chartsApi, "getIndicatorValues")

    def test_chart_types_exported(self):
        """Test that chart types are properly exported."""
        from frontend.lib.api.charts import (
            ChartDataPoint,
            ChartDrawing,
            TechnicalIndicatorValue,
            ChartDrawingManager,
        )

        assert ChartDataPoint is not None
        assert ChartDrawing is not None
        assert TechnicalIndicatorValue is not None
        assert ChartDrawingManager is not None
