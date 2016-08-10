from main.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fsis2',
        'USER': 'adam',
        'PASSWORD': 'django',
        'HOST': '142.143.160.56',
        'PORT': '',
    }
}
