from main.settings.base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fsis2',
        'USER': get_env_variable('PG_USER'),
        'PASSWORD': get_env_variable('PG_PASS'),
        'HOST': get_env_variable('PG_HOST'),
        'PORT': '',
    }
}
