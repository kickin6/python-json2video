# app/test_config.py
class TestConfig:
    TESTING = True
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CACHE_DIR = 'cache'
    MOVIES_DIR = 'movies'
    SCHEME = 'http'
    PUBLIC_PORT = '5003'
    SECRET_KEY = 'blahblah'
