#!/bin/bash
# PostgreSQL Replica Recovery Script
# This script fixes the corrupted replica on port 5434

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PostgreSQL Replica Recovery Script${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo ""

# Configuration
REPLICA_NAME="postgresql-replica1"
REPLICA_PORT="5434"
REPLICA_DATA_DIR="/var/lib/postgresql/15/replica1"
PRIMARY_PORT="5432"
PRIMARY_USER="puxbay"

echo -e "${YELLOW}Step 1: Stopping corrupted replica service...${NC}"
sudo systemctl stop ${REPLICA_NAME} || echo "Service already stopped"
sleep 2

echo -e "${YELLOW}Step 2: Checking service status...${NC}"
sudo systemctl status ${REPLICA_NAME} --no-pager || true

echo -e "${YELLOW}Step 3: Backing up corrupted data directory (just in case)...${NC}"
if [ -d "${REPLICA_DATA_DIR}" ]; then
    BACKUP_DIR="${REPLICA_DATA_DIR}.corrupted.$(date +%Y%m%d_%H%M%S)"
    echo "Moving ${REPLICA_DATA_DIR} to ${BACKUP_DIR}"
    sudo mv ${REPLICA_DATA_DIR} ${BACKUP_DIR}
else
    echo "Data directory does not exist, skipping backup"
fi

echo -e "${YELLOW}Step 4: Creating fresh replica from primary server...${NC}"
echo "This may take a few minutes depending on database size..."
sudo -u postgres pg_basebackup \
    -h localhost \
    -p ${PRIMARY_PORT} \
    -U ${PRIMARY_USER} \
    -D ${REPLICA_DATA_DIR} \
    -Fp \
    -Xs \
    -P \
    -R

echo -e "${YELLOW}Step 5: Setting correct permissions...${NC}"
sudo chown -R postgres:postgres ${REPLICA_DATA_DIR}
sudo chmod 700 ${REPLICA_DATA_DIR}

echo -e "${YELLOW}Step 6: Starting replica service...${NC}"
sudo systemctl start ${REPLICA_NAME}
sleep 3

echo -e "${YELLOW}Step 7: Checking service status...${NC}"
sudo systemctl status ${REPLICA_NAME} --no-pager

echo ""
echo -e "${GREEN}Step 8: Verifying replication...${NC}"
sudo -u postgres psql -p ${PRIMARY_PORT} -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;" || echo "Could not verify replication status"

echo ""
echo -e "${GREEN}Step 9: Testing replica connection...${NC}"
psql -h localhost -p ${REPLICA_PORT} -U ${PRIMARY_USER} -d puxbay -c "SELECT 1 AS test;" || echo "Could not connect to replica"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Recovery Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Next steps:"
echo "1. Verify your application can connect to the database"
echo "2. Run Django migrations: python manage.py migrate"
echo "3. Monitor the replica service: sudo systemctl status ${REPLICA_NAME}"
