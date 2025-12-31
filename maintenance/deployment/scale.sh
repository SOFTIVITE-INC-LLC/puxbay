#!/bin/bash
# Scale replicas script
# Usage: bash scale.sh <number_of_replicas>

set -e

if [ -z "$1" ]; then
    echo "Usage: bash scale.sh <number_of_replicas>"
    echo "Example: bash scale.sh 5"
    exit 1
fi

REPLICAS=$1
APP_NAME="possystem"
APP_DIR="/opt/possystem"
VENV_DIR="$APP_DIR/venv"
USER="www-data"

echo "Scaling to $REPLICAS replicas..."

# Stop existing replicas
echo "Stopping existing replicas..."
sudo supervisorctl stop ${APP_NAME}_replicas:* || true

# Regenerate Supervisor configuration
echo "Updating Supervisor configuration..."
cat > /tmp/${APP_NAME}.conf << EOF
# Multiple Gunicorn instances (replicas)
EOF

# Generate replica configurations
REPLICA_NAMES=""
for i in $(seq 1 $REPLICAS); do
    PORT=$((8000 + i))
    if [ $i -eq 1 ]; then
        REPLICA_NAMES="${APP_NAME}_replica_${i}"
    else
        REPLICA_NAMES="${REPLICA_NAMES},${APP_NAME}_replica_${i}"
    fi
    
    cat >> /tmp/${APP_NAME}.conf << EOF
[program:${APP_NAME}_replica_${i}]
command=$VENV_DIR/bin/gunicorn --workers 2 --bind 127.0.0.1:$PORT possystem.asgi:application
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/gunicorn-replica-${i}.log
environment=PATH="$VENV_DIR/bin"

EOF
done

# Add Celery workers
cat >> /tmp/${APP_NAME}.conf << EOF
[program:${APP_NAME}_celery]
command=$VENV_DIR/bin/celery -A possystem worker -l info --concurrency=4
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/celery.log
environment=PATH="$VENV_DIR/bin"

[program:${APP_NAME}_celery_beat]
command=$VENV_DIR/bin/celery -A possystem beat -l info
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/celery-beat.log
environment=PATH="$VENV_DIR/bin"

# Group all replicas for easy management
[group:${APP_NAME}_replicas]
programs=$REPLICA_NAMES
EOF

sudo mv /tmp/${APP_NAME}.conf /etc/supervisor/conf.d/${APP_NAME}.conf

# Update Nginx configuration
echo "Updating Nginx configuration..."
UPSTREAM_SERVERS=""
for i in $(seq 1 $REPLICAS); do
    PORT=$((8000 + i))
    UPSTREAM_SERVERS="${UPSTREAM_SERVERS}    server 127.0.0.1:$PORT;\n"
done

cat > /tmp/${APP_NAME}_nginx << EOF
# Load balancer configuration
upstream django_backend {
$(echo -e "$UPSTREAM_SERVERS")
}

server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location /static/ {
        alias /opt/possystem/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/possystem/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /health/ {
        proxy_pass http://django_backend;
        access_log off;
    }
}
EOF

sudo mv /tmp/${APP_NAME}_nginx /etc/nginx/sites-available/${APP_NAME}

# Reload configurations
echo "Reloading services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ${APP_NAME}_replicas:*
sudo nginx -t && sudo systemctl reload nginx

echo "✓ Scaled to $REPLICAS replicas successfully!"
echo ""
echo "Check status: sudo supervisorctl status ${APP_NAME}_replicas:*"
