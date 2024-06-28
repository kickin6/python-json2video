import re
import os
from urllib.parse import urlparse

from functools import wraps
from flask import request, jsonify
from jsonschema import validate, ValidationError

from .config import Config

input_schema = {
    "type": "object",
    "properties": {
        "record_id": {"type": "string"},
        "input_url": {"type": "string"},
        "webhook_url": {"type": "string"},
        "framerate": {"type": "number"},
        "duration": {"type": "number"},
        "cache": {"type": "boolean"},
        "zoom": {"type": "number"},
        "output_width": {"type": "integer"},
        "output_height": {"type": "integer"}
    },
    "required": ["record_id", "input_url", "webhook_url", "framerate", "duration", "cache", "output_width", "output_height"]
}

def validate_json(data):
    """Validate JSON data against the schema."""
    try:
        validate(instance=data, schema=input_schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def directory_exists(api_key):
    """Check if a directory exists for the given API key."""
    fullpath = os.path.normpath(os.path.join(Config.MOVIES_DIR, api_key))
    if not fullpath.startswith(Config.MOVIES_DIR):
        raise Exception("not allowed")
    return os.path.isdir(fullpath)

def validate_api_key(pass_api_key=False):
    """Decorator to validate the API key."""
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('x-api-key')

            if not api_key:
                return jsonify({'error': 'Missing x-api-key header'}), 400

            if not is_valid_api_key(api_key):
                return jsonify({'error': 'Invalid API key'}), 400

            if not directory_exists(api_key):
                return jsonify({'error': 'Directory does not exist'}), 400

            if pass_api_key:
                return func(*args, api_key=api_key, **kwargs)
            else:
                return func(*args, **kwargs)
        return decorated_function
    return decorator

def is_valid_record_id(record_id):
    return re.match(r'^[0-9a-zA-Z]+$', record_id) is not None

def is_valid_api_key(api_key):
    return re.match(r'^[a-zA-Z0-9]+$', api_key) is not None

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    # Basic regex validation
    if not re.match(regex, url):
        return False
    
    # Parse the URL to check hostname and scheme
    parsed_url = urlparse(url)
    
    # Ensure the URL uses http or https
    if parsed_url.scheme not in ['http', 'https']:
        return False
    
    # Ensure the hostname is in the allowed IPs or domains
    allowed_ips = [ip for sublist in Config.ALLOWED_IPS.values() for ip in sublist]
    if parsed_url.hostname not in allowed_ips and parsed_url.hostname not in Config.ALLOWED_DOMAINS:
        return False
    
    return True

def is_valid_zoom_level(zoom):
    if zoom == "":
        return Config.DEFAULT_ZOOM
    try:
        zoom = int(zoom)
        return zoom >= -100 and zoom <= 100
    except ValueError:
        return False

def is_valid_crop(crop):
    if isinstance(crop, str):
        if crop.lower() == 'true':
            return True
        elif crop.lower() == 'false':
            return True
    return isinstance(crop, bool)

def is_valid_dimension(value):
    try:
        value = int(value)
        return value > 0
    except ValueError:
        return False

def is_valid_framerate(value):
    try:
        value = int(value)
        return value > 0
    except ValueError:
        return False

def is_valid_duration(value):
    try:
        value = int(value)
        return value <= 60
    except ValueError:
        return False

def is_valid_cache(cache):
    if isinstance(cache, str):
        if cache.lower() == 'true':
            return True
        elif cache.lower() == 'false':
            return True
    return isinstance(cache, bool)