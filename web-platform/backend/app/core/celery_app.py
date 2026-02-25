from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "eval_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.services.eval_runner"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4小时超时
    worker_prefetch_multiplier=1,  # 一次只取一个任务
)
