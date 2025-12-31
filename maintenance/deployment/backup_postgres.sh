#!/bin/bash
# Automated PostgreSQL backup script
# Usage: bash backup_postgres.sh

set -e

# Configuration
BACKUP_DIR="/opt/possystem/backups/postgres"
DB_NAME="possystem"
DB_USER="posuser"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create backup directory
mkdir -p $BACKUP_DIR

echo -e "${YELLOW}Starting PostgreSQL backup...${NC}"

# Perform backup
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_FILE

if [ $? -eq 0 ]; then
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${GREEN}✓ Backup completed: $BACKUP_FILE ($SIZE)${NC}"
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Delete old backups
echo -e "${YELLOW}Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

REMAINING=$(ls -1 $BACKUP_DIR/*.sql.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Cleanup complete. $REMAINING backups remaining.${NC}"

# Optional: Upload to S3/cloud storage
# aws s3 cp $BACKUP_FILE s3://your-bucket/backups/

echo -e "${GREEN}✓ Backup process complete!${NC}"
