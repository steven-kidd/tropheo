#!/bin/bash

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Build and collect static files
python manage.py collectstatic --noinput

# Prepare log files and start outputting logs to stdout
touch /usr/src/app/logs/gunicorn.log
touch /usr/src/app/logs/access.log
tail -n 0 -f /usr/src/app/logs/*.log &
echo Starting nginx 

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn tropheo.wsgi:application \
    --name tropheo \
    --bind unix:/usr/src/app/tropheo/tropheo.sock \
    --workers 3 \
    --log-level=info \
    --timeout 300 \
    --log-file=/usr/src/app/logs/gunicorn.log \
    --access-logfile=/usr/src/app/logs/access.log & 
exec service nginx start
