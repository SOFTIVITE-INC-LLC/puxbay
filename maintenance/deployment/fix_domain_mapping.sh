#!/bin/bash
# Quick fix for "No tenant for hostname" error
# This script adds the domain mapping for puxbay.com

cd /var/www/possystem

echo "Adding domain mapping for puxbay.com..."
python maintenance/deployment/add_domain_mapping.py

echo ""
echo "Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "✓ Fix applied! Try accessing https://puxbay.com again"
