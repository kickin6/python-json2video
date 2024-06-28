#!/bin/bash

# Function to stop and remove containers by pattern
cleanup_containers_by_pattern() {
  PATTERN=$1
  CONTAINERS=$(docker ps -a --filter "name=$PATTERN" -q)
  if [ -n "$CONTAINERS" ]; then
    echo "Stopping and removing containers with pattern $PATTERN..."
    docker stop $CONTAINERS
    docker rm -f $CONTAINERS
  fi
}

# Build the Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.test.yml build

# Start the services
echo "Starting Docker services..."
docker-compose -f docker-compose.test.yml up -d

# Run the tests
echo "Running tests..."
docker-compose -f docker-compose.test.yml run test

# Stop and remove the services
echo "Stopping and removing Docker services..."
docker-compose -f docker-compose.test.yml down

# Cleanup test images
echo "Removing test images..."
IMAGES=("test-image" "test-redis-image" "test-json2video-image" "test-celery-worker-image")
for IMAGE in "${IMAGES[@]}"; do
  docker rmi -f $IMAGE || echo "Failed to remove image: $IMAGE"
done

# Cleanup dynamically named containers
cleanup_containers_by_pattern "python-json2video-test-run-"

echo "Tests completed and environment cleaned up."
