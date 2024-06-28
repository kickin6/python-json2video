from celery import Celery

def make_celery(app=None):
    app = app or create_app()
    celery = Celery(app.import_name, backend='redis://redis:6379/0', broker='redis://redis:6379/0')
    celery.conf.update(app.config)
    return celery
