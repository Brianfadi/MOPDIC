#!/bin/bash

# Create the media directory if it doesn't exist
mkdir -p media

# Copy all media files to the media directory
echo "Copying media files..."

# Copy event images
if [ -d "main/static/main/images/events" ]; then
    mkdir -p media/events
    cp -r main/static/main/images/events/* media/events/
    echo "Copied event images"
fi

# Copy news images
if [ -d "main/static/main/images/news" ]; then
    mkdir -p media/news
    cp -r main/static/main/images/news/* media/news/
    echo "Copied news images"
fi

# Copy project images
if [ -d "main/static/main/images/projects" ]; then
    mkdir -p media/projects
    cp -r main/static/main/images/projects/* media/projects/
    echo "Copied project images"
fi

# Set proper permissions
chmod -R 755 media

echo "Media files copied successfully!"
