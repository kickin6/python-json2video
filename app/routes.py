import os
import subprocess
import requests
from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.utils import secure_filename
from .validations import validate_json, validate_api_key, is_valid_record_id, is_valid_api_key, is_valid_url, is_valid_zoom_level, is_valid_dimension
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
    data = request.json

    is_valid, error = validate_json(data)
    if not is_valid:
        return jsonify({'error': f'Invalid input data: {error}'}), 400

    record_id = data['record_id']
    input_url = data['input_url']
    zoom = data.get('zoom', Config.DEFAULT_ZOOM)
    output_width = data['output_width']
    output_height = data['output_height']
    webhook_url = data.get('webhook_url')

    if not is_valid_record_id(record_id):
        return jsonify({'error': 'Invalid record ID'}), 400
    if not is_valid_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 400
    if not is_valid_url(input_url):
        return jsonify({'error': 'Invalid input URL'}), 400
    if webhook_url and not is_valid_url(webhook_url):
        return jsonify({'error': 'Invalid webhook URL'}), 400
    if not is_valid_zoom_level(zoom):
        return jsonify({'error': 'Invalid zoom level'}), 400
    if not is_valid_dimension(output_width):
        return jsonify({'error': 'Invalid output width'}), 400
    if not is_valid_dimension(output_height):
        return jsonify({'error': 'Invalid output height'}), 400

    # Ensure the cache directory exists
    os.makedirs(Config.CACHE_DIR, exist_ok=True)

    # Secure the filename and replace special characters
    cached_input_file = os.path.join(Config.CACHE_DIR, secure_filename(input_url.replace('://', '_').replace('/', '_')))
    movies_folder = os.path.join(Config.MOVIES_DIR, api_key)
    os.makedirs(movies_folder, exist_ok=True)

    try:
        # Download the file from the URL
        response = requests.get(input_url, stream=True)
        response.raise_for_status()
        with open(cached_input_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.RequestException as e:
        app.logger.error(f'Failed to download input file: {str(e)}')
        return jsonify({'error': 'Failed to download input file'}), 400

    # Generate a random filename for the output file
    output_file = os.path.join(movies_folder, generate_random_filename())

    try:
        # Run the ffmpeg command to create the video
        command = [
            'ffmpeg', '-loop', '1', '-i', cached_input_file,
            '-vf', f"zoompan=z='zoom+{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125*25,scale={output_width}:{output_height}",
            '-t', '5', '-r', '25', '-pix_fmt', 'yuv420p', output_file
        ]
        app.logger.info(f'Running command: {" ".join(command)}')
        subprocess.run(command, check=True)
        app.logger.info(f'Video created at {output_file}')

        # Full URL for the created video file
        BASE_URL = f"{Config.SCHEME}://{request.host}:{Config.PUBLIC_PORT}"
        full_url = f"{BASE_URL}/{output_file}"

        # Payload for the webhook
        payload = {
            'record_id': record_id,
            'filename': full_url
        }

        # Call the webhook
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        app.logger.info(f'Webhook called successfully with payload: {payload}')

        return jsonify({'message': 'Video created successfully', 'output_file': output_file}), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f'FFmpeg command failed: {str(e)}')
        return jsonify({'error': str(e)}), 500
    except requests.RequestException as e:
        app.logger.error(f'Webhook call failed: {str(e)}')
        return jsonify({'error': f'Webhook call failed: {str(e)}'}), 500