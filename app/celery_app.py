from celery import Celery
from .config import DATABASE_URL
import os

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery instance
celery_app = Celery(
    "task_manager",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.tasks.send_email_notification": {"queue": "notifications"},
        "app.tasks.process_bulk_tasks": {"queue": "bulk_operations"},
        "app.tasks.cleanup_old_tasks": {"queue": "maintenance"},
    },
    beat_schedule={
        'cleanup-old-tasks': {
            'task': 'app.tasks.cleanup_old_tasks',
            'schedule': 86400.0,  # Run daily (24 hours)
        },
    }
) 