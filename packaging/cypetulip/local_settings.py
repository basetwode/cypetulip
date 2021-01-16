import os

from home.settings import BASE_DIR

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', '/opt/dart-sass/sass {infile} {outfile}'),
)
COMPRESS_CACHE_BACKEND = "default"
COMPRESS_CACHEABLE_PRECOMPILERS = ['text/x-scss']
SESSION_COOKIE_AGE= int(os.environ.get("SESSION_COOKIE_AGE", default=604800))
CACHE_MIDDLEWARE_SECONDS = int(os.environ.get("CACHE_MIDDLEWARE_SECONDS", default=600))    # number of seconds to cache a page for (TTL)

DATABASES = {
    'default': {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db2.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
