import docker
import pytest

# Define unique tags and names for all test-related resources
TEST_IMAGE_TAGS = [
    'test-image',
    'test-redis-image',
    'test-json2video-image',
    'test-celery-worker-image'
]
# Explicitly named containers
TEST_CONTAINER_NAMES = [
    'test-container',
    'test-redis',
    'test-json2video',
    'test-celery-worker'
]
# Patterns for dynamically named containers
TEST_CONTAINER_PATTERNS = [
    'python-json2video-test-run-',  # Add any other patterns as needed
]

@pytest.fixture(scope='session')
def docker_client():
    client = docker.from_env()
    yield client
    client.close()

@pytest.fixture(scope='function')
def redis_container(docker_client):
    container = docker_client.containers.run(
        TEST_IMAGE_TAGS[1],  # 'test-redis-image'
        name=TEST_CONTAINER_NAMES[1],  # 'test-redis'
        ports={'6379/tcp': 6379},
        detach=True
    )
    yield container
    container.stop()
    container.remove()

@pytest.fixture(scope='session', autouse=True)
def cleanup_docker_resources(docker_client):
    yield
    # Remove explicitly named containers
    containers = docker_client.containers.list(all=True)
    for container in containers:
        if container.name in TEST_CONTAINER_NAMES or any(pattern in container.name for pattern in TEST_CONTAINER_PATTERNS):
            print(f"Stopping and removing container: {container.name}")
            container.stop()
            container.remove(force=True)
    
    # Ensure all test images are removed
    images = docker_client.images.list()
    for image in images:
        for tag in image.tags:
            if any(test_tag in tag for test_tag in TEST_IMAGE_TAGS):
                print(f"Removing image: {tag}")
                try:
                    docker_client.images.remove(image.id, force=True)
                except docker.errors.APIError as e:
                    print(f"Error removing image {tag}: {e}")
