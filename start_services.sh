#!/bin/bash
set -e

# Ensure the logs folder exists
mkdir -p logs

echo "Starting Django server..."
nohup python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &

sleep 2

echo "Starting Celery worker..."
nohup celery -A transaction_simulation worker --loglevel=info > logs/celery.log 2>&1 &

echo "All services started successfully!"
echo "Django server → logs/django.log"
echo "Celery worker → logs/celery.log"
