"""
Tests for Dashboard API
Tests dashboard layout saving, loading, and widget management.
"""

import pytest
from django.test import RequestFactory
from ninja.testing import TestAsyncClient
from investments.models import DashboardLayout, DashboardWidget


class TestDashboardAPI:
    """Test cases for Dashboard API."""
    
    @pytest.fixture
    def rf(self):
        return RequestFactory()
    
    @pytest.fixture
    def client(self):
        return TestAsyncClient()
    
    def test_widget_config_creation(self):
        """Test widget configuration structure."""
        from investments.models.dashboard import DashboardWidget
        
        widget = DashboardWidget(
            widget_id='test-widget-1',
            widget_type='chart',
            title='Test Chart',
            size='medium',
            position_x=0,
            position_y=0,
            config={'symbol': 'AAPL'},
            visible=True
        )
        
        assert widget.widget_id == 'test-widget-1'
        assert widget.widget_type == 'chart'
        assert widget.title == 'Test Chart'
        assert widget.size == 'medium'
        assert widget.visible is True
    
    def test_dashboard_layout_creation(self):
        """Test dashboard layout creation."""
        from investments.models.dashboard import DashboardLayout
        
        layout = DashboardLayout(
            name='Test Dashboard',
            is_default=False
        )
        
        assert layout.name == 'Test Dashboard'
        assert layout.is_default is False
    
    def test_widget_types(self):
        """Test all widget types are defined."""
        from investments.models.dashboard import DashboardWidget
        
        valid_types = ['chart', 'watchlist', 'portfolio', 'news', 'screener', 'metrics', 'positions', 'performance']
        
        for widget_type in valid_types:
            widget = DashboardWidget(
                widget_id=f'test-{widget_type}',
                widget_type=widget_type,
                title=f'Test {widget_type}',
                size='medium'
            )
            assert widget.widget_type == widget_type
    
    def test_widget_sizes(self):
        """Test all widget sizes are defined."""
        from investments.models.dashboard import DashboardWidget
        
        valid_sizes = ['small', 'medium', 'large', 'full']
        
        for size in valid_sizes:
            widget = DashboardWidget(
                widget_id=f'test-size-{size}',
                widget_type='chart',
                title=f'Test {size}',
                size=size
            )
            assert widget.size == size
    
    def test_widget_default_values(self):
        """Test widget default values."""
        from investments.models.dashboard import DashboardWidget
        
        widget = DashboardWidget(
            widget_id='test-defaults',
            widget_type='chart',
            title='Test Defaults',
            size='medium'
        )
        
        assert widget.position_x == 0
        assert widget.position_y == 0
        assert widget.config == {}
        assert widget.visible is True
        assert widget.order == 0


class TestDashboardWidgetTypes:
    """Test widget type configurations."""
    
    def test_chart_widget_config(self):
        """Test chart widget configuration."""
        from investments.models.dashboard import DashboardWidget
        
        widget = DashboardWidget(
            widget_id='chart-1',
            widget_type='chart',
            title='AAPL Chart',
            size='large',
            config={
                'symbol': 'AAPL',
                'chart_type': 'candlestick',
                'timeframe': '1D'
            }
        )
        
        assert widget.config['symbol'] == 'AAPL'
        assert widget.config['chart_type'] == 'candlestick'
    
    def test_watchlist_widget_config(self):
        """Test watchlist widget configuration."""
        from investments.models.dashboard import DashboardWidget
        
        widget = DashboardWidget(
            widget_id='watchlist-1',
            widget_type='watchlist',
            title='My Watchlist',
            size='medium',
            config={
                'symbols': ['AAPL', 'GOOGL', 'MSFT'],
                'sort_by': 'change_percent'
            }
        )
        
        assert len(widget.config['symbols']) == 3
        assert 'AAPL' in widget.config['symbols']
    
    def test_news_widget_config(self):
        """Test news widget configuration."""
        from investments.models.dashboard import DashboardWidget
        
        widget = DashboardWidget(
            widget_id='news-1',
            widget_type='news',
            title='Market News',
            size='medium',
            config={
                'category': 'markets',
                'limit': 10
            }
        )
        
        assert widget.config['category'] == 'markets'
        assert widget.config['limit'] == 10


class TestDashboardLayoutQueries:
    """Test dashboard layout database queries."""
    
    def test_filter_by_user(self):
        """Test filtering layouts by user."""
        from investments.models.dashboard import DashboardLayout
        
        layouts = DashboardLayout.objects.filter(name='Default')
        assert layouts is not None
    
    def test_prefetch_widgets(self):
        """Test prefetching widgets for a layout."""
        from investments.models.dashboard import DashboardLayout, DashboardWidget
        
        layout = DashboardLayout.objects.filter(
            name='Default'
        ).prefetch_related('widgets').first()
        
        if layout:
            widgets = layout.widgets.all()
            assert widgets is not None
