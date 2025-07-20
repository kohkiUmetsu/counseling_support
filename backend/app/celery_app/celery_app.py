from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "counseling_support",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.celery_app.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)