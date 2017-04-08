#!/bin/bash

# move to app directory
cd /usr/src/app

# Set up local environment variables, if dot env file present
source .env

# Set up nginx configuration settings
cp ./django_nginx.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/
echo "daemon off;" >> /etc/nginx/nginx.conf

# Prepare log files and start outputting logs to stdout
touch /usr/src/app/logs/gunicorn.log
touch /usr/src/app/logs/access.log
tail -n 0 -f /usr/src/app/logs/*.log &
echo Starting nginx

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Build and collect static files
python manage.py collectstatic --noinput --clear

# Start gunicorn processes
echo Starting Gunicorn.
exec gunicorn tropheo.wsgi:application \
    --name tropheo \
    --bind unix:/usr/src/app/tropheo/tropheo.sock \
    # --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info \
    --timeout 300 \
    --log-file=/usr/src/app/logs/gunicorn.log \
    --access-logfile=/usr/src/app/logs/access.log & 
exec service nginx start
