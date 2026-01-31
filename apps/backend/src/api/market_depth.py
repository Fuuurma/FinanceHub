from ninja import Router, Query
from typing import Optional
from investments.services.market_depth_service import MarketDepthService

router = Router(tags=["market_depth"])
depth_service = MarketDepthService()


@router.get("/market-depth/{asset_id}/order-book")
def get_order_book(request, asset_id: int, depth: int = 20):
    """Get current order book (Level 2 data)"""
    return depth_service.get_order_book(asset_id, depth=depth)


@router.get("/market-depth/{asset_id}/time-sales")
def get_time_and_sales(request, asset_id: int, limit: int = 100):
    """Get recent trades (tick-by-tick)"""
    return depth_service.get_time_and_sales(asset_id, limit=limit)


@router.get("/market-depth/{asset_id}/summary")
def get_depth_summary(request, asset_id: int):
    """Get market depth summary"""
    return depth_service.get_depth_summary(asset_id)


@router.get("/market-depth/{asset_id}/large-orders")
def get_large_orders(
    request,
    asset_id: int,
    min_value: Optional[float] = None,
    hours: int = 24,
):
    """Get large orders (whale activity)"""
    return depth_service.get_large_orders(asset_id, min_value=min_value, hours=hours)


@router.get("/market-depth/{asset_id}/order-flow-heatmap")
def get_order_flow_heatmap(request, asset_id: int, hours: int = 1):
    """Get order flow heatmap"""
    return depth_service.get_order_flow_heatmap(asset_id, hours=hours)
