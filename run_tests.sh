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

# Initialize default values for test file and test case
TEST_FILE=""
TEST_CASE=""

# Check if the test file and test case were passed as arguments
if [ "$#" -eq 2 ]; then
  TEST_FILE=$1
  TEST_CASE=$2
elif [ "$#" -eq 1 ]; then
  TEST_FILE=$1
fi

# Build the Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.test.yml build

# Start the services
echo "Starting Docker services..."
docker-compose -f docker-compose.test.yml up -d

# Run the tests
if [ -n "$TEST_FILE" ] && [ -n "$TEST_CASE" ]; then
  echo "Running specific test case: $TEST_FILE::$TEST_CASE"
  docker-compose -f docker-compose.test.yml run test pytest $TEST_FILE::$TEST_CASE
elif [ -n "$TEST_FILE" ]; then
  echo "Running all tests in file: $TEST_FILE"
  docker-compose -f docker-compose.test.yml run test pytest $TEST_FILE
else
  echo "Running all tests"
  docker-compose -f docker-compose.test.yml run test pytest
fi

# Stop and remove the services
echo "Stopping and removing Docker services..."
docker-compose -f docker-compose.test.yml down

# Cleanup test images
IMAGES=("test-image" "test-redis-image" "test-json2video-image" "test-celery-worker-image")
for IMAGE in "${IMAGES[@]}"; do
  docker rmi -f $IMAGE || echo "Failed to remove image: $IMAGE"
done

# Cleanup dynamically named containers
cleanup_containers_by_pattern "python-json2video-test-run-"

echo "Tests completed and environment cleaned up."
