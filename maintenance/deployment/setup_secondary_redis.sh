#!/bin/bash
# Puxbay Dynamic Redis Scaling Script
# Use this to create multiple isolated Redis instances in bulk.
# Usage: sudo bash setup_secondary_redis.sh [COUNT] [STARTING_PORT]
# Example: sudo bash setup_secondary_redis.sh 3 6380
# This would create redis2 (6380), redis3 (6381), and redis4 (6382)

set -e

COUNT=${1:-1}
START_PORT=${2:-6380}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "Scaling Redis Instances"
echo "Count to Create: ${COUNT}"
echo "Starting Port:   ${START_PORT}"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

for i in $(seq 1 $COUNT); do
    # Offset by 1 to start suffixes from 2 (assuming 6379 is the primary)
    SUFFIX=$((i + 1))
    PORT=$((START_PORT + i - 1))
    INSTANCE_NAME="redis${SUFFIX}"

    echo ""
    echo -e "${YELLOW}>>> Setting up ${INSTANCE_NAME} on port ${PORT}...${NC}"

    # 1. Create Data Directory
    mkdir -p /var/lib/${INSTANCE_NAME}
    chown redis:redis /var/lib/${INSTANCE_NAME}
    chmod 750 /var/lib/${INSTANCE_NAME}

    # 2. Setup Configuration
    cp /etc/redis/redis.conf /etc/redis/${INSTANCE_NAME}.conf

    # Update configuration values
    sed -i "s/^port .*/port ${PORT}/" /etc/redis/${INSTANCE_NAME}.conf
    sed -i "s/^pidfile .*/pidfile \/var\/run\/redis\/redis-server${SUFFIX}.pid/" /etc/redis/${INSTANCE_NAME}.conf
    sed -i "s/^logfile .*/logfile \/var\/log\/redis\/redis-server${SUFFIX}.log/" /etc/redis/${INSTANCE_NAME}.conf
    sed -i "s/^dir .*/dir \/var\/lib\/${INSTANCE_NAME}/" /etc/redis/${INSTANCE_NAME}.conf

    # Ensure it binds locally
    if ! grep -q "^bind " /etc/redis/${INSTANCE_NAME}.conf; then
        echo "bind 127.0.0.1" >> /etc/redis/${INSTANCE_NAME}.conf
    fi

    # 3. Create Systemd Service
    cat > /etc/systemd/system/${INSTANCE_NAME}.service << EOF
[Unit]
Description=Redis In-Memory Data Store (Instance ${SUFFIX})
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/bin/redis-server /etc/redis/${INSTANCE_NAME}.conf --supervised systemd
ExecStop=/usr/bin/redis-cli -p ${PORT} shutdown
Restart=always
Type=notify
RuntimeDirectory=redis${SUFFIX}
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
EOF

    # 4. Start Instance
    systemctl daemon-reload
    systemctl enable ${INSTANCE_NAME}
    systemctl start ${INSTANCE_NAME}

    # 5. Verification
    if redis-cli -p ${PORT} ping | grep -q "PONG"; then
        echo -e "${GREEN}✓ Success! ${INSTANCE_NAME} is up at redis://localhost:${PORT}/0${NC}"
    else
        echo -e "${RED}✗ Error: ${INSTANCE_NAME} failed to start.${NC}"
    fi
done

echo ""
echo "========================================="
echo -e "${GREEN}🎉 Scaling Complete!${NC}"
echo "========================================="
echo "Managed Services: redis2 through redis$((COUNT + 1))"
echo "Port Range:       ${START_PORT} through $((START_PORT + COUNT - 1))"
echo "========================================="
