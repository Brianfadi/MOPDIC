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

# Collect static files
echo "Collecting static files..."
run_command python manage.py collectstatic --noinput

echo "=== Build completed successfully! ==="
