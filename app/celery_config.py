from celery import Celery
from app import create_app
from .config import Config

def create_celery_app(flask_app=None):
    flask_app = flask_app or create_app()
    celery = Celery(flask_app.import_name, broker=flask_app.config['CELERY_BROKER_URL'])
    celery.conf.update(flask_app.config)
    return celery

celery_app = create_celery_app()
