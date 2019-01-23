from main.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fsis2',
        'USER': 'cottrillad',
        'PASSWORD': 'django123',
    }
}


INTERNAL_IPS = ('127.0.0.1', )
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


#MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

INSTALLED_APPS += (
    #'debug_toolbar',
    #'django_extensions',
)
