#!/bin/bash

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/Erunno/water-manager"
REPO_BRANCH="production"
REPO_DIR="${SCRIPT_DIR}/repo"
DATA_DIR="${SCRIPT_DIR}/data"
CONTAINER_NAME="water-manager"

echo "===== Water Manager Startup Script ====="
echo "Working directory: ${SCRIPT_DIR}"

# Make sure the data directory exists
mkdir -p "${DATA_DIR}"
echo "Ensuring data directory exists: ${DATA_DIR}"

# Check if repository directory exists
if [ -d "${REPO_DIR}" ]; then
    echo "Repository directory exists, pulling latest changes..."
    cd "${REPO_DIR}"
    git fetch origin
    git reset --hard "origin/${REPO_BRANCH}"
else
    echo "Cloning repository..."
    git clone -b "${REPO_BRANCH}" "${REPO_URL}" "${REPO_DIR}"
    cd "${REPO_DIR}"
fi

# Check if container is already running and stop it
if docker ps -a | grep -q ${CONTAINER_NAME}; then
    echo "Stopping and removing existing container..."
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# Build new image
echo "Building Docker image..."
docker build -t ${CONTAINER_NAME}:latest "${REPO_DIR}"

# Run container with standard ports (80 for HTTP, 443 for HTTPS)
echo "Starting container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 80:80 \
    -p 443:5000 \
    -v "${DATA_DIR}:/data" \
    --restart unless-stopped \
    ${CONTAINER_NAME}:latest

echo "===== Startup Complete ====="
echo "Water Manager is running on:"
echo "  HTTP:  http://$(hostname -I | awk '{print $1}'):80"
echo "  HTTPS: https://$(hostname -I | awk '{print $1}'):443"
echo ""
echo "Data is stored in: ${DATA_DIR}"
echo ""
echo "To view logs: docker logs ${CONTAINER_NAME}"
echo "To stop: docker stop ${CONTAINER_NAME}"
