#!/bin/bash
# Quick Fix: Disable PostgreSQL Replicas
# Use this if you want to proceed with deployment without fixing replicas

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Disabling PostgreSQL Replicas...${NC}"
echo ""

# Stop all replica services
for i in {1..5}; do
    SERVICE_NAME="postgresql-replica${i}"
    echo "Stopping ${SERVICE_NAME}..."
    sudo systemctl stop ${SERVICE_NAME} 2>/dev/null || echo "  Service not found or already stopped"
    sudo systemctl disable ${SERVICE_NAME} 2>/dev/null || echo "  Service not enabled"
done

echo ""
echo -e "${GREEN}Replicas disabled.${NC}"
echo ""
echo "Next steps:"
echo "1. Update your .env file: DB_NUM_REPLICAS=0"
echo "2. Or export in your shell: export DB_NUM_REPLICAS=0"
echo "3. Restart your Django application"
echo "4. Run migrations: python manage.py migrate"
