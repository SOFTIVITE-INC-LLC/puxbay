#!/bin/bash
# Puxbay Update and Restart Script
# Use this script to update the system when a new build is released.
# Usage: sudo bash update_system.sh

set -e  # Exit on error

echo "========================================="
echo "Puxbay System Update & Restart"
echo "========================================="
echo ""

# Configuration (Matches deploy_ultimate.sh)
APP_NAME="puxbay"
APP_DIR="/opt/puxbay"
VENV_DIR="$APP_DIR/venv"
USER="www-data"
GROUP="www-data"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

cd $APP_DIR

echo -e "${YELLOW}Step 1: Fetching latest code from Git...${NC}"
git pull origin main # Uncomment this line if you use git for deployments
echo "Note: Manual pull might be required if git is not configured for automatic pulls."

echo -e "${YELLOW}Step 2: Updating Python dependencies...${NC}"
source $VENV_DIR/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies updated${NC}"

echo -e "${YELLOW}Step 3: Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"

echo -e "${YELLOW}Step 4: Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

echo -e "${YELLOW}Step 4.5: Updating system data (Manual, Plans, SEO)...${NC}"
python manage.py populate_plans
python manage.py seed_manual
python manage.py seed_seo
echo -e "${GREEN}✓ System data updated${NC}"

echo -e "${YELLOW}Step 5: Restarting all services...${NC}"
bash $APP_DIR/maintenance/deployment/restart_services.sh
echo -e "${GREEN}✓ All services restarted${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}🎉 Update Complete!${NC}"
echo "========================================="
echo "Your system has been updated and all services have been restarted."
echo "Check logs if you encounter any issues:"
echo "  - Gunicorn: tail -f $APP_DIR/logs/gunicorn-replica-1.log"
echo "  - Celery: tail -f $APP_DIR/logs/celery.log"
echo "========================================="
