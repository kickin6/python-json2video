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
4. [Running Tests](#running-tests)
5. [Contributing](#contributing)
6. [License](#license)
7. [Disclaimer](#disclaimer)

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

## Running Tests

To run the tests, you can use the provided `run_tests.sh` script. The script allows running all tests, tests in a specific file, or a specific test case.

1. **Run all tests**:

   ```bash
   ./run_tests.sh
   ```

2. **Run all tests in a specific file**:

   ```bash
   ./run_tests.sh tests/test_validations.py
   ```

3. **Run a specific test case**:
   ```bash
   ./run_tests.sh tests/test_validations.py test_is_valid_url
   ```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

**Warning:** The user is responsible for all security aspects of the application and the environment it runs in, including but not limited to the computer, network, user access, and execution, other scripts and code running on connected systems, and external services like Make.com.

**Disclosure:** We will not be held liable for any use or misuse of this application. By using this application, you agree to these terms.
