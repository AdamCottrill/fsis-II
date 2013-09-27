from main.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

#these need to be reset to work with heroku:
DATABASES = {
    'default': {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'fsis2',
         'USER': 'adam',
         'PASSWORD': 'django',
     }
}
