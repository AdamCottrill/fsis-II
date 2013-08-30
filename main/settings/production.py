from main.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

###these need to be reset to work with heroku:
##DATABASES = {
##    'default': {
##          'ENGINE': 'django.db.backends.postgresql_psycopg2', 
##          'NAME': 'snippets',
##          'USER': 'adam',
##          'Password': 'adam',
##        #  'HOST': '', 
##        #  'PORT': '',
##    }
##}
