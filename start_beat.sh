#!/bin/bash

echo "Starting Celery Beat Scheduler..."
celery -A app.celery_app beat --loglevel=info 