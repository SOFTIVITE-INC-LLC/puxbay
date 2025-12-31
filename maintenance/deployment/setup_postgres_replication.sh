#!/bin/bash
# Setup PostgreSQL streaming replication with 5 replicas on same server
# This creates 5 standby replicas for high availability and load distribution

set -e

# Configuration
PRIMARY_PORT=5432
NUM_REPLICAS=5
BASE_STANDBY_PORT=5433
DATA_DIR_PRIMARY="/var/lib/postgresql/15/main"
BASE_DATA_DIR="/var/lib/postgresql/15"
REPLICATION_USER="replicator"
REPLICATION_PASSWORD="changeme_replication"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "PostgreSQL Replication Setup (5 Replicas)"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating replication user...${NC}"
sudo -u postgres psql -c "CREATE USER $REPLICATION_USER WITH REPLICATION ENCRYPTED PASSWORD '$REPLICATION_PASSWORD';" || echo "User already exists"

echo -e "${GREEN}✓ Replication user created${NC}"

echo -e "${YELLOW}Step 2: Configuring primary server...${NC}"

# Update pg_hba.conf for replication
cat >> /etc/postgresql/15/main/pg_hba.conf << EOF

# Replication connections
host    replication     $REPLICATION_USER    127.0.0.1/32            md5
host    replication     $REPLICATION_USER    ::1/128                 md5
EOF

# Update postgresql.conf for replication
cat >> /etc/postgresql/15/main/postgresql.conf << EOF

# Replication settings (5 replicas)
wal_level = replica
max_wal_senders = 10
wal_keep_size = 128
hot_standby = on
EOF

# Restart primary
systemctl restart postgresql

echo -e "${GREEN}✓ Primary server configured${NC}"

# Create 5 replicas
for i in $(seq 1 $NUM_REPLICAS); do
    STANDBY_PORT=$((BASE_STANDBY_PORT + i - 1))
    DATA_DIR_STANDBY="$BASE_DATA_DIR/standby$i"
    
    echo -e "${YELLOW}Step $((i+2)): Creating replica $i (port $STANDBY_PORT)...${NC}"
    
    # Create standby data directory
    mkdir -p $DATA_DIR_STANDBY
    chown postgres:postgres $DATA_DIR_STANDBY
    
    # Create base backup
    sudo -u postgres pg_basebackup -h localhost -D $DATA_DIR_STANDBY -U $REPLICATION_USER -v -P -W
    
    # Create standby.signal file
    sudo -u postgres touch $DATA_DIR_STANDBY/standby.signal
    
    # Configure standby postgresql.conf
    cat > $DATA_DIR_STANDBY/postgresql.auto.conf << EOF
port = $STANDBY_PORT
primary_conninfo = 'host=localhost port=$PRIMARY_PORT user=$REPLICATION_USER password=$REPLICATION_PASSWORD'
EOF
    
    chown postgres:postgres $DATA_DIR_STANDBY/postgresql.auto.conf
    
    # Create systemd service for standby
    cat > /etc/systemd/system/postgresql-standby$i.service << EOF
[Unit]
Description=PostgreSQL Standby Server $i
After=network.target postgresql.service

[Service]
Type=forking
User=postgres
Group=postgres
ExecStart=/usr/lib/postgresql/15/bin/pg_ctl start -D $DATA_DIR_STANDBY
ExecStop=/usr/lib/postgresql/15/bin/pg_ctl stop -D $DATA_DIR_STANDBY
ExecReload=/usr/lib/postgresql/15/bin/pg_ctl reload -D $DATA_DIR_STANDBY
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable postgresql-standby$i
    systemctl start postgresql-standby$i
    
    echo -e "${GREEN}✓ Replica $i created and started (port $STANDBY_PORT)${NC}"
done

echo ""
echo "========================================="
echo -e "${GREEN}Replication Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Primary server: localhost:$PRIMARY_PORT"
echo "Replica servers:"
for i in $(seq 1 $NUM_REPLICAS); do
    STANDBY_PORT=$((BASE_STANDBY_PORT + i - 1))
    echo "  - Replica $i: localhost:$STANDBY_PORT"
done
echo ""
echo "Check replication status:"
echo "  sudo -u postgres psql -c \"SELECT * FROM pg_stat_replication;\""
echo ""
echo "Check all replicas:"
for i in $(seq 1 $NUM_REPLICAS); do
    STANDBY_PORT=$((BASE_STANDBY_PORT + i - 1))
    echo "  sudo -u postgres psql -p $STANDBY_PORT -c \"SELECT pg_is_in_recovery();\""
done
echo ""
