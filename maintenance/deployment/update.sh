#!/bin/bash
# Quick update script for production deployments
# Usage: bash update.sh

set -e

APP_DIR="/opt/possystem"
VENV_DIR="$APP_DIR/venv"

echo "Updating POS System..."

# Navigate to app directory
cd $APP_DIR

# Activate virtual environment
source $VENV_DIR/bin/activate

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Install/update dependencies
echo "Updating dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart services
echo "Restarting services..."
sudo supervisorctl restart possystem
sudo supervisorctl restart possystem_celery

echo "✓ Update complete!"
echo "Check status: sudo supervisorctl status"
