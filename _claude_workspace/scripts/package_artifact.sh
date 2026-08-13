#!/bin/bash

# Exit on error
set -e

echo "Building MODE Research Artifact v1.0.0-submission..."

# Define artifact name
ARTIFACT_NAME="mode_research_artifact_v1.0.0"
STAGING_DIR="/tmp/$ARTIFACT_NAME"

# Clean up any previous staging
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

# Copy directories
echo "Copying source files..."
cp -r env "$STAGING_DIR/"
cp -r scripts "$STAGING_DIR/"
cp -r analysis "$STAGING_DIR/"
cp -r checkpoints* "$STAGING_DIR/"
cp -r reproducibility "$STAGING_DIR/"
cp -r paper "$STAGING_DIR/"

# Remove any Pycache or hidden files
find "$STAGING_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$STAGING_DIR" -type f -name "*.DS_Store" -delete 2>/dev/null || true

# Create tarball
echo "Zipping artifact..."
tar -czf "${ARTIFACT_NAME}.tar.gz" -C /tmp "$ARTIFACT_NAME"

# Clean staging
rm -rf "$STAGING_DIR"

echo "Artifact successfully built: ${ARTIFACT_NAME}.tar.gz"
