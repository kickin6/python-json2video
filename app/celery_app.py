from celery import Celery

def make_celery(app_name=__name__):
    celery = Celery(app_name)
    celery.config_from_object('app.celery_config')
    return celery

celery_app = make_celery()

# Import tasks to ensure they are registered with Celery
import app.tasks
