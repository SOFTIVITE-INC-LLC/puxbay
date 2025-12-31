#!/bin/bash
# Monitor PostgreSQL replication status

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "PostgreSQL Replication Status"
echo "========================================="
echo ""

# Check if primary is running
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ Primary server: RUNNING${NC}"
else
    echo -e "${RED}✗ Primary server: STOPPED${NC}"
fi

# Check if standby is running
if systemctl is-active --quiet postgresql-standby; then
    echo -e "${GREEN}✓ Standby server: RUNNING${NC}"
else
    echo -e "${RED}✗ Standby server: STOPPED${NC}"
fi

echo ""
echo "Replication Status:"
echo "-------------------"
sudo -u postgres psql -c "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;" 2>/dev/null || echo "No replication connections"

echo ""
echo "Standby Recovery Status:"
echo "------------------------"
sudo -u postgres psql -p 5433 -c "SELECT pg_is_in_recovery();" 2>/dev/null || echo "Standby not accessible"

echo ""
echo "Replication Lag:"
echo "----------------"
sudo -u postgres psql -c "SELECT CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN 0 ELSE EXTRACT (EPOCH FROM now() - pg_last_xact_replay_timestamp()) END AS log_delay;" -p 5433 2>/dev/null || echo "Cannot calculate lag"

echo ""
echo "Recent Backups:"
echo "---------------"
ls -lh /opt/possystem/backups/postgres/*.sql.gz 2>/dev/null | tail -5 || echo "No backups found"

echo ""
