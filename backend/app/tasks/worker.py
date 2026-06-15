from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.extraction",
        "app.tasks.duplicate"
    ]
)

celery_app.conf.task_routes = {
    "app.tasks.extraction.*": {"queue": "extraction"},
    "app.tasks.duplicate.*": {"queue": "duplicate"},
}