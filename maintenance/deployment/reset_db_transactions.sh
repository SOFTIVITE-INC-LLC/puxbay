#!/bin/bash
# Database Transaction Reset Script
# Run this if you encounter "transaction is aborted" errors

echo "Resetting database connections and clearing aborted transactions..."

# Method 1: Restart PostgreSQL to clear all connections
echo "1. Restarting PostgreSQL..."
sudo systemctl restart postgresql

# Wait for PostgreSQL to be ready
sleep 3

# Method 2: Drop all connections to the database (alternative)
# Uncomment if restart doesn't work
# echo "2. Dropping all connections..."
# sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'puxbay' AND pid <> pg_backend_pid();"

echo "3. Testing database connection..."
python manage.py dbshell -c "SELECT 1;" || echo "Database connection test failed"

echo ""
echo "Database reset complete. You can now retry your deployment."
echo "Run: sudo bash maintenance/deployment/deploy_ultimate.sh"
