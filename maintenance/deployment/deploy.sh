#!/bin/bash
# Production deployment script for Puxbay System (without Docker)
# Usage: sudo bash deploy.sh

set -e  # Exit on error

echo "========================================="
echo "Puxbay Production Deployment"
echo "========================================="

# Configuration
APP_NAME="puxbay"
APP_DIR="/opt/puxbay"
VENV_DIR="$APP_DIR/venv"
USER="www-data"
GROUP="www-data"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing system dependencies...${NC}"
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git

echo -e "${GREEN}✓ System dependencies installed${NC}"

echo -e "${YELLOW}Step 2: Creating application directory...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/staticfiles
mkdir -p $APP_DIR/media

echo -e "${GREEN}✓ Directories created${NC}"

echo -e "${YELLOW}Step 3: Setting up Python virtual environment...${NC}"
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

echo -e "${GREEN}✓ Virtual environment created${NC}"

echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo -e "${YELLOW}Step 5: Setting up PostgreSQL database...${NC}"
sudo -u postgres psql -c "CREATE DATABASE puxbay;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER puxbay WITH PASSWORD 'Thinkce@softivitepuxbay';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE puxbay TO puxbay;"

echo -e "${GREEN}✓ Database configured${NC}"

echo -e "${YELLOW}Step 6: Running migrations...${NC}"
python manage.py migrate --noinput

echo -e "${GREEN}✓ Migrations completed${NC}"

echo -e "${YELLOW}Step 7: Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}✓ Static files collected${NC}"

echo -e "${YELLOW}Step 8: Setting up Supervisor with multiple replicas...${NC}"

# Number of replicas (adjust as needed)
REPLICAS=3

# Create Supervisor configuration with multiple instances
cat > /etc/supervisor/conf.d/$APP_NAME.conf << EOF
# Multiple Gunicorn instances (replicas)
EOF

# Generate replica configurations
for i in $(seq 1 $REPLICAS); do
    PORT=$((8000 + i))
    cat >> /etc/supervisor/conf.d/$APP_NAME.conf << EOF
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
cat >> /etc/supervisor/conf.d/$APP_NAME.conf << EOF
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
programs=${APP_NAME}_replica_1,${APP_NAME}_replica_2,${APP_NAME}_replica_3
EOF

supervisorctl reread
supervisorctl update

echo -e "${GREEN}✓ Supervisor configured with $REPLICAS replicas${NC}"

echo -e "${YELLOW}Step 9: Setting up Nginx with load balancing...${NC}"

# Generate upstream configuration dynamically
UPSTREAM_SERVERS=""
for i in $(seq 1 $REPLICAS); do
    PORT=$((8000 + i))
    UPSTREAM_SERVERS="${UPSTREAM_SERVERS}    server 127.0.0.1:$PORT;\n"
done

cat > /etc/nginx/sites-available/$APP_NAME << EOF
# Load balancer configuration
upstream django_backend {
$(echo -e "$UPSTREAM_SERVERS")
    # Load balancing method (default is round-robin)
    # Other options: least_conn, ip_hash
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name www.puxbay.com puxbay.com *.puxbay.com;
    
    # Allow Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name www.puxbay.com puxbay.com *.puxbay.com;

    # SSL Configuration (update paths after running certbot)
    ssl_certificate /etc/letsencrypt/live/puxbay.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/puxbay.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /opt/puxbay/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/puxbay/media/;
        expires 7d;
    }

    # WebSocket support for Django Channels
    location /ws/ {
        proxy_pass http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # WebSocket timeout settings
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Main application
    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        
        # Connection settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health/ {
        proxy_pass http://django_backend;
        access_log off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo -e "${GREEN}✓ Nginx configured${NC}"

echo -e "${YELLOW}Step 10: Setting permissions...${NC}"
chown -R $USER:$GROUP $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${GREEN}✓ Permissions set${NC}"

echo -e "${YELLOW}Step 11: Starting services...${NC}"
supervisorctl start ${APP_NAME}_replicas:*
supervisorctl start ${APP_NAME}_celery
supervisorctl start ${APP_NAME}_celery_beat

echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Running $REPLICAS application replicas with load balancing"
echo "Application URL: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo supervisorctl status"
echo "  - View all replicas: sudo supervisorctl status ${APP_NAME}_replicas:*"
echo "  - Restart all replicas: sudo supervisorctl restart ${APP_NAME}_replicas:*"
echo "  - Restart single replica: sudo supervisorctl restart ${APP_NAME}_replica_1"
echo "  - View logs: tail -f $APP_DIR/logs/gunicorn-replica-1.log"
echo "  - Scale replicas: Edit REPLICAS variable in deploy.sh and re-run"
echo "  - Update code: cd $APP_DIR && git pull && sudo supervisorctl restart ${APP_NAME}_replicas:*"
echo ""
echo "Load balancing:"
echo "  - Method: Round-robin (default)"
echo "  - Replicas: $REPLICAS instances"
echo "  - Ports: 8001-$((8000 + REPLICAS))"
echo ""
echo "Next steps:"
echo "  1. Update .env with production settings"
echo "  2. Create superuser: cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo "  3. Set up SSL with Let's Encrypt:"
echo "     sudo apt-get install certbot python3-certbot-nginx"
echo "     sudo certbot --nginx -d puxbay.com -d www.puxbay.com -d *.puxbay.com"
echo "  4. Update ALLOWED_HOSTS in .env:"
echo "     ALLOWED_HOSTS=puxbay.com,www.puxbay.com,.puxbay.com"
echo "  5. Test WebSocket connection at wss://www.puxbay.com/ws/"
echo ""
