import os

class Config:
    CACHE_DIR = 'cache'
    MOVIES_DIR = 'movies'
    DEFAULT_ZOOM = 0.002
    SCHEME = os.getenv('SCHEME', 'https')
    PUBLIC_PORT = os.getenv('PUBLIC_PORT')

config = Config()
