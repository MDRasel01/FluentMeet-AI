from app.celery_app import celery_app
import time

@celery_app.task(name="test_worker_ping")
def test_worker_ping(message: str) -> dict:
    return {
        "status": "success",
        "echo": message,
        "processed_at": time.time(),
    }

