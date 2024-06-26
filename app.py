from flask import Flask, request, jsonify
from OpenSSL import SSL
import subprocess
import os
import string
import random
import shutil
import requests

app = Flask(__name__)

CACHE_DIR = 'cache'
MOVIES_DIR = 'movies'
DEFAULT_ZOOM_INCREMENT = 0.002  # Default zoom level if not provided

# Define the SSL context
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/app/ssl/key.pem')
context.use_certificate_file('/app/ssl/cert.pem')

def generate_random_filename(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length)) + '.mp4'

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    filename = url.split('/')[-1]
    file_path = os.path.join(dest_folder, filename)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        return None
    return file_path

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

    # Use default zoom if zoom key is present but value is blank
    if zoom == '':
        zoom = DEFAULT_ZOOM_INCREMENT
    else:
        zoom = float(zoom)

    # Check if required parameters are provided
    if not input_file or not output_height or not output_width or not record_id or not webhook_url or not api_key:
        app.logger.error('Missing required parameters')
        return jsonify({'error': 'Missing required parameters'}), 400

    app.logger.info(f'Received request with input_file={input_file}, output_height={output_height}, output_width={output_width}, record_id={record_id}, webhook_url={webhook_url}, api_key={api_key}, zoom={zoom}')

    # Ensure cache and movies directories exist
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(MOVIES_DIR, exist_ok=True)
    
    # Create or use subfolder under movies directory named after the api_key
    api_key_folder = os.path.join(MOVIES_DIR, api_key)
    os.makedirs(api_key_folder, exist_ok=True)
    
    # Check if the input file is a URL and download it
    if input_file.startswith('http://') or input_file.startswith('https://'):
        input_file_path = download_file(input_file, '/app/temp')
        if not input_file_path:
            app.logger.error(f'Failed to download file from {input_file}')
            return jsonify({'error': 'Failed to download file'}), 400
    else:
        input_file_path = input_file

    # Define cache path for the input file
    cached_input_file = os.path.join(CACHE_DIR, os.path.basename(input_file_path))
    
    # Copy the input file to the cache directory if it doesn't already exist
    if not os.path.isfile(cached_input_file):
        shutil.copy(input_file_path, cached_input_file)
        app.logger.info(f'Copied {input_file_path} to cache.')
    else:
        app.logger.info(f'Using cached version of {input_file_path}.')

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
        full_url = request.host_url + output_file

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

@app.route('/')
def hello():
    return "Hello, SSL on port 5000!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=context)

