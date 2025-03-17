#!/bin/bash

# Enable error handling. if one build fails, the script stops immediately.
set -e

# Define an array of image names and corresponding Dockerfiles
images=("app" "task" "msg" "backend" "db")

# Loop through and build each image
for image in "${images[@]}"; do
    echo "Building $image:v1..."
    docker build --no-cache -t "$image:v1" -f "$image.Dockerfile" .
    echo "$image:v1 built successfully!"
done

echo "All images built successfully!"
