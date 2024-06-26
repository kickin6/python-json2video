# Python JSON Video Processor

This project implements a JSON to Video processor using FFMPEG and Flask, encapsulated within Docker for ease of deployment and operation.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Cloning the Repository](#cloning-the-repository)
   - [Setting Up Docker](#setting-up-docker)
3. [Running the Application](#running-the-application)
   - [Starting the Services](#starting-the-services)
   - [Stopping the Services](#stopping-the-services)
4. [Usage](#usage)
   - [Creating a Zoom Video](#creating-a-zoom-video)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction

This project processes video files based on JSON input using FFMPEG, a powerful multimedia framework. The Flask web server handles incoming requests, manages video processing, and sends status updates via webhooks.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- Docker: [Download and Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Cloning the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/kickin6/python-jsonvideo/python-jsonvideo.git
cd python-jsonvideo
```

### Setting Up Docker

Build the Docker image and set up the Docker containers using the following commands:

```bash
docker-compose build
docker-compose up -d
```

## Running the Application

### Starting the Services

To start the Flask application and all necessary services, run:

```bash
docker-compose up
```

The application will be accessible at `http://localhost:5000`.

### Stopping the Services

To stop the running services, execute:

```bash
docker-compose down
```

## Usage

### Creating a Zoom Video

Send a POST request to the `/create_zoom_video` endpoint to create a zoom video. Here is an example using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "input_file": "/app/movies/scene1.png",
    "output_height": 720,
    "output_width": 1280, 
    "webhook_url":"http://my-webhook-server.com/", 
    "record_id":"9235634", 
    "zoom":"", 
    "api_key":"my-key"
}' http://localhost:5000/create_zoom_video
```

Ensure the input file exists in the `./movies` directory, as this directory is mounted inside the Docker container.

## Configuration

### Docker Compose

The `docker-compose.yml` file defines the services and their configurations:

```yaml
version: '3.8'

services:
  flask-zoom-app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./movies:/app/movies
    environment:
      FLASK_APP: app.py
    command: flask run --host=0.0.0.0
```

### Environment Variables

You can configure the Flask application using environment variables defined in the Docker Compose file.

### Requirements

The `requirements.txt` file lists all Python dependencies needed for the Flask application:

```text
blinker==1.8.2
certifi==2024.6.2
charset-normalizer==3.3.2
click==8.1.7
Flask==3.0.3
idna==3.7
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
requests==2.32.3
urllib3==2.2.2
Werkzeug==3.0.3
```

## Troubleshooting

- **Issue:** Input file does not exist.
  - **Solution:** Ensure the file is placed in the `./movies` directory.
  
- **Issue:** Webhook call failed.
  - **Solution:** Verify the webhook server is running and accessible from the Docker container.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or additions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
