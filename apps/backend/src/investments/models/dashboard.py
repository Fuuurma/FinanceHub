"""
Dashboard Models
Models for storing dashboard layouts and widget configurations.
"""

from django.db import models
from django.contrib.auth.models import User


class DashboardLayout(models.Model):
    """User dashboard layout model."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_layouts'
    )
    name = models.CharField(max_length=100, default='Default')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DashboardWidget(models.Model):
    """Dashboard widget configuration model."""
    
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('watchlist', 'Watchlist'),
        ('portfolio', 'Portfolio'),
        ('news', 'News'),
        ('screener', 'Screener'),
        ('metrics', 'Metrics'),
        ('positions', 'Positions'),
        ('performance', 'Performance'),
    ]
    
    WIDGET_SIZES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('full', 'Full'),
    ]
    
    layout = models.ForeignKey(
        DashboardLayout,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    widget_id = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    size = models.CharField(max_length=10, choices=WIDGET_SIZES, default='medium')
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.layout.name} - {self.widget_type} ({self.widget_id})"
