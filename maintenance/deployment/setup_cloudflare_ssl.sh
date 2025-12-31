#!/bin/bash
# Cloudflare SSL Configuration Script for Puxbay
# This configures Nginx to work with Cloudflare's proxy and SSL

set -e

echo "========================================="
echo "Cloudflare SSL Configuration for Puxbay"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create SSL directory
echo "Step 1: Creating SSL directory..."
mkdir -p /etc/ssl/cloudflare
chmod 755 /etc/ssl/cloudflare

echo "✓ SSL directory created"
echo ""

# Get certificates
echo "Step 2: Setting up Cloudflare Origin Certificate"
echo ""
echo "Please follow these steps in Cloudflare Dashboard:"
echo "1. Go to SSL/TLS → Origin Server"
echo "2. Click 'Create Certificate'"
echo "3. Select hostnames: puxbay.com and *.puxbay.com"
echo "4. Click 'Create'"
echo ""
echo "Now paste the Origin Certificate below and press Ctrl+D when done:"
cat > /etc/ssl/cloudflare/origin.pem

echo ""
echo "Now paste the Private Key below and press Ctrl+D when done:"
cat > /etc/ssl/cloudflare/origin-key.pem

# Set permissions
chmod 644 /etc/ssl/cloudflare/origin.pem
chmod 600 /etc/ssl/cloudflare/origin-key.pem

echo ""
echo "✓ Certificates saved"
echo ""

# Update Nginx configuration
echo "Step 3: Updating Nginx configuration..."

cat > /etc/nginx/sites-available/puxbay << 'EOF'
# Cloudflare upstream
upstream django_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Main application
    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

# Enable site
ln -sf /etc/nginx/sites-available/puxbay /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "✓ Nginx configuration updated"
echo ""

# Test Nginx
echo "Step 4: Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    echo ""
    
    # Reload Nginx
    echo "Step 5: Reloading Nginx..."
    systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    echo "✗ Nginx configuration has errors. Please fix them before proceeding."
    exit 1
fi

echo ""
echo "========================================="
echo "Configuration Complete!"
echo "========================================="
echo ""
echo "Next steps in Cloudflare Dashboard:"
echo "1. Go to SSL/TLS → Overview"
echo "2. Set encryption mode to: Full (strict)"
echo "3. Go to DNS"
echo "4. Add A records with Proxy enabled (orange cloud):"
echo "   - @ → YOUR_SERVER_IP (Proxied)"
echo "   - www → YOUR_SERVER_IP (Proxied)"
echo "   - * → YOUR_SERVER_IP (Proxied)"
echo "5. Go to SSL/TLS → Edge Certificates"
echo "6. Enable 'Always Use HTTPS'"
echo "7. Enable 'Automatic HTTPS Rewrites'"
echo ""
echo "Test your setup:"
echo "  https://www.puxbay.com"
echo "  wss://www.puxbay.com/ws/"
echo ""
