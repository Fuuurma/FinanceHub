#!/bin/bash

# Background Jobs Startup Script
# Sets up Django environment and starts background workers

cd /Users/sergi/Desktop/Projects/FinanceHub/Backend

# Set environment variables
export PYTHONPATH="/Users/sergi/Desktop/Projects/FinanceHub/Backend/src"
export DJANGO_SETTINGS_MODULE="core.settings"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis is not running. Starting Redis..."
    brew services start redis
    sleep 2
fi

# Start Dramatiq worker with Redis broker
echo "Starting Dramatiq background workers..."
/Users/sergi/Desktop/Projects/FinanceHub/Backend/venv/bin/python -m dramatiq src.tasks.crypto_data_tasks
