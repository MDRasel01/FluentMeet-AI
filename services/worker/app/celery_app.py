import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "fluentmeet_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.test_task",
        "app.tasks.audio_task",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 min max for heavy processing
    task_soft_time_limit=1500,
    worker_prefetch_multiplier=1,
)

if __name__ == "__main__":
    celery_app.start()

