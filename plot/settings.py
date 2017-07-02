# coding=utf-8

import os
import sys
from pathlib import PurePath
from django.core.management.color import color_style

from edc_device.constants import CENTRAL_SERVER

style = color_style()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETC_DIR = os.path.join(str(PurePath(BASE_DIR).parent), 'etc')

APP_NAME = 'plot'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')78^w@s3^kt)6lu6()tomqjg#8_%!381-nx5dtu#i=kn@68h_^'
CONFIG_FILE = '{}.conf'.format(APP_NAME)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# CONFIG_PATH = os.path.join(ETC_DIR, APP_NAME, CONFIG_FILE)
# sys.stdout.write(style.SUCCESS('Reading config from {}\n'.format(CONFIG_PATH)))
#
# config = configparser.RawConfigParser()
# config.read(os.path.join(CONFIG_PATH))


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'rest_framework.authtoken',
    'django_crypto_fields.apps.AppConfig',
    'django_revision.apps.AppConfig',
    'edc_base.apps.AppConfig',
    'edc_identifier.apps.AppConfig',
    'edc_protocol.apps.AppConfig',
    'household.apps.AppConfig',
    'edc_device.apps.AppConfig',
    'edc_search.apps.AppConfig',
    'edc_sync.apps.AppConfig',
    'survey.apps.AppConfig',
    'plot.apps.EdcMapAppConfig',
    'plot.apps.AppConfig',
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

ROOT_URLCONF = 'plot.urls'

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

WSGI_APPLICATION = 'plot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {
#             'read_default_file': os.path.join(ETC_DIR, 'mysql_test.conf'),
#         },
#     },
# }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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

TIME_ZONE = 'Africa/Gaborone'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

KEY_PATH = os.path.join(BASE_DIR, 'crypto_fields')
GIT_DIR = BASE_DIR

ANONYMOUS_ENABLED = True
CURRENT_MAP_AREA = 'test_community'
DEVICE_ID = '99'
DEVICE_ROLE = CENTRAL_SERVER
SURVEY_GROUP_NAME = 'test_survey'
SURVEY_SCHEDULE_NAME = 'year-1'
LOAD_SURVEYS = 'manual'
# edc_map
GPS_FILE_NAME = '/Volumes/GARMIN/GPX/temp.gpx'
GPS_DEVICE = '/Volumes/GARMIN/'
GPX_TEMPLATE = os.path.join(STATIC_ROOT, 'edc_map/gpx/template.gpx')


if 'test' in sys.argv:

    class DisableMigrations:
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
