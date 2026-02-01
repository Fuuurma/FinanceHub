"""
Dashboard API
Provides endpoints for saving and loading dashboard layouts.
"""

from ninja import Router
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from django.db import transaction
from investments.models import DashboardLayout as DashboardLayoutModel

router = Router(tags=["Dashboard"])


class WidgetData(BaseModel):
    id: str
    type: str
    title: str
    size: str
    position: Dict[str, int]
    config: Dict[str, Any]
    visible: bool = True


class SaveLayoutRequest(BaseModel):
    dashboard: str = 'Default'
    widgets: List[WidgetData]


class CreateDashboardRequest(BaseModel):
    name: str


@router.get("/dashboard/widgets/")
def get_dashboard_widgets(request):
    """Get widgets for the current user's dashboard."""
    dashboard_name = request.GET.get('dashboard', 'Default')
    
    try:
        layout = DashboardLayoutModel.objects.filter(
            user=request.user,
            name=dashboard_name
        ).prefetch_related('widgets').first()
        
        if layout:
            widgets = []
            for widget in layout.widgets.all():
                widgets.append({
                    'id': widget.widget_id,
                    'type': widget.widget_type,
                    'title': widget.title,
                    'size': widget.size,
                    'position': {'x': widget.position_x, 'y': widget.position_y},
                    'config': widget.config or {},
                    'visible': widget.visible,
                })
            return {'widgets': widgets}
        else:
            return {'widgets': []}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {'error': str(e)}, 500


@router.post("/dashboard/save/")
def save_dashboard_layout(request, data: SaveLayoutRequest):
    """Save dashboard layout."""
    try:
        with transaction.atomic():
            layout, created = DashboardLayoutModel.objects.get_or_create(
                user=request.user,
                name=data.dashboard,
                defaults={'user': request.user, 'name': data.dashboard}
            )
            
            layout.widgets.all().delete()
            
            for widget_data in data.widgets:
                layout.widgets.create(
                    widget_id=widget_data.id,
                    widget_type=widget_data.type,
                    title=widget_data.title,
                    size=widget_data.size,
                    position_x=widget_data.position.get('x', 0),
                    position_y=widget_data.position.get('y', 0),
                    config=widget_data.config,
                    visible=widget_data.visible,
                )
            
            return {'status': 'saved', 'dashboard': data.dashboard}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {'error': str(e)}, 500


@router.post("/dashboard/create/")
def create_dashboard(request, data: CreateDashboardRequest):
    """Create a new dashboard."""
    try:
        if DashboardLayoutModel.objects.filter(
            user=request.user,
            name=data.name
        ).exists():
            return {'error': 'Dashboard already exists'}, 400
        
        DashboardLayoutModel.objects.create(
            user=request.user,
            name=data.name
        )
        
        return {'status': 'created', 'name': data.name}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {'error': str(e)}, 500


@router.delete("/dashboard/{dashboard_name}/")
def delete_dashboard(request, dashboard_name: str):
    """Delete a dashboard."""
    try:
        deleted, _ = DashboardLayoutModel.objects.filter(
            user=request.user,
            name=dashboard_name
        ).delete()
        
        if deleted == 0:
            return {'error': 'Dashboard not found'}, 404
        
        return {'status': 'deleted', 'name': dashboard_name}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {'error': str(e)}, 500


@router.get("/dashboard/list/")
def list_dashboards(request):
    """List all dashboards for the current user."""
    try:
        layouts = DashboardLayoutModel.objects.filter(
            user=request.user
        ).values_list('name', flat=True)
        
        return {'dashboards': list(layouts)}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {'error': str(e)}, 500
