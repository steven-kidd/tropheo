#!/bin/bash

# Set up local environment variables, if dot env file present
APP_DIR=/usr/src/app
LOG_DIR=$APP_DIR/logs
source $APP_DIR/.env

# set up log files
mkdir $LOG_DIR
touch $LOG_DIR/gunicorn.log $LOG_DIR/access.log

# Set up nginx configuration settings
cp $APP_DIR/nginx.tropheo.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/nginx.tropheo.conf /etc/nginx/sites-enabled/
echo "daemon off;" >> /etc/nginx/nginx.conf

# start outputting logs to stdout
tail -n 0 -f $LOG_DIR/*.log &
echo Performing database migration.

# Apply database migrations
python $APP_DIR/manage.py migrate

# Build and collect static files
# echo Collecting static files to serve.
# python $APP_DIR/manage.py collectstatic --noinput --clear

# Start gunicorn processes
echo Starting Gunicorn and nginx.
exec gunicorn tropheo.wsgi:application \
    --name tropheo \
    --bind unix:$APP_DIR/tropheo.sock \
    --workers 3 \
    --log-level=info \
    --timeout 300 \
    --log-file=$LOG_DIR/gunicorn.log \
    --access-logfile=$LOG_DIR/access.log & 
exec service nginx start
