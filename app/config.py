import os

class Config:
    CACHE_DIR = os.getenv('CACHE_DIR', 'cache')
    MOVIES_DIR = os.getenv('MOVIES_DIR', 'movies')
    DEFAULT_ZOOM = float(os.getenv('DEFAULT_ZOOM', 0.002))
    SCHEME = os.getenv('SCHEME', 'https')
    PUBLIC_PORT = os.getenv('PUBLIC_PORT', '80')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_LOG_LEVEL = os.getenv('CELERY_LOG_LEVEL', 'ERROR')

config = Config()
