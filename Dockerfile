#
# tropheo Dockerfile
#

# Pull base image. (Python + NodeJS + Bower + Gulp)
FROM node:argon

# Hey, that's me
MAINTAINER willgraf

# Set production settings
ENV DJANGO_PRODUCTION true
ENV NPM_CONFIG_PRODUCTION true

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
WORKDIR /usr/src/app

# Install app python dependencies
ADD requirements.txt
RUN pip install -r requirements.txt

# just install with bower for faster images
ADD bower.json
RUN bower install --allow-root

# Copy all application files into the image.
ADD .

EXPOSE 8000

# COPY ./django_nginx.conf /etc/nginx/sites-available/
# RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/
# RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ENTRYPOINT ["docker-entrypoint.sh"]
