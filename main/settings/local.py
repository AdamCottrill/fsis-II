from main.settings.base import *

DATABASES = {
    'default': {
<<<<<<< HEAD
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/db/fsis2.db' % root(),
      }


    #'default': {
    #     'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #     'NAME': 'fsis2',
    #     'USER': 'adam',
    #     'PASSWORD': 'django',
    #
    # }


#          'ENGINE': 'django.db.backends.postgresql_psycopg2',
#          'NAME': 'snippets',
#  ***REMOVED***
#          'Password': 'adam',
        #  'HOST': '',
        #  'PORT': '',

=======
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'fsis2',
 ***REMOVED***
 ***REMOVED***
     }
>>>>>>> 4e315ca2b10ddf64238133ee8ed784527acff6bf
}


INTERNAL_IPS = ('127.0.0.1', )   #added for debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',)


