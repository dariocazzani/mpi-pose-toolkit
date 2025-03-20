#!/bin/bash

# Script to clean up dataset folders
# Removes all subject_XX directories and the util directory

# Set script to exit on error
set -e

echo "=== Dataset Cleanup Script ==="
echo "This script will delete all subject_XX folders and the util folder."
echo "Warning: This operation cannot be undone!"

# Get the current directory or use the provided path
DATASET_DIR=$(realpath "${1:-.}")
echo "Target directory: $DATASET_DIR"

# Count the subject directories
SUBJECT_COUNT=$(find "$DATASET_DIR" -maxdepth 1 -type d -name "subject_*" | wc -l)
echo "Found $SUBJECT_COUNT subject directories to remove"

# Check if util directory exists
if [ -d "$DATASET_DIR/util" ]; then
    UTIL_EXISTS=1
    echo "Found util directory to remove"
else
    UTIL_EXISTS=0
    echo "No util directory found"
fi

if [ "$SUBJECT_COUNT" -eq 0 ] && [ "$UTIL_EXISTS" -eq 0 ]; then
    echo "No directories to remove. Exiting."
    exit 0
fi

# Ask for confirmation
read -p "Are you sure you want to proceed with deletion? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo "Starting cleanup..."

# Remove subject directories
if [ "$SUBJECT_COUNT" -gt 0 ]; then
    echo "Removing subject directories..."
    find "$DATASET_DIR" -maxdepth 1 -type d -name "subject_*" -exec rm -rf {} \;
    echo "Subject directories removed successfully."
fi

# Remove util directory if it exists
if [ "$UTIL_EXISTS" -eq 1 ]; then
    echo "Removing util directory..."
    rm -rf "$DATASET_DIR/util"
    echo "Util directory removed successfully."
fi

echo "Cleanup completed!"