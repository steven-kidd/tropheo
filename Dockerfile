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
    libmysqlclient-dev \
    python \
    python-dev \
    python-pip \
    python-virtualenv

# Install bower
RUN npm install -g bower

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install app python dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

# just install with bower for faster images
ADD bower.json .
RUN bower install --allow-root

# Copy all application files into the image.
ADD . .

# Expose Django port
EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
