# tests/test_tasks.py
import pytest
import subprocess
import json
import logging

from unittest.mock import patch, MagicMock
from app.tasks import create_video_task
import os
import requests

@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['PUBLIC_PORT'] = '80'

@pytest.fixture
def mock_subprocess(mocker):
    mock_popen = mocker.patch('app.tasks.subprocess.Popen')
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    mock_process.communicate.return_value = (b'output', b'')
    mock_process.returncode = 0
    return mock_process

@pytest.fixture
def mock_requests(mocker):
    return mocker.patch('app.tasks.requests.post')

@pytest.fixture
def mock_flask_app(mocker):
    return mocker.patch('app.create_app', autospec=True)

def run_ffprobe(file_path):
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        file_path
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f'ffprobe failed with error: {stderr.decode("utf-8")}')

    return json.loads(stdout.decode('utf-8'))

def test_create_video_task_image_original(tmp_path, caplog, mock_requests):
    # Set up test data
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())  # Ensure the path is absolute
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': False,
        'input_width': 1024,
        'input_height': 1024,
        'output_width': 1024,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    # Mock the webhook call
    mock_requests.post('http://example.com/webhook', text='success')

    # Run the task
    with caplog.at_level(logging.INFO):
        create_video_task(data)

    # Verify the output file exists
    assert os.path.exists(output_file)

    # Verify the output file properties
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']

    assert output_width == data['output_width']
    assert output_height == data['output_height']

    # Verify log messages
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    
    # Print captured logs
    print(caplog.text)

def test_create_video_task_image_portrait_crop(tmp_path, caplog, mock_requests):
    # Set up test data
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())  # Ensure the path is absolute
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': True,
        'input_width': 1024,
        'input_height': 1024,
        'output_width': 720,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    # Mock the webhook call
    mock_requests.post('http://example.com/webhook', text='success')

    # Run the task
    with caplog.at_level(logging.INFO):
        create_video_task(data)

    # Verify the output file exists
    assert os.path.exists(output_file)

    # Verify the output file properties
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']

    assert output_width == data['output_width']
    assert output_height == data['output_height']

    # Verify log messages
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    
    # Print captured logs
    print(caplog.text)

def test_create_video_task_image_portrait_nocrop(tmp_path, caplog, mock_requests):
    # Set up test data
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())  # Ensure the path is absolute
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': False,
        'input_width': 1024,
        'input_height': 1024,
        'output_width': 720,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    # Mock the webhook call
    mock_requests.post('http://example.com/webhook', text='success')

    # Run the task
    with caplog.at_level(logging.INFO):
        create_video_task(data)

    # Verify the output file exists
    assert os.path.exists(output_file)

    # Verify the output file properties
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']

    assert output_width == data['output_width']
    assert output_height == data['output_height']

    # Verify log messages
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    
    # Print captured logs
    print(caplog.text)

def test_create_video_task_success(mock_subprocess, mock_requests, mock_flask_app):
    # Arrange
    mock_flask_app_instance = MagicMock()
    mock_flask_app.return_value = mock_flask_app_instance

    data = {
        'record_id': '123',
        'framerate': 30,
        'duration': 10,
        'zoom': 0.01,
        'crop': True,
        'input_width': 1280,
        'input_height': 720,
        'output_width': 640,
        'output_height': 360,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': '/path/to/input.mp4',
        'output_file': 'path/to/output.mp4',  # Ensure no leading slash
        'request_host': 'localhost'
    }

    # Act
    result = create_video_task(data)

    # Assert
    assert result == 'Video created successfully'
    mock_subprocess.communicate.assert_called_once()
    mock_requests.assert_called_once_with(
        'http://example.com/webhook',
        json={'record_id': '123', 'filename': 'https://localhost:80/path/to/output.mp4'}
    )

def test_create_video_task_ffmpeg_failure(mock_subprocess, mock_flask_app):
    # Arrange
    mock_subprocess.returncode = 1
    mock_subprocess.communicate.return_value = (b'', b'error')

    data = {
        'record_id': '123',
        'framerate': 30,
        'duration': 10,
        'zoom': 0.01,
        'crop': True,
        'input_width': 1280,
        'input_height': 720,
        'output_width': 640,
        'output_height': 360,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': '/path/to/input.mp4',
        'output_file': 'path/to/output.mp4',  # Ensure no leading slash
        'request_host': 'localhost'
    }

    # Act
    result = create_video_task(data)

    # Assert
    assert result == 'FFmpeg command failed'

def test_create_video_task_webhook_failure(mock_subprocess, mock_requests, mock_flask_app):
    # Arrange
    mock_requests.side_effect = requests.RequestException('Webhook call failed')

    data = {
        'record_id': '123',
        'framerate': 30,
        'duration': 10,
        'zoom': 0.01,
        'crop': True,
        'input_width': 1280,
        'input_height': 720,
        'output_width': 640,
        'output_height': 360,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': '/path/to/input.mp4',
        'output_file': 'path/to/output.mp4',  # Ensure no leading slash
        'request_host': 'localhost'
    }

    # Act
    result = create_video_task(data)

    # Assert
    assert result == 'Webhook call failed'

def test_create_video_task_image_different_aspect_ratios(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1920x1080.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': True,
        'input_width': 1920,
        'input_height': 1080,
        'output_width': 720,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with caplog.at_level(logging.INFO):
        create_video_task(data)

    assert os.path.exists(output_file)
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']
    assert output_width == data['output_width']
    assert output_height == data['output_height']
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    print(caplog.text)

def test_create_video_task_maximum_dimensions(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_8000x8000.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': True,
        'input_width': 8000,
        'input_height': 8000,
        'output_width': 1920,
        'output_height': 1080,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with caplog.at_level(logging.INFO):
        create_video_task(data)

    assert os.path.exists(output_file)
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']
    assert output_width == data['output_width']
    assert output_height == data['output_height']
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    print(caplog.text)

def test_create_video_task_minimum_dimensions(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_150x150.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': True,
        'input_width': 150,
        'input_height': 150,
        'output_width': 600,
        'output_height': 600,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with caplog.at_level(logging.INFO):
        create_video_task(data)

    assert os.path.exists(output_file)
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']
    assert output_width == data['output_width']
    assert output_height == data['output_height']
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    print(caplog.text)

def test_create_video_task_zoom_only(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 50,
        'crop': False,
        'input_width': 1024,
        'input_height': 1024,
        'output_width': 1024,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with caplog.at_level(logging.INFO):
        create_video_task(data)

    assert os.path.exists(output_file)
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']
    assert output_width == data['output_width']
    assert output_height == data['output_height']
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    print(caplog.text)

def test_create_video_task_invalid_dimensions(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 30,
        'duration': 10,
        'zoom': 0,
        'crop': False,
        'input_width': -1024,  # Invalid dimension
        'input_height': 1024,
        'output_width': 720,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with pytest.raises(ValueError):
        create_video_task(data)

    # assert f"Received data: {data}" in caplog.text
    print(caplog.text)

def test_create_video_task_different_durations_and_framerates(tmp_path, caplog, mock_requests):
    input_file = os.path.join(os.path.dirname(__file__), 'test_data', 'image_1024x1024.jpg')
    output_file = tmp_path / 'output.mp4'
    output_file = str(output_file.resolve())
    data = {
        'record_id': 'test_record',
        'framerate': 60,
        'duration': 5,
        'zoom': 0,
        'crop': False,
        'input_width': 1024,
        'input_height': 1024,
        'output_width': 720,
        'output_height': 1024,
        'webhook_url': 'http://example.com/webhook',
        'cached_input_file': input_file,
        'output_file': output_file,
        'request_host': 'localhost'
    }

    mock_requests.post('http://example.com/webhook', text='success')

    with caplog.at_level(logging.INFO):
        create_video_task(data)

    assert os.path.exists(output_file)
    output_properties = run_ffprobe(output_file)
    output_width = output_properties['streams'][0]['width']
    output_height = output_properties['streams'][0]['height']
    assert output_width == data['output_width']
    assert output_height == data['output_height']
    assert f"Received data: {data}" in caplog.text
    assert f"Video created at {output_file}" in caplog.text
    print(caplog.text)
