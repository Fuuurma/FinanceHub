"""
Charts API
Provides endpoints for chart data, drawings, and layouts
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from ninja import Router, Schema
from pydantic import BaseModel, Field
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from utils.helpers.logger.logger import get_logger
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from core.exceptions import NotFoundException, ValidationException

logger = get_logger(__name__)
router = Router(tags=["Charts"])


class ChartDataPoint(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class ChartDrawing(BaseModel):
    id: str
    user: str
    symbol: str
    timeframe: str
    drawing_type: str
    coordinates: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    color: str
    is_visible: bool = True
    created_at: str
    updated_at: str


class DrawingCreateRequest(BaseModel):
    symbol: str
    timeframe: str
    drawing_type: str
    coordinates: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    color: str = "#3b82f6"


class DrawingUpdateRequest(BaseModel):
    coordinates: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    color: Optional[str] = None
    is_visible: Optional[bool] = None


class ChartLayout(BaseModel):
    id: str
    user: str
    name: str
    description: Optional[str] = None
    is_default: bool = False
    layout_config: Dict[str, Any] = {}
    created_at: str
    updated_at: str


class LayoutCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    layout_config: Dict[str, Any] = {}


class TechnicalIndicatorValue(BaseModel):
    id: str
    symbol: str
    timeframe: str
    indicator_type: str
    timestamp: str
    value: float
    signal: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@router.get("/historical/{symbol}", response=List[ChartDataPoint])
async def get_historical_data(
    request, symbol: str, timeframe: str = "1h", limit: int = 100
):
    """
    Get historical price data for charting.
    """
    from data.data_providers.binance.scraper import BinanceScraper
    from assets.models.asset import Asset

    try:
        asset = await Asset.objects.filter(symbol=symbol.upper()).afirst()

        if not asset:
            return []

        scraper = BinanceScraper()

        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w",
        }

        interval = interval_map.get(timeframe, "1h")

        data = await scraper.get_price_data(
            symbol=f"{symbol.upper()}USDT", interval=interval, limit=min(limit, 1000)
        )

        return [
            ChartDataPoint(
                timestamp=d["timestamp"],
                open=float(d["open"]),
                high=float(d["high"]),
                low=float(d["low"]),
                close=float(d["close"]),
                volume=float(d["volume"]),
            )
            for d in data
        ]

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return []


@router.get("/drawings/{symbol}", response=List[ChartDrawing])
async def list_drawings(request, symbol: str, timeframe: Optional[str] = None):
    """
    List all drawings for a symbol.
    """
    from investments.models.chart_drawing import ChartDrawingModel

    if not request.user.is_authenticated:
        return []

    queryset = ChartDrawingModel.objects.filter(
        user=request.user, symbol=symbol.upper()
    )

    if timeframe:
        queryset = queryset.filter(timeframe=timeframe)

    drawings = await queryset.order_by("-created_at")[:100]

    return [
        ChartDrawing(
            id=str(d.id),
            user=d.user.username,
            symbol=d.symbol,
            timeframe=d.timeframe,
            drawing_type=d.drawing_type,
            coordinates=d.coordinates,
            parameters=d.parameters,
            color=d.color,
            is_visible=d.is_visible,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat(),
        )
        for d in drawings
    ]


@router.get("/drawings/by-id/{drawing_id}", response=ChartDrawing)
async def get_drawing(request, drawing_id: str):
    """
    Get a specific drawing by ID.
    """
    from investments.models.chart_drawing import ChartDrawingModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        drawing = await ChartDrawingModel.objects.aget(id=drawing_id, user=request.user)

        return ChartDrawing(
            id=str(drawing.id),
            user=drawing.user.username,
            symbol=drawing.symbol,
            timeframe=drawing.timeframe,
            drawing_type=drawing.drawing_type,
            coordinates=drawing.coordinates,
            parameters=drawing.parameters,
            color=drawing.color,
            is_visible=drawing.is_visible,
            created_at=drawing.created_at.isoformat(),
            updated_at=drawing.updated_at.isoformat(),
        )
    except ChartDrawingModel.DoesNotExist:
        return {"error": "Drawing not found"}, 404


@router.post("/drawings/{symbol}", response=ChartDrawing)
async def create_drawing(request, symbol: str, data: DrawingCreateRequest):
    """
    Create a new drawing.
    """
    from investments.models.chart_drawing import ChartDrawingModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    valid_types = [
        "horizontal_line",
        "vertical_line",
        "trend_line",
        "fibonacci",
        "rectangle",
        "text",
        "support",
        "resistance",
    ]

    if data.drawing_type not in valid_types:
        return {"error": f"Invalid drawing type. Must be one of: {valid_types}"}, 400

    drawing = await ChartDrawingModel.objects.acreate(
        user=request.user,
        symbol=symbol.upper(),
        timeframe=data.timeframe,
        drawing_type=data.drawing_type,
        coordinates=data.coordinates,
        parameters=data.parameters,
        color=data.color,
        is_visible=True,
    )

    return ChartDrawing(
        id=str(drawing.id),
        user=drawing.user.username,
        symbol=drawing.symbol,
        timeframe=drawing.timeframe,
        drawing_type=drawing.drawing_type,
        coordinates=drawing.coordinates,
        parameters=drawing.parameters,
        color=drawing.color,
        is_visible=drawing.is_visible,
        created_at=drawing.created_at.isoformat(),
        updated_at=drawing.updated_at.isoformat(),
    )


@router.put("/drawings/by-id/{drawing_id}", response=ChartDrawing)
async def update_drawing(request, drawing_id: str, data: DrawingUpdateRequest):
    """
    Update a drawing.
    """
    from investments.models.chart_drawing import ChartDrawingModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        drawing = await ChartDrawingModel.objects.aget(id=drawing_id, user=request.user)

        if data.coordinates is not None:
            drawing.coordinates = data.coordinates
        if data.parameters is not None:
            drawing.parameters = data.parameters
        if data.color is not None:
            drawing.color = data.color
        if data.is_visible is not None:
            drawing.is_visible = data.is_visible

        drawing.save()

        return ChartDrawing(
            id=str(drawing.id),
            user=drawing.user.username,
            symbol=drawing.symbol,
            timeframe=drawing.timeframe,
            drawing_type=drawing.drawing_type,
            coordinates=drawing.coordinates,
            parameters=drawing.parameters,
            color=drawing.color,
            is_visible=drawing.is_visible,
            created_at=drawing.created_at.isoformat(),
            updated_at=drawing.updated_at.isoformat(),
        )
    except ChartDrawingModel.DoesNotExist:
        return {"error": "Drawing not found"}, 404


@router.delete("/drawings/by-id/{drawing_id}")
async def delete_drawing(request, drawing_id: str):
    """
    Delete a drawing.
    """
    from investments.models.chart_drawing import ChartDrawingModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        drawing = await ChartDrawingModel.objects.aget(id=drawing_id, user=request.user)
        drawing.delete()
        return {"success": True}
    except ChartDrawingModel.DoesNotExist:
        return {"error": "Drawing not found"}, 404


@router.get("/layouts", response=List[ChartLayout])
async def list_layouts(request):
    """
    List all chart layouts.
    """
    from investments.models.chart_layout import ChartLayoutModel

    if not request.user.is_authenticated:
        return []

    layouts = await ChartLayoutModel.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:50]

    return [
        ChartLayout(
            id=str(l.id),
            user=l.user.username,
            name=l.name,
            description=l.description,
            is_default=l.is_default,
            layout_config=l.layout_config or {},
            created_at=l.created_at.isoformat(),
            updated_at=l.updated_at.isoformat(),
        )
        for l in layouts
    ]


@router.get("/layouts/{layout_id}", response=ChartLayout)
async def get_layout(request, layout_id: str):
    """
    Get a specific layout.
    """
    from investments.models.chart_layout import ChartLayoutModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        layout = await ChartLayoutModel.objects.aget(id=layout_id, user=request.user)

        return ChartLayout(
            id=str(layout.id),
            user=layout.user.username,
            name=layout.name,
            description=layout.description,
            is_default=layout.is_default,
            layout_config=layout.layout_config or {},
            created_at=layout.created_at.isoformat(),
            updated_at=layout.updated_at.isoformat(),
        )
    except ChartLayoutModel.DoesNotExist:
        return {"error": "Layout not found"}, 404


@router.post("/layouts", response=ChartLayout)
async def create_layout(request, data: LayoutCreateRequest):
    """
    Create a new chart layout.
    """
    from investments.models.chart_layout import ChartLayoutModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    layout = await ChartLayoutModel.objects.acreate(
        user=request.user,
        name=data.name,
        description=data.description,
        is_default=data.is_default,
        layout_config=data.layout_config,
    )

    return ChartLayout(
        id=str(layout.id),
        user=layout.user.username,
        name=layout.name,
        description=layout.description,
        is_default=layout.is_default,
        layout_config=layout.layout_config or {},
        created_at=layout.created_at.isoformat(),
        updated_at=layout.updated_at.isoformat(),
    )


@router.put("/layouts/{layout_id}", response=ChartLayout)
async def update_layout(request, layout_id: str, data: LayoutCreateRequest):
    """
    Update a layout.
    """
    from investments.models.chart_layout import ChartLayoutModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        layout = await ChartLayoutModel.objects.aget(id=layout_id, user=request.user)

        layout.name = data.name
        if data.description is not None:
            layout.description = data.description
        layout.is_default = data.is_default
        layout.layout_config = data.layout_config

        layout.save()

        return ChartLayout(
            id=str(layout.id),
            user=layout.user.username,
            name=layout.name,
            description=layout.description,
            is_default=layout.is_default,
            layout_config=layout.layout_config or {},
            created_at=layout.created_at.isoformat(),
            updated_at=layout.updated_at.isoformat(),
        )
    except ChartLayoutModel.DoesNotExist:
        return {"error": "Layout not found"}, 404


@router.delete("/layouts/{layout_id}")
async def delete_layout(request, layout_id: str):
    """
    Delete a layout.
    """
    from investments.models.chart_layout import ChartLayoutModel

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        layout = await ChartLayoutModel.objects.aget(id=layout_id, user=request.user)
        layout.delete()
        return {"success": True}
    except ChartLayoutModel.DoesNotExist:
        return {"error": "Layout not found"}, 404


@router.get(
    "/indicators/{symbol}/{indicator_type}", response=List[TechnicalIndicatorValue]
)
async def get_indicator_values(
    request,
    symbol: str,
    indicator_type: str,
    timeframe: Optional[str] = None,
    limit: int = 100,
):
    """
    Get technical indicator values for a symbol.
    """
    from investments.models.technical_indicators import TechnicalIndicator

    queryset = TechnicalIndicator.objects.filter(
        symbol=symbol.upper(), indicator_type=indicator_type.lower()
    )

    if timeframe:
        queryset = queryset.filter(timeframe=timeframe)

    indicators = await queryset.order_by("-timestamp")[:limit]

    return [
        TechnicalIndicatorValue(
            id=str(ind.id),
            symbol=ind.symbol,
            timeframe=ind.timeframe,
            indicator_type=ind.indicator_type,
            timestamp=ind.timestamp.isoformat(),
            value=float(ind.value),
            signal=ind.signal,
            additional_data=ind.additional_data,
        )
        for ind in indicators
    ]


class ScreenshotRequest(BaseModel):
    image_data: str
    symbol: str
    timeframe: str
    drawings: Optional[List[Dict[str, Any]]] = None


class ShareResponse(BaseModel):
    share_id: str
    share_url: str
    expires_at: str


@router.post("/screenshots", response=Dict[str, str])
async def save_screenshot(request, data: ScreenshotRequest):
    """
    Save a chart screenshot for sharing.
    Returns a shareable ID and URL.
    """
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    import uuid
    import base64
    from io import BytesIO
    from datetime import datetime, timedelta

    share_id = uuid.uuid4().hex[:12]
    expires_at = datetime.now() + timedelta(days=7)

    header, encoded = data.image_data.split(",", 1)
    image_data = base64.b64decode(encoded)

    from investments.models.chart_drawing import ChartScreenshot

    screenshot = await ChartScreenshot.objects.acreate(
        user=request.user,
        symbol=data.symbol.upper(),
        timeframe=data.timeframe,
        share_id=share_id,
        image_data=image_data,
        drawings=data.drawings or [],
        expires_at=expires_at,
    )

    return {
        "share_id": share_id,
        "share_url": f"/shared/chart/{share_id}",
        "expires_at": expires_at.isoformat(),
    }


@router.get("/share/{share_id}", response=Dict)
async def get_shared_chart(request, share_id: str):
    """
    Get a shared chart by ID.
    """
    from investments.models.chart_drawing import ChartScreenshot

    try:
        screenshot = await ChartScreenshot.objects.select_related("user").aget(
            share_id=share_id
        )

        if screenshot.expires_at and screenshot.expires_at < timezone.now():
            return {"error": "Shared chart has expired"}, 410

        return {
            "id": str(screenshot.id),
            "symbol": screenshot.symbol,
            "timeframe": screenshot.timeframe,
            "image_data": f"data:image/png;base64,{screenshot.image_data.decode('latin-1')}"
            if screenshot.image_data
            else None,
            "drawings": screenshot.drawings,
            "created_at": screenshot.created_at.isoformat(),
            "expires_at": screenshot.expires_at.isoformat()
            if screenshot.expires_at
            else None,
            "shared_by": screenshot.user.username if screenshot.user else None,
        }
    except ChartScreenshot.DoesNotExist:
        return {"error": "Shared chart not found"}, 404


@router.delete("/share/{share_id}")
async def delete_shared_chart(request, share_id: str):
    """
    Delete a shared chart.
    """
    from investments.models.chart_drawing import ChartScreenshot

    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        screenshot = await ChartScreenshot.objects.aget(
            share_id=share_id, user=request.user
        )
        screenshot.delete()
        return {"success": True}
    except ChartScreenshot.DoesNotExist:
        return {"error": "Shared chart not found"}, 404
