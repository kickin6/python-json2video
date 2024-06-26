import os
import json
import subprocess
import requests
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from .validations import validate_json, validate_api_key, is_valid_record_id, is_valid_url, is_valid_framerate, is_valid_duration, is_valid_cache, is_valid_zoom_level, is_valid_crop, is_valid_dimension
from .utils import generate_random_filename
from .config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/validate', methods=['GET'])
@validate_api_key(pass_api_key=False)
def validate():
    """Endpoint to validate the API key."""
    return jsonify({'message': 'API key is valid'}), 200

@main_bp.route('/create-video', methods=['POST'])
@validate_api_key(pass_api_key=True)
def create_video(api_key):
    from app.tasks import create_video_task  # Import here to avoid circular import
    data = request.json

    is_valid, error = validate_json(data)
    if not is_valid:
        return jsonify({'error': f'Invalid input data'}), 400

    record_id = data['record_id']
    input_url = data['input_url']
    framerate = data['framerate']
    duration = data['duration']
    cache = data['cache']
    zoom = data['zoom']
    crop = data['crop']
    output_width = data['output_width']
    output_height = data['output_height']
    webhook_url = data.get('webhook_url')

    if not is_valid_record_id(record_id):
        return jsonify({'error': 'Invalid record ID'}), 400
    if not is_valid_url(input_url):
        return jsonify({'error': 'Invalid input URL'}), 400
    if webhook_url and not is_valid_url(webhook_url):
        return jsonify({'error': 'Invalid webhook URL'}), 400
    if not is_valid_framerate(framerate):
        return jsonify({'error': 'Invalid framerate'}), 400
    if not is_valid_duration(duration):
        return jsonify({'error': 'Invalid duration level'}), 400
    if not is_valid_cache(cache):
        return jsonify({'error': 'Invalid cache value'}), 400
    if not is_valid_zoom_level(zoom):
        return jsonify({'error': 'Invalid zoom level'}), 400
    if not is_valid_crop(crop):
        return jsonify({'error': 'Invalid crop value'}), 400
    if not is_valid_dimension(output_width):
        return jsonify({'error': 'Invalid output width'}), 400
    if not is_valid_dimension(output_height):
        return jsonify({'error': 'Invalid output height'}), 400


    try:
        # Validate and sanitize URL again before making a request
        if not is_valid_url(input_url):
            return jsonify({'error': 'Invalid input URL'}), 400

        response = requests.get(input_url, stream=True, timeout=10)
        response.raise_for_status()

        # Validate response content type and length
        if 'content-length' in response.headers and int(response.headers['content-length']) > 10 * 1024 * 1024:
            return jsonify({'error': 'File is too large'}), 400
        if 'content-type' in response.headers and 'application/json' in response.headers['content-type']:
            return jsonify({'error': 'Invalid file type'}), 400

        # Process the response as required
        cached_input_file = generate_random_filename()
        with open(cached_input_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        ffprobe_command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            cached_input_file
        ]
        process = subprocess.Popen(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            current_app.logger.error(f'ffprobe error: {stderr.decode("utf-8")}')
            raise Exception(f'ffprobe failed with error: {stderr.decode("utf-8")}')
        
        dimensions = json.loads(stdout.decode('utf-8'))
        data['input_width'] = dimensions['streams'][0]['width']
        data['input_height'] = dimensions['streams'][0]['height']
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to download input file'}), 400

    # Generate a random filename for the output file
    movies_folder = Config.MOVIES_DIR
    filename = generate_random_filename()
    output_file = os.path.join(movies_folder, filename)
    
    data['request_host'] = request.host
    data['cached_input_file'] = cached_input_file
    data['output_file'] = output_file

    create_video_task.apply_async(args=[data])

    response_payload = {
        'record_id': record_id, 
        'filename': filename, 
        'message': 'Video processing started', 
        'input_height': data['input_height'], 
        'input_width': data['input_width'],
        'output_height': data['output_height'], 
        'output_width': data['output_width']
    }
    return jsonify(response_payload), 200
