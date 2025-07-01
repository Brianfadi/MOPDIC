#!/usr/bin/env bash
# Exit on error
set -o errexit
set -o pipefail
set -o nounset

# Enable debug mode if DEBUG is set to True
if [ "${DEBUG:-False}" = "True" ]; then
    set -x
fi

# Function to handle errors
function error_exit {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to run a command with error handling
function run_command {
    echo "Running: $@"
    "$@" || error_exit "Command failed: $*"
}

echo "=== Starting build process ==="

# Install dependencies
echo "Installing dependencies..."
run_command pip install -r requirements.txt

# Set up the database
echo "Setting up database..."
if ! python setup_database.py; then
    error_exit "Database setup failed"
fi

# Apply database migrations
echo "Applying migrations..."
run_command python manage.py check
run_command python manage.py migrate --noinput

# Create media directory if it doesn't exist
run_command mkdir -p media

# Set proper permissions for media directory
run_command chmod -R 755 media

# Collect static files
echo "Collecting static files..."
run_command python manage.py collectstatic --noinput --clear

# Copy media files to the correct location
if [ -d "media" ]; then
    echo "Copying media files..."
    run_command cp -r media/* /opt/render/project/src/media/ 2>/dev/null || true
    run_command chmod -R 755 /opt/render/project/src/media/
fi

echo "=== Build completed successfully! ==="
