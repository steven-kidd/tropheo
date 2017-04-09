#!/bin/bash

# move to app directory
# APP_DIR=/Users/Will/Projects/tropheo
APP_DIR=/usr/src/app

# Logging
LOG_DIR=$APP_DIR/logs
mkdir $LOG_DIR

# Prepare log files and start outputting logs to stdout
touch $LOG_DIR/gunicorn.log $LOG_DIR/access.log

# Set up local environment variables, if dot env file present
source .env

# Set up nginx configuration settings
cp ./django_nginx.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/
echo "daemon off;" >> /etc/nginx/nginx.conf

cd $APP_DIR

tail -n 0 -f $LOG_DIR/*.log &
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
    --bind unix:$APP_DIR/tropheo.sock \
    --workers 3 \
    --log-level=debug \
    --timeout 300 \
    --log-file=$LOG_DIR/gunicorn.log \
    --access-logfile=$LOG_DIR/access.log & 
exec service nginx start
