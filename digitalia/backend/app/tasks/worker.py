import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("digitalia_tasks", broker=redis_url, backend=redis_url)

# Auto-discover or register standard tasks
@app.task(name="dummy_task")
def dummy_task():
    return "Celery is running perfectly!"
