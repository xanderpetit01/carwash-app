#!/bin/bash

# Define variables
DOCKER_USERNAME="rednax01"
IMAGE_NAME="carwash-app"
VERSION="v1.0.0"

# Build the Docker image
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION .

# Tag the Docker image with the latest version
docker tag $DOCKER_USERNAME/$IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:latest

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
docker login -u $DOCKER_USERNAME

# Push the Docker images to Docker Hub
echo "Pushing images to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_USERNAME/$IMAGE_NAME:latest

# Logout from Docker Hub
echo "Logging out from Docker Hub..."
docker logout
