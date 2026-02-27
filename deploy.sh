#!/bin/bash

# Jotly Deployment Script
CONDA_ENV="bullet-journal"

echo "--- Starting Deployment ---"

# 1. Get latest code
git pull origin main

# 2. Run migrations and collect static
echo "--- Running Migrations & Collecting Static Files ---"
conda run -n $CONDA_ENV python manage.py migrate
conda run -n $CONDA_ENV python manage.py collectstatic --noinput

# 3. Restart services
echo "--- Restarting Services ---"
sudo systemctl daemon-reload
sudo systemctl restart jotly
sudo systemctl restart nginx

echo "--- Deployment Complete! ---"
echo "Check status: sudo systemctl status jotly"
