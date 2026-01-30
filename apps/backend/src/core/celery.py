"""
Celery configuration for FinanceHub.
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("FinanceHub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(
    [
        "ai_advisor",
        "tasks",
    ]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_prefetch_multiplier=4,
    beat_schedule={
        # AI Template Refresh Tasks
        "refresh-stale-templates-hourly": {
            "task": "ai_advisor.tasks.template_refresh.refresh_stale_templates",
            "schedule": crontab(minute=0),  # Every hour
        },
        "generate-market-summary-morning": {
            "task": "ai_advisor.tasks.template_refresh.generate_market_summary_task",
            "schedule": crontab(hour=6, minute=0),  # 6 AM
        },
        "generate-market-summary-evening": {
            "task": "ai_advisor.tasks.template_refresh.generate_market_summary_task",
            "schedule": crontab(hour=18, minute=0),  # 6 PM
        },
        "generate-crypto-market-frequent": {
            "task": "ai_advisor.tasks.template_refresh.generate_crypto_market_task",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes (rate limited)
        },
        "generate-risk-commentary-morning": {
            "task": "ai_advisor.tasks.template_refresh.generate_risk_commentary_task",
            "schedule": crontab(hour=7, minute=0),  # 7 AM
        },
        "generate-risk-commentary-evening": {
            "task": "ai_advisor.tasks.template_refresh.generate_risk_commentary_task",
            "schedule": crontab(hour=19, minute=0),  # 7 PM
        },
        "generate-sentiment-summary-morning": {
            "task": "ai_advisor.tasks.template_refresh.generate_sentiment_summary_task",
            "schedule": crontab(hour=8, minute=0),  # 8 AM
        },
        "generate-sentiment-summary-evening": {
            "task": "ai_advisor.tasks.template_refresh.generate_sentiment_summary_task",
            "schedule": crontab(hour=20, minute=0),  # 8 PM
        },
        "generate-bond-market-daily": {
            "task": "ai_advisor.tasks.template_refresh.generate_bond_market_task",
            "schedule": crontab(hour=5, minute=0),  # 5 AM
        },
        # User Reports Tasks
        "generate-user-reports-nightly": {
            "task": "ai_advisor.tasks.user_reports.generate_all_user_reports",
            "schedule": crontab(hour=2, minute=0),  # 2 AM
        },
        # Maintenance Tasks
        "cleanup-template-logs-weekly": {
            "task": "ai_advisor.tasks.template_refresh.cleanup_old_template_logs",
            "schedule": crontab(hour=4, minute=0, day_of_week=0),  # Sunday 4 AM
        },
        # Legacy tasks (kept for compatibility)
        "generate-ai-templates-morning": {
            "task": "tasks.ai_template_generation.generate_all_templates",
            "schedule": crontab(hour=0, minute=0),
        },
        "generate-ai-templates-afternoon": {
            "task": "tasks.ai_template_generation.generate_all_templates",
            "schedule": crontab(hour=12, minute=0),
        },
        "generate-user-reports": {
            "task": "tasks.ai_user_reports.generate_user_portfolio_reports",
            "schedule": crontab(hour=2, minute=0),
        },
        "cleanup-expired-alerts": {
            "task": "tasks.alerts.cleanup_expired_alerts",
            "schedule": crontab(hour=3, minute=0),
        },
        "sync-market-data": {
            "task": "tasks.market_data.sync_market_data",
            "schedule": 60.0,
        },
    },
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
