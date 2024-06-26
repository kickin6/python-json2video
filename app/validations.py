import re
import os

from functools import wraps
from flask import request, jsonify
from jsonschema import validate, ValidationError

from .config import Config

input_schema = {
    "type": "object",
    "properties": {
        "record_id": {"type": "string"},
        "input_url": {"type": "string"},
        "zoom": {"type": "number"},
        "output_width": {"type": "integer"},
        "output_height": {"type": "integer"}
    },
    "required": ["record_id", "input_url", "output_width", "output_height"]
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
    directory = os.path.join(Config.MOVIES_DIR, api_key)
    return os.path.isdir(directory)

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
                return jsonify({'error': 'Directory does not exist for the provided API key'}), 400

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
    return re.match(regex, url) is not None

def is_valid_zoom_level(zoom):
    if zoom == "":
        return Config.DEFAULT_ZOOM
    try:
        zoom = float(zoom)
        return 0.0 <= zoom <= 1.0
    except ValueError:
        return False

def is_valid_dimension(value):
    try:
        value = int(value)
        return value > 0
    except ValueError:
        return False
