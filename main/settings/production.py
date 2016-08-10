from main.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fsis2',
***REMOVED***
***REMOVED***
***REMOVED***
        'PORT': '',
    }
}
