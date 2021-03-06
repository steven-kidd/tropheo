"""
Django settings for tropheo project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

for d in [DATA_DIR, LOG_DIR, PROJECT_DIR, STATIC_ROOT]:
    if not os.path.isdir(d):
        os.mkdir(d)

BOWER_COMPONENTS_ROOT = BASE_DIR#os.path.join(STATIC_ROOT, 'components')

# Application Level Settings

WSGI_APPLICATION = 'tropheo.wsgi.application'

ROOT_URLCONF = 'tropheo.urls'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'tropheo'),
        'USER': os.environ.get('DATABASE_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432')
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'totally_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

ALLOWED_HOSTS = ['.willgraf.com', os.environ.get('ENV_URL'),
                 'localhost', '127.0.0.1', '[::1]']

# Login / Registration Settings

LOGIN_REDIRECT_URL = 'home' # go to url home after successful login.
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.
REGISTRATION_OPEN = True

# Email SMTP Server / hack / workaround
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# AUTHENTICATION_BACKENDS = ['trohpeo.backends.EmailBackend']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangobower',
    'django_nvd3',
    'bootstrap_pagination',
    'tropheo'
]

# Django extensions
try:
    import django_extensions
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)

# this is replaced by bower.json.  Json file is necessary when being run from Docker
# this variable is used when using bower_install at a user-level.
BOWER_INSTALLED_APPS = (
    'bootstrap#v4.0.0-alpha.6',
    'font-awesome',
    'jquery',
    'tether',
    'underscore',
    'nvd3#1.8.1',
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'djangobower.finders.BowerFinder'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
# SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Caches
# https://docs.djangoproject.com/en/dev/topics/cache/
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
