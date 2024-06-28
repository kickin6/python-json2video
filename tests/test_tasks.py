# tests/test_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from app.tasks import long_running_task
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

def test_long_running_task_success(mock_subprocess, mock_requests, mock_flask_app):
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
    result = long_running_task(data)

    # Assert
    assert result == 'Video created successfully'
    mock_subprocess.communicate.assert_called_once()
    mock_requests.assert_called_once_with(
        'http://example.com/webhook',
        json={'record_id': '123', 'filename': 'https://localhost:80/path/to/output.mp4'}
    )

def test_long_running_task_ffmpeg_failure(mock_subprocess, mock_flask_app):
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
    result = long_running_task(data)

    # Assert
    assert result == 'FFmpeg command failed'

def test_long_running_task_webhook_failure(mock_subprocess, mock_requests, mock_flask_app):
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
    result = long_running_task(data)

    # Assert
    assert result == 'Webhook call failed'
