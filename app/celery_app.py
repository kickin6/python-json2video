from .celery_config import celery_app

# Import tasks to ensure they are registered with Celery
import app.tasks
