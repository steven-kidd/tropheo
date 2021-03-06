#!/bin/bash

# Set up local environment variables, if dot env file present
APP_DIR=/usr/src/app
LOG_DIR=$APP_DIR/logs

# set up log files
touch $LOG_DIR/gunicorn.log $LOG_DIR/access.log

# Set up nginx configuration settings
cp $APP_DIR/nginx.tropheo.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/nginx.tropheo.conf /etc/nginx/sites-enabled/
echo "daemon off;" >> /etc/nginx/nginx.conf

# Apply database migrations
echo Performing database migration.
python $APP_DIR/manage.py makemigrations
python $APP_DIR/manage.py migrate

# Start outputting logs to stdout
tail -n 0 -f $LOG_DIR/*.log &
# Start gunicorn processes
echo Starting Gunicorn and nginx. &
exec gunicorn tropheo.wsgi:application \
    --name=tropheo \
    --bind=unix:$APP_DIR/tropheo.sock \
    --workers=3 \
    --log-level=info \
    --timeout=300 \
    --log-file=$LOG_DIR/gunicorn.log \
    --access-logfile=$LOG_DIR/access.log & 
exec service nginx start
