# app/tasks.py
import subprocess
import requests
from .config import Config
from .utils import generate_random_filename
from werkzeug.utils import secure_filename
import os
from app.celery_app import celery_app
import logging
from celery import Celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@celery_app.task
def create_video_task(data, flask_app=None):
    logger.info(f"Received data: {data}")

    if flask_app is None:
        from app import create_app
        flask_app = create_app()

    record_id = data['record_id']
    framerate = data['framerate']
    duration = data['duration']
    zoom = data['zoom']
    crop = data['crop']
    input_width = data['input_width']
    input_height = data['input_height']
    output_width = data['output_width']
    output_height = data['output_height']
    webhook_url = data.get('webhook_url')
    cached_input_file = data['cached_input_file']
    output_file = data['output_file']
    request_host = data['request_host']

    # Validate input dimensions
    if input_width <= 0 or input_height <= 0 or output_width <= 0 or output_height <= 0:
        raise ValueError("Input and output dimensions must be positive integers")

    try:
        flask_app.logger.info(f'Duration param: {duration}')
        total_frames = duration * framerate  # Total number of frames

        crop_filter = ""
        if crop and (input_width != output_width or input_height != output_height):
            crop_width = min(input_width, output_width)
            crop_height = min(input_height, output_height)
            crop_x = (input_width - crop_width) // 2
            crop_y = (input_height - crop_height) // 2
            crop_filter = f",crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"

        pad_filter = ""
        if not crop and (input_width != output_width or input_height != output_height):
            pad_filter = f",scale=w=min({output_width}/iw\\,{output_height}/ih)*iw:h=-2,scale={output_width}:{output_height}:force_original_aspect_ratio=decrease,pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2"

        zoom_filter = ""
        if zoom != 0:
            max_zoom_rate = 0.1
            normalized_zoom = (zoom / 100) * max_zoom_rate
            if zoom > 0:
                zoom_filter = f",zoompan=z='min(zoom+{normalized_zoom},2)':d=1"
            else:
                zoom_filter = f",zoompan=z='max(zoom-{abs(normalized_zoom)},1)':d=1"

        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',
            '-i', cached_input_file,
            '-vf', (
                f"format=yuv420p"
                + crop_filter
                + pad_filter
                # + zoom_filter
                + f",scale={output_width}:{output_height}"
            ),
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-r', str(framerate),
            output_file
        ]

        flask_app.logger.info(f'Running FFmpeg command: {" ".join(ffmpeg_command)}')

        with flask_app.app_context():
            try:
                process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                stdout, stderr = process.communicate()

                flask_app.logger.info(f'ffmpeg output: {stdout.decode("utf-8")}')
                if process.returncode != 0:
                    flask_app.logger.error(f'ffmpeg error: {stderr.decode("utf-8")}')
                    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=ffmpeg_command, output=stderr)

                flask_app.logger.info(f'Processing video: {cached_input_file} to {output_file} completed successfully.')
            except Exception as e:
                flask_app.logger.error(f'Error processing video: {str(e)}')
                raise e

        flask_app.logger.info(f'Video created at {output_file}')

        # BASE_URL = f"{Config.SCHEME}://my-image-server.com"
        BASE_URL = f"{Config.SCHEME}://{request_host}:{Config.PUBLIC_PORT}"
        full_url = f"{BASE_URL}/{output_file}"

        webhook_payload = {
            'record_id': record_id,
            'filename': full_url
        }

        # Call the webhook
        try:
            response = requests.post(webhook_url, json=webhook_payload)
            response.raise_for_status()
            flask_app.logger.info(f'Webhook called successfully with payload: {webhook_payload}')
        except requests.RequestException as e:
            flask_app.logger.error(f'Webhook call failed: {str(e)}')
            return 'Webhook call failed'

        return 'Video created successfully'
    except subprocess.CalledProcessError as e:
        flask_app.logger.error('FFmpeg command failed.')
        return 'FFmpeg command failed'
