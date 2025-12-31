#!/bin/bash
# Complete Production Deployment Script for Puxbay
# Includes application deployment + Cloudflare SSL configuration
# Usage: sudo bash deploy_complete.sh

set -e  # Exit on error

echo "========================================="
echo "Puxbay Complete Production Deployment"
echo "========================================="
echo ""

# Configuration
APP_NAME="puxbay"
APP_DIR="/opt/puxbay"
VENV_DIR="$APP_DIR/venv"
USER="www-data"
GROUP="www-data"
REPLICAS=3

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

# Ask about Cloudflare
echo -e "${YELLOW}Will you be using Cloudflare as a proxy?${NC}"
echo "1) Yes - Configure with Cloudflare Origin Certificate"
echo "2) No - Use Let's Encrypt (manual setup later)"
read -p "Enter choice [1-2]: " CLOUDFLARE_CHOICE

echo ""
echo "========================================="
echo "Phase 1: System Setup"
echo "========================================="
echo ""

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
    git \
    curl

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

echo ""
echo "========================================="
echo "Phase 2: Application Replicas Setup"
echo "========================================="
echo ""

echo -e "${YELLOW}Step 8: Setting up Supervisor with $REPLICAS replicas...${NC}"

# Create Supervisor configuration
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

echo ""
echo "========================================="
echo "Phase 3: Nginx & SSL Configuration"
echo "========================================="
echo ""

# Generate upstream configuration
UPSTREAM_SERVERS=""
for i in $(seq 1 $REPLICAS); do
    PORT=$((8000 + i))
    UPSTREAM_SERVERS="${UPSTREAM_SERVERS}    server 127.0.0.1:$PORT;\n"
done

if [ "$CLOUDFLARE_CHOICE" = "1" ]; then
    echo -e "${YELLOW}Configuring Nginx for Cloudflare...${NC}"
    
    # Create SSL directory for Cloudflare
    mkdir -p /etc/ssl/cloudflare
    chmod 755 /etc/ssl/cloudflare
    
    echo ""
    echo "========================================="
    echo "Cloudflare Origin Certificate Setup"
    echo "========================================="
    echo ""
    echo "Please follow these steps in Cloudflare Dashboard:"
    echo "1. Go to SSL/TLS → Origin Server"
    echo "2. Click 'Create Certificate'"
    echo "3. Hostnames: puxbay.com and *.puxbay.com"
    echo "4. Validity: 15 years"
    echo "5. Click 'Create'"
    echo ""
    echo -e "${YELLOW}Paste the Origin Certificate below and press Ctrl+D when done:${NC}"
    cat > /etc/ssl/cloudflare/origin.pem
    
    echo ""
    echo -e "${YELLOW}Paste the Private Key below and press Ctrl+D when done:${NC}"
    cat > /etc/ssl/cloudflare/origin-key.pem
    
    # Set permissions
    chmod 644 /etc/ssl/cloudflare/origin.pem
    chmod 600 /etc/ssl/cloudflare/origin-key.pem
    
    echo -e "${GREEN}✓ Cloudflare certificates saved${NC}"
    
    # Create Nginx config for Cloudflare
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
# Cloudflare upstream
upstream django_backend {
$(echo -e "$UPSTREAM_SERVERS")
}

# Main HTTPS server (Cloudflare → Server)
server {
    listen 443 ssl http2;
    server_name www.puxbay.com puxbay.com *.puxbay.com;

    # Cloudflare Origin Certificate
    ssl_certificate /etc/ssl/cloudflare/origin.pem;
    ssl_certificate_key /etc/ssl/cloudflare/origin-key.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Cloudflare Real IP
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    real_ip_header CF-Connecting-IP;

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

    # WebSocket support
    location /ws/ {
        proxy_pass http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
    }

    # Health check
    location /health/ {
        proxy_pass http://django_backend;
        access_log off;
    }
}

# Block direct IP access
server {
    listen 443 ssl http2 default_server;
    server_name _;
    ssl_certificate /etc/ssl/cloudflare/origin.pem;
    ssl_certificate_key /etc/ssl/cloudflare/origin-key.pem;
    return 444;
}
EOF

else
    echo -e "${YELLOW}Configuring Nginx for Let's Encrypt...${NC}"
    
    # Create Nginx config for Let's Encrypt
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
# Load balancer configuration
upstream django_backend {
$(echo -e "$UPSTREAM_SERVERS")
}

# HTTP server (for Let's Encrypt challenges)
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

# HTTPS server (configure after getting certificate)
server {
    listen 443 ssl http2;
    server_name www.puxbay.com puxbay.com *.puxbay.com;

    # SSL Configuration (update after running certbot)
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

    # WebSocket support
    location /ws/ {
        proxy_pass http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
    }

    # Health check
    location /health/ {
        proxy_pass http://django_backend;
        access_log off;
    }
}
EOF

fi

# Enable site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx
echo -e "${YELLOW}Testing Nginx configuration...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
    systemctl restart nginx
    echo -e "${GREEN}✓ Nginx restarted${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo "Phase 4: Final Setup"
echo "========================================="
echo ""

echo -e "${YELLOW}Setting permissions...${NC}"
chown -R $USER:$GROUP $APP_DIR
chmod -R 755 $APP_DIR
echo -e "${GREEN}✓ Permissions set${NC}"

echo -e "${YELLOW}Starting services...${NC}"
supervisorctl start ${APP_NAME}_replicas:*
supervisorctl start ${APP_NAME}_celery
supervisorctl start ${APP_NAME}_celery_beat
echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Application: Puxbay"
echo "Replicas: $REPLICAS instances"
echo "Ports: 8001-$((8000 + REPLICAS))"
echo ""

if [ "$CLOUDFLARE_CHOICE" = "1" ]; then
    echo "SSL: Cloudflare Origin Certificate"
    echo ""
    echo "Next steps in Cloudflare Dashboard:"
    echo "1. Go to SSL/TLS → Overview"
    echo "   Set encryption mode to: Full (strict)"
    echo ""
    echo "2. Go to DNS and add A records (with Proxy enabled):"
    echo "   @ → YOUR_SERVER_IP (Proxied ☁️)"
    echo "   www → YOUR_SERVER_IP (Proxied ☁️)"
    echo "   * → YOUR_SERVER_IP (Proxied ☁️)"
    echo ""
    echo "3. Go to SSL/TLS → Edge Certificates"
    echo "   ✓ Enable 'Always Use HTTPS'"
    echo "   ✓ Enable 'Automatic HTTPS Rewrites'"
    echo ""
    echo "4. Update .env file:"
    echo "   ALLOWED_HOSTS=puxbay.com,www.puxbay.com,.puxbay.com"
    echo ""
    echo "Test your setup:"
    echo "  https://www.puxbay.com"
    echo "  wss://www.puxbay.com/ws/"
else
    echo "SSL: Let's Encrypt (manual setup required)"
    echo ""
    echo "Next steps:"
    echo "1. Install Certbot:"
    echo "   sudo apt-get install certbot python3-certbot-nginx"
    echo ""
    echo "2. Get SSL certificate:"
    echo "   sudo certbot --nginx -d puxbay.com -d www.puxbay.com"
    echo ""
    echo "3. Update .env file:"
    echo "   ALLOWED_HOSTS=puxbay.com,www.puxbay.com,.puxbay.com"
fi

echo ""
echo "Useful commands:"
echo "  - Check status: sudo supervisorctl status"
echo "  - View replicas: sudo supervisorctl status ${APP_NAME}_replicas:*"
echo "  - Restart all: sudo supervisorctl restart ${APP_NAME}_replicas:*"
echo "  - View logs: tail -f $APP_DIR/logs/gunicorn-replica-1.log"
echo "  - Create superuser: cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo ""
echo "🚀 Puxbay is ready for production!"
echo ""
