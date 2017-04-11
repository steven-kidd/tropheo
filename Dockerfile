#
# tropheo Dockerfile
#

# Pull base image. (Python + NodeJS + Bower + Gulp)
FROM node:argon

# Hey, that's me
MAINTAINER willgraf

# Set production settings
ENV DJANGO_PRODUCTION true

# Update and install packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    vim \
    nginx \
    python \
    python-dev \
    python-pip \
    python-virtualenv

# Install bower
RUN npm install -g bower

# Create app directory
RUN mkdir -p /usr/src/app/tropheo
WORKDIR /usr/src/app/

# Install app python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# just install with bower for faster images
COPY bower.json .
RUN bower install --allow-root

# Copy application files
COPY . .

# Collect static files
RUN python ./manage.py collectstatic --noinput --clear

# Expose Django port
# EXPOSE 8000 # Do I even need this? nginx is already listening inside the container

ENTRYPOINT ["./docker-entrypoint.sh"]
