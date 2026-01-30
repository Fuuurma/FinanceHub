from typing import List, Optional
from datetime import datetime, timedelta
from ninja import Router, Query, Schema
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from charts.models.chart_drawing import (
    ChartDrawing,
    TechnicalIndicatorValue,
    ChartDrawingManager,
)
from assets.models.asset import Asset
from users.models.user import User

router = Router(tags=["Charts"])


class ChartDrawingOut(Schema):
    id: str
    user_id: str
    asset_id: str
    asset_symbol: str
    drawing_type: str
    timeframe: str
    start_x: float
    start_y: float
    end_x: Optional[float]
    end_y: Optional[float]
    color: str
    width: int
    line_style: str
    text: Optional[str]
    fibonacci_levels: List[float]
    visible: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TechnicalIndicatorValueOut(Schema):
    id: str
    asset_id: str
    asset_symbol: str
    indicator_type: str
    timeframe: str
    timestamp: datetime
    value: float
    parameters: dict
    signal: Optional[str]
    strength: Optional[int]

    class Config:
        from_attributes = True


class ChartDrawingManagerOut(Schema):
    id: str
    user_id: str
    name: str
    layout: dict
    indicators: List[str]
    default_timeframe: str
    chart_type: str
    show_volume: bool
    show_indicators: bool
    show_drawings: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChartDrawingCreateIn(Schema):
    asset_id: str
    drawing_type: str
    timeframe: str
    start_x: float
    start_y: float
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    color: str = "#ef4444"
    width: int = 2
    line_style: str = "solid"
    text: Optional[str] = None
    fibonacci_levels: Optional[List[float]] = None
    visible: bool = True


class ChartDrawingUpdateIn(Schema):
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    color: Optional[str] = None
    width: Optional[int] = None
    line_style: Optional[str] = None
    visible: Optional[bool] = None
    text: Optional[str] = None


@router.get("/drawings/{symbol}", response=List[ChartDrawingOut], auth=JWTAuth())
def list_drawings(
    request,
    symbol: str,
    timeframe: str = "1d",
):
    """Get all drawings for a symbol and timeframe"""
    user = request.auth
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    drawings = ChartDrawing.objects.filter(
        user=user, asset=asset, timeframe=timeframe, is_deleted=False
    ).order_by("-created_at")

    return list(drawings)


@router.post("/drawings", response=ChartDrawingOut, auth=JWTAuth())
def create_drawing(request, data: ChartDrawingCreateIn):
    """Create a new chart drawing"""
    user = request.auth
    asset = get_object_or_404(Asset, id=data.asset_id)

    drawing = ChartDrawing.objects.create(
        user=user,
        asset=asset,
        drawing_type=data.drawing_type,
        timeframe=data.timeframe,
        start_x=data.start_x,
        start_y=data.start_y,
        end_x=data.end_x,
        end_y=data.end_y,
        color=data.color,
        width=data.width,
        line_style=data.line_style,
        text=data.text,
        fibonacci_levels=data.fibonacci_levels,
        visible=data.visible,
    )

    return drawing


@router.put("/drawings/{drawing_id}", response=ChartDrawingOut, auth=JWTAuth())
def update_drawing(request, drawing_id: str, data: ChartDrawingUpdateIn):
    """Update an existing drawing"""
    user = request.auth
    drawing = get_object_or_404(
        ChartDrawing, id=drawing_id, user=user, is_deleted=False
    )

    if data.end_x is not None:
        drawing.end_x = data.end_x
    if data.end_y is not None:
        drawing.end_y = data.end_y
    if data.color is not None:
        drawing.color = data.color
    if data.width is not None:
        drawing.width = data.width
    if data.line_style is not None:
        drawing.line_style = data.line_style
    if data.visible is not None:
        drawing.visible = data.visible
    if data.text is not None:
        drawing.text = data.text

    drawing.save()
    return drawing


@router.delete("/drawings/{drawing_id}", auth=JWTAuth())
def delete_drawing(request, drawing_id: str):
    """Delete a drawing"""
    user = request.auth
    drawing = get_object_or_404(
        ChartDrawing, id=drawing_id, user=user, is_deleted=False
    )

    drawing.soft_delete()

    return {"success": True, "message": "Drawing deleted successfully"}


@router.get(
    "/indicators/{symbol}", response=List[TechnicalIndicatorValueOut], auth=JWTAuth()
)
def get_indicator_values(
    request,
    symbol: str,
    indicator_type: str,
    timeframe: str = "1d",
    limit: int = 200,
    offset: int = 0,
):
    """Get historical indicator values for an asset"""
    user = request.auth
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    values = TechnicalIndicatorValue.objects.filter(
        asset=asset, indicator_type=indicator_type, timeframe=timeframe
    ).order_by("-timestamp")[offset : offset + limit]

    return list(values)


@router.get("/layouts", response=List[ChartDrawingManagerOut], auth=JWTAuth())
def list_chart_layouts(request):
    """Get user's saved chart layouts"""
    user = request.auth
    layouts = ChartDrawingManager.objects.filter(user=user, is_deleted=False).order_by(
        "-created_at"
    )

    return list(layouts)


@router.post("/layouts", response=ChartDrawingManagerOut, auth=JWTAuth())
def create_chart_layout(request, data: Schema):
    """Create a new chart layout/workspace"""
    user = request.auth

    layout = ChartDrawingManager.objects.create(
        user=user,
        name=data.dict()["name"],
        layout=data.dict().get("layout", {}),
        indicators=data.dict().get("indicators", []),
        default_timeframe=data.dict().get("default_timeframe", "1d"),
        chart_type=data.dict().get("chart_type", "line"),
        show_volume=data.dict().get("show_volume", True),
        show_indicators=data.dict().get("show_indicators", True),
        show_drawings=data.dict().get("show_drawings", True),
        is_default=data.dict().get("is_default", False),
    )

    return layout


@router.get("/layouts/{layout_id}", response=ChartDrawingManagerOut, auth=JWTAuth())
def get_chart_layout(request, layout_id: str):
    """Get details of a specific chart layout"""
    user = request.auth
    layout = get_object_or_404(
        ChartDrawingManager, id=layout_id, user=user, is_deleted=False
    )
    return layout


@router.put("/layouts/{layout_id}", response=ChartDrawingManagerOut, auth=JWTAuth())
def update_chart_layout(request, layout_id: str, data: Schema):
    """Update a chart layout"""
    user = request.auth
    layout = get_object_or_404(
        ChartDrawingManager, id=layout_id, user=user, is_deleted=False
    )

    update_data = data.dict()
    if "name" in update_data:
        layout.name = update_data["name"]
    if "layout" in update_data:
        layout.layout = update_data["layout"]
    if "indicators" in update_data:
        layout.indicators = update_data["indicators"]
    if "default_timeframe" in update_data:
        layout.default_timeframe = update_data["default_timeframe"]
    if "chart_type" in update_data:
        layout.chart_type = update_data["chart_type"]
    if "show_volume" in update_data:
        layout.show_volume = update_data["show_volume"]
    if "show_indicators" in update_data:
        layout.show_indicators = update_data["show_indicators"]
    if "show_drawings" in update_data:
        layout.show_drawings = update_data["show_drawings"]

    layout.save()
    return layout


@router.delete("/layouts/{layout_id}", auth=JWTAuth())
def delete_chart_layout(request, layout_id: str):
    """Delete a chart layout"""
    user = request.auth
    layout = get_object_or_404(
        ChartDrawingManager, id=layout_id, user=user, is_deleted=False
    )

    layout.soft_delete()

    return {"success": True, "message": "Chart layout deleted successfully"}
