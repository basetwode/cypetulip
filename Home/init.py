

from os import sep
__author__ = ''


def load_settings():

    from configparser import RawConfigParser

    config = RawConfigParser()
    from Home import settings
    config.read(settings.BASE_DIR + sep + 'settings.conf')

    # getfloat() raises an exception if the value is not a float
    # getint() and getboolean() also do this for their respective types
    media_dir = config.get('data', 'DATA_DIR')
    # an_int = config.getint('Section1', 'an_int')
    # print a_float + an_int
    if media_dir:
        settings.MEDIA_ROOT = media_dir

    db_engine = config.get('db','engine')
    if db_engine and db_engine == 'mysql':
        settings.DATABASES['default'] = {
            'ENGINE' :'django.db.backends.mysql',
            'NAME': config.get('db','name'),
            'USER': config.get('db','user'),
            'PASSWORD': config.get('db','pwd'),
            'HOST': config.get('db','host'),
            'PORT': config.get('db','port')
        }
    # Notice that the next output does not interpolate '%(bar)s' or '%(baz)s'.
    # This is because we are using a RawConfigParser().
    # if config.getboolean('Section1', 'a_bool'):
    #     print config.get('Section1', 'foo')