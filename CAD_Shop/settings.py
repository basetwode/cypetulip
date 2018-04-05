"""
Django settings for CAD_Shop project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lvik6rr1p^p5b6es!g@jcgbj)u!yh#7tud8dmu^**^xmrfewt('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Shop',
    'Administration',
    'Billing',
    'Payment',
    'CMS',
    'MediaServer',
    'Permissions', 'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware'
)

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]
print (LOCALE_PATHS)
ROOT_URLCONF = 'CAD_Shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'CMS.context_processors.get_sites',
                'CMS.context_processors.get_version',
                'CMS.context_processors.get_page_title',
                'django.template.context_processors.i18n',
                'Shop.context_processors.get_open_orders',
                'Shop.context_processors.language'
            ],
        },
    },
]

WSGI_APPLICATION = 'CAD_Shop.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

from django.utils.translation import ugettext_lazy as _, gettext

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# gettext = lambda s: s
# LANGUAGES = (
#     ('de', gettext('German')),
#     ('en', gettext('English')),
#     ('ja', gettext('Japanese')),
# )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = "/var/easyshop/static"

MEDIA_ROOT = '/var/easyshop/'

SHOP_NAME = u'CAD Noerdlingen'

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'level':'DEBUG',
#     'class': 'logging.StreamHandler',
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             #'filename': 'debug.log',
#         },
#     },
#
#     'loggers': {
#
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # root logger
        '': {
            'handlers': ['console'],
        },
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'Shop': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

build = open(os.path.join(BASE_DIR, 'build'), "r")
VERSION = "2.0 - BUILD #" + build.readline()
build.close()

print(VERSION)

from CAD_Shop.init import load_settings

load_settings()
