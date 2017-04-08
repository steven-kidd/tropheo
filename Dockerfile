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
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install app python dependencies
ADD requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

# just install with bower for faster images
ADD bower.json /usr/src/app/
RUN bower install --allow-root

# Copy all application files into the image.
ADD . /usr/src/app

# RUN python manage.py bower install -- --allow-root

COPY ./docker-entrypoint.sh /
COPY ./django_nginx.conf /etc/nginx/sites-available/

EXPOSE 8000

RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ENTRYPOINT ["/docker-entrypoint.sh"]
