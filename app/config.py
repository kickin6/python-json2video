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
    ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', 'example.com,trusted.com').split(',')
    ALLOWED_IPS = {
        'MAKE_US1': [
            '54.209.79.175',
            '54.80.47.193',
            '54.161.178.114'
        ],
        'MAKE_EU2': [
            '34.254.1.9',
            '52.31.156.93',
            '52.50.32.186'
        ],
        'MAKE_EU1': [
            '54.75.157.176',
            '54.78.149.203',
            '52.18.144.195'
        ]
    }

config = Config()
