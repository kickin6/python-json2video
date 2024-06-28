# app/tasks.py
import subprocess
import requests
from .config import Config
from .utils import generate_random_filename
from werkzeug.utils import secure_filename
import os
from .celery_config import celery_app

@celery_app.task
def long_running_task(data, flask_app=None):
    if flask_app is None:
        from app import create_app
        flask_app = create_app()

    record_id = data['record_id']
    framerate = data['framerate']
    duration = data['duration']
    zoom = data.get('zoom', Config.DEFAULT_ZOOM)
    crop = data['crop']
    input_width = data.get('input_width', 1024)
    input_height = data.get('input_height', 1024)
    output_width = data['output_width']
    output_height = data['output_height']
    webhook_url = data.get('webhook_url')
    cached_input_file = data['cached_input_file']
    output_file = data['output_file'].lstrip('/')  # Ensure no leading slash
    request_host = data['request_host']

    try:
        # Run the ffmpeg command to create the video
        flask_app.logger.info(f'Duration param: {duration}')
        total_frames = duration * framerate  # Total number of frames

        # Calculate crop parameters if needed
        crop_filter = ""
        if crop and (input_width != output_width or input_height != output_height):
            crop_width = min(input_width, output_width)
            crop_height = min(input_height, output_height)
            crop_x = (input_width - crop_width) // 2
            crop_y = (input_height - crop_height) // 2
            crop_filter = f",crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"

        # Calculate zoom parameters
        zoom_filter = ""
        if zoom != 0:
            if zoom > 0:
                zoom_rate = zoom / 100
                zoom_filter = f",zoompan=z='min(zoom+{zoom_rate},2)':d=1"
            else:
                zoom_rate = abs(zoom) / 100
                zoom_filter = f",zoompan=z='max(zoom-{zoom_rate},1)':d=1"

        ffmpeg_command = [
            "ffmpeg",
            "-i", cached_input_file,  # Input file
            "-vf", f"scale={output_width}:{output_height}{crop_filter}{zoom_filter}",  # Video filters
            "-r", str(framerate),  # Frame rate
            output_file  # Output file
        ]

        flask_app.logger.info(f'Running FFmpeg command: {" ".join(ffmpeg_command)}')

        with flask_app.app_context():
            try:
                # Start the ffmpeg process
                process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Capture and handle stdout and stderr
                stdout, stderr = process.communicate()

                # Log stdout and stderr
                flask_app.logger.info(f'ffmpeg output: {stdout.decode("utf-8")}')
                if process.returncode != 0:
                    flask_app.logger.error(f'ffmpeg error: {stderr.decode("utf-8")}')
                    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=ffmpeg_command, output=stderr)

                flask_app.logger.info(f'Processing video: {cached_input_file} to {output_file} completed successfully.')
            except Exception as e:
                flask_app.logger.error(f'Error processing video: {str(e)}')
                raise e

        flask_app.logger.info(f'Video created at {output_file}')

        # Full URL for the created video file
        BASE_URL = f"{Config.SCHEME}://{request_host}:{Config.PUBLIC_PORT}"
        full_url = f"{BASE_URL}/{output_file}"

        # Payload for the webhook
        payload = {
            'record_id': record_id,
            'filename': full_url
        }

        # Call the webhook
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            flask_app.logger.info(f'Webhook called successfully with payload: {payload}')
        except requests.RequestException as e:
            flask_app.logger.error(f'Webhook call failed: {str(e)}')
            return 'Webhook call failed'

        return 'Video created successfully'
    except subprocess.CalledProcessError as e:
        flask_app.logger.error('FFmpeg command failed.')
        return 'FFmpeg command failed'
