from main.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fsis2',
        'USER': get_env_variable('PG_USER'),
        'PASSWORD': get_env_variable('PG_PASS'),
    }
}


INTERNAL_IPS = ('127.0.0.1', )

MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)
