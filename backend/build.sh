#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p /tmp/data
mkdir -p /tmp/data/projects

echo "Build completed successfully!"
