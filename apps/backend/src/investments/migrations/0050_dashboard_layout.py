"""
Migration: Create Dashboard Layout Models
Generated: 2026-01-31
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('investments', '0049_remove_portfolioriskmetrics_portfolio_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default', max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_layouts', to='auth.user')),
            ],
            options={
                'unique_together': {('user', 'name')},
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_id', models.CharField(max_length=100)),
                ('widget_type', models.CharField(choices=[('chart', 'Chart'), ('watchlist', 'Watchlist'), ('portfolio', 'Portfolio'), ('news', 'News'), ('screener', 'Screener'), ('metrics', 'Metrics'), ('positions', 'Positions'), ('performance', 'Performance')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('full', 'Full')], default='medium', max_length=10)),
                ('position_x', models.IntegerField(default=0)),
                ('position_y', models.IntegerField(default=0)),
                ('config', models.JSONField(blank=True, default=dict)),
                ('visible', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('layout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='investments.dashboardlayout')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
