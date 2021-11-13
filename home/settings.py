"""
Django settings for home project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import os

from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from home.init import load_settings

# from django_auth_ldap.config import GroupOfNamesType, LDAPSearch


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lvik6rr1p^p5b6es!g@jcgbj)u!yh#7tud8dmu^**^xmrfewt('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = (
    'bootstrap5',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'rest_framework',
    'drf_spectacular',
    'installer',
    'shop',
    'management',
    'billing',
    'payment',
    'cms',
    'mediaserver',
    'permissions',
    'shipping',
    'accounting',
    #'utils',
    'rma',
    'filebrowser',
    'django.contrib.admin',
    'tinymce',
    'django_filters',
    'captcha',
    'cookiebanner',
    'compressor',
)

MIDDLEWARE = (
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]
print(LOCALE_PATHS)
ROOT_URLCONF = 'home.urls'

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
                'cms.context_processors.get_sites',
                'cms.context_processors.get_nav_sites',
                'cms.context_processors.get_version',
                'cms.context_processors.get_page_title',
                'django.template.context_processors.i18n',
                'shop.context_processors.get_open_orders',
                'shop.context_processors.language',
                'shop.context_processors.header',
                'shop.context_processors.footer',
                'shop.context_processors.categories',
                'shop.context_processors.cache_clear_neccessary',
            ],
        },
    },
]

WSGI_APPLICATION = 'home.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db2.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]
TINYMCE_DEFAULT_CONFIG = {
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
               "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
               "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
               "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
               "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
               "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,  # To force a specific language instead of the Django current language.
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = False

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/var/cypetulip/static'

MEDIA_ROOT = '/var/cypetulip'

MEDIA_URL = '/media/'

FILEBROWSER_DIRECTORY = ''
FILEBROWSER_VERSION_QUALITY = 70
FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    'medium': {'verbose_name': 'Medium (4col )', 'width': 270, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''}
}
DIRECTORY = ''
FILEBROWSER_MEDIA_ROOT = '/var/cypetulip/public'

SHOP_NAME = u'Cypetulip'

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'asd',
}
GOOGLE_TAG_ID = 'asd'

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
        'shop': {
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

load_settings()

# Default settings
BOOTSTRAP5 = {
    # The complete URL to the Bootstrap CSS file
    # Note that a URL can be either a string,
    # e.g. "https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css",
    # or a dict like the default value below.
    "css_url": {
        "href": "/static/bootstrap/css/bootstrap.min.css",
    },
    # The complete URL to the Bootstrap JavaScript file
    "javascript_url": {
        "url": "/static/bootstrap/js/bootstrap.bundle.min.js",
    },
    # The complete URL to the Bootstrap CSS file (None means no theme)
    "theme_url": None,
    # The URL to the Popper.js JavaScript file (slim)
    "popper_url": {
        "url": "/static/jquery/js/popper.min.js",
    },

    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-3',
    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-9',
    # Set placeholder attributes to label if no placeholder is provided
    'set_placeholder': True,
    # Class to indicate required (better to set this in your Django form)
    'required_css_class': '',
    # Class to indicate error (better to set this in your Django form)
    'error_css_class': 'has-error',
    # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
    'success_css_class': 'has-success',
    # Renderers (only set these if you have studied the source and understand the inner workings)
    'formset_renderers': {
        'default': 'bootstrap5.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap5.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap5.renderers.FieldRenderer',
        'inline': 'bootstrap5.renderers.InlineFieldRenderer',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Host for sending e-mail.
EMAIL_HOST = 'mail.bwk-technik.de'
# Port for sending e-mail.
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'shop@bwk-technik.de'
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''  # remove last letter
EMAIL_USE_TLS = True

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'management.api.authentication.CsrfExemptSessionAuthentication',
    ), 'DATETIME_FORMAT': '%Y-%m-%d',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

COOKIEBANNER = {
    "title": _("Cookie settings"),
    "footer_text": _("Please accept our cookies"),
    "footer_links": [
        {
            "title": _("Imprint"),
            "href": "/cms/legal"
        },
        {
            "title": _("Privacy"),
            "href": "/cms/privacy-policy"
        },
    ],
    "groups": [
        {
            "id": "essential",
            "name": _("Essential"),
            "description": _("Essential cookies allow this page to work."),
            "cookies": [
                {
                    "pattern": "cookiebanner",
                    "description": _("Meta cookie for the cookies that are set."),
                },
                {
                    "pattern": "csrftoken",
                    "description": _("This cookie prevents Cross-Site-Request-Forgery attacks."),
                },
                {
                    "pattern": "sessionid",
                    "description": _("This cookie is necessary to allow logging in, for example."),
                },
                {
                    "pattern": "django_language",
                    "description": _("This cookie is necessary to allow saving your language preference"),
                },
            ],
        },
        {
            "id": "analytics",
            "name": _("Analytics"),
            "description": _("These Cookies help us analyzing the website"),
            "optional": True,
            "cookies": [
                {
                    "pattern": "_pk_.*",
                    "description": _("Analytics cookie for website analysis."),
                },
            ],
        },
    ],
}
CACHE_MIDDLEWARE_SECONDS = 0

# SESSION_COOKIE_AGE = 60

RECAPTCHA_PUBLIC_KEY = 'MyRecaptchaKey123'
RECAPTCHA_PRIVATE_KEY = 'MyRecaptchaPrivateKey456'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True
if os.environ.get('GITHUB_WORKFLOW'):
    COMPRESS_ENABLED = False

COMPRESS_FILTERS = {'css': ['cms.compressor.CSSMinFilter'], 'js': ['compressor.filters.jsmin.JSMinFilter']}
COMPRESS_PRECOMPILERS = (
    # ('text/x-scss', 'sass.bat {infile} {outfile}'), # windows / development
    ('text/x-scss', 'sass {infile} {outfile}'),
)

CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None
FLOWER_URL = None #'http://localhost:8888/'

import sys

sys.path.append('/etc/cypetulip/')
try:
    from local_settings import *
except ImportError as e:
    print(e)
