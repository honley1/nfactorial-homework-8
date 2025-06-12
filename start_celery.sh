#!/bin/bash

echo "Starting Celery Worker..."
celery -A app.celery_app worker --loglevel=info --concurrency=4

# For development with auto-reload:
# celery -A app.celery_app worker --loglevel=info --concurrency=4 --pool=solo 