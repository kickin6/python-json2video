from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
import os
import string
import random
import shutil
import requests
import re

app = Flask(__name__)

CACHE_DIR = 'cache'
MOVIES_DIR = 'movies'
DEFAULT_ZOOM_INCREMENT = 0.002  # Default zoom level if not provided

SCHEME = os.getenv('SCHEME', 'https')
PORT = os.getenv('PORT', '8890')

def generate_random_filename(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length)) + '.mp4'

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def is_valid_record_id(record_id):
    return re.match(r'^[0-9a-zA-Z]+$', record_id) is not None

def is_valid_api_key(api_key):
    return re.match(r'^[a-z]+$', api_key) is not None

@app.route('/create_zoom_video', methods=['POST'])
def create_zoom_video():
    data = request.json

    input_file = data.get('input_file')
    output_height = data.get('output_height')
    output_width = data.get('output_width')
    record_id = data.get('record_id')
    webhook_url = data.get('webhook_url')
    api_key = data.get('api_key')
    zoom = data.get('zoom', '0')

    # Validate input parameters
    if not input_file or not is_valid_url(input_file):
        return jsonify({'error': 'Invalid input_file URL'}), 400
    if not output_height or not isinstance(output_height, int):
        return jsonify({'error': 'Invalid output_height'}), 400
    if not output_width or not isinstance(output_width, int):
        return jsonify({'error': 'Invalid output_width'}), 400
    if not record_id or not is_valid_record_id(record_id):
        return jsonify({'error': 'Invalid record_id'}), 400
    if not webhook_url or not is_valid_url(webhook_url):
        return jsonify({'error': 'Invalid webhook_url'}), 400
    if not api_key or not is_valid_api_key(api_key):
        return jsonify({'error': 'Invalid api_key'}), 400

    # Create directories if not exist
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    if not os.path.exists(MOVIES_DIR):
        os.makedirs(MOVIES_DIR)

    # Create a sub-directory for this API key if it doesn't exist
    secure_api_key = secure_filename(api_key)
    api_key_folder = os.path.join(MOVIES_DIR, secure_api_key)
    if not os.path.exists(api_key_folder):
        os.makedirs(api_key_folder)

    cached_input_file = os.path.join(CACHE_DIR, secure_filename(os.path.basename(input_file)))

    # Download the input file to the cache directory
    if is_valid_url(input_file):
        try:
            response = requests.get(input_file, stream=True)
            response.raise_for_status()
            with open(cached_input_file, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            app.logger.info(f'Downloaded {input_file} to cache.')
        except requests.RequestException as e:
            app.logger.error(f'Failed to download input file: {str(e)}')
            return jsonify({'error': 'Failed to download input file'}), 400
    else:
        return jsonify({'error': 'Input file must be a valid URL'}), 400

    # Generate a random filename for the output file
    output_file = os.path.join(api_key_folder, generate_random_filename())

    try:
        command = [
            'ffmpeg', '-loop', '1', '-i', cached_input_file,
            '-vf', f"zoompan=z='zoom+{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125*25,scale={output_width}:{output_height}",
            '-t', '5', '-r', '25', '-pix_fmt', 'yuv420p', output_file
        ]
        app.logger.info(f'Running command: {" ".join(command)}')
        subprocess.run(command, check=True)
        app.logger.info(f'Video created at {output_file}')

        # Full URL for the created video file
        BASE_URL = f"{SCHEME}://{request.host}:{PORT}"
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=False, host='0.0.0.0', port=port)
