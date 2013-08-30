from main.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/db/fsis2.db' % root(),

#          'ENGINE': 'django.db.backends.postgresql_psycopg2', 
#          'NAME': 'snippets',
#  ***REMOVED***
#          'Password': 'adam',
        #  'HOST': '', 
        #  'PORT': '',
    }
}


INTERNAL_IPS = ('127.0.0.1', )   #added for debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

INSTALLED_APPS += ('debug_toolbar',)

    
