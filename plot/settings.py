# coding=utf-8

import configparser
import os
import sys

from django.core.management.color import color_style

from survey.apps import S

style = color_style()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_NAME = 'plot'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/
DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')78^w@s3^kt)6lu6()tomqjg#8_%!381-nx5dtu#i=kn@68h_^'
CONFIG_FILE = '{}.conf'.format(APP_NAME)
if DEBUG:
    ETC_DIR = '/etc'
else:
    ETC_DIR = '/etc'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

CONFIG_PATH = os.path.join(ETC_DIR, APP_NAME, CONFIG_FILE)
sys.stdout.write(style.SUCCESS('Reading config from {}\n'.format(CONFIG_PATH)))

config = configparser.RawConfigParser()
config.read(os.path.join(CONFIG_PATH))


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    # 'rest_framework',
    # 'rest_framework.authtoken',
    'django_crypto_fields.apps.AppConfig',
    'django_revision.apps.AppConfig',
    'edc_base.apps.AppConfig',
    # 'edc_consent.apps.AppConfig',
    'edc_device.apps.AppConfig',
    'edc_identifier.apps.AppConfig',
    'edc_protocol.apps.AppConfig',
    # 'edc_sync.apps.AppConfig',
    # 'member.apps.AppConfig',
    # 'example_survey.apps.EdcMapAppConfig',
    # 'household.apps.AppConfig',
    'edc_search.apps.AppConfig',
    'survey.apps.AppConfig',
    'plot.apps.AppConfig',
    'edc_map.apps.AppConfig',
    # 'example_survey.apps.EdcBaseTestAppConfig',
    # 'example_survey.apps.AppConfig',
    # 'example_survey.apps.EdcDeviceAppConfig',
]

# if 'test' in sys.argv:
#     INSTALLED_APPS = INSTALLED_APPS = ['example_survey.apps.AppConfig']

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


# and 'mysql' not in DATABASES.get('default').get('ENGINE'):
if 'test' in sys.argv:
    MIGRATION_MODULES = {
        "django_crypto_fields": None,
        "edc_call_manager": None,
        "edc_appointment": None,
        "edc_call_manager": None,
        "edc_consent": None,
        "edc_death_report": None,
        "edc_export": None,
        "edc_identifier": None,
        "edc_metadata": None,
        "edc_rule_groups": None,
        "edc_registration": None,
        "edc_sync": None,
        "bcpp": None,
        "bcpp_subject": None,
        "plot": None,
        "household": None,
        "member": None,
        "survey": None,
        'admin': None,
        "auth": None,
        'bcpp_map': None,
        'contenttypes': None,
        'sessions': None,
    }
if 'test' in sys.argv:
    PASSWORD_HASHERS = ('django_plainpasswordhasher.PlainPasswordHasher', )
if 'test' in sys.argv:
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'


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

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'plot', 'media')
DEVICE_ID = '99'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'


# edc_map
GPS_FILE_NAME = '/Volumes/GARMIN/GPX/temp.gpx'
GPS_DEVICE = '/Volumes/GARMIN/'
GPX_TEMPLATE = os.path.join(STATIC_ROOT, 'edc_map/gpx/template.gpx')

CURRENT_MAP_AREA = 'test_community'

KEY_PATH = '/Volumes/crypto_keys'

CURRENT_MAP_AREA = config['edc_map'].get('map_area', 'test_community')
DEVICE_ID = config['edc_device'].get('device_id', '99')
DEVICE_ROLE = config['edc_device'].get('role')
LABEL_PRINTER = config['edc_label'].get('label_printer', 'label_printer')
SURVEY_GROUP_NAME = config['survey'].get('group_name')
SURVEY_SCHEDULE_NAME = config['survey'].get('schedule_name')
ANONYMOUS_ENABLED = config['bcpp'].get('anonymous_enabled')
DEVICE_IDS = [d.strip() for d in config['edc_map'].get('device_ids').split(',')]
